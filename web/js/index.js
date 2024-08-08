const PHOTO_ICON = `<svg width="25px" height="25px" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" onclick="location.href='/quiz-album/{{quiz._id}}'">
    <path d="M277.333333,1.42108547e-14 C277.333333,1.42108547e-14 277.681778,0.557511111 278.378667,1.67253333 L278.698667,2.18453333 C279.438222,3.36782222 280.478222,5.03182222 281.818667,7.17653333 L282.458667,8.20053333 C283.891556,10.4931556 285.624889,13.2664889 287.658667,16.5205333 L288.618667,18.0565333 C290.744889,21.4584889 293.171556,25.3411556 295.898667,29.7045333 L297.178667,31.7525333 C299.998222,36.2638222 303.118222,41.2558222 306.538667,46.7285333 L308.138667,49.2885333 C311.003462,53.8722052 314.068069,58.775577 317.332489,63.9986486 L426.666667,64 L426.666667,362.666667 L7.10542736e-15,362.666667 L7.10542736e-15,64 L109.333,64 L149.333333,1.42108547e-14 L277.333333,1.42108547e-14 L277.333333,1.42108547e-14 Z M213.333333,85.3333333 C148.531923,85.3333333 96,137.865256 96,202.666667 C96,267.468077 148.531923,320 213.333333,320 C278.134744,320 330.666667,267.468077 330.666667,202.666667 C330.666667,137.865256 278.134744,85.3333333 213.333333,85.3333333 Z M213.333333,128 C254.570595,128 288,161.429405 288,202.666667 C288,243.903928 254.570595,277.333333 213.333333,277.333333 C172.096072,277.333333 138.666667,243.903928 138.666667,202.666667 C138.666667,161.429405 172.096072,128 213.333333,128 Z M384,106.666667 C372.217925,106.666667 362.666667,116.217925 362.666667,128 C362.666667,139.782075 372.217925,149.333333 384,149.333333 C395.782075,149.333333 405.333333,139.782075 405.333333,128 C405.333333,116.217925 395.782075,106.666667 384,106.666667 Z" transform="translate(42.666667, 64.000000)" />
</svg>`

const PLAYERS_ICON = `<svg class="form-row-fill-icon" width="22px" height="22px" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
    <path d="M36.31,176c0.674,0.386 24.255,13.789 43.69,13.789c19.435,0 43.826,-13.403 44.524,-13.789l9.047,0c14.641,0.044 26.429,11.859 26.429,26.429l0,101.571c0,17.673
    -14.327,32 -32,32l0,120c0,13.255 -10.745,24 -24,24l-48,0c-13.255,0 -24,-10.745 -24,-24l0,-120c-17.673,0 -32,-14.327 -32,-32l0,-100.738c0,-15.028 12.16,-27.216 27.262,
    -27.262l9.048,0Zm176,0c0.674,0.386 24.256,13.789 43.69,13.789c19.434,0 43.826,-13.403 44.524,-13.789l9.047,0c14.641,0.044 26.429,11.859 26.429,26.429l0,101.571c0,17.673
    -14.327,32 -32,32l0,120c0,13.255 -10.745,24 -24,24l-48,0c-13.255,0 -24,-10.745 -24,-24l0,-120c-17.673,0 -32,-14.327 -32,-32l0,-100.738c0,-15.028 12.16,-27.216 27.262,
    -27.262l9.048,0Zm243.69,304l-48,0c-13.255,0 -24,-10.745 -24,-24l0,-120c-17.673,0 -32,-14.327 -32,-32l0,-100.738c0,-15.056 12.206,-27.262 27.262,-27.262l9.048,0c0,0
    23.978,13.789 43.69,13.789c19.712,0 44.524,-13.789 44.524,-13.789l9.047,0c14.597,0 26.429,11.832 26.429,26.429l0,101.571c0,17.673 -14.327,32 -32,32l0,120c0,13.222
    -10.691,23.946 -24,24Zm-376,-320c35.346,0 64,-28.654 64,-64c0,-35.346 -28.654,-64 -64,-64c-35.346,0 -64,28.654 -64,64c0,35.346 28.654,64 64,64Zm176,0c35.346,0 64,
    -28.654 64,-64c0,-35.346 -28.654,-64 -64,-64c-35.346,0 -64,28.654 -64,64c0,35.346 28.654,64 64,64Zm240,-64c0,35.346 -28.654,64 -64,64c-35.346,0 -64,-28.654 -64,-64c0,
    -35.346 28.654,-64 64,-64c35.346,0 64,28.654 64,64Z"></path>
</svg>`

const RUB_ICON = `<svg width="25px" height="25px" viewBox="1 1 22 22" xmlns="http://www.w3.org/2000/svg" fill="none">
<path stroke="#000000" stroke-width="1.4" d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/>
<path stroke="#000000" stroke-width="1.4" d="M10 11h4a2 2 0 0 0 2-2v0a2 2 0 0 0-2-2h-4v4zm0 0v3m0-3H8m2 6v-3m0 0H8m2 0h3"/>
</svg>`

