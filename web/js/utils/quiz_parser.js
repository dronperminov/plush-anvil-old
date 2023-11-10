const MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
const WEEKDAYS = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]

function QuizParser(places, year) {
    this.places = places
    this.year = year
}

QuizParser.prototype.Parse = function(line) {
    let match = this.ParseSmuzi(line)
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

    return new RegExp(`${day}\\s${month}\\s+${weekday}\\s+${time}\\s+/${place}/\\s+${name}\\.\\s*${description}$`, "gi")
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
        name: match.groups.name.replace(/№\d+\s*/gi, ""),
        weekday: match.groups.weekday,
        time: match.groups.time,
        place: this.GetPlace(match.groups.place),
        description: match.groups.description,
        cost: +match.groups.cost,
        organizer: "Смузи"
    }
}

QuizParser.prototype.GetPlace = function(parsedPlace) {
    for (let place of this.places)
        if (place.toLowerCase() == parsedPlace.toLowerCase())
            return place

    return null
}
