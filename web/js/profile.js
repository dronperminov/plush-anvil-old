function LoadProfileImage() {
    let input = document.getElementById("profile-input")
    input.click()
}

function UpdateProfileImage(e) {
    let input = document.getElementById("profile-input")
    let image = document.getElementById("profile-image-preview")
    image.src = URL.createObjectURL(input.files[0])
}

function ShowProfileImagePopup() {
    let popup = document.getElementById("profile-image-settings")
    popup.classList.remove("hidden")
    cropper.Init()
}

function SaveProfileImage() {
    let input = document.getElementById("profile-input")
    let {x, y, size} = cropper.GetParams()

    let formData = new FormData()
    formData.append("image", input.files[0])
    formData.append("x", x)
    formData.append("y", y)
    formData.append("size", size)

    let profileBlock = document.getElementById("profile-block")
    let error = GetChildBlock(profileBlock, "error")
    error.innerText = ""

    SendRequest("/update-avatar", formData).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return
        }

        let popup = document.getElementById("profile-image-settings")
        popup.classList.add("hidden")

        let image = document.getElementById("profile-image")
        image.src = response.src

        let menuImage = document.getElementById("menu-profile-image")
        menuImage.src = response.src

        input.value = null
    })
}

function CancelProfileImage() {
    let input = document.getElementById("profile-input")
    input.value = null

    let popup = document.getElementById("profile-image-settings")
    popup.classList.add("hidden")
}