function LoadProfileImage() {
    let input = document.getElementById("profile-input")
    input.click()
}

function UpdateProfileImage(e) {
    let input = document.getElementById("profile-input")
    let formData = new FormData()
    formData.append("image", input.files[0])

    let profileBlock = document.getElementById("profile-block")
    let error = GetChildBlock(profileBlock, "error")
    error.innerText = ""

    SendRequest("/update-avatar", formData).then(response => {
        if (response.status != "success") {
            error.innerText = response.message
            return
        }

        let image = document.getElementById("profile-image")
        image.src = response.src

        let menuImage = document.getElementById("menu-profile-image")
        menuImage.src = response.src
    })
}
