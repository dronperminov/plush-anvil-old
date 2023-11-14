const GALLERY_CLOSE_ICON = `<svg class="gallery-stroke-icon" width="30px" height="30px" viewBox="-0.5 0 25 25" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 21.32L21 3.32001" stroke-width="1.5"/>
    <path d="M3 3.32001L21 21.32" stroke-width="1.5"/>
</svg>`

const GALLERY_DOWNLOAD_ICON = `<svg class="gallery-stroke-icon" width="30px" height="30px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 15V18C20 19.1046 19.1046 20 18 20H6C4.89543 20 4 19.1046 4 18L4 15M8 11L12 15M12 15L16 11M12 15V3" stroke-width="1.5" fill="none" />
</svg>`

const GALLERY_MARKUP_ICON = `<svg class="gallery-fill-icon" width="30px" height="30px" viewBox="0 0 56 56" xmlns="http://www.w3.org/2000/svg">
    <path d="M 13.7851 49.5742 L 42.2382 49.5742 C 47.1366 49.5742 49.5743 47.1367 49.5743 42.3086 L 49.5743 13.6914 C 49.5743 8.8633 47.1366 6.4258 42.2382
    6.4258 L 13.7851 6.4258 C 8.9101 6.4258 6.4257 8.8398 6.4257 13.6914 L 6.4257 42.3086 C 6.4257 47.1602 8.9101 49.5742 13.7851 49.5742 Z M 28.0117 35.8164
    C 19.6913 35.8164 13.7148 39.8242 11.1835 44.9102 C 10.5507 44.2774 10.1992 43.3633 10.1992 42.1211 L 10.1992 13.8789 C 10.1992 11.4414 11.5117 10.1992
    13.8554 10.1992 L 42.1679 10.1992 C 44.4882 10.1992 45.8007 11.4414 45.8007 13.8789 L 45.8007 42.1211 C 45.8007 43.3399 45.4726 44.2774 44.8398 44.8867 C
    42.3320 39.8008 36.5429 35.8164 28.0117 35.8164 Z M 28.0117 31.9023 C 32.4882 31.9492 36.0273 28.1289 36.0273 23.1133 C 36.0273 18.4023 32.4882 14.5118
    28.0117 14.5118 C 23.5351 14.5118 19.9726 18.4023 19.9960 23.1133 C 20.0429 28.1289 23.5351 31.8320 28.0117 31.9023 Z"/>
</svg>`

