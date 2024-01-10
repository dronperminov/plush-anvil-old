function SetAttributes(element, attributes) {
    if (attributes === null)
        return

    for (let [name, value] of Object.entries(attributes)) {
        if (name == "innerText")
            element.innerText = value
        else if (name == "innerHTML")
            element.innerHTML = value
        else if (name != "tag")
            element.setAttribute(name, value)
    }
}

function MakeElement(className, parent = null, attributes = null) {
    let tagName = attributes !== null && "tag" in attributes ? attributes["tag"] : "div"
    let element = null

    if (["svg", "path", "text", "foreignObject"].indexOf(tagName) > -1)
        element = document.createElementNS("http://www.w3.org/2000/svg", tagName)
    else
        element = document.createElement(tagName)

    element.setAttribute("class", className)
    SetAttributes(element, attributes)

    if (parent !== null)
        parent.appendChild(element)

    return element
}

function MakeFormRow(parent, id, icon, labelText, inputClass, inputAttributes) {
    let row = MakeElement("form-row" + (inputAttributes.tag === "textarea" ? " form-row-top" : ""), parent)

    MakeElement("form-row-icon", row, {id: `${id}-icon`, innerHTML: icon})

    let labelBlock = MakeElement("form-row-label", row)
    MakeElement("", labelBlock, {"for": id, id: `${id}-label`, innerText: labelText})

    let nameBlock = MakeElement("form-row-input", row)
    let name = MakeElement(inputClass, nameBlock, inputAttributes)
    name.setAttribute("id", id)
    name.addEventListener("input", () => ChangeInput(id))
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

function FormatDate(date) {
    let day = `${date.day}`.padStart(2, '0')
    let month = `${date.month}`.padStart(2, '0')
    return `${day}.${month}.${date.year}`
}

function GetWordForm(number, words) {
    if ([0, 5, 6, 7, 8, 9].indexOf(number % 10) > -1 || [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20].indexOf(number % 100) > -1)
        return words[0]

    if ([2, 3, 4].indexOf(number % 10) > -1)
        return words[1]

    return words[2]
}
