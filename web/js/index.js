function CloseAllDetails() {
    for (let details of document.getElementsByClassName("quiz-details"))
        details.classList.add("hidden")
}

function CloseDetails(detailsId) {
    let body = document.getElementsByTagName("body")[0]
    body.classList.remove("no-overflow")

    let details = document.getElementById(detailsId)
    details.classList.add("hidden")
}

function ShowDetails(detailsId) {
    CloseAllDetails()

    let body = document.getElementsByTagName("body")[0]
    body.classList.add("no-overflow")

    let details = document.getElementById(detailsId)
    details.classList.remove("hidden")
}
