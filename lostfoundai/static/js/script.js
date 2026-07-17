// Counter Animation

const counters = document.querySelectorAll(".counter");

counters.forEach(counter => {

let target = parseInt(counter.dataset.target);

let count = 0;

let speed = target / 100;

let update = () => {

if(count < target){

count += speed;

counter.innerText = Math.floor(count);

requestAnimationFrame(update);

}else{

counter.innerText = target + "+";

}

};

update();

});

// Dark Mode

const themeBtn = document.getElementById("themeToggle");

if(themeBtn){

themeBtn.addEventListener("click",()=>{

document.body.classList.toggle("light-mode");

});

}