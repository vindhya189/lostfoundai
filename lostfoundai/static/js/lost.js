const upload =
document.getElementById("imageUpload");

const preview =
document.getElementById("preview");

upload.addEventListener("change",(e)=>{

const file =
e.target.files[0];

if(file){

preview.src =
URL.createObjectURL(file);

preview.style.display =
"block";

}

});