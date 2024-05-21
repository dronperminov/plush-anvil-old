function BarChart(config = null) {
    if (config === null)
        config = {}

    this.padding = config.padding || 5
    this.topPadding = config.topPadding || 18
    this.bottomPadding = config.bottomPadding || 25
    this.minRectWidth = config.minRectWidth || 48
    this.maxRectWidth = config.maxRectWidth || 60
    this.radius = config.radius || 5
    this.barColor = config.barColor || "#00bcd4"
    this.labelColor = config.labelColor || "#fff"
    this.labelSize = config.labelSize || 10
}

BarChart.prototype.GetLimits = function(data, key) {
    let max = -Infinity
    let min = Infinity

    for (let dataItem of data) {
        max = Math.max(max, dataItem[key])
        min = Math.min(min, dataItem[key])
    }

    if (min == max)
        max = min + 1

    if (min > 0)
        min = 0

    if (max < 0)
        max = 0

    return {max: max, min: min, delta: max - min}
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

BarChart.prototype.AppendBar = function(svg, x, y, rectWidth, rectHeight) {
    if (rectHeight <= 0)
        return

    let bar = document.createElementNS('http://www.w3.org/2000/svg', "rect")
    bar.setAttribute("x", x)
    bar.setAttribute("y", y)
    bar.setAttribute("width", rectWidth)
    bar.setAttribute("height", rectHeight)
    bar.setAttribute("rx", Math.min(this.radius, rectHeight / 4))
    bar.setAttribute("fill", this.barColor)

    svg.appendChild(bar)
}

BarChart.prototype.Map = function(x, xmin, xmax, min, max) {
    return (x - xmin) * (max - min) / (xmax - xmin) + min
}

BarChart.prototype.Plot = function(svg, data, axisKey, labelKey) {
    let width = svg.clientWidth
    let height = svg.clientHeight
    let rectWidth = width / data.length - this.padding
    let limits = this.GetLimits(data, labelKey)

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

    let availableHeight = (height - this.topPadding - this.bottomPadding)
    let zero = limits.min / limits.delta * availableHeight + height - this.bottomPadding

    for (let i = 0; i < data.length; i++) {
        let rectHeight = data[i][labelKey] / limits.delta * availableHeight
        let x = this.padding / 2 + i * (this.padding + rectWidth)
        let y = zero - Math.max(rectHeight, 0)

        this.AppendBar(svg, x, y, rectWidth, Math.abs(rectHeight))
        this.AppendLabel(svg, x + rectWidth / 2, height - this.bottomPadding, data[i][axisKey], "before-edge")

        if (data[i][labelKey] == 0)
            continue

        this.AppendLabel(svg, x + rectWidth / 2, y - 3, `${data[i][labelKey]}`, "top")
    }
}
