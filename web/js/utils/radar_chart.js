function RadarChart(config = null) {
	if (config === null)
        config = {}

	this.paddingX = config.paddingX || 25
	this.paddingY = config.paddingY || 20

	this.labelColor = config.labelColor || "#212121"
	this.labelSize = config.labelSize || 10
	this.labelPadding = config.labelPadding || 20

	this.axesColor = config.axesColor || "#d9d9d9"
	this.axesWidth = config.axesWidth || 1

	this.lineColor = config.lineColor || "#c238a2"
	this.lineFillColor = config.lineFillColor || "#c238a220"
	this.lineWidth = config.lineWidth || 2

	this.pointColor = config.pointColor || "#c238a2"
	this.pointFillColor = config.pointFillColor || "#ffffff"
	this.pointRadius = config.pointRadius || 3
	this.pointStrokeSize = config.pointStrokeSize || 2
}

RadarChart.prototype.GetAxesData = function(data, size, x, y) {
	let maxValue = Math.max(...data.map(v => v.value))
	let axesData = []
	let indices = []

	for (let i = 0; i < data.length; i++) {
		let angle = i / data.length * 2 * Math.PI + Math.PI / 4
		let ax = x + size / 2 * Math.cos(angle)
		let ay = y + size / 2 * Math.sin(angle)

		let lx = x + (size + this.labelPadding) / 2 * Math.cos(angle)
		let ly = y + (size + this.labelPadding) / 2 * Math.sin(angle)

		axesData.push({angle, ax, ay, lx, ly})
		indices.push(i)
	}

	axesData.sort((a, b) => Math.abs(a.lx - x) - Math.abs(b.lx - x))
	indices.sort((a, b) => data[b].label.length - data[a].label.length)

	for (let i = 0; i < data.length; i++) {
		let value = data[indices[i]].value / maxValue
		axesData[i].vx = x + value * (size - this.pointRadius) / 2 * Math.cos(axesData[i].angle)
		axesData[i].vy = y + value * (size - this.pointRadius) / 2 * Math.sin(axesData[i].angle)

		axesData[i].label = data[indices[i]].label
		axesData[i].color = data[indices[i]].color || this.labelColor
	}

	axesData.sort((a, b) => a.angle - b.angle)

	return axesData
}

RadarChart.prototype.GetPathCircle = function(x, y, r) {
	return `M${x} ${y} m${r}, 0 a${r},${r} 0 1,0 -${r * 2},0 a${r},${r} 0 1,0 ${r * 2},0`
}

RadarChart.prototype.PlotAxes = function(svg, size, x, y, axesData) {
	let path = this.GetPathCircle(x, y, size / 2) + this.GetPathCircle(x, y, size / 4)

	for (let point of axesData)
		path += ` M${x} ${y} L${point.ax} ${point.ay}`

	let axes = document.createElementNS('http://www.w3.org/2000/svg', "path")
	axes.setAttribute("d", path)
	axes.setAttribute("stroke", this.axesColor)
	axes.setAttribute("fill", "none")
	axes.setAttribute("stroke-width", this.axesWidth)
	svg.appendChild(axes)
}

RadarChart.prototype.PlotLabels = function(svg, x, y, axesData) {
	let radius = this.labelSize / 3

	for (let point of axesData) {
		let label = document.createElementNS('http://www.w3.org/2000/svg', "text")
		let isRight = point.lx > x
		let isCenter = Math.abs(point.lx - x) < 10

        label.textContent = point.label
        label.setAttribute("x", isRight ? point.lx + radius + 2 : point.lx)
        label.setAttribute("y", point.ly)
        label.setAttribute("dominant-baseline", "central")
        label.setAttribute("text-anchor", isCenter ? "middle" : (isRight ? "start" : "end"))
        label.setAttribute("fill", this.labelColor)
        label.setAttribute("font-size", this.labelSize)
        svg.appendChild(label)

        let circle = document.createElementNS('http://www.w3.org/2000/svg', "circle")
		circle.setAttribute("cx", isRight ? point.lx : label.getBBox().x - radius - 2)
		circle.setAttribute("cy", point.ly)
		circle.setAttribute("r", radius)
		circle.setAttribute("stroke", "none")
		circle.setAttribute("fill", point.color)
		svg.appendChild(circle)
	}
}

RadarChart.prototype.PlotRadar = function(svg, axesData) {
	let path = axesData.map((point, index) => `${index == 0 ? "M" : "L"}${point.vx} ${point.vy}`)

	let line = document.createElementNS('http://www.w3.org/2000/svg', "path")
	line.setAttribute("d", `${path.join(" ")} z`)
	line.setAttribute("stroke", this.lineColor)
	line.setAttribute("fill", this.lineFillColor)
	line.setAttribute("stroke-width", this.lineWidth)
	svg.appendChild(line)

	for (let point of axesData) {
		let circle = document.createElementNS('http://www.w3.org/2000/svg', "circle")
		circle.setAttribute("cx", point.vx)
		circle.setAttribute("cy", point.vy)
		circle.setAttribute("r", this.pointRadius)
		circle.setAttribute("stroke", this.pointColor)
		circle.setAttribute("fill", this.pointFillColor)
		circle.setAttribute("stroke-width", this.pointStrokeSize)
		svg.appendChild(circle)
	}
}

RadarChart.prototype.Plot = function(svgId, data) {
	let svg = document.getElementById(svgId)
	let width = svg.clientWidth
	let height = svg.clientHeight

	let size = Math.min(width - 2 * this.paddingX, height - 2 * this.paddingY)
	let x = Math.floor(width / 2)
	let y = Math.floor(height / 2)
	let axesData = this.GetAxesData(data, size, x, y)

	svg.innerHTML = ""
	this.PlotAxes(svg, size, x, y, axesData)
	this.PlotLabels(svg, x, y, axesData)
	this.PlotRadar(svg, axesData)
}
