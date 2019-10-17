var button = document.querySelector('.upload_button');
var upload = document.querySelector('.upload');
var arrow = document.querySelector('.arrow');
var ok = document.querySelector('.ok');

button.addEventListener('click', function() {
  upload.classList.toggle('uploading')
  arrow.classList.toggle('arrow-out')

    if(arrow.classList.contains('arrow-out')){
      ok.classList.add('bounce');
    }else{
      ok.classList.remove('bounce');
    }
  if (button.getAttribute("data-text-swap") == button.innerHTML) {
    button.innerHTML = button.getAttribute("data-text-original");
  } else {
    button.setAttribute("data-text-original", button.innerHTML);
    button.innerHTML = button.getAttribute("data-text-swap");
  }
});
