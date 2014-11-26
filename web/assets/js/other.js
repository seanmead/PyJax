/**
 * Created by seanmead on 11/25/14.
 */


function logout(){
    $.post("/Logout",
    function(data, status){
	   loadOuterLinks();
	   load('Login');
    });
}

var INNER_LINKS = ["Home", "About", "Logout"];
var OUTER_LINKS = ["Home", "About", "Login", "Register"];

function loadOuterLinks(){
    for (var index = 0; index < INNER_LINKS.length; ++index) {
	    $('#' + INNER_LINKS[index]).addClass('hidden');
    }

    for (index = 0; index < OUTER_LINKS.length; ++index) {
	    $('#' + OUTER_LINKS[index]).removeClass('hidden');
    }

}

function loadInnerLinks(){
    for (index = 0; index < OUTER_LINKS.length; ++index) {
	    $('#' + OUTER_LINKS[index]).addClass('hidden');
    }
    for (var index = 0; index < INNER_LINKS.length; ++index) {
	    $('#' + INNER_LINKS[index]).removeClass('hidden');
    }
}