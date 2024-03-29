function PlotAnalyticsChart() {
    let svg = document.getElementById("analytics-info-chart")
    let chart = new Chart()
    chart.Plot(svg, chart_data)
}

function PlotPositionsChart() {
    let svg = document.getElementById("analytics-positions-chart")
    let chart = new BarChart('positions', 5, 18, 25, 32, 45)
    let data = []

    for (let position = 1; position <= 16; position++)
        data.push({"position": position, "position-label": position <= 15 ? `${position}` : "ниже", "count": positions_data[position]})

    chart.Plot(svg, data, ["position"], "position-label", "count", "")
}

function PlotMonthData() {
    let svg = document.getElementById("analytics-months-info-chart")
    let chart = new BarChart()
    chart.Plot(svg, months_data, ["wins", "prizes", "top10", "other"], "date", "games", "")

    for (let key of ["wins", "prizes", "top10", "games", "last"]) {
        let keySvg = document.getElementById(`analytics-months-info-${key}-chart`)
        let keyChart = new BarChart()
        keyChart.Plot(keySvg, months_data, [key], "date", key, "")
    }
}
