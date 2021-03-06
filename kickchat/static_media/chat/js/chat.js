 function scroll_down() {
        var messages_container_height = $('#messages-container').height();
			//$("#message-column").animate({ scrollTop: messages_container_height }, "fast");        
        $('#message-column').scrollTop(messages_container_height);
    }
$(document).ready(function(){
    $(window).resize(function(){
        
        // Chat Table resize
        var window_height = $(window).height();
        var navbar_height = 60;
        var message_box_height = 40;
        var message_container_height = window_height - navbar_height - message_box_height;
        message_column_id="#message-column";
        $(message_column_id).height(message_container_height);
        console.log(message_container_height);

        // Chat Input group resize
        var chat_input_group_width = $('#message-column').width();
        var chat_submit_button_width = $('#chat-submit-button').width();
        var chat_input_width = chat_input_group_width - chat_submit_button_width;
        console.log(chat_input_width);
        $('#chat-input').width(chat_input_width - 50);
        scroll_down();
    });
    $(window).resize();


    // Scroll to the bottom of messages
   
    //scroll_down();
});
$("#chat-input").keypress(function(e) {
    if(e.which == 13) {
        $("#chat-submit-button").click();
    }
});