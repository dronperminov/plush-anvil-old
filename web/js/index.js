function CloseAllDetails() {
    for (let details of document.getElementsByClassName("quiz-details"))
        details.classList.add("hidden")
}

function CloseDetails(detailsId) {
    let scrollable = document.getElementById("scrollable")
    let details = document.getElementById(detailsId)
    details.classList.add("hidden")
    scrollable.scrollTo({top: 0, left: +details.getAttribute("data-scroll"), behavior: 'smooth'});
}

function ShowDetails(detailsId) {
    CloseAllDetails()

    let details = document.getElementById(detailsId)
    details.classList.remove("hidden")
    details.children[0].scrollIntoView({behavior: 'smooth', block: 'nearest', inline: 'center'})

    let scrollable = document.getElementById("scrollable")
    details.setAttribute("data-scroll", scrollable.scrollLeft)
}
