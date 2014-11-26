//%%%%%%%%%%%%%%%%%%%%%%%%%__NAVIGATION__%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function activeLink(id) {
    $('nav>a.active').removeClass('active');
    $('#' + id).addClass('active');
}

function load(id) {
    if (id != location.pathname.substring(1)) {
        main(id);
        state(id);
    }
}

function refresh() {
    var id = location.pathname.substring(1);
    main(id);
    state(id);
}

function state(id) {
    if (history.pushState) history.pushState(null, null, id);
    else location.hash = id;
}

function main(id) {
    $.get(id + '?ajax=true', function(data, status) {
        $('#main').html(data);
        activeLink(id);
        $('a[load]').click(hasLoad);
    });
}

window.onpopstate = function(event) {
    main(location.pathname.substring(1));
};

$('nav > a').click(function(event) {
    var $this = $(this);
    load($this.attr('id'));
    event.preventDefault();
});

$(document).ready(function() {
    $('a[load]').click(hasLoad);
});

function hasLoad(event){
    var $this = $(this);
    load($this.attr('load'));
    event.preventDefault();
}

var cur = location.pathname.substring(1);
if (cur) activeLink(cur);
else load('<inject-home>');

//%%%%%%%%%%%%%%%%%%%%%%%__END_NAVIGATION__%%%%%%%%%%%%%%%%%%%%%%%%%%