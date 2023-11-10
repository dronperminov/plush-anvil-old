function AddParsedQuiz(line, parsed) {
    let block = document.getElementById("parsed")

    if (block.children.length == 0) {
        MakeElement("margin-bottom", block, {tag: "h3", innerText: "Результат парсинга:"})
    }

    let index = block.children.length

    let quizBlock = MakeElement("quiz", block)
    let quizData = MakeElement("quiz-data", quizBlock)

    let quizFields = MakeElement("quiz-fields", quizData)
    MakeFormRow(quizFields, `date-${index}`, DATE_ICON, "Дата", "basic-input default-input", {tag: "input", type: "date", value: parsed.date, placeholder: "когда будет квиз?"})
    MakeFormRow(quizFields, `name-${index}`, NAME_ICON, "Название", "basic-input default-input", {tag: "input", type: "text", value: parsed.name, placeholder: "как называется квиз?"})
    MakeFormRow(quizFields, `place-${index}`, PLACE_ICON, "Место", "basic-input default-input", {tag: "input", type: "text", value: parsed.place, placeholder: "где будет проходить квиз?", list: "places"})
    MakeFormRow(quizFields, `organizer-${index}`, ORGANIZER_ICON, "Организатор", "basic-input default-input", {tag: "input", type: "text", value: parsed.organizer, placeholder: "кто организует квиз?", list: "organizers"})
    MakeFormRow(quizFields, `time-${index}`, ORGANIZER_ICON, "Время", "basic-input default-input", {tag: "input", type: "text", value: parsed.time, placeholder: "во сколько начнётся квиз?", list: "times"})
    MakeFormRow(quizFields, `description-${index}`, DESCRIPTION_ICON, "Описание", "basic-textarea default-textarea", {tag: "textarea", innerText: parsed.description, placeholder: "что это за квиз вообще?", rows: 5})
    MakeFormRow(quizFields, `cost-${index}`, COST_ICON, "Стоимость", "basic-input default-input", {tag: "input", type: "text", value: parsed.cost, placeholder: "сколько стоит квиз?", list: "costs", inputmode: "numeric"})

    let quizIcons = MakeElement("quiz-icons", quizData)
    let deleteBlock = MakeElement("interactive-fill-icon", quizIcons, {innerHTML: DELETE_ICON})
    let saveBlock = MakeElement("interactive-fill-icon save-button", quizIcons, {innerHTML: SAVE_ICON})
    deleteBlock.addEventListener("click", () => DeleteParsedQuiz(quizBlock))
    saveBlock.addEventListener("click", () => SaveParsedQuiz(quizBlock, `${parsed.date} 00:00:00`, `-${index}`))

    MakeElement("error", quizBlock)
}

function AddInvalidLines(lines) {
    let block = document.getElementById("invalid-lines")
    block.innerHTML = ""

    if (lines.length == 0)
        return

    MakeElement("", block, {innerHTML: "<b>Некоторые строки распознать не удалось:</b>"})

    for (let line of lines)
        MakeElement("form-row", block, {innerText: line})
}

function ParseQuizzes() {
    let text = GetTextField("text", "Текст не заполнен")
    if (text === null)
        return

    let year = GetFormatTextField("year", /^\d\d\d\d$/g, "Год не введён", "Год введён некорректно")
    if (year === null)
        return

    let parsedBlock = document.getElementById("parsed")
    parsedBlock.innerHTML = ""

    let lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0)
    let invalidLines = []

    let places = GetDatalist("places")
    let parser = new QuizParser(places, year)

    for (let line of lines) {
        let parsed = parser.Parse(line)

        if (parsed === null) {
            invalidLines.push(line)
            continue
        }

        AddParsedQuiz(line, parsed)
    }

    AddInvalidLines(invalidLines)
}

function DeleteParsedQuiz(quizBlock) {
    quizBlock.remove()

    let block = document.getElementById("parsed")
    if (block.children.length == 1)
        block.children[0].remove()
}

function SaveParsedQuiz(block, date, quizId = "") {
    let quizData = ParseQuiz(date, quizId)

    if (quizData === null)
        return

    let error = GetChildBlock(block, "error")
    error.innerText = ""

    SendRequest("/add-quiz", quizData).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        block.remove()
    })
}
