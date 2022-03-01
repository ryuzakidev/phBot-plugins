from phBot import *
import QtBind
import math
import json
import os

pName = 'ItemCounter'
pVersion = '1.5'

gui = QtBind.init(__name__, pName)
baseY = 30
pageLimit = 12
labelItems = []
countIn = 'Inventory'
currPage = 0
totalPages = 0
searchText = ''
buttonItems = {}
quickSearchList = []
configStamp = None

# static labels
QtBind.createLabel(gui, 'Search', 10, baseY + 4)
QtBind.createLabel(gui, 'by Ryuzaki', 670, 267)
QtBind.createLabel(gui, 'Where do you want to look?', 565, 10)
QtBind.createLabel(gui, 'Quick Search', 310, baseY + 4)

# dynamic labels
lblTitle = QtBind.createLabel(gui, 'ITEMS', 10, 10)
lblPaging = QtBind.createLabel(gui, '0/0', 100, baseY + 220)

# buttons
btnStorage = QtBind.createButton(
    gui, 'btnStorage_clicked', "  Storage  ", 595, 57)
btnGuildStorage = QtBind.createButton(
    gui, 'btnGuildStorage_clicked', "  Guild Storage  ", 590, 80)
btnInventory = QtBind.createButton(
    gui, 'btnInventory_clicked', "  Inventory  ", 595, 34)
btnPet = QtBind.createButton(
    gui, 'btnPet_clicked', "  Pet  ", 595, 103)
btnPagingPrev = QtBind.createButton(
    gui, 'btnPagingPrev_clicked', "<", 10, baseY + 215)
btnPagingNext = QtBind.createButton(
    gui, 'btnPagingNext_clicked', ">", 130, baseY + 215)
btnClearSearchBox = QtBind.createButton(
    gui, 'btnClearSearchBox_clicked', 'Clear', 205, baseY - 1)
btnQuickSearchAdd = QtBind.createButton(
    gui, 'btnQuickSearchAdd_clicked', 'Add', 380, baseY - 1)
btnQuickSearchRemove = QtBind.createButton(
    gui, 'btnQuickSearchRemove_clicked', 'Remove', 460, baseY - 1)

# inputs
txtBxSearch = QtBind.createLineEdit(gui, '', 50, baseY, 150, 21)

# lines
QtBind.createList(gui, 295, baseY - 5, 1, 670)


# button events
def btnStorage_clicked():
    global countIn
    countIn = 'Storage'
    countItems(countIn)

def btnGuildStorage_clicked():
    global countIn
    countIn = 'Guild Storage'
    countItems(countIn)

def btnInventory_clicked():
    global countIn
    countIn = 'Inventory'
    countItems(countIn)

def btnPet_clicked():
    global countIn
    countIn = 'Pet'
    countItems(countIn)

def btnPagingPrev_clicked():
    global currPage
    currPage -= 1
    if currPage < 0:
        currPage = 0
    countItems(countIn, currPage)

def btnPagingNext_clicked():
    global currPage
    currPage += 1
    if currPage >= totalPages:
        currPage = totalPages - 1
    countItems(countIn, currPage)

def btnClearSearchBox_clicked():
    QtBind.setText(gui, txtBxSearch, '')
    countItems(countIn)

def btnQuickSearchAdd_clicked():
    txt = QtBind.text(gui, txtBxSearch).strip()
    if txt.lower() not in map(str.lower, quickSearchList) and txt and len(quickSearchList) < 8:
        quickSearchList.append(txt)
    updateQuickSearchButtons()

def btnQuickSearchRemove_clicked():
    global quickSearchList
    txt = QtBind.text(gui, txtBxSearch).strip()
    i = 0
    for qs in quickSearchList:
        if qs == txt:
            quickSearchList.remove(qs)
        i += 1
    updateQuickSearchButtons()

# other functions
def updateQuickSearchButtons():
    # clear buttons from screen
    i = 0
    for k in buttonItems:
        QtBind.move(gui, buttonItems[k], 3100, baseY + 33 + (i * 28))
        i += 1
    # display quick search buttons in order
    i = 0
    for qs in quickSearchList:
        j = 0
        btn = None
        for k in buttonItems:
            if i == j:
                btn = buttonItems[k]
                break
            j += 1
        if btn is not None:
            QtBind.setText(gui, btn, '   {}   '.format(qs))
            QtBind.move(gui, btn, 310, baseY + 33 + (i * 28))
        i += 1
    # save
    saveConfig()

def str_in(search, text):
    return search.lower() in text.lower()

# create labels
for x in range(pageLimit):
    labelItems.append(QtBind.createLabel(
        gui, 'None', 10, baseY + ((x + 2) * 15)))
