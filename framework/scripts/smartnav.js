var CURRENT = "current";

window.onload = function(){
  $("#menu > a").click(function(event){
    var $this = $(this);
    load($this.attr('id'));
    event.preventDefault();
  });

  var cur = localStorage.getItem(CURRENT);
  if(!cur){
  	load("<inject-home>");
  }else{
    activeLink(cur);
  }
};

function activeLink(id){
    $("#menu>a.active").removeClass("active");
    $("#" + id).addClass("active");
}

function load(id){
    $.get(id + "?ajax=true",
    function(data, status){
    	localStorage.setItem(CURRENT, id);
	if(history.pushState) {
	  history.pushState(null, null, id);
	}
	else {
	  location.hash = id;
	}
        $("#main").html(data);
        activeLink(id);
    });	
}

