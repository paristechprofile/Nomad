// prevents refresh of page when you toggle the sidebar
$('.fa-bars').click(function(e){
  e.preventDefault();
  $('.ui.labeled.icon.sidebar').sidebar('toggle')
});
