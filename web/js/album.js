function SelectImages() {
    let input = document.getElementById("images-input")
    input.click()
}

function UploadImage(file, albumId) {
    let block = document.getElementById("photos")
    let error = document.getElementById("error")
    let noPhotos = document.getElementById("no-photos")

    let data = new FormData()
    data.append("image", file)
    data.append("album_id", albumId)

    return SendRequest("/upload-photo", data).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = "некоторые фотографии не удалось загрузить"
            return false
        }

        if (response.added) {
            let photoBlock = MakeElement("photo", block)
            let link = MakeElement("", photoBlock, {tag: "a", "href": response.src})
            let img = MakeElement("", link, {tag: "img", "src": response.preview_src})
            photoBlock.scrollIntoView({behaviors: "smooth"})
            noPhotos.classList.add("hidden")
        }

        return true
    })
}

function UploadImages() {
    let input = document.getElementById("images-input")
    let block = document.getElementById("photos")
    let error = document.getElementById("error")
    error.innerText = ""

    let albumId = +block.getAttribute("data-album-id")
    let fetches = []

    for (let file of input.files)
        fetches.push(UploadImage(file, albumId))

    Promise.all(fetches)
}

function DeletePhoto(icon, albumId, photoUrl) {
    if (!confirm("Вы уверены, что хотите удалить это фото?"))
        return

    let block = GetBlock(icon, "photo")
    let photosBlock = block.parentNode
    let noPhotos = document.getElementById("no-photos")
    let error = GetChildBlock(block, "error")
    error.innerText = ""

    SendRequest("/remove-photo", {album_id: albumId, photo_url: photoUrl}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        block.remove()

        if (photosBlock.children.length == 0)
            noPhotos.classList.remove("hidden")
    })
}

function EditAlbum() {
    let saveIcon = document.getElementById("save-album")
    let cancelIcon = document.getElementById("cancel-edit-album")
    let editIcon = document.getElementById("edit-album")
    let editBlock = document.getElementById("edit-block")

    saveIcon.classList.remove("hidden")
    cancelIcon.classList.remove("hidden")
    editIcon.classList.add("hidden")
    editBlock.classList.remove("hidden")
}

function CancelEdit() {
    let saveIcon = document.getElementById("save-album")
    let cancelIcon = document.getElementById("cancel-edit-album")
    let editIcon = document.getElementById("edit-album")
    let editBlock = document.getElementById("edit-block")
    let originalTitle = document.getElementById("original-title")

    let title = document.getElementById("album-title")
    title.value = originalTitle.innerText

    saveIcon.classList.add("hidden")
    cancelIcon.classList.add("hidden")
    editIcon.classList.remove("hidden")
    editBlock.classList.add("hidden")
}

function SaveAlbum(albumId) {
    let title = GetTextField("album-title", "Введено пустое название альбома")
    if (title === null)
        return

    let error = document.getElementById("error")
    error.innerText = ""

    SendRequest("/rename-album", {album_id: albumId, title: title}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        let originalTitle = document.getElementById("original-title")
        originalTitle.innerText = title

        CancelEdit()
    })
}

function SetPreview(icon, albumId, previewUrl) {
    let block = GetBlock(icon, "photo")
    let error = GetChildBlock(block, "error")
    error.innerText = ""

    SendRequest("/set-album-preview", {album_id: albumId, preview_url: previewUrl}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        for (let photo of document.getElementsByClassName("photo-preview"))
            photo.classList.remove("photo-album-preview")

        icon.classList.add("photo-album-preview")
    })
}
