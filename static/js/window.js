document.querySelector(".max").onclick = function () {
    document.querySelector(".window").classList.toggle("maximized")
}

document.querySelector(".cls").onclick = function () {
    document.querySelector(".window").style.display = "none"
}

document.querySelector(".note-pad").ondblclick = function () {
    setTimeout( ()=> { this.classList.remove("selected") }, 2 )
    document.querySelector(".window").style.display = "initial"
    document.querySelector(".window").classList.remove("minimized")
}