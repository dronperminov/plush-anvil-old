function ChangePassword() {
    let currPassword = GetTextField("curr-password", "Текущий пароль не введён")
    if (currPassword === null)
        return

    let password = GetPassword()
    if (password === null)
        return

    let error = document.getElementById("error")
    let info = document.getElementById("info")
    error.innerText = ""
    info.innerText = ""

    SendRequest("/change-password", {curr_password: currPassword, password: password}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        document.getElementById("curr-password").value = ""
        document.getElementById("password").value = ""
        document.getElementById("password-check").value = ""
        info.innerText = "Пароль успешно изменён"
    })
}
