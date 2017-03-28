var menuShown = false;

function showFilterMenu() {
  if(!menuShown) {
    $(".filter-wrapper").show();
    $(".overlay").show();
    menuShown = true;
    $( ".overlay" ).bind( "click", function() {
      closeMenu();
      console.log("Closing")
    });
  }
  else {
    closeMenu()
  }
}

function closeMenu() {
  $(".filter-wrapper").hide();
  $(".overlay").hide();
  menuShown = false;
}
