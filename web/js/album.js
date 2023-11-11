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
