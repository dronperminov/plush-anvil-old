function ImageCropper(blockId) {
    this.block = document.getElementById(blockId)
    this.image = this.block.children[0]
    this.cropper = this.block.children[1]
    this.cropperPath = this.cropper.children[0]

    this.block.addEventListener("wheel", (e) => this.Scroll(e))
    this.block.addEventListener("mousedown", (e) => this.MouseDown(e))
    this.block.addEventListener("mousemove", (e) => this.MouseMove(e))
    this.block.addEventListener("mouseup", (e) => this.MouseUp(e))
    this.block.addEventListener("mouseleave", (e) => this.MouseUp(e))
}

ImageCropper.prototype.Init = function() {
    this.size = Math.min(this.image.clientWidth, this.image.clientHeight)
    this.offsetX = (this.image.clientWidth - this.size) / 2
    this.offsetY = (this.image.clientHeight - this.size) / 2

    this.Update()
}

ImageCropper.prototype.Update = function() {
    this.size = Math.max(100, Math.min(this.size, Math.min(this.image.clientWidth, this.image.clientHeight)))
    this.offsetX = Math.max(0, Math.min(this.image.clientWidth - this.size, this.offsetX))
    this.offsetY = Math.max(0, Math.min(this.image.clientHeight - this.size, this.offsetY))

    let w = this.image.clientWidth
    let h = this.image.clientHeight
    let r = this.size / 2

    this.cropper.setAttribute("viewBox", `0 0 ${w} ${h}`)
    this.cropperPath.setAttribute("d", `M0 0 H${w} V${h} H${-w}z M ${this.offsetX} ${this.offsetY + r} a ${r},${r} 0 1,0 ${2*r},0 a ${r},${r} 0 1,0 ${-2*r},0z`)
}

ImageCropper.prototype.Scroll = function(e) {
    e.preventDefault()

    let scale = Math.sign(e.deltaY) > 0 ? 0.5 : 2
    this.size = Math.max(100, Math.min(this.size * scale, Math.min(this.image.clientWidth, this.image.clientHeight)))
    this.offsetX = e.offsetX - this.size / 2
    this.offsetY = e.offsetY - this.size / 2
    this.Update()
}

ImageCropper.prototype.MouseDown = function(e) {
    e.preventDefault()
    this.isPressed = true
    this.pointX = e.offsetX
    this.pointY = e.offsetY

    this.offsetX = e.offsetX - this.size / 2
    this.offsetY = e.offsetY - this.size / 2
    this.Update()
}

ImageCropper.prototype.MouseUp = function(e) {
    e.preventDefault()
    this.isPressed = false
}

ImageCropper.prototype.MouseMove = function(e) {
    if (!this.isPressed)
        return

    e.preventDefault()

    this.offsetX += e.offsetX - this.pointX
    this.offsetY += e.offsetY - this.pointY
    this.pointX = e.offsetX
    this.pointY = e.offsetY

    this.Update()
}

ImageCropper.prototype.GetParams = function() {
    let imageSize = Math.min(this.image.clientWidth, this.image.clientHeight)
    let size = this.size / imageSize
    let x = this.offsetX / imageSize
    let y = this.offsetY / imageSize
    return {x, y, size}
}
