# Create your views here.
from django.shortcuts import render, render_to_response, redirect
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from chat.models import message
from profiles.models import CustomUser
from django.contrib.auth.models import User
import json

import time

from pulsar import HttpException
from pulsar.apps import ws
from pulsar.apps.data import PubSubClient, create_store
from pulsar.utils.system import json
from pulsar.utils.security import random_string


activated_navbar_element = 'chat'


def index(request):
	if not request.user.is_authenticated():
		return redirect('/')
	from django.template import RequestContext
	messages = []
	if message.objects.count() > 0:
		latest_message = message.objects.latest('time')
		if latest_message.id > 31:
			messages = message.objects.all()[latest_message.id-30:latest_message.id]
		else:
			messages = message.objects.all()
	else:
		latest_message = []
	online_users = CustomUser.objects.filter(is_online=True)
	current_user = User.objects.get(username=request.user.username)
	context = RequestContext(request, {
		'msg' : messages,
		'online_users' : online_users,
		'activate_navbar_element_id' : 'chat',
		'request_user' : request.user,
		'HOST': request.get_host()
		})

	return render_to_response('chat/chat.html', context_instance=context)


class ChatClient(PubSubClient):

	def __init__(self, websocket):
		self.joined = time.time()
		self.websocket = websocket

	def __call__(self, channel, message):
		# The message is an encoded JSON string
		self.websocket.write(message, opcode=1)


class Chat(ws.WS):
	''':class:`.WS` handler managing the chat application.'''
	_store = None
	_pubsub = None
	_client = None

	def get_pubsub(self, websocket):
		'''Create the pubsub handler if not already available'''
		if not self._store:
			cfg = websocket.cfg
			self._store = create_store(cfg.data_store)
			self._client = self._store.client()
			self._pubsub = self._store.pubsub()
			webchat = '%s:webchat' % cfg.exc_id
			chatuser = '%s:chatuser' % cfg.exc_id
			self._pubsub.subscribe(webchat, chatuser)
		return self._pubsub

	def on_open(self, websocket):
		'''A new websocket connection is established.

		Add it to the set of clients listening for messages.
		'''
		self.get_pubsub(websocket).add_client(ChatClient(websocket))
		user, _ = self.user(websocket)
		users_key = 'webchatusers:%s' % websocket.cfg.exc_id
		# add counter to users
		registered = yield self._client.hincrby(users_key, user, 1)
		if registered == 1:
			self.publish(websocket, 'chatuser', 'joined')

	def on_close(self, websocket):
		'''Leave the chat room
		'''
		user, waste= self.user(websocket)
		users_key = 'webchatusers:%s' % websocket.cfg.exc_id
		registered = yield self._client.hincrby(users_key, user, -1)
		if not registered:
			self.publish(websocket, 'chatuser', 'gone')
		if registered <= 0:
			self._client.hdel(users_key, user)

	def on_message(self, websocket, msg):
		'''When a new message arrives, it publishes to all listening clients.
		'''
		if msg:
			lines = []
			for l in msg.split('\n'):
				l = l.strip()
				if l:
					lines.append(l)
			msg = ' '.join(lines)
			if msg:
				time=datetime.now().strftime('%b %d `%y, %H:%M:%S')
				user,=self.user(websocket)
				mesg = message(username=user,
					  time=time,
					  message=msg
						)
				mesg.save()
		
				self.publish(websocket, 'webchat', msg,time)

	def user(self, websocket):
		user = websocket.handshake.get('django.user')
		if user.is_authenticated():
			return user.username, True
		else:
			session = websocket.handshake.get('django.session')
			user = session.get('chatuser')
			if not user:
				user = 'an_%s' % random_string(length=6).lower()
				session['chatuser'] = user
			return user, False

	def publish(self, websocket, channel, message='',time=None):
		if(time==None):
			time=datetime.now().strftime('%b %d `%y, %H:%M:%S')
	
		user, authenticated = self.user(websocket)
		msg = {'message': message,
			   'user': user,
			   'authenticated': authenticated,
			   'channel': channel,
			   'time': time}
		channel = '%s:%s' % (websocket.cfg.exc_id, channel)
		return self._pubsub.publish(channel, json.dumps(msg))


class middleware(object):
	'''Django middleware for serving the Chat websocket.'''
	def __init__(self):
		self._web_socket = ws.WebSocket('/chat/chat-input', Chat())

	def process_request(self, request):
		from django.http import HttpResponse
		environ = request.META
		environ['django.user'] = request.user
		environ['django.session'] = request.session
		try:
			response = self._web_socket(environ)
		except HttpException as e:
			return HttpResponse(status=e.status)
		if response is not None:
			# we have a response, this is the websocket upgrade.
			# Convert to django response
			resp = HttpResponse(status=response.status_code,
								content_type=response.content_type)
			for header, value in response.headers:
				resp[header] = value
			return resp
		else:
			environ.pop('django.user')
			environ.pop('django.session')
