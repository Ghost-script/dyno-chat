# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect
from django.template import Context, RequestContext
from home.forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from profiles.models import CustomUser

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        request_user = authenticate(username=username, password=password)
        if request_user is not None:
            login(request, request_user)
            CustomClient = CustomUser.objects.get(user=request_user)
            CustomClient.is_online = True
            CustomClient.save()
            return True
        else:
            return False
    return False

def logout_user(request):
    CustomClient = CustomUser.objects.get(user=request.user)
    CustomClient.is_online = False
    CustomClient.save()
    logout(request)
    return redirect('/')
    
def index(request):
    if request.user.is_authenticated():
		return redirect('/chat/')
    registration_form = RegistrationForm(auto_id=False)
    login_form = LoginForm(auto_id=False)
    if not request.user.is_authenticated():
        if request.method == 'POST':

            if request.POST['commit'] == 'Sign In':
                if login_user(request):
                    return redirect('/profile/')
                else:
                    return redirect('/')

            elif request.POST['commit'] == 'Register':
                new_user = User.objects.create_user(
                username = request.POST['username'],
                email = request.POST['email'],
                password = request.POST['password'],
            )
            new_user.first_name = request.POST['firstname']
            new_user.last_name = request.POST['lastname']
            new_user.is_staff = False
            new_user.is_superuser = False
            new_user.save()

            new_user_custom = CustomUser.objects.create(
                user = new_user,
                )
            new_user_custom.is_online = True
            new_user_custom.save()

            request_user = authenticate(username=request.POST['username'],
                    password=request.POST['password'])
            login(request,request_user)
            return redirect('/profile/')
        else:
            context = RequestContext(request, {
			'activate_navbar_element' : 'kickchat',
            'registration_form' : registration_form,
            'login_form' : login_form,
            'request_user' : request.user,
            })
            return render_to_response('home/home.html',context_instance=context)

    context = RequestContext(request, {
        'activate_navbar_element' : 'kickchat',
        'request_user' : request.user,
        })

    return render_to_response('home/home.html',context_instance=context)
    
def about(request):
    login_form = LoginForm(auto_id=False)
    
    context = RequestContext(request, {
            'activate_navbar_element_id' : 'about',
			'login_form' : login_form,
            'request_user' : request.user,
    })
    return render_to_response('home/about.html', context_instance=context)
