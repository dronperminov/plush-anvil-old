const PHOTO_ICON = `<svg width="25px" height="25px" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" onclick="location.href='/quiz-album/{{quiz._id}}'">
    <path d="M277.333333,1.42108547e-14 C277.333333,1.42108547e-14 277.681778,0.557511111 278.378667,1.67253333 L278.698667,2.18453333 C279.438222,3.36782222 280.478222,5.03182222 281.818667,7.17653333 L282.458667,8.20053333 C283.891556,10.4931556 285.624889,13.2664889 287.658667,16.5205333 L288.618667,18.0565333 C290.744889,21.4584889 293.171556,25.3411556 295.898667,29.7045333 L297.178667,31.7525333 C299.998222,36.2638222 303.118222,41.2558222 306.538667,46.7285333 L308.138667,49.2885333 C311.003462,53.8722052 314.068069,58.775577 317.332489,63.9986486 L426.666667,64 L426.666667,362.666667 L7.10542736e-15,362.666667 L7.10542736e-15,64 L109.333,64 L149.333333,1.42108547e-14 L277.333333,1.42108547e-14 L277.333333,1.42108547e-14 Z M213.333333,85.3333333 C148.531923,85.3333333 96,137.865256 96,202.666667 C96,267.468077 148.531923,320 213.333333,320 C278.134744,320 330.666667,267.468077 330.666667,202.666667 C330.666667,137.865256 278.134744,85.3333333 213.333333,85.3333333 Z M213.333333,128 C254.570595,128 288,161.429405 288,202.666667 C288,243.903928 254.570595,277.333333 213.333333,277.333333 C172.096072,277.333333 138.666667,243.903928 138.666667,202.666667 C138.666667,161.429405 172.096072,128 213.333333,128 Z M384,106.666667 C372.217925,106.666667 362.666667,116.217925 362.666667,128 C362.666667,139.782075 372.217925,149.333333 384,149.333333 C395.782075,149.333333 405.333333,139.782075 405.333333,128 C405.333333,116.217925 395.782075,106.666667 384,106.666667 Z" transform="translate(42.666667, 64.000000)" />
</svg>`

const POLL_ICON = `<svg width="25px" height="25px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M7 11h7v2H7zm0-4h10.97v2H7zm0 8h13v2H7zM4 4h2v16H4z"/>
</svg>`

function CloseAllDetails() {
    for (let details of document.getElementsByClassName("quiz-details"))
        details.classList.add("hidden")
}

function CloseDetails(detailsId) {
    let body = document.getElementsByTagName("body")[0]
    body.classList.remove("no-overflow")

    let details = document.getElementById(detailsId)
    details.classList.add("hidden")
}

function ShowDetails(detailsId) {
    CloseAllDetails()

    let body = document.getElementsByTagName("body")[0]
    body.classList.add("no-overflow")

    let details = document.getElementById(detailsId)
    details.classList.remove("hidden")
}

function UpdateScheduleMonth(schedule) {
    let month = document.getElementById("schedule-month")
    let prevDate = document.getElementById("schedule-prev-date")
    let nextDate = document.getElementById("schedule-next-date")

    month.innerText = `${schedule.month.toUpperCase()} ${schedule.year}`
    prevDate.setAttribute("data-date", schedule.prev_date)
    nextDate.setAttribute("data-date", schedule.next_date)
}

function BuildScedulePlaces(schedule, places) {
    let placesBlock = document.getElementById("schedule-places")
    placesBlock.innerHTML = ""

    for (let place of schedule.places) {
        let placeBlock = MakeElement("schedule-place", placesBlock)
        let colorSpan = MakeElement("schedule-place-color", placeBlock, {tag: "span", style: `background: ${places[place].color}`})
        let info = MakeElement("", placeBlock, {tag: "span", innerText: ` ${place} (м. ${places[place].metro_station})`})
    }
}

function FixFontSize(foreign, nameSpan) {
    for (let fontSize = 1; fontSize > 0.01; fontSize -= 0.01) {
        nameSpan.style.fontSize = `${fontSize}em`

        let rect1 = foreign.getBoundingClientRect()
        let rect2 = nameSpan.getBoundingClientRect()

        if (rect2.width <= rect1.width && rect2.height <= rect1.height)
            break
    }
}

function QuizToName(quiz) {
    let name = quiz.short_name

    if (quiz.position > 0)
        name += `<br><span class='schedule-quiz-position'>${quiz.position} / ${quiz.teams}</span>`

    return name
}

let resizebleBlocks = []

