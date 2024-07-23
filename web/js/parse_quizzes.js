function AddParsedQuiz(parsed) {
    let block = document.getElementById("parsed")
    let index = block.children.length

    let quizBlock = MakeElement("quiz", block)
    let quizData = MakeElement("quiz-data", quizBlock)

    let quizFields = MakeElement("quiz-fields", quizData)
    MakeFormRow(quizFields, `date-${index}`, DATE_ICON, "Дата", "basic-input default-input", {tag: "input", type: "date", value: parsed.date, placeholder: "когда будет квиз?"})
    MakeFormRow(quizFields, `name-${index}`, NAME_ICON, "Название", "basic-input default-input", {tag: "input", type: "text", value: parsed.name, placeholder: "как называется квиз?"})
    MakeFormRow(quizFields, `short-name-${index}`, NAME_ICON, "Сокрашение", "basic-input default-input", {tag: "input", type: "text", value: parsed.name, placeholder: "как сокращается квиз?"})
    MakeFormRow(quizFields, `place-${index}`, PLACE_ICON, "Место", "basic-input default-input", {tag: "input", type: "text", value: parsed.place, placeholder: "где будет проходить квиз?", list: "places"})
    MakeFormRow(quizFields, `organizer-${index}`, ORGANIZER_ICON, "Организатор", "basic-input default-input", {tag: "input", type: "text", value: parsed.organizer, placeholder: "кто организует квиз?", list: "organizers"})
    MakeFormRow(quizFields, `time-${index}`, TIME_ICON, "Время", "basic-input default-input", {tag: "input", type: "text", value: parsed.time, placeholder: "во сколько начнётся квиз?", list: "times"})
    MakeFormRow(quizFields, `description-${index}`, DESCRIPTION_ICON, "Описание", "basic-textarea default-textarea", {tag: "textarea", innerText: parsed.description, placeholder: "что это за квиз вообще?", rows: 5})
    MakeFormRow(quizFields, `category-${index}`, CATEGORY_ICON, "Категория", "basic-input default-input", {tag: "input", type: "text", value: parsed.category, placeholder: "какой тип игры?", list: "categories"})
    MakeFormRow(quizFields, `cost-${index}`, COST_ICON, "Стоимость", "basic-input default-input", {tag: "input", type: "text", value: parsed.cost, placeholder: "сколько стоит квиз?", list: "costs", inputmode: "numeric"})

    let quizIcons = MakeElement("quiz-icons", quizData)
    let deleteBlock = MakeElement("interactive-fill-icon", quizIcons, {innerHTML: DELETE_ICON})
    let saveBlock = MakeElement("interactive-fill-icon save-button", quizIcons, {innerHTML: SAVE_ICON})
    deleteBlock.addEventListener("click", () => DeleteParsedQuiz(quizBlock))
    saveBlock.addEventListener("click", () => SaveParsedQuiz(quizBlock, `${parsed.date} 00:00:00`, `-${index}`))

    MakeElement("error", quizBlock)
    return quizBlock
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

function UpdatePostQuizzes(quizBlock, check) {
    let result = document.getElementById("parsed-result")

    if (check.checked)
        quizBlock.classList.remove("hidden")
    else
        quizBlock.classList.add("hidden")

    for (let block of document.getElementById("parsed").children) {
        if (!block.classList.contains("hidden")) {
            result.classList.remove("hidden")
            return
        }
    }

    result.classList.add("hidden")
}

function AddPostQuiz(quiz) {
    let postQuizzes = document.getElementById("post-quizzes")
    let postQuiz = MakeElement("post-quiz", postQuizzes)

    let text = ` ${quiz.day} ${quiz.month} ${quiz.time} ${quiz.place} ${quiz.name}`
    let checkQuiz = MakeElement("post-quiz-check", postQuiz)
    let checkLabel = MakeElement("", checkQuiz, {tag: "label"})
    let check = MakeElement("", checkLabel, {tag: "input", type: "checkbox"})
    let name = MakeElement("", checkLabel, {tag: "span", innerText: text})

    let quizBlock = AddParsedQuiz(quiz)
    quizBlock.classList.add("hidden")

    check.addEventListener("change", () => UpdatePostQuizzes(quizBlock, check))
}

function ParseSmuziResponse(parser, text) {
    document.getElementById("text").value = text

    let quizzes = parser.ParsePost(text)
    for (let quiz of quizzes)
        AddPostQuiz(quiz)

    if (quizzes.length == 0) {
        let postQuizzes = document.getElementById("post-quizzes")
        MakeElement("error", postQuizzes, {innerText: "Не удалось найти ни одного квиза"})
        MakeElement("info", postQuizzes, {innerHTML: "<b>Текст:</b>"})
        MakeElement("info", postQuizzes, {innerText: text})
    }
}

function ParseVKPost(link, parser) {
    let match = /wall(?<post>-\d+_\d+)$/g.exec(link).groups
    let group = match.group
    let postId = match.post

    let error = document.getElementById("parse-error")
    error.innerText = ""

    SendRequest("/get-vk-post", {post_id: postId}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        ParseSmuziResponse(parser, response.text)
    })

    AddInvalidLines([])
}

function ParseSmuziGames(link, parser) {
    let error = document.getElementById("parse-error")
    error.innerText = ""

    SendRequest("/get-html-content", {url: "https://store.tildaapi.com/api/getproductslist/?storepartuid=220534520881&size=360"}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        let products = []
        for (let product of JSON.parse(response.text)["products"])
            products.push(`${product.title} ${product.text}`)

        let div = MakeElement("")
        div.innerHTML = products.join("\n\n")
        ParseSmuziResponse(parser, div.innerText)
    })

    AddInvalidLines([])
}

function ParseLines(lines, parser) {
    let invalidLines = []

    for (let line of lines) {
        let parsed = parser.ParseLine(line)

        if (parsed === null) {
            invalidLines.push(line)
            continue
        }

        AddParsedQuiz(parsed)
        let result = document.getElementById("parsed-result")
        result.classList.remove("hidden")
    }

    AddInvalidLines(invalidLines)
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

    let result = document.getElementById("parsed-result")
    result.classList.add("hidden")

    let postQuizzes = document.getElementById("post-quizzes")
    postQuizzes.innerHTML = ""

    let lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0)

    let places = GetDatalist("places")
    let parser = new SmuziParser(places, year)

    if (lines.length == 1 && lines[0].match(/wall-\d+_\d+$/g))
        ParseVKPost(lines[0], parser)
    else if (lines.length == 1 && lines[0].match(/(smuzi\-quiz\.com\/games\/?$)|^смузи$/gi))
        ParseSmuziGames(lines[0], parser)
    else
        ParseLines(lines, parser)
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

function SaveAll() {
    for (let block of document.getElementById("parsed").children) {
        if (block.classList.contains("hidden"))
            continue

        let button = block.getElementsByClassName("save-button")[0]
        button.click()
    }
}