# create buttons
for x in range(8):
    btn = 'btnQuickSearch' + str(x)
    buttonItems[btn] = QtBind.createButton(gui, btn + '_clicked', '', 3100, baseY + 33 + (x * 28))
    func = f'''
def {btn}_clicked():
    global searchText
    btn = buttonItems['{btn}']
    searchText = QtBind.text(gui, btn).strip()
    QtBind.setText(gui, txtBxSearch, searchText)
    countItems(countIn)
    '''
    exec(func)

# Called every 500ms
def event_loop():
    global searchText, configStamp
    txt = QtBind.text(gui, txtBxSearch)
    if searchText != txt:
        countItems(countIn)
    searchText = txt
    # update if config is changed
    stamp = os.stat(getConfigPath()).st_mtime
    if stamp != configStamp:
        loadConfig()
    configStamp = stamp

# plugin folder path
def getPath():
    return get_config_dir() + pName + "\\"
# plugin config path
def getConfigPath():
    return getPath() + "data.json"
# load config data
def loadConfig():
    global quickSearchList
    if os.path.exists(getConfigPath()):
        data = {}
        with open(getConfigPath(), "r") as f:
            try:
                data = json.load(f)
            except:
                pass
            f.close()
        if "QuickSearchList" in data:
            quickSearchList = data["QuickSearchList"]
    updateQuickSearchButtons()
# save config data
def saveConfig():
    data = {"QuickSearchList": quickSearchList}
    with open(getConfigPath(), "w") as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))
        f.close()

def countItems(countIn, page=0):
    global currPage, totalPages, pageLimit
    currPage = page
    clearLabels()
    items = []
    itemCounter = {}
    # get items
    try:
        if countIn == 'Storage':
            items = get_storage()['items']
        elif countIn == 'Guild Storage':
            items = get_guild_storage()['items']
        elif countIn == 'Inventory':
            items = get_inventory()['items']
        elif countIn == 'Pet':
            pets = get_pets()
            if pets != None:
                for key in pets:
                    pet = pets[key]
                    if pet['type'] == 'pick':
                        items = pet['items']
                        break
    except:
        clearLabels('None')
        return
    # update title
    QtBind.setText(gui, lblTitle, 'ITEMS (' + countIn + ')')
    # count items
    start = 13
    i = 0
    txt = QtBind.text(gui, txtBxSearch)
    itemFound = False
    for item in items:
        if i < start and countIn == 'Inventory':
            i += 1
            continue
        if item != None:
            itemFound = True
            if str_in(txt, item['name']) or str_in(txt, item['servername']):
                name = item['name'] + ' (+' + str(
                    item['plus']) + ')' if '_CH_' in item['servername'] or '_EU_' in item['servername'] else item['name']
                if name in itemCounter.keys():
                    itemCounter[name] += item['quantity']
                else:
                    itemCounter[name] = item['quantity']
        i += 1
    if len(itemCounter) == 0 and (len(txt) == 0 or not itemFound):
        clearLabels('None')
    # sort items
    currLetter = None
    letterCounter = 0
    itemCounter = {key: itemCounter[key] for key in sorted(itemCounter.keys())}
    sortedItems = {}
    i = 0
    for key in itemCounter:
        letter = key[0].lower()
        if letter != currLetter and i % pageLimit != 0:
            sortedItems['---' + ('-' * letterCounter)] = -1
            i += 1
            currLetter = letter
            letterCounter += 1
        elif letter != currLetter:
            currLetter = letter
        sortedItems[key] = itemCounter[key]
        i += 1
    # display items
    i = 0
    totalPages = math.ceil(len(sortedItems) / pageLimit)
    sortedItems = sliceDict(sortedItems, page * pageLimit, len(labelItems))
    for key in sortedItems:
        count = sortedItems[key]
        itemString = key if count == -1 else key + ': ' + str(count)
        QtBind.setText(gui, labelItems[i], itemString)
        i += 1
    # paging
    QtBind.setText(gui, lblPaging, str(page + 1) + '/' + str(totalPages))


def sliceDict(dict, start, length=0):
    i = 0
    temp = {}
    for k in dict:
        if i >= start and (length == 0 or i < start + length):
            temp[k] = dict[k]
        i += 1
    return temp


def clearLabels(text=''):
    global labelItems
    for item in labelItems:
        QtBind.setText(gui, item, text)

# check plugin folder is exists
if not os.path.exists(getPath()):
	# Creating plugin folder
	os.makedirs(getPath())
# load config
loadConfig()

log('Plugin: ['+pName+' v'+pVersion+'] successfully loaded')