function FillQuizSVG(svg, cell, places, isAdmin) {
    if (cell.quizzes.length == 2) {
        MakeElement("", svg, {tag: "path", d: "M0 0 L100 0 L0 100 Z", fill: places[cell.quizzes[0].place].color})
        MakeElement("", svg, {tag: "path", d: "M0 100 L100 100 L100 0 Z", fill: places[cell.quizzes[1].place].color})
        MakeElement("", svg, {tag: "path", d: "M0 100 L100 0", stroke: "#ffffff", "stroke-width": "2%"})

        let foreign1 = MakeElement("", svg, {tag: "foreignObject", x: "2", y: "2", width: "96", height: "96"})
        let name1 = MakeElement("schedule-quiz-name schedule-quiz-name-left", foreign1)
        let name1Span = MakeElement("schedule-quiz-name-span", name1, {tag: "span", innerHTML: QuizToName(cell.quizzes[0])})

        MakeElement("schedule-quiz-time", svg, {tag: "text", x: "50", y: "2", "dominant-baseline": "text-before-edge", "text-anchor": "middle", innerHTML: cell.quizzes[0].time})
        MakeElement("schedule-quiz-time", svg, {tag: "text", x: "50", y: "98", "dominant-baseline": "text-after-edge", "text-anchor": "middle", innerHTML: cell.quizzes[1].time})

        let foreign2 = MakeElement("", svg, {tag: "foreignObject", x: "2", y: "2", width: "96", height: "96"})
        let name2 = MakeElement("schedule-quiz-name schedule-quiz-name-right", foreign2)
        let name2Span = MakeElement("schedule-quiz-name-span", name2, {tag: "span", innerHTML: QuizToName(cell.quizzes[1])})

        svg.addEventListener("click", (e) => {
            e.preventDefault()

            let bbox = svg.getBoundingClientRect()
            let x = (e.x - bbox.x) / bbox.width
            let y = (e.y - bbox.y) / bbox.height

            if (y > 0.2 && y < 0.8)
                ShowDetails(`${cell.day}-${x < y ? 1 : 2}`)
        })

        resizebleBlocks.push({foreign: foreign1, nameSpan: name1Span})
        resizebleBlocks.push({foreign: foreign2, nameSpan: name2Span})
    }
    else if (cell.quizzes.length > 0) {
        let h = 100 / cell.quizzes.length

        for (let i = 0; i < cell.quizzes.length; i++) {
            let y = i * h
            let yc = (i + 0.5) * h

            if (i > 0)
                MakeElement("", svg, {tag: "path", d: `M0 ${y} L100 ${y}`, stroke: "#ffffff", "stroke-width": "1%"})

            MakeElement("", svg, {tag: "path", d: `M0 ${y} L100 ${y} L100 ${y + h} L0 ${y + h} Z`, fill: places[cell.quizzes[i].place].color})
            MakeElement("schedule-quiz-time", svg, {tag: "text", x: "96", y: `${y + 2}`, "dominant-baseline": "text-before-edge", "text-anchor": "end", innerHTML: cell.quizzes[i].time})

            let foreign = MakeElement("", svg, {tag: "foreignObject", x: "2", y: `${y}`, width: "96", height: `${h}`})
            let name = MakeElement("schedule-quiz-name schedule-quiz-name-grid", foreign)
            let nameSpan = MakeElement("", name, {tag: "span", innerHTML: QuizToName(cell.quizzes[i])})
            nameSpan.addEventListener("click", () => ShowDetails(`${cell.day}-${i + 1}`))

            resizebleBlocks.push({foreign: foreign, nameSpan: nameSpan})
        }
    }
    else {
        MakeElement("", svg, {tag: "path", d: `M0 0 L100 0 L100 100 L0 100 Z`, fill: "#efefef"})
    }

    if (!cell.current)
        return

    let day = MakeElement("schedule-day", svg, {tag: "text", x: "4", y: "2", "dominant-baseline": "text-before-edge", "text-anchor": "start", innerHTML: cell.day})

    if (cell.quizzes.length > 0)
        day.classList.add("schedule-day-current")

    if (isAdmin)
        day.addEventListener("click", () => location.href = `/quizzes/${cell.year}-${cell.month}-${cell.day}`)
}

function BuildScheduleCells(schedule, places, isAdmin) {
    let scheduleBlock = document.getElementById("schedule")

    while (scheduleBlock.children.length > 7)
        scheduleBlock.children[scheduleBlock.children.length - 1].remove()

    resizebleBlocks = []

    for (let row of schedule.calendar) {
        for (let cell of row) {
            let cellBlock = MakeElement("schedule-cell", scheduleBlock)

            let quizzes = MakeElement("schedule-quizzes", cellBlock)
            let svg = MakeElement("schedule-quiz", quizzes, {viewBox: "0 0 100 100", preserveAspectRatio: "none", tag: "svg"})
            FillQuizSVG(svg, cell, places, isAdmin)
        }
    }
}

