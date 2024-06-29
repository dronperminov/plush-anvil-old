function YearGrid(blockId, events, colors) {
	this.block = document.getElementById(blockId)
	this.grid = this.MakeElement("year-grid", this.MakeElement("year-grid-scrollable", this.block))

	this.events = events
	this.colors = colors
	this.years = this.GetYears()

	this.InitMarkers()
}

YearGrid.prototype.InitMarkers = function() {
	this.markers = this.MakeElement("year-grid-markers", this.MakeElement("year-grid-scrollable", this.block))

	for (let year of this.years) {
		let marker = this.MakeElement("year-grid-marker", this.markers, {innerText: year})
		marker.addEventListener("click", () => this.ClickOnMarker(marker, year))
	}

	this.markers.children[0].click()
}

YearGrid.prototype.GetYears = function() {
	if (this.events.length == 0)
		return [new Date().getFullYear()]

	let years = new Set()

	for (let date of this.events)
		years.add(+date.split("-")[0])

	return Array.from(years).sort().reverse()
}

YearGrid.prototype.GetKey = function(date) {
	let month = `${date.getMonth() + 1}`.padStart(2, '0')
	let day = `${date.getDate()}`.padStart(2, '0')
	let year = date.getFullYear()
	return `${day}.${month}.${year}`
}

YearGrid.prototype.FilterEvents = function(startDate, endDate) {
	let events = {}

	for (let eventDate of this.events) {
		let [year, month, day] = eventDate.split("-").map(v => +v)
		let date = new Date(year, month - 1, day)

		if (date < startDate || endDate < date)
			continue

		let key = this.GetKey(date)

		if (key in events)
			events[key] += 1
		else
			events[key] = 1
	}

	return events
}

YearGrid.prototype.SetAttributes = function(element, attributes) {
    for (let [name, value] of Object.entries(attributes)) {
        if (name == "innerText")
            element.innerText = value
        else
            element.setAttribute(name, value)
    }
}

YearGrid.prototype.MakeElement = function(className, parent, attributes = null) {
    let element = document.createElement("div")
    element.setAttribute("class", className)

    if (attributes !== null)
    	this.SetAttributes(element, attributes)

    parent.appendChild(element)

    return element
}

YearGrid.prototype.AddMonths = function(date, months) {
	let month = date.getMonth() + months
	let year = date.getFullYear() + Math.floor(month / 12)
	return new Date(year, month % 12, 0)
}

YearGrid.prototype.GetColor = function(count, max) {
	if (count == 0)
		return this.colors[0]

	if (max == 1)
		return this.colors[1]

	return this.colors[1 + Math.floor(count / max * (this.colors.length - 2))]
}

YearGrid.prototype.Build = function(startDate = null) {
	if (startDate == null)
		startDate = new Date(this.years[0], 0, 1)

	let endDate = this.AddMonths(startDate, 12)

	let startSkip = (startDate.getDay() + 6) % 7
	let endSkip = (7 - endDate.getDay()) % 7

	let events = this.FilterEvents(startDate, endDate)
	let max = Math.max(...Object.values(events))

	let months = this.GetMonths(startDate, endDate, startSkip)
	let monthIndex = 0

	this.grid.innerHTML = ""

	this.AddWeekdayCells()
	this.AddMonthCell(months[monthIndex++])
	this.AddSkipCells(startSkip)

	let lastMonth = startDate.getMonth()
	let weekCount = 0
	let weekCells = []

	for (let date = new Date(startDate), index = startSkip; date <= endDate; date.setDate(date.getDate() + 1), index++) {
		if (date.getMonth() != lastMonth && index % 7 == 0) {
			this.AddMonthCell(months[monthIndex++])
			lastMonth = date.getMonth()
		}

		let dateKey = this.GetKey(date)
		let count = dateKey in events ? events[dateKey] : 0
		this.MakeElement("year-grid-day-cell", this.grid, {title: `${dateKey}: ${count}`, style: `background: ${this.GetColor(count, max)}`})

		weekCount += count

		if (index % 7 == 6) {
			weekCells.push(this.AddWeekCell(weekCount))
			weekCount = 0
		}
	}

	this.AddSkipCells(endSkip)

	if (endSkip > 0)
		weekCells.push(this.AddWeekCell(weekCount))

	this.UpdateWeekCells(weekCells)
}

YearGrid.prototype.AddMonthCell = function(month) {
	this.MakeElement("year-grid-month-cell", this.grid, {innerText: month.name, style: `grid-column-end: span ${month.span}`})
}

YearGrid.prototype.AddWeekdayCells = function() {
	for (let day of ["", "пн", "вт", "ср", "чт", "пт", "сб", "вс", "", "нед"])
		this.MakeElement("year-grid-weekday-cell", this.grid, {innerText: day})
}

YearGrid.prototype.AddSkipCells = function(skip) {
	for (let i = 0; i < skip; i++)
		this.MakeElement("year-grid-skip-cell", this.grid)
}

YearGrid.prototype.AddWeekCell = function(count) {
	this.MakeElement("year-grid-week-cell", this.grid, {innerText: count > 0 ? count : ""})
	let cell = this.MakeElement("year-grid-day-cell", this.grid, {title: count})

	return {cell, count}
}

YearGrid.prototype.UpdateWeekCells = function(weekCells) {
	let max = Math.max(...weekCells.map(v => v.count))

	for (let cell of weekCells)
		cell.cell.style.background = this.GetColor(cell.count, max)
}

YearGrid.prototype.GetMonths = function(startDate, endDate, skip) {
	let lastMonth = startDate.getMonth() - 1
	let monthNames = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
	let months = []
	let indices = []
	let index = skip

	for (let date = new Date(startDate); date <= endDate; date.setDate(date.getDate() + 1), index++) {
		let month = date.getMonth()

		if (month != lastMonth && (index == skip || index % 7 == 0)) {
			months.push({name: monthNames[month], span: 0})
			lastMonth = month
			indices.push(Math.floor(index / 7))
		}
	}

	indices.push(Math.floor((index - 1) / 7) + 1)

	for (let i = 1; i < indices.length; i++)
		months[i - 1].span = indices[i] - indices[i - 1]

	return months
}

YearGrid.prototype.ClickOnMarker = function(target, year) {
	for (let marker of this.markers.children)
		marker.classList.remove("year-grid-marker-active")
	
	target.classList.add("year-grid-marker-active")

	this.Build(new Date(year, 0, 1))
}