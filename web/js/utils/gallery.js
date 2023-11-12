const GALLERY_CLOSE_ICON = `<svg class="gallery-stroke-icon" width="30px" height="30px" viewBox="-0.5 0 25 25" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 21.32L21 3.32001" stroke-width="1.5"/>
    <path d="M3 3.32001L21 21.32" stroke-width="1.5"/>
</svg>`

const GALLERY_DOWNLOAD_ICON = `<svg class="gallery-stroke-icon" width="30px" height="30px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 15V18C20 19.1046 19.1046 20 18 20H6C4.89543 20 4 19.1046 4 18L4 15M8 11L12 15M12 15L16 11M12 15V3" stroke-width="1.5" />
</svg>`

const GALLERY_LEFT_ICON = `<svg width="30px" height="30px" viewBox="100 -100 1024 1024" xmlns="http://www.w3.org/2000/svg">
    <path d="M768 903.232l-50.432 56.768L256 512l461.568-448 50.432 56.768L364.928 512z" />
</svg>`

const GALLERY_RIGHT_ICON = `<svg width="30px" height="30px" viewBox="-100 -100 1024 1024" xmlns="http://www.w3.org/2000/svg">
    <path d="M256 120.768L306.432 64 768 512l-461.568 448L256 903.232 659.072 512z" />
</svg>`

const GALLERY_LOADER_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="62px" height="62px" viewBox="-20 -20 296 296" fill="#000">
    <path d="M248,91.3V67H80v8H9c0,0,10.7,40.6,67.3,40.6c30.3,0,34.4,12.7,34.4,19.1c0,8.4-5.1,21.9-36.7,32.8V191h38.7
    c6.8-5.2,15.3-8.2,24.5-8.2s17.7,3.1,24.5,8.2H201c0,0,0-15.1,0-22.9c-23.4-7.7-38.7-20.4-38.7-34.8
    C162.3,110.6,200.1,92.5,248,91.3z M80,87c-52,0-52-4-52-4h52C80,83,80,85.4,80,87z M88,79v-4h152v4H88z"/>
    <animateTransform xmlns="http://www.w3.org/2000/svg" attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="0.9s" repeatCount="indefinite"/>
</svg>`

function Gallery(popupId) {
    this.popup = document.getElementById(popupId)
    this.body = document.getElementsByTagName("body")[0]
    this.downloadLink = this.MakeElement("", null, {download: ""}, "a")
    this.open = false

    this.BuildControls()
    this.BuildPhotos()
}

Gallery.prototype.BuildControls = function() {
    let topControls = this.MakeElement("gallery-top-controls", this.popup)

    let topInfo = this.MakeElement("gallery-top-info", topControls)
    this.positionSpan = this.MakeElement("gallery-top-info-text", topInfo, {}, "span")

    let download = this.MakeElement("gallery-top-control", topControls, {innerHTML: GALLERY_DOWNLOAD_ICON})
    download.addEventListener("click", () => this.Download())

    let close = this.MakeElement("gallery-top-control", topControls, {innerHTML: GALLERY_CLOSE_ICON})
    close.addEventListener("click", () => this.Close())

    let prev = this.MakeElement("gallery-prev-control", this.popup, {innerHTML: GALLERY_LEFT_ICON})
    prev.addEventListener("click", () => this.Prev())

    let next = this.MakeElement("gallery-next-control", this.popup, {innerHTML: GALLERY_RIGHT_ICON})
    next.addEventListener("click", () =>this.Next())

    document.addEventListener("keydown", (e) => this.KeyDown(e))
}

Gallery.prototype.BuildPhotos = function() {
    this.gallery = this.MakeElement("gallery-photos", this.popup)
    this.photos = []

    for (let image of document.getElementsByClassName("gallery-source")) {
        image.setAttribute("data-index", this.photos.length)
        image.addEventListener("click", () => this.ShowPhoto(image))

        let alt = image.getAttribute("alt")
        let previewUrl = image.getAttribute("src")
        let originalUrl = image.getAttribute("data-src")

        let photo = this.MakeElement("gallery-photo", this.gallery)
        let photoImage = this.MakeElement("gallery-photo-image", photo, {alt: alt}, "img")
        let loader = this.MakeElement("gallery-loader", photo, {innerHTML: GALLERY_LOADER_ICON})
        photoImage.addEventListener("load", () => loader.remove())
        this.photos.push({original: originalUrl, image: photoImage, loader: loader})
    }

    this.photoIndex = 0
}

Gallery.prototype.SetAttributes = function(element, attributes) {
    if (attributes === null)
        return

    for (let [name, value] of Object.entries(attributes)) {
        if (name == "innerText")
            element.innerText = value
        else if (name == "innerHTML")
            element.innerHTML = value
        else
            element.setAttribute(name, value)
    }
}

Gallery.prototype.MakeElement = function(className, parent = null, attributes = null, tagName = "div") {
    let element = document.createElement(tagName)
    element.className = className

    this.SetAttributes(element, attributes)

    if (parent !== null)
        parent.appendChild(element)

    return element
}

Gallery.prototype.Show = function() {
    this.photos[this.photoIndex].image.setAttribute("src", this.photos[this.photoIndex].original)
    this.gallery.style.transform = `translateX(-${this.photoIndex * 100}%)`
    this.positionSpan.innerText = `${this.photoIndex + 1} / ${this.photos.length}`
}

Gallery.prototype.ShowPhoto = function(image) {
    this.photoIndex = +image.getAttribute("data-index")

    this.Open()
    this.Show()
}

Gallery.prototype.Open = function() {
    if (this.open)
        return

    this.popup.classList.add("gallery-open")
    this.body.classList.add("gallery-body")
    this.open = true
    this.Show()
}

Gallery.prototype.Close = function() {
    this.popup.classList.remove("gallery-open")
    this.body.classList.remove("gallery-body")
    this.open = false
}

Gallery.prototype.Next = function() {
    this.photoIndex = (this.photoIndex + 1) % this.photos.length
    this.Show()
}

Gallery.prototype.Prev = function() {
    this.photoIndex = (this.photoIndex - 1 + this.photos.length) % this.photos.length
    this.Show()
}

Gallery.prototype.Download = function() {
    this.downloadLink.setAttribute("href", this.photos[this.photoIndex].original)
    this.downloadLink.click()
}

Gallery.prototype.KeyDown = function(e) {
    if (!this.open)
        return

    if (e.code == "ArrowLeft") {
        e.preventDefault()
        this.Prev()
    }
    else if (e.code == "ArrowRight") {
        e.preventDefault()
        this.Next()
    }
    else if (e.code == "Escape") {
        e.preventDefault()
        this.Close()
    }
    else if (e.code == "KeyS" && e.ctrlKey) {
        e.preventDefault()
        this.Download()
    }
}
