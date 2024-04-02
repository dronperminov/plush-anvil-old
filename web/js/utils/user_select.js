function UserSelect(users, blockId, canChangePaid, onChange) {
    this.users = users
    this.onChange = onChange
    this.canChangePaid = canChangePaid

    this.Build(blockId)
}

UserSelect.prototype.Build = function(blockId) {
    this.block = document.getElementById(blockId)
    this.block.classList.add("user-select")

    this.inputBlock = this.MakeElement("user-select-input", this.block)
    this.resultsBlock = this.MakeElement("user-select-result", this.block)

    this.BuildQuery()
    this.BuildUsers()
    this.BuildResults()
}

UserSelect.prototype.BuildQuery = function() {
    let queryBlock = this.MakeElement("user-select-query", this.inputBlock)
    this.queryInput = this.MakeElement("user-select-query-input basic-input default-input", queryBlock, {type: "text", placeholder: "начните вводить"}, "input")
    this.queryInput.addEventListener("input", () => this.FilterUsers())
}

UserSelect.prototype.BuildUsers = function() {
    let usersBlock = this.MakeElement("user-select-users", this.inputBlock)

    for (let [username, user] of Object.entries(this.users)) {
        user.block = this.BuildUser(usersBlock, user)
        user.isSelect = false
        user.isPaid = true
    }

    this.noMatches = this.MakeElement("user-select-no-matches user-select-hidden", this.inputBlock, {innerText: "никого не нашлось"})
}

UserSelect.prototype.BuildResults = function() {
    let block = this.MakeElement("user-select-results", this.resultsBlock)
    this.MakeElement("user-select-results-header user-select-hidde", block, {innerText: "Выбранные пользователи"})

    for (let user of Object.values(this.users)) {
        let result = this.BuildResultUser(block, user)
        user.resultBlock = result.block
        user.resultCheckbox = result.checkbox
    }

    this.noResults = this.MakeElement("user-select-no-results", block, {innerText: "нет выбранных пользователей"})
}

UserSelect.prototype.BuildUser = function(parent, user) {
    let block = this.MakeElement("user-select-user", parent)
    let img = this.MakeElement("user-select-user-avatar", block, {src: user.image_src, alt: `Аватар пользователя ${user.username}`}, "img")
    let name = this.MakeElement("user-select-user-name", block, {innerText: `${user.fullname} (@${user.username})`})

    block.addEventListener("click", () => {
        this.SelectUser(user.username)
        this.onChange()
    })

    return block
}

UserSelect.prototype.BuildResultUser = function(parent, user, isResult, onclick) {
    let block = this.MakeElement("user-select-user user-select-hidden", parent)
    let img = this.MakeElement("user-select-user-avatar", block, {src: user.image_src, alt: `Аватар пользователя ${user.username}`}, "img")
    let name = this.MakeElement("user-select-user-name", block, {innerText: `${user.fullname} (@${user.username})`})

    img.addEventListener("click", () => {
        this.RemoveUser(user.username)
        this.onChange()
    })

    let paid = this.MakeElement("user-select-user-paid", name)
    let label = this.MakeElement("", paid, {}, "label")
    let checkbox = this.MakeElement("", label, {type: "checkbox", checked: true}, "input")
    let span = this.MakeElement("", label, {innerText: " платно"}, "span")

    if (!this.canChangePaid)
        paid.classList.add("user-select-hidden")

    checkbox.addEventListener("change", () => {
        user.isPaid = checkbox.checked
        this.onChange()

    })

    return {"block": block, "checkbox": checkbox}
}

UserSelect.prototype.FilterUsers = function() {
    let query = this.queryInput.value.toLowerCase().trim()
    let translit = this.Transliterate(query)

    let haveMatched = false
    let haveSelected = false

    for (let user of Object.values(this.users)) {
        user.resultCheckbox.checked = user.isPaid

        if (user.isSelect) {
            user.resultBlock.classList.remove("user-select-hidden")
            haveSelected = true
        }
        else
            user.resultBlock.classList.add("user-select-hidden")

        if (!user.isSelect && this.IsUserMatch(user, [query, translit])) {
            haveMatched = true
            user.block.classList.remove("user-select-hidden")
        }
        else
            user.block.classList.add("user-select-hidden")
    }

    if (haveMatched)
        this.noMatches.classList.add("user-select-hidden")
    else
        this.noMatches.classList.remove("user-select-hidden")

    if (haveSelected)
        this.noResults.classList.add("user-select-hidden")
    else
        this.noResults.classList.remove("user-select-hidden")
}

UserSelect.prototype.IsUserMatch = function(user, queries) {
    for (let query of queries) {
        if (user.username.toLowerCase().indexOf(query) != -1)
            return true

        if (user.fullname.toLowerCase().indexOf(query) != -1)
            return true
    }

    return false
}

UserSelect.prototype.Transliterate = function(query) {
    let rus = "абвгдеёжзийклмнопрстуфхцшщю"
    let eng = "abvgdeezzijklmnoprstufhcssu"
    let map = {}

    for (let i = 0; i < rus.length; i++) {
        map[rus[i]] = eng[i]
        map[eng[i]] = rus[i]
    }

    return query.split("").map(c => c in map ? map[c] : c).join("")
}

UserSelect.prototype.SelectUser = function(username, isPaid = true) {
    this.users[username].isSelect = true
    this.users[username].isPaid = isPaid

    this.FilterUsers()
}

UserSelect.prototype.RemoveUser = function(username) {
    this.users[username].isSelect = false
    this.users[username].isPaid = true

    this.FilterUsers()
}

UserSelect.prototype.GetSelected = function() {
    let selected = []

    for (let [username, user] of Object.entries(this.users))
        if (user.isSelect)
            selected.push({username: username, paid: this.canChangePaid ? user.isPaid : true})

    return selected
}

UserSelect.prototype.SetAttributes = function(element, attributes) {
    if (attributes === null)
        return

    for (let [name, value] of Object.entries(attributes)) {
        if (name == "innerText")
            element.innerText = value
        else if (name == "innerHTML")
            element.innerHTML = value
        else
            element.setAttribute(name, value)
    }
}

UserSelect.prototype.MakeElement = function(className, parent = null, attributes = null, tagName = "div") {
    let element = document.createElement(tagName)
    element.className = className

    this.SetAttributes(element, attributes)

    if (parent !== null)
        parent.appendChild(element)

    return element
}
