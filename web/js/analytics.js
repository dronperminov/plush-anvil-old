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
    svg.clientHeight = 300

    let chart = new BarChart({barColor: colors.positions, minRectWidth: 32, maxRectWidth: 45, bottomPadding: 12})
    let data = []

    for (let position = 1; position <= 16; position++)
        data.push({"position": position, "position-label": position <= 15 ? `${position}` : "ниже", "count": positions[position]})

    chart.Plot(svg, data, "position-label", "count")
}

function PlotMonthData() {
    for (let key of ["wins", "prizes", "top10", "games", "last", "mean_position", "mean_players"]) {
        let keySvg = document.getElementById(`analytics-months-info-${key}-chart`)
        let keyChart = new BarChart({barColor: colors[key]})
        keyChart.Plot(keySvg, months_data, "date", key)
    }

    if (+months_data[months_data.length - 1]["date"].split("\n")[1] < 2024)
        return

    let start = months_data.map(data => data["date"]).indexOf("декабрь\n2023") + 1
    let svg = document.getElementById(`analytics-months-info-rating-chart`)
    let chart = new BarChart({barColor: colors["rating"]})
    chart.Plot(svg, months_data, "date", "rating", start)
}
