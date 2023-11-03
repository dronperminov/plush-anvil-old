const SUCCESS_STATUS = "success"
const ERROR_STATUS = "error"
const TOKEN_NAME = "quiz_token"

async function SendRequest(url, data = null) {
    try {
        let params = {
            method: data == null ? 'GET' : 'POST',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            redirect: 'follow',
            referrerPolicy: 'no-referrer'
        }

        let isForm = data !== null && data instanceof FormData

        if (data != null)
            params.body = isForm ? data : JSON.stringify(data)

        if (!isForm)
            params.headers = {'Content-Type': 'application/json'}

        const response = await fetch(url, params)

        if (response?.ok)
            return await response.json()

        const error = await response.json()
        return {"status": "error", "message": error["message"]}
    }
    catch (error) {
        let message = error

        if (error.message == "Failed to fetch")
            message = "Не удалось связаться с сервером"

        return {"status": "error", "message": message}
    }
}

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

    let error = document.getElementById("error")
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