function CopyPollHeader(quiz, weekday, places) {
    const weekday2str = {
        "понедельник": "Пн",
        "вторник": "Вт",
        "среда": "Ср",
        "четверг": "Чт",
        "пятница": "Пт",
        "суббота": "Сб",
        "воскресенье": "Вс",
    }

    let day = `${quiz.date.day}`.padStart(2, '0')
    let month = `${quiz.date.month}`.padStart(2, '0')
    let name = quiz.name.replace(/\.$/g, "")

    let headerDate = `${day}.${month} ${weekday2str[weekday]} ${quiz.time}`
    let headerPlace = `${quiz.place} (м. ${places[quiz.place].metro_station}) ${quiz.cost} руб.`
    let headerLength = headerDate.length + headerPlace.length

    if (headerDate.length + headerPlace.length + name.length >= 240)
        name = quiz.short_name.replace(/\.$/g, "")

    let header = `${headerDate} ${name}. ${headerPlace}`
    navigator.clipboard.writeText(header)
}

function BuildScheduleDetails(schedule, places, isAdmin) {
    let scheduleBlock = document.getElementById("schedule")

    for (let row of schedule.calendar) {
        for (let cell of row) {
            for (let i = 0; i < cell.quizzes.length; i++) {
                let quiz = cell.quizzes[i]
                let details = MakeElement("quiz-details hidden", scheduleBlock, {id: `${cell.day}-${i + 1}`})
                let content = MakeElement("quiz-details-content", details)
                let close = MakeElement("quiz-details-content-close", content)
                close.addEventListener("click", () => CloseDetails(`${cell.day}-${i + 1}`))

                if (isAdmin) {
                    let icon = MakeElement("schedule-quiz-album interactive-fill-icon", content, {innerHTML: PHOTO_ICON})
                    icon.addEventListener("click", () => location.href = `/quiz-album/${quiz._id}`)
                    let poll = MakeElement("schedule-quiz-poll interactive-fill-icon", content, {innerHTML: POLL_ICON})
                    poll.addEventListener("click", () => CopyPollHeader(quiz, cell.weekday, places))
                }

                MakeElement("quiz-details-name", content, {innerText: quiz.name})
                MakeElement("quiz-details-cost", content, {innerHTML: `<b>Сколько?</b> ${quiz.cost}₽`})
                MakeElement("quiz-details-datetime", content, {innerHTML: `<b>Когда?</b> ${FormatDate(quiz.date)} ${cell.weekday} в ${quiz.time}`})
                MakeElement("quiz-details-place", content, {innerHTML: `<b>Где?</b> ${quiz.place} (м. ${places[quiz.place].metro_station})`})
                MakeElement("quiz-details-organizer", content, {innerHTML: `<b>От кого?</b> ${quiz.organizer}`})
                MakeElement("quiz-details-description", content, {innerHTML: `<b>Что ожидается?</b><br>${quiz.description}`})

                if (quiz.position > 0)
                    MakeElement("quiz-details-description", content, {innerHTML: `<b>Результат игры:</b> ${quiz.position} / ${quiz.teams}`})
            }
        }
    }
}

function BuildScheduleStatistics(schedule) {
    let statistics = schedule.statistics
    let values = []

    if (statistics.wins > 0)
        values.push(`<b>${statistics.wins}</b> ${GetWordForm(statistics.wins, ['раз', 'раза', 'раз'])} победили`)

    if (statistics.prizes > 0)
        values.push(`<b>${statistics.prizes}</b> ${GetWordForm(statistics.prizes, ['раз', 'раза', 'раз'])} заняли призовое место`)

    if (statistics.top10 > 0)
        values.push(`<b>${statistics.top10}</b> ${GetWordForm(statistics.top10, ['раз', 'раза', 'раз'])} вошли в топ-10`)

    let text = values.length > 0 ? `<div class="schedule-statistic-header">Статистика:</div>` : ""

    let block = document.getElementById("schedule-statistic")
    block.innerHTML = text + values.map(v => `<div class="schedule-statistic-row">${v}</div>`).join("")
}

function BuildSchedule(schedule, places, isAdmin) {
    UpdateScheduleMonth(schedule)
    BuildScedulePlaces(schedule, places)
    BuildScheduleCells(schedule, places, isAdmin)
    BuildScheduleDetails(schedule, places, isAdmin)
    BuildScheduleStatistics(schedule)
}

function SwitchSchedule(link, isAdmin) {
    let date = link.getAttribute("data-date")
    let error = document.getElementById("schedule-error")
    error.innerText = ""

    SendRequest("/schedule", {date: date}).then(response => {
        if (response.status != SUCCESS_STATUS) {
            error.innerText = response.message
            return
        }

        console.log(response)
        BuildSchedule(response.schedule, response.places, isAdmin)
    })
}

function FixFontSizes() {
    for (let block of resizebleBlocks)
        FixFontSize(block.foreign, block.nameSpan)

    window.requestAnimationFrame(FixFontSizes)
}

FixFontSizes()