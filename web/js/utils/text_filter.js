function TextFilter(inputId, clearId, blocks, className = "hidden") {
    this.className = className

    this.input = document.getElementById(inputId)
    this.input.addEventListener("input", () => this.Filter())

    this.clear = document.getElementById(clearId)
    this.clear.addEventListener("click", () => this.Clear())
    this.clear.classList.add(className)

    this.blocks = []

    for (let block of blocks)
        this.blocks.push({div: document.getElementById(block.id), text: this.Preprocess(block.text)})
}

TextFilter.prototype.Filter = function() {
    let text = this.Preprocess(this.input.value)

    if (text === "")
        this.clear.classList.add(this.className)
    else
        this.clear.classList.remove(this.className)

    for (let block of this.blocks)
        if (text === "" || block.text.indexOf(text) > -1)
            block.div.classList.remove(this.className)
        else
            block.div.classList.add(this.className)
}

TextFilter.prototype.Clear = function() {
    this.input.value = ""
    this.Filter()
}

TextFilter.prototype.Preprocess = function(text) {
    return text.trim().toLowerCase().replace(/ё/gi, "е")
}
