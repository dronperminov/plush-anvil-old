const MIN_SIZE = 50


function ImageCropper(blockId) {
    this.block = document.getElementById(blockId)
    this.image = this.block.children[0]
    this.cropper = this.block.children[1]
    this.cropperPath = this.cropper.children[0]

    if ((('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0))) {
        this.block.addEventListener("touchstart", (e) => this.MouseDown(this.ConvertTouchEvent(e)))
        this.block.addEventListener("touchmove", (e) => this.MouseMove(this.ConvertTouchEvent(e)))
        this.block.addEventListener("touchend", (e) => this.MouseUp())
        this.block.addEventListener("touchleave", (e) => this.MouseUp())
    }
    else {
        this.block.addEventListener("mousedown", (e) => this.MouseDown(e))
        this.block.addEventListener("mousemove", (e) => this.MouseMove(e))
        this.block.addEventListener("mouseup", (e) => this.MouseUp())
        this.block.addEventListener("mouseleave", (e) => this.MouseUp())
    }
}

ImageCropper.prototype.ConvertTouchEvent = function(e) {
    let rect = this.block.getBoundingClientRect()
    e.offsetX = e.targetTouches[0].clientX - rect.x
    e.offsetY = e.targetTouches[0].clientY - rect.y
    return e
}

ImageCropper.prototype.Init = function() {
    this.size = Math.min(this.image.clientWidth, this.image.clientHeight)
    this.offsetX = (this.image.clientWidth - this.size) / 2
    this.offsetY = (this.image.clientHeight - this.size) / 2

    this.Update()
}

ImageCropper.prototype.Update = function() {
    this.size = Math.max(MIN_SIZE, Math.min(this.size, Math.min(this.image.clientWidth, this.image.clientHeight)))
    this.offsetX = Math.max(0, Math.min(this.image.clientWidth - this.size, this.offsetX))
    this.offsetY = Math.max(0, Math.min(this.image.clientHeight - this.size, this.offsetY))

    let w = this.image.clientWidth
    let h = this.image.clientHeight
    let r = this.size / 2

    this.cropper.setAttribute("viewBox", `0 0 ${w} ${h}`)
    this.cropperPath.setAttribute("d", `M0 0 H${w} V${h} H${-w}z M ${this.offsetX} ${this.offsetY + r} a ${r},${r} 0 1,0 ${2*r},0 a ${r},${r} 0 1,0 ${-2*r},0z`)
}

ImageCropper.prototype.MouseDown = function(e) {
    e.preventDefault()

    let dx = e.offsetX - (this.offsetX + this.size / 2)
    let dy = e.offsetY - (this.offsetY + this.size / 2)

    if (dx * dx + dy * dy > this.size * this.size / 4)
        return

    this.isPressed = true
    this.pointX = e.offsetX
    this.pointY = e.offsetY

    this.Update()
}

ImageCropper.prototype.MouseUp = function() {
    this.isPressed = false
}

ImageCropper.prototype.MouseMove = function(e, offsetX, offsetY) {
    if (!this.isPressed)
        return

    e.preventDefault()

    this.offsetX += e.offsetX - this.pointX
    this.offsetY += e.offsetY - this.pointY
    this.pointX = e.offsetX
    this.pointY = e.offsetY

    this.Update()
}

ImageCropper.prototype.SetScale = function(scale) {
    let x = this.offsetX + this.size / 2
    let y = this.offsetY + this.size / 2
    this.size = MIN_SIZE + scale * (Math.min(this.image.clientWidth, this.image.clientHeight) - MIN_SIZE)
    this.offsetX = x - this.size / 2
    this.offsetY = y - this.size / 2

    this.Update()
}

ImageCropper.prototype.GetParams = function() {
    let imageSize = Math.min(this.image.clientWidth, this.image.clientHeight)
    let size = this.size / imageSize
    let x = this.offsetX / imageSize
    let y = this.offsetY / imageSize
    return {x, y, size}
}
