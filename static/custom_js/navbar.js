/**
* Created by steve on 5/9/17.
*/

function save_username_locally(username){

    return sessionStorage.setItem('username', username);

}

function save_logout_status_locally(status) {

    return sessionStorage.setItem('login_status', status);

}

function retrieve_username() {

    return sessionStorage.getItem('username');
}

function retrieve_logout_status() {

    return sessionStorage.getItem('login_status');
}

function registration_call(method){

    var server_endpoint = '/create_user';
    if (method){
        server_endpoint = '/login';
    }

    var username = $('#username_input').val();

    var letterNumber = /^[0-9a-zA-Z]+$/;
    if(!username.match(letterNumber)) {
        alert('Username cannot have special characters.');
        return;
    }

    $.ajax({headers : {},
        type: "POST",
        data: {
            "username" : username
        },
        dataType: "json",
        url: server_endpoint,
        success: function (data) {
            change_username_prompt(username);
        },
        error: function (data) {
            alert("Query for existing user failed - could not log in.");
        }
    });
}

function change_username_prompt(username) {
    var logout = retrieve_logout_status();
    if(logout === "hide"){
        save_username_locally(username);
        $('#username_log_out').show();
        $('#sign_up_button').hide();
        $('#username_input').hide();
        $('#username_label').hide();
        $('#username_text').html(retrieve_username());
        $('#username_text').attr('href','/recommend/'.concat(retrieve_username()));
        $('#username_text').show();
        $('#username_button').hide();
        save_logout_status_locally("show");
    }
    else {
        $('#username_log_out').hide();
        $('#sign_up_button').show();
        $('#username_input').show();
        $('#username_label').show();
        $('#username_text').hide();
        $('#username_button').show();
        save_logout_status_locally("hide");
    }
}

function check_on_load(){
    var logout = retrieve_logout_status();
    if(logout === null) {
        logout = "hide";
        save_logout_status_locally(logout);
    }
    if(logout === "show"){
        $('#username_log_out').show();
        $('#sign_up_button').hide();
        $('#username_input').hide();
        $('#username_label').hide();
        $('#username_text').html(retrieve_username());
        $('#username_text').attr('href','/recommend/'.concat(retrieve_username()));
        $('#username_text').show();
        $('#username_button').hide();
    }
    else {
        $('#username_log_out').hide();
        $('#sign_up_button').show();
        $('#username_input').show();
        $('#username_label').show();
        $('#username_text').hide();
        $('#username_button').show();
    }

}