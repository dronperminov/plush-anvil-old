function FilterTable(tableId, showSize = 10, showAdditionalColumns = false) {
    this.table = document.getElementById(tableId)
    this.header = this.table.children[0]

    this.showBtn = document.getElementById(`${tableId}-show`)
    this.showBtn.addEventListener("click", () => this.ShowNewRows())

    this.collapseBtn = document.getElementById(`${tableId}-collapse`)
    this.collapseBtn.addEventListener("click", () => this.CollapseRows())

    this.showSize = showSize
    this.showCount = 0
    this.showAdditionalColumns = showAdditionalColumns

    this.ShowNewRows()
}

FilterTable.prototype.UpdateAdditionalColumns = function(value) {
    this.showAdditionalColumns = value
    this.Show()
}

FilterTable.prototype.Show = function() {
    this.UpdateButtons()

    let index = -1

    for (let tr of this.table.children) {
        if (index < this.showCount)
            tr.classList.remove("hidden")
        else
            tr.classList.add("hidden")

        for (let td of tr.getElementsByClassName("column-addition")) {
            if (this.showAdditionalColumns)
                td.classList.remove("hidden")
            else
                td.classList.add("hidden")
        }

        index++
    }
}

FilterTable.prototype.HideButton = function(button, condition) {
    if (condition)
        button.classList.add("hidden")
    else
        button.classList.remove("hidden")
}

FilterTable.prototype.UpdateButtons = function() {
    let total = this.GetTotalRows()

    this.showCount = Math.min(this.showCount, total)
    this.HideButton(this.showBtn, this.showCount == total)
    this.HideButton(this.collapseBtn, this.showCount <= this.showSize)
}

FilterTable.prototype.ShowNewRows = function() {
    this.showCount += this.showSize
    this.Show()
}

FilterTable.prototype.CollapseRows = function() {
    this.showCount = this.showSize
    this.Show()
    this.table.scrollIntoView({behavior: "smooth", block: "start"})
}

FilterTable.prototype.GetTotalRows = function() {
    return this.table.children.length - 1
}

FilterTable.prototype.GetColumn = function(tr, name, autoType) {
    let content = tr.getElementsByClassName(`column-${name}`)[0].innerText

    if (!autoType)
        return content.toLowerCase()

    if (content.match(/^\d+$/g) !== null)
        return +content

    if (content.match(/^\d\d?\.\d\d?\.\d\d\d\d$/g) !== null) {
        let [day, month, year] = content.split(".")
        return new Date(+year, +month - 1, +day)
    }

    return content
}

FilterTable.prototype.CompareRows = function(row1, row2, sign) {
    if (row1.value < row2.value)
        return -sign

    if (row1.value > row2.value)
        return sign

    return row1.index - row2.index
}

FilterTable.prototype.SortByColumn = function(name, autoType = true) {
    let data = []

    for (let i = 1; i < this.table.children.length; i++)
        data.push({tr: this.table.children[i], index: +this.table.children[i].getAttribute("data-index"), value: this.GetColumn(this.table.children[i], name, autoType)})

    let targetCell = this.header.getElementsByClassName(`column-${name}`)[0]

    if (targetCell.classList.contains("order-asc") || targetCell.classList.contains("order-desc")) {
        targetCell.classList.toggle("order-asc")
        targetCell.classList.toggle("order-desc")
    }
    else {
        targetCell.classList.add("order-asc")
    }

    let sign = targetCell.classList.contains("order-asc") ? 1 : -1

    for (let td of this.header.children) {
        if (td == targetCell)
            continue

        td.classList.remove("order-asc")
        td.classList.remove("order-desc")
    }

    data.sort((a, b) => this.CompareRows(a, b, sign))

    while (this.table.children.length > 1)
        this.table.removeChild(this.table.children[this.table.children.length - 1])

    for (let row of data)
        this.table.appendChild(row.tr)

    this.Show()
}