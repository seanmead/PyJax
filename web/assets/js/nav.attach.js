var menu = document.getElementById('menu');
var wrap = document.getElementById('nav-wrap');
var scrollTimeout = null;

window.onscroll = function() {
    scrollTimeout = setTimeout(scrollEvent, 50);
};

function scrollEvent() {
    if (window.scrollY >= wrap.offsetTop) menu.className = 'fixed';
    else menu.className = '';
}