const PLACE_ICON = `<svg width="25px" height="25px" viewBox="1 1 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M5 9.5C5 6.09371 8.00993 3 12 3C15.9901 3 19 6.09371 19 9.5C19 11.6449 17.6877 14.0406 15.9606 16.2611C14.5957 18.016 13.0773 19.5329 12 20.5944C10.9227 19.5329 9.40427 18.016 8.03935 16.2611C6.31229 14.0406 5 11.6449 5 9.5ZM12 1C6.99007 1 3 4.90629 3 9.5C3 12.3551 4.68771 15.2094 6.46065 17.4889C7.99487 19.4615 9.7194 21.1574 10.7973 22.2173C10.9831 22.4001 11.1498 22.564 11.2929 22.7071C11.4804 22.8946 11.7348 23 12 23C12.2652 23 12.5196 22.8946 12.7071 22.7071C12.8502 22.564 13.0169 22.4001 13.2027 22.2174L13.2028 22.2173C14.2806 21.1573 16.0051 19.4615 17.5394 17.4889C19.3123 15.2094 21 12.3551 21 9.5C21 4.90629 17.0099 1 12 1ZM12 12.5C13.3807 12.5 14.5 11.3807 14.5 10C14.5 8.61929 13.3807 7.5 12 7.5C10.6193 7.5 9.5 8.61929 9.5 10C9.5 11.3807 10.6193 12.5 12 12.5Z" fill="#000000"/>
</svg>`

const POSITION_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="25px" height="25px" viewBox="2 2 28 28">
    <path d="M26,4H6C4.9,4,4,4.9,4,6v6c0,1.1,0.9,2,2,2h2c0.087,0,0.171-0.015,0.256-0.026
    c0.717,2.821,2.928,5.037,5.744,5.764V22H8v6h16v-6h-6v-2.262c2.817-0.726,5.027-2.943,5.744-5.764C23.829,13.985,23.913,14,24,14h2
    c1.1,0,2-0.9,2-2V6C28,4.9,27.1,4,26,4z M8,12H6V6h2V12z M22,24v2H10v-2H22z M22,12c0,3.308-2.692,6-6,6s-6-2.692-6-6V6h12V12z
     M26,12h-2V6h2V12z M17,14h-2V8h2V14z"/>
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

function BuildScedulePlaces(schedule, places, withMetroStation = true) {
    let placesBlock = document.getElementById("schedule-places")
    placesBlock.innerHTML = ""

    for (let place of schedule.places) {
        let placeBlock = MakeElement("schedule-place", placesBlock)
        let colorSpan = MakeElement("schedule-place-color", placeBlock, {tag: "span", style: `background: ${places[place].color}`})
        let placeText = ` ${place}` + (withMetroStation ? ` (м. ${places[place].metro_station})` : "")
        let info = MakeElement("", placeBlock, {tag: "span", innerText: placeText})
    }
}

function FixFontSize(foreign, nameSpan) {
    if (nameSpan.style.fontSize != "")
        return

    for (let fontSize = 1; fontSize > 0.01; fontSize -= 0.01) {
        nameSpan.style.fontSize = `${fontSize}em`

        let rect1 = foreign.getBoundingClientRect()
        let rect2 = nameSpan.getBoundingClientRect()

        if (rect2.width <= rect1.width && rect2.height <= rect1.height)
            break
    }
}

