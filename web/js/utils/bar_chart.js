function BarChart(config = null) {
    if (config === null)
        config = {}

    this.padding = config.padding || 5
    this.topPadding = config.topPadding || 18
    this.bottomPadding = config.bottomPadding || 25
    this.minRectWidth = config.minRectWidth || 48
    this.maxRectWidth = config.maxRectWidth || 60
    this.gap = config.gap || 2
    this.radius = config.radius || 5
    this.barColor = config.barColor || "#00bcd4"
    this.labelColor = config.labelColor || "#fff"
    this.labelSize = config.labelSize || 10
}

BarChart.prototype.GetMaxValue = function(data, key) {
    let max = 0

    for (let dataItem of data)
        max = Math.max(max, dataItem[key])

    return max > 0 ? max : 1
}

BarChart.prototype.AppendLabel = function(svg, x, y, labelText, baseline = "middle") {
    let lines = labelText.split("\n")

    for (let line of lines) {
        let label = document.createElementNS('http://www.w3.org/2000/svg', "text")
        label.textContent = line
        label.setAttribute("x", x)
        label.setAttribute("y", y)
        label.setAttribute("alignment-baseline", baseline)
        label.setAttribute("text-anchor", "middle")
        label.setAttribute("fill", this.labelColor)
        label.setAttribute("font-size", this.labelSize)
        svg.appendChild(label)
        y += label.getBBox().height
    }
}

BarChart.prototype.MakeBar = function(x, y, rectWidth, rectHeight, color) {
    let bar = document.createElementNS('http://www.w3.org/2000/svg', "rect")
    bar.setAttribute("x", x)
    bar.setAttribute("y", y)
    bar.setAttribute("width", rectWidth)
    bar.setAttribute("height", rectHeight)
    bar.setAttribute("rx", Math.min(this.radius, rectHeight / 4))
    bar.setAttribute("fill", color)
    return bar
}

BarChart.prototype.MakeDivider = function(x, y, width) {
    let path = document.createElementNS('http://www.w3.org/2000/svg', "path")
    path.setAttribute("d", `M${x} ${y} l${width} 0`)
    path.setAttribute("stroke-width", this.gap)
    path.setAttribute("class", 'chart-divider')
    return path
}

BarChart.prototype.AppendBar = function(svg, x, y, rectWidth, rectHeight, data, keys) {
    if (rectHeight == 0)
        return []

    let coords = []
    let total = 0
    let wasStart = false

    for (let key of keys)
        total += data[key]

    for (let i = 0; i < keys.length; i++) {
        let partHeight = data[keys[i]] / total * rectHeight
        svg.appendChild(this.MakeBar(x, y, rectWidth, partHeight, this.barColor))

        if (wasStart && partHeight > 0)
            coords.push(y)

        if (partHeight > 0)
            wasStart = true

        y += partHeight
    }

    for (let coord of coords)
        svg.appendChild(this.MakeDivider(x, coord, rectWidth))
}

BarChart.prototype.Plot = function(svg, data, keys, axisKey, labelKey, labelUnit) {
    let width = svg.clientWidth
    let height = svg.clientHeight
    let rectWidth = width / data.length - this.padding
    let maxValue = this.GetMaxValue(data, labelKey)

    if (rectWidth < this.minRectWidth) {
        rectWidth = this.minRectWidth
        width = (rectWidth + this.padding) * data.length
        svg.style.width = `${width}px`
    }
    else if (rectWidth > this.maxRectWidth) {
        rectWidth = this.maxRectWidth
    }

    svg.setAttribute("viewBox", `0 0 ${width} ${height}`)
    svg.innerHTML = ''

    for (let i = 0; i < data.length; i++) {
        let rectHeight = data[i][labelKey] / maxValue * (height - this.topPadding - this.bottomPadding)
        let x = this.padding / 2 + i * (this.padding + rectWidth)
        let y = height - this.bottomPadding - rectHeight

        this.AppendBar(svg, x, y, rectWidth, rectHeight, data[i], keys)

        this.AppendLabel(svg, x + rectWidth / 2, height - this.bottomPadding, data[i][axisKey], "before-edge")

        if (data[i][labelKey] == 0)
            continue

        this.AppendLabel(svg, x + rectWidth / 2, y - 3, `${data[i][labelKey]}`, "top")
    }
}