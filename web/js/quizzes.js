function ParseQuiz(date, quizId = "") {
    let quizData = {date: date}

    quizData.name = GetTextField(`name${quizId}`, "Название квиза не указано")
    if (quizData.name === null)
        return null

    quizData.place = GetDatalistTextField(`place${quizId}`, "places", "Место проведения квиза не выбрано", "Необходимо выбрать место из имеющихся")
    if (quizData.place === null)
        return null

    quizData.organizer = GetDatalistTextField(`organizer${quizId}`, "organizers", "Организатор квиза не выбран", "Необходимо выбрать организатора из имеющихся")
    if (quizData.organizer === null)
        return null

    quizData.time = GetFormatTextField(`time${quizId}`, /^\d\d?:\d\d$/g, "Время квиза не указано", "Время квиза указано внекорректном формате")
    if (quizData.time == null)
        return null

    quizData.description = GetTextField(`description${quizId}`, "Описание квиза не указано")
    if (quizData.description === null)
        return null

    quizData.cost = GetFormatTextField(`cost${quizId}`, /^\d+$/g, "Стоимость квиза не указана", "Стоимость квиза введена некорректно")
    if (quizData.cost === null)
        return null

    return quizData
}

function AddQuiz(date) {
    let quizData = ParseQuiz(date)

    if (quizData === null)
        return

    let error = document.getElementById("error")
    error.innerText = ""

    SendRequest("/add-quiz", quizData).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        location.reload()
    })
}

function DeleteQuiz(icon, quizId) {
    let quizBlock = GetBlock(icon, "quiz")
    let name = quizBlock.getAttribute("data-name")
    let place = quizBlock.getAttribute("data-place")

    if (!confirm(`Вы уверены, что хотите удалить квиз с названием "${name}" в ${place}`))
        return

    let error = quizBlock.getElementsByClassName("error")[0]
    error.innerText = ""

    SendRequest("/delete-quiz", {quiz_id: quizId}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            error.scrollIntoView({behavior: "smooth"})

            setTimeout(() => error.innerText = "", 1500)
            return
        }

        quizBlock.remove()
    })
}

function UpdateQuiz(button, date, quizId, blockId) {
    let quizData = ParseQuiz(date, blockId)

    if (quizData == null)
        return

    let quizBlock = GetBlock(button, "quiz")
    quizData.quiz_id = quizId

    let error = GetChildBlock(quizBlock, "error")
    error.innerText = ""

    SendRequest("/update-quiz", quizData).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            error.scrollIntoView({behavior: "smooth"})
            return
        }

        quizBlock.setAttribute("data-name", quizData.name)
        quizBlock.setAttribute("data-place", quizData.place)
        let button = quizBlock.getElementsByClassName("save-button")[0]
        button.classList.add("hidden")
    })
}
