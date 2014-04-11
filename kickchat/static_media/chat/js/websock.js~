(function ($) {
    "use strict";
    $.wschat = function (ws) {
        var messages = $('#messages'),
            users = $('#users'),
            message = $('#chat-input'),
            user_label,
            who_ami,
            content,
            wall = function (user, message,time,action) {
					if (action=="joined")
					{
						var color="text-success";
					}
					else
					{
						if (action=="left")
						{
							var color="text-danger";
						}
						else
						{
							var color="";
						}
					}
						content="<tr>"+
					"<td class='chat-username'><a href=''><b>" + user + "</b></a></td>"+
               "<td class='chat-message "+color+"'>" + message + "</td>"+
               "<td class='chat-timestamp'><small>" + time+ "</small></td>"+
                "</tr>";                
                messages.append(content);
                scroll_down();
            };

        ws.onmessage = function (e) {
            var data = $.parseJSON(e.data),
            //    label = 'info">@',
                user = data.user,
                time=data.time,
                userid = 'chatuser-' + user;
            if (!data.authenticated) {
                label = 'inverse">';
            }
            
            if (!who_ami) {
                who_ami = user;
            }
            //user_label = '<span class="label label-' + label + user + '</span>';
            if (data.channel === 'webchat') {
                wall(user, data.message,time,"normal");
            } else if (data.channel === 'chatuser') {
                if (data.message === 'joined') {
                    if (users.find('#' + userid).length === 0) {
								content="<li class='list-group-item' id='"+userid+"'>"+
								"<a href='/profile' class='text-primary' target='blank' style='border:0px;'>"
                			+"<!--<img src='/static/images/images.jpg' height=20px width=20px</img>-->"+
                			"<b>"+user+"</b></a></li>";                        
                        users.append(content);
                        wall(user, 'joined the chat',time,'joined');
                    }
                } else {
                    wall(user, 'left the chat',time,'left');
                    users.find('#' + userid).remove();
                }
            }
        };
        $('#chat-submit-button').click(function () {
            var msg = message.val();
            ws.send(msg);
            message.val('');
        });
    };

}(jQuery));