const GALLERY_LINK_ICON = `<svg class="gallery-fill-icon" width="30px" height="30px" viewBox="-2 -2 28 28" xmlns="http://www.w3.org/2000/svg">
    <path d="M15.7285 3.88396C17.1629 2.44407 19.2609 2.41383 20.4224 3.57981C21.586 4.74798 21.5547 6.85922 20.1194 8.30009L17.6956 10.7333C17.4033 11.0268 17.4042 11.5017 17.6976 11.794C17.9911 12.0863 18.466 12.0854 18.7583 11.7919L21.1821 9.35869C23.0934 7.43998 23.3334 4.37665 21.4851 2.5212C19.6346 0.663551 16.5781 0.905664 14.6658 2.82536L9.81817 7.69182C7.90688 9.61053 7.66692 12.6739 9.51519 14.5293C9.80751 14.8228 10.2824 14.8237 10.5758 14.5314C10.8693 14.2391 10.8702 13.7642 10.5779 13.4707C9.41425 12.3026 9.44559 10.1913 10.8809 8.75042L15.7285 3.88396Z"/>
    <path d="M14.4851 9.47074C14.1928 9.17728 13.7179 9.17636 13.4244 9.46868C13.131 9.76101 13.1301 10.2359 13.4224 10.5293C14.586 11.6975 14.5547 13.8087 13.1194 15.2496L8.27178 20.1161C6.83745 21.556 4.73937 21.5863 3.57791 20.4203C2.41424 19.2521 2.44559 17.1408 3.88089 15.6999L6.30473 13.2667C6.59706 12.9732 6.59614 12.4984 6.30268 12.206C6.00922 11.9137 5.53434 11.9146 5.24202 12.2081L2.81818 14.6413C0.906876 16.5601 0.666916 19.6234 2.51519 21.4789C4.36567 23.3365 7.42221 23.0944 9.33449 21.1747L14.1821 16.3082C16.0934 14.3895 16.3334 11.3262 14.4851 9.47074Z"/>
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

const GALLERY_TRANSITION = "transform 150ms"
const GALLERY_DEFAULT_MODE = "default"
const GALLERY_SWIPE_MODE = "swipe"
const GALLERY_HORIZONTAL_SWIPE_MODE = "swipe-horizontal"
const GALLERY_VERTICAL_SWIPE_MODE = "swipe-vertical"
const GALLERY_SCALE_MODE = "scale"
const GALLERY_MARKUP_MODE = "markup"

const GALLERY_BBOX_MIN_SIZE = 20
const GALLERY_RESIZE_OFFSET = 10

function Gallery(popupId, markups = null, users = null, isAdmin, withAlbumLinks) {
    this.isAdmin = isAdmin

    this.popup = document.getElementById(popupId)
    this.body = document.getElementsByTagName("body")[0]
    this.open = false
    this.mode = GALLERY_DEFAULT_MODE

    this.offsetX = 0
    this.offsetY = 0

    this.bbox = null
    this.users = users

    this.BuildControls(withAlbumLinks)
    this.BuildPhotos(markups)
    this.BuildMarkup()
    this.InitEvents()
}

Gallery.prototype.BuildControls = function(withAlbumLinks) {
    let topControls = this.MakeElement("gallery-top-controls", this.popup)

    let topInfo = this.MakeElement("gallery-top-info", topControls)
    this.positionSpan = this.MakeElement("gallery-top-info-text", topInfo, {}, "span")

    if (this.isAdmin) {
        this.markupControl = this.MakeElement("gallery-top-control", topControls, {innerHTML: GALLERY_MARKUP_ICON, title: "Перейти в альбом"})
        this.markupControl.addEventListener("click", () => this.Markup())
    }

    if (withAlbumLinks) {
        this.albumLink = this.MakeElement("", null, {}, "a")
        let albumIcon = this.MakeElement("gallery-top-control", topControls, {innerHTML: GALLERY_LINK_ICON})
        albumIcon.addEventListener("click", () => this.GoToAlbum())
    }

    this.downloadLink = this.MakeElement("", null, {download: ""}, "a")
    let downloadIcon = this.MakeElement("gallery-top-control", topControls, {innerHTML: GALLERY_DOWNLOAD_ICON})
    downloadIcon.addEventListener("click", () => this.Download())

    let close = this.MakeElement("gallery-top-control", topControls, {innerHTML: GALLERY_CLOSE_ICON})
    close.addEventListener("click", () => this.Close())

    this.prev = this.MakeElement("gallery-prev-control", this.popup, {innerHTML: GALLERY_LEFT_ICON})
    this.prev.addEventListener("click", () => this.Prev())

    this.next = this.MakeElement("gallery-next-control", this.popup, {innerHTML: GALLERY_RIGHT_ICON})
    this.next.addEventListener("click", () => this.Next())
}

Gallery.prototype.BuildPhotos = function(markups) {
    this.gallery = this.MakeElement("gallery-photos", this.popup)
    this.photos = []

    for (let image of document.getElementsByClassName("gallery-source"))
        this.AddPhoto(image, markups[this.photos.length])

    this.photoIndex = 0
}

Gallery.prototype.AddPhoto = function(image, markup) {
    let index = this.photos.length
    image.setAttribute("data-index", index)
    image.addEventListener("click", () => this.ShowPhoto(image))

    let alt = image.getAttribute("alt")
    let previewUrl = image.getAttribute("src")
    let originalUrl = image.getAttribute("data-src")
    let albumId = +image.getAttribute("data-album-id")

    let photo = this.MakeElement("gallery-photo", this.gallery)
    let photoImage = this.MakeElement("gallery-photo-image", photo, {alt: alt}, "img")
    let loader = this.MakeElement("gallery-loader", photo, {innerHTML: GALLERY_LOADER_ICON})

    photoImage.addEventListener("load", () => this.LoadImage(loader, photo, photoImage, markup))
    photo.addEventListener("contextmenu", (e) => e.preventDefault())
    this.photos.push({original: originalUrl, image: photoImage, loader: loader, block: photo, albumId: albumId})
}

Gallery.prototype.BuildMarkup = function() {
    this.usersMarkup = this.MakeElement("gallery-users-markup gallery-hidden", this.popup)

    for (let user of Object.values(this.users)) {
        let userMarkup = this.MakeElement("gallery-user-markup", this.usersMarkup)
        let avatar = this.MakeElement("gallery-user-avatar", userMarkup)
        let img = this.MakeElement("gallery-user-avatar-image", avatar, {src: user.image_src, alt: `аватар пользователя ${user.username}`}, "img")
        let fullname = this.MakeElement("gallery-user-fullname", userMarkup, {innerText: `${user.fullname}`})

        userMarkup.addEventListener("click", () => this.AddUserMarkup(user.username))
    }
}

Gallery.prototype.InitEvents = function() {
    this.gallery.addEventListener("mousedown", (e) => this.TouchStart(e))
    this.gallery.addEventListener("mousemove", (e) => this.TouchMove(e))
    this.gallery.addEventListener("mouseup", (e) => this.TouchEnd(e))
    this.gallery.addEventListener("mouseleave", (e) => this.TouchEnd(e))

    this.gallery.addEventListener("touchstart", (e) => this.TouchStart(e))
    this.gallery.addEventListener("touchmove", (e) => this.TouchMove(e))
    this.gallery.addEventListener("touchend", (e) => this.TouchEnd(e))
    this.gallery.addEventListener("touchleave", (e) => this.TouchEnd(e))

    this.gallery.addEventListener("transitionend", () => this.TransitionEnd())
    window.addEventListener("resize", () => this.Resize())
    document.addEventListener("keydown", (e) => this.KeyDown(e))
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

Gallery.prototype.LoadImage = function(loader, block, image, markup) {
    loader.remove()

    for (let bbox of markup) {
        let x = bbox.x * image.clientWidth + image.offsetLeft
        let y = bbox.y * image.clientHeight + image.offsetTop
        let width = bbox.width * image.clientWidth
        let height = bbox.height * image.clientHeight

        let userBbox = this.MakeElement("gallery-bbox gallery-finished-bbox", block, {style: `left: ${x}px; top: ${y}px; width: ${width}px; height: ${height}px;`})
        this.AddInfoToBbox(userBbox, bbox.username, bbox.markup_id, bbox.x, bbox.y, bbox.width, bbox.height, true)
    }
}

Gallery.prototype.AddDataAttributesToBbox = function(bbox, x, y, width, height) {
    bbox.setAttribute("data-x", x)
    bbox.setAttribute("data-y", y)
    bbox.setAttribute("data-width", width)
    bbox.setAttribute("data-height", height)
}

Gallery.prototype.AddInfoToBbox = function(bbox, username, markupId, x, y, width, height, isFirst = false) {
    this.AddDataAttributesToBbox(bbox, x, y, width, height)

    let removeIcon = this.MakeElement("gallery-remove-bbox", bbox, {innerHTML: GALLERY_CLOSE_ICON})
    let userName = this.MakeElement("gallery-fullname-bbox", bbox)
    let user = this.MakeElement("gallery-fullname-span", userName, {innerText: this.users[username].fullname})
    removeIcon.addEventListener("click", () => this.RemoveUserMarkup(bbox, markupId))

    if (!this.isAdmin || isFirst)
        removeIcon.children[0].classList.add("gallery-hidden")
}

Gallery.prototype.Show = function() {
    if (this.photos.length == 1) {
        this.prev.classList.add("gallery-hidden")
        this.next.classList.add("gallery-hidden")
    }
    else {
        this.prev.classList.remove("gallery-hidden")
        this.next.classList.remove("gallery-hidden")
    }

    for (let delta of [0, -1, 1]) {
        let index = this.GetIndex(delta)
        let photo = this.photos[index]

        if (!photo.image.getAttribute("src"))
            photo.image.setAttribute("src", photo.original)
    }

    this.gallery.style.transform = `translate(${(-this.photoIndex + this.offsetX) * 100}%, ${this.offsetY * 100}%)`
    this.photos[this.photoIndex].image.style.transform = null

    for (let bbox of document.getElementsByClassName("gallery-bbox")) {
        bbox.style.transform = null
        this.ResizeBbox(bbox, this.photos[this.photoIndex].image)
    }

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
    if (this.mode == GALLERY_MARKUP_MODE) {
        this.Markup()
        this.mode = GALLERY_DEFAULT_MODE
    }

    this.popup.classList.remove("gallery-open")
    this.body.classList.remove("gallery-body")
    this.open = false
}

Gallery.prototype.GetIndex = function(delta = 0) {
    return (this.photoIndex + delta + this.photos.length) % this.photos.length
}

Gallery.prototype.Next = function() {
    if (this.mode == GALLERY_MARKUP_MODE && this.bbox !== null)
        this.Escape()

    this.gallery.style.transition = GALLERY_TRANSITION
    this.photoIndex = this.GetIndex(1)
    this.Show()
}

Gallery.prototype.Prev = function() {
    if (this.mode == GALLERY_MARKUP_MODE && this.bbox !== null)
        this.Escape()

    this.gallery.style.transition = GALLERY_TRANSITION
    this.photoIndex = this.GetIndex(-1)
    this.Show()
}

Gallery.prototype.GoToAlbum = function() {
    let albumId = this.photos[this.photoIndex].albumId
    this.albumLink.setAttribute("href", `/albums/${albumId}`)
    this.albumLink.click()
}

Gallery.prototype.Download = function() {
    this.downloadLink.setAttribute("href", this.photos[this.photoIndex].original)
    this.downloadLink.click()
}

Gallery.prototype.Markup = function() {
    this.markupControl.classList.toggle("gallery-selected-icon")
    this.mode = this.mode == GALLERY_DEFAULT_MODE ? GALLERY_MARKUP_MODE : GALLERY_DEFAULT_MODE
    this.usersMarkup.classList.add("gallery-hidden")

    for (let bbox of document.getElementsByClassName("gallery-bbox")) {
        if (bbox.classList.contains("gallery-editing-bbox"))
            continue

        let removeIcon = bbox.getElementsByClassName("gallery-remove-bbox")[0]

        if (this.mode == GALLERY_MARKUP_MODE)
            removeIcon.children[0].classList.remove("gallery-hidden")
        else
            removeIcon.children[0].classList.add("gallery-hidden")
    }

    if (this.mode != GALLERY_MARKUP_MODE && this.bbox !== null) {
        this.bbox.div.remove()
        this.bbox = null
    }
}

Gallery.prototype.Escape = function() {
    if (this.mode != GALLERY_MARKUP_MODE) {
        this.Close()
        return
    }

    if (this.bbox === null) {
        this.Markup()
        return
    }

    this.usersMarkup.classList.add("gallery-hidden")
    this.bbox.div.remove()
    this.bbox = null
}

Gallery.prototype.KeyDown = function(e) {
    if (!this.open)
        return

    if (e.code == "Escape") {
        e.preventDefault()
        this.Escape()
        return
    }

    if (this.mode != GALLERY_DEFAULT_MODE)
        return

    if (e.code == "ArrowLeft") {
        e.preventDefault()
        this.Prev()
    }
    else if (e.code == "ArrowRight") {
        e.preventDefault()
        this.Next()
    }
    else if (e.code == "KeyS" && e.ctrlKey) {
        e.preventDefault()
        this.Download()
    }
}

Gallery.prototype.GetPosition = function(e) {
    if (!e.touches)
        return {x: e.clientX / this.popup.clientWidth, y: e.clientY / this.popup.clientHeight}

    if (e.touches.length != 2)
        return {x: e.touches[0].clientX / this.popup.clientWidth, y: e.touches[0].clientY / this.popup.clientHeight}

    return {
        p1: {x: e.touches[0].clientX, y: e.touches[0].clientY}, 
        p2: {x: e.touches[1].clientX, y: e.touches[1].clientY}
    }
}

Gallery.prototype.TouchStart = function(e) {
    if (this.offsetX != 0 && e.touches && e.touches.length == 2)
        return

    this.isPressed = true
    this.position = this.GetPosition(e)
    this.initialPosition = this.GetPosition(e)

    if (this.mode == GALLERY_MARKUP_MODE) {
        this.MarkupStart(e)
    }
    else {
        this.mode = e.touches && e.touches.length == 2 ? GALLERY_SCALE_MODE : GALLERY_SWIPE_MODE
    }

    this.gallery.style.transition = null
}

Gallery.prototype.TouchMove = function(e) {
    e.preventDefault()

    if (this.mode == GALLERY_SWIPE_MODE || this.mode == GALLERY_HORIZONTAL_SWIPE_MODE || this.mode == GALLERY_VERTICAL_SWIPE_MODE) {
        this.SwipeMove(e)
    }
    else if (this.mode == GALLERY_SCALE_MODE) {
        this.ScaleMove(e)
    }
    else if (this.mode == GALLERY_MARKUP_MODE) {
        this.MarkupMove(e)
    }
}

Gallery.prototype.TouchEnd = function(e) {
    if (!this.isPressed)
        return

    if (this.mode == GALLERY_SWIPE_MODE || this.mode == GALLERY_HORIZONTAL_SWIPE_MODE || this.mode == GALLERY_VERTICAL_SWIPE_MODE) {
        this.SwipeEnd()
    }
    else if (this.mode == GALLERY_SCALE_MODE) {
        this.ScaleEnd()
    }
    else if (this.mode == GALLERY_MARKUP_MODE) {
        this.MarkupEnd()
    }

    this.isPressed = false
}

Gallery.prototype.SwipeMove = function(e) {
    if (!this.isPressed)
        return

    let position = this.GetPosition(e)
    let dx = position.x - this.initialPosition.x
    let dy = position.y - this.initialPosition.y

    if (this.photos.length > 1 && (Math.abs(dx) > Math.abs(dy) && this.mode == GALLERY_SWIPE_MODE || this.mode == GALLERY_HORIZONTAL_SWIPE_MODE)) {
        this.offsetX += position.x - this.position.x
        this.offsetY = 0
        this.mode = GALLERY_HORIZONTAL_SWIPE_MODE
    }
    else {
        this.offsetX = 0
        this.offsetY += position.y - this.position.y
        this.mode = GALLERY_VERTICAL_SWIPE_MODE
    }

    this.position = position
    this.Show()
}

Gallery.prototype.SwipeEnd = function() {
    if (Math.abs(this.offsetY) > 0.2) {
        this.Close()
    }
    else if (this.offsetX < -0.2) {
        this.photoIndex = this.GetIndex(1)
    }
    else if (this.offsetX > 0.2) {
        this.photoIndex = this.GetIndex(-1)
    }

    this.offsetX = 0
    this.offsetY = 0
    this.gallery.style.transition = GALLERY_TRANSITION
    this.mode = GALLERY_DEFAULT_MODE
    this.Show()
}

Gallery.prototype.GetDistance = function(p1, p2) {
    let dx = p2.x - p1.x
    let dy = p2.y - p1.y
    return Math.sqrt(dx * dx + dy * dy)
}

Gallery.prototype.ScaleMove = function(e) {
    if (!this.isPressed)
        return

    let block = this.photos[this.photoIndex].block
    let image = this.photos[this.photoIndex].image

    let position = this.GetPosition(e)
    let prevSize = this.GetDistance(this.position.p1, this.position.p2)
    let currSize = this.GetDistance(position.p1, position.p2)
    let scale = currSize / prevSize

    let x = (this.position.p1.x + this.position.p2.x) / 2 - (image.offsetLeft + image.clientWidth / 2)
    let y = (this.position.p1.y + this.position.p2.y) / 2 - (image.offsetTop + image.clientHeight / 2)

    image.style.transform = `translate(${x}px, ${y}px) scale(${Math.max(1, scale)}) translate(${-x}px, ${-y}px)`

    for (let bbox of document.getElementsByClassName("gallery-bbox")) {
        x = (this.position.p1.x + this.position.p2.x) / 2 - (bbox.offsetLeft + bbox.clientWidth / 2)
        y = (this.position.p1.y + this.position.p2.y) / 2 - (bbox.offsetTop + bbox.clientHeight / 2)

        bbox.style.transform = `translate(${x}px, ${y}px) scale(${Math.max(1, scale)}) translate(${-x}px, ${-y}px)`
    }
}

Gallery.prototype.ScaleEnd = function() {
    this.mode = GALLERY_DEFAULT_MODE
}

Gallery.prototype.IsInsideBbox = function(x, y, bbox) {
    let horizontal = bbox.x - GALLERY_RESIZE_OFFSET <= x && x <= bbox.x + bbox.width + GALLERY_RESIZE_OFFSET
    let vertical = bbox.y - GALLERY_RESIZE_OFFSET <= y && y <= bbox.y + bbox.height + GALLERY_RESIZE_OFFSET
    return horizontal && vertical
}

Gallery.prototype.GetMarkupCursor = function(x, y) {
    if (this.bbox === null)
        return "default"

    let left = Math.abs(this.bbox.x - x) < GALLERY_RESIZE_OFFSET
    let right = Math.abs(this.bbox.x + this.bbox.width - x) < GALLERY_RESIZE_OFFSET
    let top = Math.abs(this.bbox.y - y) < GALLERY_RESIZE_OFFSET
    let bottom = Math.abs(this.bbox.y + this.bbox.height - y) < GALLERY_RESIZE_OFFSET

    if (left) {
        if (top)
            return "nw-resize"

        if (bottom)
            return "sw-resize"

        return "w-resize"
    }

    if (right) {
        if (top)
            return "ne-resize"

        if (bottom)
            return "se-resize"

        return "e-resize"
    }

    if (top)
        return "n-resize"

    if (bottom)
        return "s-resize"

    if (this.IsInsideBbox(x, y, this.bbox))
        return "move"

    return "default"
}

Gallery.prototype.MarkupStart = function(e) {
    let block = this.photos[this.photoIndex].block
    let image = this.photos[this.photoIndex].image
    let x = this.position.x * this.popup.clientWidth
    let y = this.position.y * this.popup.clientHeight

    this.usersMarkup.classList.add("gallery-hidden")

    if (this.bbox !== null && !this.IsInsideBbox(x, y, this.bbox)) {
        this.bbox.div.remove()
        this.bbox = null
    }

    if (x < image.offsetLeft || y < image.offsetTop || x > image.offsetLeft + image.clientWidth || y > image.offsetTop + image.clientHeight)
        return

    if (this.bbox === null) {
        this.bbox = {x: x, y: y, width: 0, height: 0, mode: "default", div: this.MakeElement("gallery-bbox gallery-editing-bbox", block, {style: `left: ${x}px; top: ${y}px;`}), username: null}
        return
    }

    let cursor = this.GetMarkupCursor(x, y)
    block.style.cursor = cursor
    this.bbox.mode = cursor
}

Gallery.prototype.MoveBboxHorizontally = function(image, x1, x2) {
    let dx = x2 - x1

    if (this.bbox.x + dx < image.offsetLeft || this.bbox.x + this.bbox.width + dx > image.offsetLeft + image.clientWidth)
        return

    this.bbox.x += dx
    this.position.x = Math.max(image.offsetLeft, Math.min(image.offsetLeft + image.clientWidth, x2)) / this.popup.clientWidth
}

Gallery.prototype.MoveBboxVertically = function(image, y1, y2) {
    let dy = y2 - y1

    if (this.bbox.y + dy < image.offsetTop || this.bbox.y + this.bbox.height + dy > image.offsetTop + image.clientHeight)
        return

    this.bbox.y += dy
    this.position.y = Math.max(image.offsetTop, Math.min(image.offsetTop + image.clientHeight, y2)) / this.popup.clientHeight
}

Gallery.prototype.ResizeBboxHorizontally = function(image, x1, x2) {
    dx = x2 - x1

    if (this.bbox.mode == "nw-resize" || this.bbox.mode == "sw-resize" || this.bbox.mode == "w-resize") {
        if (this.bbox.width - dx < GALLERY_BBOX_MIN_SIZE || this.bbox.x + dx < image.offsetLeft)
            return

        this.bbox.x += dx
        this.bbox.width -= dx

    }
    else if (this.bbox.mode == "ne-resize" || this.bbox.mode == "se-resize" || this.bbox.mode == "e-resize") {
        if (this.bbox.width + dx < GALLERY_BBOX_MIN_SIZE || this.bbox.x + this.bbox.width + dx > image.offsetLeft + image.clientWidth)
            return

        this.bbox.width += dx
    }

    this.position.x = Math.max(image.offsetLeft, Math.min(image.offsetLeft + image.clientWidth, x2)) / this.popup.clientWidth
}

Gallery.prototype.ResizeBboxVertically = function(image, y1, y2) {
    let dy = y2 - y1

    if (this.bbox.mode == "nw-resize" || this.bbox.mode == "ne-resize" || this.bbox.mode == "n-resize") {
        if (this.bbox.height - dy < GALLERY_BBOX_MIN_SIZE || this.bbox.y + dy < image.offsetTop)
            return

        this.bbox.y += dy
        this.bbox.height -= dy

    }
    else if (this.bbox.mode == "sw-resize" || this.bbox.mode == "se-resize" || this.bbox.mode == "s-resize") {
        if (this.bbox.height + dy < GALLERY_BBOX_MIN_SIZE || this.bbox.y + this.bbox.height + dy > image.offsetTop + image.clientHeight)
            return

        this.bbox.height += dy
    }

    this.position.y = Math.max(image.offsetTop, Math.min(image.offsetTop + image.clientHeight, y2)) / this.popup.clientHeight
}

Gallery.prototype.MarkupMove = function(e) {
    let position = this.GetPosition(e)
    let x2 = position.x * this.popup.clientWidth
    let y2 = position.y * this.popup.clientHeight

    let cursor = this.GetMarkupCursor(x2, y2)
    let block = this.photos[this.photoIndex].block
    block.style.cursor = cursor

    if (!this.isPressed || this.bbox === null)
        return

    let x1 = this.position.x * this.popup.clientWidth
    let y1 = this.position.y * this.popup.clientHeight
    let image = this.photos[this.photoIndex].image

    if (this.bbox.mode == "default") {
        x2 = Math.max(image.offsetLeft, Math.min(image.offsetLeft + image.clientWidth, x2))
        y2 = Math.max(image.offsetTop, Math.min(image.offsetTop + image.clientHeight, y2))

        this.bbox.x = Math.min(x1, x2)
        this.bbox.y = Math.min(y1, y2)
        this.bbox.width = Math.abs(x2 - x1)
        this.bbox.height = Math.abs(y2 - y1)
    }
    else if (this.bbox.mode == "move") {
        this.MoveBboxHorizontally(image, x1, x2)
        this.MoveBboxVertically(image, y1, y2)
    }
    else {
        this.ResizeBboxHorizontally(image, x1, x2)
        this.ResizeBboxVertically(image, y1, y2)
    }

    this.bbox.div.style = `left: ${this.bbox.x}px; top: ${this.bbox.y}px; width: ${this.bbox.width}px; height: ${this.bbox.height}px;`
}

Gallery.prototype.PlaceUsersMarkup = function() {
    this.usersMarkup.classList.remove("gallery-hidden")

    let px = (this.popup.clientWidth - this.usersMarkup.offsetWidth) / 2

    if (this.bbox.x + Math.max(this.bbox.width, this.usersMarkup.offsetWidth) < this.popup.clientWidth)
        px = this.bbox.x
    else if (this.bbox.x + this.bbox.width - this.usersMarkup.offsetWidth > 0)
        px = this.bbox.x + this.bbox.width - this.usersMarkup.offsetWidth

    let py = this.bbox.y + this.bbox.height + this.usersMarkup.clientHeight > this.popup.clientHeight ? this.bbox.y - this.usersMarkup.clientHeight : this.bbox.y + this.bbox.height

    this.usersMarkup.style = `left: ${px}px; top: ${py}px;`
}

Gallery.prototype.MarkupEnd = function() {
    if (!this.bbox)
        return

    if (this.bbox.width < GALLERY_BBOX_MIN_SIZE || this.bbox.height < GALLERY_BBOX_MIN_SIZE) {
        this.bbox.div.remove()
        this.bbox = null
        return
    }

    this.PlaceUsersMarkup()

    let image = this.photos[this.photoIndex].image
    let x = (this.bbox.x - image.offsetLeft) / image.clientWidth
    let y = (this.bbox.y - image.offsetTop) / image.clientHeight
    let width = this.bbox.width / image.clientWidth
    let height = this.bbox.height / image.clientHeight
    this.AddDataAttributesToBbox(this.bbox.div, x, y, width, height)
}

Gallery.prototype.AddUserMarkup = function(username) {
    if (this.bbox === null)
        return

    let url = this.photos[this.photoIndex].original
    let albumId = this.photos[this.photoIndex].albumId
    let image = this.photos[this.photoIndex].image
    let x = (this.bbox.x - image.offsetLeft) / image.clientWidth
    let y = (this.bbox.y - image.offsetTop) / image.clientHeight
    let width = this.bbox.width / image.clientWidth
    let height = this.bbox.height / image.clientHeight
    let bbox = this.bbox.div

    SendRequest("/add-user-markup", {album_id: albumId, username: username, x: x, y: y, width: width, height: height, photo_url: url}).then(response => {
        if (response.status != "success") {
            bbox.classList.add("gallery-error-bbox")
            return
        }

        this.bbox = null
        bbox.classList.remove("gallery-error-bbox")
        bbox.classList.remove("gallery-editing-bbox")
        bbox.classList.add("gallery-finished-bbox")
        this.usersMarkup.classList.add("gallery-hidden")
        this.AddInfoToBbox(bbox, username, response.markup_id, x, y, width, height)
    })
}

Gallery.prototype.RemoveUserMarkup = function(bbox, markupId) {
    let url = this.photos[this.photoIndex].original
    let albumId = this.photos[this.photoIndex].albumId

    SendRequest("/remove-user-markup", {album_id: albumId, photo_url: url, markup_id: markupId}).then(response => {
        if (response.status != "success") {
            bbox.classList.add("gallery-error-bbox")
            return
        }

        bbox.remove()
    })
}

Gallery.prototype.TransitionEnd = function() {
    this.gallery.style.transition = null
}

Gallery.prototype.ResizeBbox = function(bbox, image) {
    let x = +bbox.getAttribute("data-x") * image.clientWidth + image.offsetLeft
    let y = +bbox.getAttribute("data-y") * image.clientHeight + image.offsetTop
    let width = +bbox.getAttribute("data-width") * image.clientWidth
    let height = +bbox.getAttribute("data-height") * image.clientHeight
    bbox.style = `left: ${x}px; top: ${y}px; width: ${width}px; height: ${height}px;`
}

Gallery.prototype.Resize = function() {
    let image = this.photos[this.photoIndex].image

    for (let bbox of document.getElementsByClassName("gallery-bbox"))
        this.ResizeBbox(bbox, image)

    if (this.bbox === null)
        return

    this.bbox.x = this.bbox.div.offsetLeft
    this.bbox.y = this.bbox.div.offsetTop
    this.bbox.width = this.bbox.div.clientWidth
    this.bbox.height = this.bbox.div.clientHeight

    this.PlaceUsersMarkup()
}
