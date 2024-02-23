let table = document.querySelector("table")

let tds = document.querySelectorAll("table td")
tds.forEach((td)=>{
	td.setAttribute("draggable", "true")
})


tds.forEach((td)=>{
td.addEventListener("dragstart", (e)=>{
	e.preventDefault()
	let elem = document.createElement("div");
	elem.classList.add("line")
	td.appendChild(elem)
	td.classList.add("selected")
	})
})
