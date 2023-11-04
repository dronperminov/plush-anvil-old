function AddPlace() {
    let placeData = {
        color: "transparent",
        photos: []
    }

    placeData.name = GetTextField("name", "Название не указано")
    if (placeData.name === null)
        return

    placeData.metro_station = GetTextField("metro-station", "Станиця метро не указана")
    if (placeData.metro_station === null)
        return

    placeData.address = GetTextField("address", "Адрес не указан")
    if (placeData.address === null)
        return

    let error = document.getElementById("error")
    error.innerText = ""

    SendRequest("/add-place", placeData).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        location.reload()
    })
}

function ChangeColor(colorInput, place) {
    let error = GetBlock(colorInput, "place").getElementsByClassName("error")[0]
    error.innerText = ""

    SendRequest("/change-place-color", {name: place, color: colorInput.value}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }
    })
}

function DeletePlace(icon, place) {
    if (!confirm(`Вы уверены, что хотите удалить место с названием "${place}"`))
        return

    let placeBlock = GetBlock(icon, "place")
    let error = placeBlock.getElementsByClassName("error")[0]
    error.innerText = ""

    SendRequest("/delete-place", {name: place}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message

            setTimeout(() => error.innerText = "", 1500)
            return
        }

        placeBlock.remove()
    })
}
