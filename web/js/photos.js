function ShowAlbumPopup() {
    let body = document.getElementsByTagName("body")[0]
    let popup = document.getElementById("album-popup")
    body.classList.add("no-overflow")
    popup.classList.remove("hidden")
}

function CancelAlbum() {
    let body = document.getElementsByTagName("body")[0]
    let popup = document.getElementById("album-popup")

    body.classList.remove("no-overflow")
    popup.classList.add("hidden")

    let name = document.getElementById("album-name")
    name.value = ""
    InputError("album-name")
}

function CreateAlbum() {
    let title = GetTextField("album-title", "Название альома не заполнено")
    if (title === null)
        return

    let error = document.getElementById("album-error")
    error.innerText = ""

    SendRequest("/add-album", {title}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        location.href = response.url
    })
}

function DeleteAlbum(icon, albumId) {
    if (!confirm("Вы уверены, что хотите удалить этот альбом?"))
        return

    let block = GetBlock(icon, "photo-album")
    let error = GetChildBlock(block, "error")
    error.innerText = ""

    SendRequest("/remove-album", {album_id: albumId}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        block.remove()
    })
}