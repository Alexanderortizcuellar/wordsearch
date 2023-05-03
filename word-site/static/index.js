function tabManager(evt, tab) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("settings");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tab-btn");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
    tablinks[i].style.backgroundColor = "rgba(76, 175, 80, 1.0)"
  }
  document.getElementById(tab).style.display = "block";
  evt.currentTarget.className += " active";
  evt.currentTarget.style.backgroundColor = "rgba(76, 175, 80, 0.8)"
}
