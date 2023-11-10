const MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
const WEEKDAYS = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
const FULL_WEEKDAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

function QuizParser(places, year) {
    this.places = places
    this.year = year
}

QuizParser.prototype.Parse = function(line) {
    let match = this.ParseSmuzi(line)
    if (match !== null)
        return match

    match = this.ParsePeace(line)
    if (match !== null)
        return match

    return null
}

QuizParser.prototype.GetSmuziRegExp = function() {
    let day = `(?<day>\\d\\d?)`
    let month = `*(?<month>${MONTHS.join("|")})`
    let weekday = `(?<weekday>${WEEKDAYS.join("|")})`
    let time = `(?<time>\\d\\d?:\\d\\d?)`
    let place = `(?<place>${this.places.map(place => place.toLowerCase()).join("|")})`
    let name = `(?<name>[^\\.]+)`
    let cost = `(?<cost>\\d+)`
    let description = `(?<description>[\\w\\W]*(\\s+|\\()${cost}\\s+рублей.*)`

    return new RegExp(`${day}\\s${month}\\s+${weekday}\\s+${time}\\s+/\\s*${place}\\s*/\\s+${name}\\.\\s*${description}$`, "gi")
}

QuizParser.prototype.GetPeaceRegExp = function() {
    let day = `(?<day>\\d\\d?)`
    let month = `*(?<month>${MONTHS.join("|")})`
    let weekday = `(?<weekday>${FULL_WEEKDAYS.join("|")})`
    let time = `(в\\s+)?(?<time>\\d\\d?:\\d\\d?)`
    let place = `(\\|\\s*|\\(в ")(?<place>[\\w\\W]+)(\\s*\\||"\\))`
    let name = `(-\\s+|квиз\\s+")?(?<name>[^\\.]+)("\\.)?`
    let description = `\\(?(?<description>[\\w\\W]*)\\)?`

    return new RegExp(`${day}\\s${month}\\s+\\(${weekday}\\)\\s+${time}\\s+${place}\\s*${name}\\s*${description}$`, "gi")
}

QuizParser.prototype.ParseSmuzi = function(line) {
    let regexp = this.GetSmuziRegExp()
    let match = regexp.exec(line)

    if (match === null)
        return null

    let day = match.groups.day.padStart(2, '0')
    let month = `${MONTHS.indexOf(match.groups.month.toLowerCase()) + 1}`.padStart(2, '0')

    return {
        date: `${this.year}-${month}-${day}`,
        name: match.groups.name.replace(/№\d+\s*/gi, "").trim(),
        time: match.groups.time,
        place: this.GetPlace(match.groups.place),
        description: match.groups.description,
        cost: +match.groups.cost,
        organizer: "Смузи"
    }
}

QuizParser.prototype.ParsePeace = function(line) {
    let regexp = this.GetPeaceRegExp()
    let match = regexp.exec(line)

    if (match === null)
        return null

    let day = match.groups.day.padStart(2, '0')
    let month = `${MONTHS.indexOf(match.groups.month.toLowerCase()) + 1}`.padStart(2, '0')

    return {
        date: `${this.year}-${month}-${day}`,
        name: match.groups.name.replace(/№\d+\s*/gi, "").trim(),
        time: match.groups.time,
        place: this.GetPlace(match.groups.place),
        description: match.groups.description,
        cost: 600,
        organizer: "PeaceQuiz"
    }
}

QuizParser.prototype.GetPlace = function(parsedPlace) {
    for (let place of this.places)
        if (place.toLowerCase() == parsedPlace.toLowerCase())
            return place

    let bestRatio = 0
    let bestPlace = null

    for (let place of this.places) {
        let ratio = this.Ratio(place, this.PrepareParsedPlace(parsedPlace))

        if (ratio > bestRatio) {
            bestRatio = ratio
            bestPlace = place
        }
    }

    if (bestRatio > 0.7)
        return bestPlace

    return null
}

QuizParser.prototype.PrepareParsedPlace = function(place) {
    return place.replace(/бар|restobar|«|»/gi, "").trim()
}

QuizParser.prototype.LevenshteinDistance = function(s, t) {
    if (!s.length)
        return t.length

    if (!t.length)
        return s.length

    let arr = []

    for (let i = 0; i <= t.length; i++) {
        arr[i] = [i]

        for (let j = 1; j <= s.length; j++)
            arr[i][j] = i === 0 ? j : Math.min(arr[i - 1][j] + 1, arr[i][j - 1] + 1, arr[i - 1][j - 1] + (s[j - 1] === t[i - 1] ? 0 : 1))
    }

    return arr[t.length][s.length]
}

QuizParser.prototype.Ratio = function(s, t) {
    let len = Math.max(s.length, t.length)
    let distance = this.LevenshteinDistance(s, t)
    return 1 - distance / Math.max(len, 1)
}
