function PlotChart(config = null) {
    if (config === null)
        config = {}

    this.topPadding = config.topPadding || 18
    this.bottomPadding = config.bottomPadding || 25
    this.minMarkerWidth = config.minMarkerWidth || 48
    this.maxMarkerWidth = config.maxMarkerWidth || 60
    this.markerRadius = config.markerRadius || 5
    this.markerColor = config.markerColor || "#00bcd4"
    this.labelColor = config.labelColor || "#212121"
    this.labelSize = config.labelSize || 10
}

PlotChart.prototype.GetLimits = function(data, key, startIndex) {
    let max = -Infinity
    let min = Infinity

    for (let i = startIndex; i < data.length; i++) {
        max = Math.max(max, data[i][key])
        min = Math.min(min, data[i][key])
    }

    if (min == max)
        max = min + 1

    if (min > 0)
        min = 0

    if (max < 0)
        max = 0

    return {max: max, min: min, delta: max - min}
}

PlotChart.prototype.AppendLabel = function(svg, x, y, labelText, baseline = "middle", align = "middle", color) {
    let lines = labelText.split("\n")

    for (let line of lines) {
        let label = document.createElementNS('http://www.w3.org/2000/svg', "text")
        label.textContent = line
        label.setAttribute("x", x)
        label.setAttribute("y", y)
        label.setAttribute("alignment-baseline", baseline)
        label.setAttribute("text-anchor", align)
        label.setAttribute("fill", color)
        label.setAttribute("font-size", this.labelSize)
        svg.appendChild(label)
        y += label.getBBox().height
    }
}

PlotChart.prototype.AppendMarker = function(svg, x, y) {
    let marker = document.createElementNS('http://www.w3.org/2000/svg', "circle")
    marker.setAttribute("cx", x)
    marker.setAttribute("cy", y)
    marker.setAttribute("r", this.markerRadius)
    marker.setAttribute("fill", this.markerColor)

    svg.appendChild(marker)
}

PlotChart.prototype.AppendPath = function(svg) {
    let path = document.createElementNS('http://www.w3.org/2000/svg', "path")
    svg.appendChild(path)
    return path
}

PlotChart.prototype.PlotPaths = function(line, path, points, height) {
    let firstPoint = {x: points[0].x, y: height - this.bottomPadding}
    let lastPoint = {x: points[points.length - 1].x, y: height - this.bottomPadding}

    line.setAttribute("stroke", this.markerColor)
    line.setAttribute("stroke-width", this.markerRadius / 2)
    line.setAttribute("fill", "none")
    line.setAttribute("d", points.map((point, index) => `${index == 0 ? "M" : "L"}${point.x} ${point.y}`).join(" "))

    path.setAttribute("stroke", "none")
    path.setAttribute("fill", `${this.markerColor}30`)
    path.setAttribute("d", [firstPoint, ...points, lastPoint].map((point, index) => `${index == 0 ? "M" : "L"}${point.x} ${point.y}`).join(" "))
}

PlotChart.prototype.Map = function(x, xmin, xmax, min, max) {
    return (x - xmin) * (max - min) / (xmax - xmin) + min
}

PlotChart.prototype.Plot = function(svg, data, axisKey, labelKey, startIndex = 0) {
    let width = svg.clientWidth
    let height = svg.clientHeight == 0 ? 300 : svg.clientHeight
    let markerWidth = width / (data.length - startIndex)
    let limits = this.GetLimits(data, labelKey, startIndex)

    if (markerWidth < this.minMarkerWidth) {
        markerWidth = this.minMarkerWidth
        width = markerWidth * (data.length - startIndex)
        svg.style.width = `${width}px`
    }
    else if (markerWidth > this.maxMarkerWidth) {
        markerWidth = this.maxMarkerWidth
    }

    svg.setAttribute("viewBox", `0 0 ${width} ${height}`)
    svg.innerHTML = ''

    let path = this.AppendPath(svg)
    let line = this.AppendPath(svg)
    let points = []

    for (let i = startIndex; i < data.length; i++) {
        let x = (i - startIndex) * markerWidth + markerWidth / 2
        let y = this.Map(data[i][labelKey], limits.min, limits.max, height - this.bottomPadding, this.topPadding)
        let offset = i == startIndex ? this.markerRadius - markerWidth / 2 : i == data.length - startIndex - 1 ? markerWidth / 2 - this.markerRadius : 0
        let align = i == startIndex ? "start" : i == data.length - startIndex - 1 ? "end" : "middle"

        this.AppendMarker(svg, x + offset, y)
        this.AppendLabel(svg, x, height - this.bottomPadding, data[i][axisKey], "before-edge", "middle", this.labelColor)
        this.AppendLabel(svg, x + offset, y - this.markerRadius - 3, `${data[i][labelKey]}`, "top", align, this.labelColor)

        points.push({x: x + offset, y: y})
    }

    this.PlotPaths(line, path, points, height)    
}
