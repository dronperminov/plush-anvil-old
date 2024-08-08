const DELETE_ICON = `<svg width="22px" height="22px" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"">
    <path d="M12 4h3c.6 0 1 .4 1 1v1H3V5c0-.6.5-1 1-1h3c.2-1.1 1.3-2 2.5-2s2.3.9 2.5 2zM8 4h3c-.2-.6-.9-1-1.5-1S8.2 3.4 8 4zM4 7h11l-.9 10.1c0 .5-.5.9-1 .9H5.9c-.5 0-.9-.4-1-.9L4 7z"/>
</svg>`

const STAR_STROKE_ICON = `<svg width="16px" height="16px" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <path d="M32.001,2.484c0.279,0,0.463,0.509,0.463,0.509l8.806,18.759l20.729,3.167L47,40.299L50.541,62
    l-18.54-10.254L13.461,62l3.541-21.701L2.003,24.919l20.729-3.167L31.53,3.009C31.53,3.009,31.722,2.484,32.001,2.484 M32.001,0.007
    c-0.775,0-1.48,0.448-1.811,1.15l-8.815,18.778L1.701,22.941c-0.741,0.113-1.356,0.632-1.595,1.343
    c-0.238,0.71-0.059,1.494,0.465,2.031l14.294,14.657l-3.378,20.704c-0.124,0.756,0.195,1.517,0.822,1.957
    C12.653,63.877,13.057,64,13.461,64c0.332,0,0.666-0.084,0.968-0.25l17.572-9.719l17.572,9.719c0.302,0.166,0.636,0.25,0.968,0.25
    c0.404,0,0.808-0.123,1.151-0.366c0.627-0.44,0.946-1.201,0.822-1.957l-3.378-20.704l14.294-14.657
    c0.523-0.537,0.703-1.321,0.465-2.031c-0.238-0.711-0.854-1.229-1.595-1.343l-19.674-3.006L33.812,1.157
    C33.481,0.455,32.776,0.007,32.001,0.007L32.001,0.007z"/>
</svg>`

const STAR_FILL_ICON = `<svg width="16px" height="16px" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <path d="M63.893,24.277c-0.238-0.711-0.854-1.229-1.595-1.343l-19.674-3.006L33.809,1.15
        C33.479,0.448,32.773,0,31.998,0s-1.48,0.448-1.811,1.15l-8.815,18.778L1.698,22.935c-0.741,0.113-1.356,0.632-1.595,1.343
        c-0.238,0.71-0.059,1.494,0.465,2.031l14.294,14.657L11.484,61.67c-0.124,0.756,0.195,1.517,0.822,1.957
        c0.344,0.243,0.747,0.366,1.151,0.366c0.332,0,0.666-0.084,0.968-0.25l17.572-9.719l17.572,9.719c0.302,0.166,0.636,0.25,0.968,0.25
        c0.404,0,0.808-0.123,1.151-0.366c0.627-0.44,0.946-1.201,0.822-1.957l-3.378-20.704l14.294-14.657
        C63.951,25.771,64.131,24.987,63.893,24.277z"/>
</svg>`

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

    let photoBlock = MakeElement("photo", null)
    block.prepend(photoBlock)

    return SendRequest("/upload-photo", data).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = "некоторые фотографии не удалось загрузить"
            block.removeChild(photoBlock)
            return false
        }

        if (response.added) {
            let remove = MakeElement("interactive-fill-icon photo-remove", photoBlock, {innerHTML: DELETE_ICON})
            remove.children[0].addEventListener("click", () => DeletePhoto(remove.children[0], albumId, response.src))
            let starStroke = MakeElement("interactive-fill-icon photo-preview", photoBlock, {innerHTML: STAR_STROKE_ICON})
            starStroke.addEventListener("click", () => SetPreview(starStroke, albumId, response.preview_src))
            let starFill = MakeElement("interactive-fill-icon photo-preview photo-album-preview hidden", photoBlock, {innerHTML: STAR_FILL_ICON})

            let img = MakeElement("gallery-source", photoBlock, {tag: "img", "src": response.preview_src, "data-src": response.src, "data-album-id": albumId})
            let error = MakeElement("error", photoBlock)
            gallery.AddPhoto(img, [])
            block.scrollIntoView({behaviors: "smooth"})
            noPhotos.classList.add("hidden")
        }
        else {
            block.removeChild(photoBlock)
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
    let photos = document.getElementById("photos")
    let saveIcon = document.getElementById("save-album")
    let cancelIcon = document.getElementById("cancel-edit-album")
    let editIcon = document.getElementById("edit-album")
    let editBlock = document.getElementById("edit-block")

    photos.classList.add("photos-edit")
    saveIcon.classList.remove("hidden")
    cancelIcon.classList.remove("hidden")
    editIcon.classList.add("hidden")
    editBlock.classList.remove("hidden")
}

function CancelEdit() {
    let photos = document.getElementById("photos")
    let saveIcon = document.getElementById("save-album")
    let cancelIcon = document.getElementById("cancel-edit-album")
    let editIcon = document.getElementById("edit-album")
    let editBlock = document.getElementById("edit-block")
    let originalTitle = document.getElementById("original-title")

    let title = document.getElementById("album-title")
    title.value = originalTitle.innerText

    photos.classList.remove("photos-edit")
    saveIcon.classList.add("hidden")
    cancelIcon.classList.add("hidden")
    editIcon.classList.remove("hidden")
    editBlock.classList.add("hidden")
}

function SaveAlbum(albumId) {
    let title = GetTextField("album-title", "Введено пустое название альбома")
    if (title === null)
        return

    let originalTitle = document.getElementById("original-title")
    if (title == originalTitle.innerText) {
        CancelEdit()
        return
    }

    let error = document.getElementById("error")
    error.innerText = ""

    SendRequest("/rename-album", {album_id: albumId, title: title}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

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
            photo.classList.remove("hidden")

        for (let photo of document.getElementsByClassName("photo-album-preview"))
            photo.classList.add("hidden")

        icon.classList.add("hidden")
        let albumPreview = GetChildBlock(block, "photo-album-preview")
        albumPreview.classList.remove("hidden")
    })
}

function UpdateUsersPhotos() {
    let users = document.getElementById("users")
    let only = document.getElementById("only").checked
    let usernames = []

    for (let checkbox of users.getElementsByTagName("input"))
        if (checkbox.checked)
            usernames.push(`usernames=${checkbox.getAttribute("data-username")}`)

    location.href = `/photos-with-users?${usernames.join("&")}` + (only ? "&only=true" : "")
}

function ResetUsersPhotos() {
    location.href = `/photos-with-users`
}