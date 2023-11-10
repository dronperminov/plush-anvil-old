function ParseOrganizer(organizerId = "") {
    let organizerData = {}

    organizerData.name = GetTextField(`name${organizerId}`, "Название не указано")
    if (organizerData.name === null)
        return null

    organizerData.description = GetTextField(`description${organizerId}`, "Описание не указано")
    if (organizerData.description === null)
        return null

    return organizerData
}

function AddOrganizer() {
    let organizerData = ParseOrganizer()
    if (organizerData === null)
        return

    let error = document.getElementById("error")
    error.innerText = ""

    SendRequest("/add-organizer", organizerData).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        location.reload()
    })
}

function UpdateOrganizer(button, organizerId) {
    let organizerData = ParseOrganizer(organizerId)
    if (organizerData == null)
        return

    let organizerBlock = GetBlock(button, "organizer")
    organizerData.original_name = organizerBlock.getAttribute("data-name")

    let error = GetChildBlock(organizerBlock, "error")
    error.innerText = ""

    SendRequest("/update-organizer", organizerData).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        organizerBlock.setAttribute("data-name", organizerData.name)
        let button = organizerBlock.getElementsByClassName("save-button")[0]
        button.classList.add("hidden")
    })
}

function DeleteOrganizer(icon, organizer) {
    if (!confirm(`Вы уверены, что хотите удалить организатора с названием "${organizer}"`))
        return

    let organizerBlock = GetBlock(icon, "organizer")
    let error = organizerBlock.getElementsByClassName("error")[0]
    error.innerText = ""

    SendRequest("/delete-organizer", {name: organizer}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        organizerBlock.remove()
    })
}
