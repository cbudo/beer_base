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

    var retrieved = sessionStorage.getItem('username');
    if(retrieved) {
        return retrieved;
    }
    else {
        return null;
    }
}

function retrieve_logout_status() {

    var result = sessionStorage.getItem('login_status');
    console.log(result);
    return result;
}

function change_username_prompt() {
    var logout = retrieve_logout_status();
    if(logout === "hide"){
        $('#username_button').html("Logout");
        var username = $('#username_input').val();
        save_username_locally(username);
        $('#username_input').hide();
        $('#username_label').hide();
        $('#username_text').html(retrieve_username());
        $('#username_text').show();
        save_logout_status_locally("show");
    }
    else {
        $('#username_button').html("Submit");
        $('#username_input').show();
        $('#username_label').show();
        $('#username_text').hide();
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
        $('#username_input').hide();
        $('#username_label').hide();
        $('#username_text').html(retrieve_username());
        $('#username_text').show();
    }
    else {
        $('#username_input').show();
        $('#username_label').show();
        $('#username_text').hide();
    }

}