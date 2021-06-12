function get_action(form, user){
  text=document.getElementById('plantId').innerHTML;
  url = "/eventdry/"+user+"/"+text;
  form.action= url;
}
