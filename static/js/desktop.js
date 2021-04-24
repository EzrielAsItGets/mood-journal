let time = document.querySelector(".time")
time.innerHTML = new Intl.DateTimeFormat('en-IN', { hour: 'numeric', minute: 'numeric', hour12: true }).format(new Date())
time.setAttribute("title", new Intl.DateTimeFormat('en-IN', { hour: 'numeric', minute: 'numeric', hour12: true, year: 'numeric', month: 'long', day: 'numeric' }).format(new Date()))

let timeSetter = setInterval(() => {
    time.innerHTML = new Intl.DateTimeFormat('en-IN', { hour: 'numeric', minute: 'numeric', hour12: true }).format(new Date())
    time.setAttribute("title", new Intl.DateTimeFormat('en-IN', { hour: 'numeric', minute: 'numeric', hour12: true, year: 'numeric', month: 'long', day: 'numeric' }).format(new Date()))
}, 60000);

document.querySelector(".desktop").onclick = function () {
    document.querySelectorAll(".icon").forEach((e) => {
        e.classList.remove("selected")
    })
}

document.querySelectorAll(".icon").forEach((icon) => {
    icon.onclick = function () {
        setTimeout(() => {
            document.querySelectorAll(".icon").forEach((e) => {
                e.classList.remove("selected")
            })
            this.classList.add("selected")
        }, 1);
    }
})

document.querySelector(".load-entry").ondblclick = function () {
    setTimeout( ()=> { this.classList.remove("selected") }, 2 )
    window.location.replace("/load")
}

document.querySelector(".blacklist").ondblclick = function () {
    setTimeout( ()=> { this.classList.remove("selected") }, 2 )
    window.location.replace("/blacklist")
}

document.querySelector(".create-entry").ondblclick = function () {
    setTimeout( ()=> { this.classList.remove("selected") }, 2 )
    window.location.replace("/create")
}

document.querySelector(".logout-button").ondblclick = function () {
    setTimeout( ()=> { this.classList.remove("selected") }, 2 )
    window.location.replace("/logout")
}