function QuizToName(quiz, count = 1) {
    let name = quiz.short_name
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

            let dy = cell.quizzes.length > 2 ? h / 2 : 0
            let foreign = MakeElement("", svg, {tag: "foreignObject", x: "2", y: `${y + dy}`, width: "96", height: `${h - dy}`})
            let name = MakeElement("schedule-quiz-name schedule-quiz-name-grid", foreign)
            let nameSpan = MakeElement("", name, {tag: "span", innerHTML: QuizToName(cell.quizzes[i], cell.quizzes.length)})
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

function BuildScheduleDetails(schedule, places, isAdmin) {
    let scheduleBlock = document.getElementById("schedule")

    for (let row of schedule.calendar) {
        for (let cell of row) {
            for (let i = 0; i < cell.quizzes.length; i++) {
                let quiz = cell.quizzes[i]
                let details = MakeElement("quiz-details hidden", scheduleBlock, {id: `${cell.day}-${i + 1}`})
                let content = MakeElement("quiz-details-content", details)
                let close = MakeElement("quiz-details-content-close", content)
                details.addEventListener("click", (e) => { if (e.target == details) CloseDetails(`${cell.day}-${i + 1}`) })
                close.addEventListener("click", () => CloseDetails(`${cell.day}-${i + 1}`))

                if (isAdmin) {
                    let icon = MakeElement("schedule-quiz-album interactive-fill-icon", content, {innerHTML: PHOTO_ICON})
                    icon.addEventListener("click", () => location.href = `/quiz-album/${quiz._id}`)
                    let players = MakeElement("schedule-quiz-players interactive-fill-icon", content, {innerHTML: PLAYERS_ICON})
                    players.addEventListener("click", () => location.href=`/quiz-participants?quiz_id=${quiz._id}`)
                }

                MakeElement("quiz-details-name", content, {innerText: quiz.name})
                MakeElement("quiz-details-category", content, {innerHTML: `<span class="circle" style="background: ${schedule.category2color[quiz.category]}"></span> ${quiz.category}`})
                MakeElement("quiz-details-description", content, {innerHTML: `${quiz.description}`})
                MakeElement("quiz-details-date", content, {innerHTML: `${FormatDate(quiz.date)}`})
                MakeElement("quiz-details-day-time", content, {innerHTML: `${quiz.time}, ${cell.weekday}`})
                MakeElement("quiz-details-cost", content, {innerHTML: `${RUB_ICON} <div>${quiz.cost}₽</div>`})
                MakeElement("quiz-details-place", content, {innerHTML: `${PLACE_ICON} <div>${quiz.place}<div class="quiz-details-place-addition">м. ${places[quiz.place].metro_station}<br><a href="${places[quiz.place].yandex_map_link}">${places[quiz.place].address}</</div></div>`})
                MakeElement("quiz-details-organizer", content, {innerHTML: `<img src="/images/organizers/${quiz.organizer}.png"> ${quiz.organizer}`})

                if (quiz.position > 0)
                    MakeElement("quiz-details-addition", content, {innerHTML: `${POSITION_ICON} <div>${quiz.position} место из ${quiz.teams}</div>`})

                if (quiz.players > 0) {
                    MakeElement("quiz-details-addition", content, {innerHTML: `${PLAYERS_ICON} <div>${quiz.players} ${GetWordForm(quiz.players, ['игроков', 'игрока', 'игрок'])}</div>`})
                    let participants = quiz.participants.map(participant => `<a href="/profile?username=${participant.username}"><img src="${schedule.user_images[participant.username]}"></a>`).join("")
                    MakeElement("quiz-details-participants", content, {innerHTML: participants})
                }
            }
        }
    }
}

function BuildScheduleStatistics(schedule) {
    let statistics = schedule.statistics
    let values = []

    if (statistics.games > 0)
        values.push(`<div class="schedule-statistic-cell-value">${statistics.games}</div><div class="schedule-statistic-cell-label">${GetWordForm(statistics.games, ['игр', 'игры', 'игру'])} сыграли</div>`)

    if (statistics.wins > 0)
        values.push(`<div class="schedule-statistic-cell-value">${statistics.wins}</div><div class="schedule-statistic-cell-label">${GetWordForm(statistics.wins, ['раз', 'раза', 'раз'])} победили</div>`)

    if (statistics.top3 > 0)
        values.push(`<div class="schedule-statistic-cell-value">${statistics.top3}</div><div class="schedule-statistic-cell-label">${GetWordForm(statistics.top3, ['раз', 'раза', 'раз'])} вошли в тройку</div>`)

    if (statistics.games > 0)
        values.push(`<div class="schedule-statistic-cell-value">${statistics.mean_position.toFixed(1)}</div><div class="schedule-statistic-cell-label">средняя позиция</div>`)


    let block = document.getElementById("schedule-statistic")

    if (values.length == 0) {
        block.innerHTML = ""
        return
    }

    let header = `<div class="schedule-statistic-header">Статистика за месяц:</div>`
    let cells = '<div class="schedule-statistic-cells">' + values.map(v => `<div class="schedule-statistic-cell">${v}</div>`).join("") + "</div>"
    block.innerHTML = `${header}${cells}`
}

function BuildSchedule(schedule, places, isAdmin, withStatistic = true) {
    UpdateScheduleMonth(schedule)
    BuildScedulePlaces(schedule, places, withStatistic)
    BuildScheduleCells(schedule, places, isAdmin)
    BuildScheduleDetails(schedule, places, isAdmin)

    if (withStatistic)
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
        SCHEDULE = response.schedule
        PLACES = response.places
        BuildSchedule(response.schedule, response.places, isAdmin)
        // UpdateColors()
    })
}

let prevTime = 0

function FixFontSizes(time) {
    if (time - prevTime > 100) {
        prevTime = time

        for (let block of resizebleBlocks)
            FixFontSize(block.foreign, block.nameSpan)
    }

    window.requestAnimationFrame(FixFontSizes)
}

window.addEventListener("load", (event) => {
    FixFontSizes()
});
