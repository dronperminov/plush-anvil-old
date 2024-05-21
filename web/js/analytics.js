function PlotAnalyticsChart() {
    let svg = document.getElementById("analytics-info-chart")
    let chart = new Chart()
    chart.Plot(svg, chart_data)
}

function PlotCategoriesChart() {
    let svg = document.getElementById("analytics-categories-chart")
    let chart = new Chart()
    chart.Plot(svg, categories_data)
}

function PlotPositionsChart(svgId, positions) {
    let svg = document.getElementById(svgId)
    let chart = new BarChart({barColor: colors.positions, minRectWidth: 32, maxRectWidth: 45})
    let data = []

    for (let position = 1; position <= 16; position++)
        data.push({"position": position, "position-label": position <= 15 ? `${position}` : "ниже", "count": positions[position]})

    chart.Plot(svg, data, "position-label", "count")
}

function PlotMonthData() {
    for (let key of ["wins", "prizes", "top10", "games", "last", "mean_position", "mean_players", "rating"]) {
        let keySvg = document.getElementById(`analytics-months-info-${key}-chart`)
        let keyChart = new BarChart({barColor: colors[key]})
        keyChart.Plot(keySvg, months_data, "date", key)
    }
}
