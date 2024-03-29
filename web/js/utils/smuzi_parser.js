function SmuziParser(places, year) {
    this.places = places
    this.year = year
    this.months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    this.weekdays = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
}

SmuziParser.prototype.GetRegexp = function() {
    let start = "[^\\d]{0,5}"
    let day = "(?<day>\\d\\d?)"
    let month = `(?<month>${this.months.join("|")})`
    let weekday = `(?<weekday>${this.weekdays.join("|")})`
    let time = "(?<time>\\d\\d?:\\d\\d?)"
    let place = "(?<place>[^\\/\\)\\n]+)"
    let name = "(?<name>[^№\\n]+?№\\s*\\d+(\\.\\d+)?(\\s*\\([^\\)]+\\))?(\\s*:[^.!\\n]+?[\\.\\!]|[\\.\\!])?|[^\\.\\!\\n]+?[\\.\\!])"
    let description = "(?<description>.+?)"
    let questions = "(?<questions>\\d+ вопро[а-я]+)"
    let cost = "((?<cost>\\d+) рублей с (человека|игрока)\\s*)?\\)\\s*.?\\s*"
    return new RegExp(`^${start}${day}\\s*${month}\\s+\\(?${weekday}\\)\\s+${time}\\s+[/(]${place}[\\)]\\s*${name}\\s*${description}\\s*(\\(\\s*(${questions}.*[\\s\\/])?${cost})?$`, "gim")
}

SmuziParser.prototype.MatchToQuiz = function(match) {
    let day = match.groups.day.padStart(2, '0')
    let month = `${this.months.indexOf(match.groups.month.toLowerCase()) + 1}`.padStart(2, '0')
    let name = match.groups.name.replace(/\s*№\s*\d+(\.\d+)?[\.!]?|\.\s*$/gi, "").trim()

    return {
        line: match[0],
        day: +match.groups.day,
        month: match.groups.month,
        date: `${this.year}-${month}-${day}`,
        time: match.groups.time,
        place: this.GetPlace(match.groups.place),
        name: name,
        description: match.groups.description,
        category: this.GetCategory(name),
        questions: match.groups.questions === undefined ? 0 : +match.groups.questions,
        cost: +match.groups.cost,
        organizer: "Смузи"
    }
}

SmuziParser.prototype.ParsePost = function(text) {
    let regexp = this.GetRegexp()
    let quizzes = []

    for (let match of text.matchAll(regexp))
        quizzes.push(this.MatchToQuiz(match))

    return quizzes
}

SmuziParser.prototype.ParseLine = function(line) {
    let regexp = this.GetRegexp()
    let match = regexp.exec(line)

    if (match === null)
        return null

    return this.MatchToQuiz(match)
}

SmuziParser.prototype.GetPlace = function(parsedPlace) {
    for (let place of this.places)
        if (place.toLowerCase() == parsedPlace.toLowerCase())
            return place

    let bestRatio = 0
    let bestPlace = null

    for (let place of this.places) {
        let ratio = Ratio(place, this.PrepareParsedPlace(parsedPlace))

        if (ratio > bestRatio) {
            bestRatio = ratio
            bestPlace = place
        }
    }

    if (bestRatio > 0.7)
        return bestPlace

    return parsedPlace
}

SmuziParser.prototype.PrepareParsedPlace = function(place) {
    return place.replace(/бар|restobar|«|»/gi, "").trim()
}

SmuziParser.prototype.GetCategory = function(name) {
    name = name.toLowerCase().replace(/[.,!]/gi, "").replace(/\s+/g, " ")

    if (name.match(/гарри поттер|^гп /gi))
        return "ГП"

    if (name.match(/медиа-микс|кино и музыка|музыка и кино/gi))
        return "медиа-микс"

    if (name.match(/\bкмс\b|кино мультфильмы сериалы|мультфильм|угадай фильм|сериалы|топовые фильмы|кинохиты|киномания/gi))
        return "КМС"

    if (name.match(/ум[ :]|угадай мелодию/gi))
        return "УМ"

    if (name.match(/караоке/gi))
        return "караоке"

    if (name.match(/музыкальный (мега|квиз|риск)|музыка\b|танцуем и поём|русский рок/gi))
        return "музыка"

    return "прочее"
}
