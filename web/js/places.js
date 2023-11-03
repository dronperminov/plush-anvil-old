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
