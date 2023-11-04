function SetAttributes(element, attributes) {
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

function MakeElement(className, parent = null, attributes = null) {
    let tagName = attributes !== null && "tag" in attributes ? attributes["tag"] : "div"
    let element = document.createElement(tagName)
    element.className = className

    SetAttributes(element, attributes)

    if (parent !== null)
        parent.appendChild(element)

    return element
}

function InputError(inputId, errorMessage = "") {
    let input = document.getElementById(inputId)
    let label = document.getElementById(`${inputId}-label`)
    let icon = document.getElementById(`${inputId}-icon`)

    let error = GetChildBlock(input, "error")
    error.innerText = errorMessage

    if (errorMessage !== "") {
        input.classList.add("error-input")
        input.focus()

        if (icon !== null)
            icon.classList.add("error-icon")

        if (label !== null)
            label.classList.add("error-label")
    }
    else {
        input.classList.remove("error-input")

        if (icon !== null)
            icon.classList.remove("error-icon")

        if (label !== null)
            label.classList.remove("error-label")
    }
}

function GetBlock(block, className) {
    while (!block.classList.contains(className))
        block = block.parentNode

    return block
}

function GetChildBlock(block, className) {
    let children = block.getElementsByClassName(className)

    while (children.length === 0) {
        block = block.parentNode
        children = block.getElementsByClassName(className)
    }

    return children[0]
}

function ChangeInput(inputId, buttonClass = "save-button") {
    let input = document.getElementById(inputId)
    let button = GetChildBlock(input, buttonClass)
    button.classList.remove("hidden")

    InputError(inputId, "")
}

function GetTextField(inputId, errorMessage = "") {
    let input = document.getElementById(inputId)
    let value = input.value.trim()
    input.value = value

    if (value === "" && errorMessage != "") {
        InputError(inputId, errorMessage)
        return null
    }

    InputError(inputId, "")
    return value
}

function GetDatalist(datalistId) {
    let datalist = document.getElementById(datalistId)
    let options = []

    for (let option of datalist.children)
        options.push(option.getAttribute("value"))

    return options
}

function GetDatalistTextField(inputId, datalistId, errorMessage, errorDatalistMessage) {
    let value = GetTextField(inputId, errorMessage)

    if (value === null)
        return null

    let values = GetDatalist(datalistId)

    if (values.indexOf(value) == -1) {
        InputError(inputId, errorDatalistMessage)
        return null
    }

    InputError(inputId, "")
    return value
}

function GetFormatTextField(inputId, format, errorMessage, errorFormatMessage) {
    let value = GetTextField(inputId, errorMessage)

    if (value === null)
        return null

    if (value.match(format) === null) {
        InputError(inputId, errorFormatMessage)
        return null
    }

    InputError(inputId, "")
    return value
}

function AutoHeightTextareas() {
    for (let textarea of document.getElementsByTagName("textarea")) {
        textarea.style.height = "5px"
        textarea.style.height = `${textarea.scrollHeight + 2}px`
    }
}
