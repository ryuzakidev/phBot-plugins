from phBot import *
import QtBind
import math
import json
import os

pName = 'ItemCounter'
pVersion = '1.7'
pUrl = 'https://raw.githubusercontent.com/ryuzakidev/phBot-plugins/main/ItemCounter.py'

gui = QtBind.init(__name__, pName)
baseY = 30
pageLimit = 12
labelItems = []
countIn = 'Inventory'
lastCountIn = countIn
currPage = 0
totalPages = 0
lastPage = currPage
searchText = ''
buttonItems = {}
quickSearchList = []
configStamp = None
quickSearchDeleted = False

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
btnAll = QtBind.createButton(
    gui, 'btnAll_clicked', "  All  ", 595, 126)
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
    global countIn, currPage
    countIn = 'Storage'
    currPage = 0

def btnGuildStorage_clicked():
    global countIn, currPage
    countIn = 'Guild Storage'
    currPage = 0

def btnInventory_clicked():
    global countIn, currPage
    countIn = 'Inventory'
    currPage = 0

def btnPet_clicked():
    global countIn, currPage
    countIn = 'Pet'
    currPage = 0

def btnAll_clicked():
    global countIn, currPage
    countIn = 'All'
    currPage = 0

def btnPagingPrev_clicked():
    global currPage
    currPage -= 1
    if currPage < 0:
        currPage = 0

def btnPagingNext_clicked():
    global currPage
    currPage += 1
    if currPage >= totalPages:
        currPage = totalPages - 1

def btnClearSearchBox_clicked():
    global currPage
    currPage = 0
    QtBind.setText(gui, txtBxSearch, '')

def btnQuickSearchAdd_clicked():
    txt = QtBind.text(gui, txtBxSearch).strip()
    if txt.lower() not in map(str.lower, quickSearchList) and txt and len(quickSearchList) < 8:
        quickSearchList.append(txt)
    updateQuickSearchButtons()

def btnQuickSearchRemove_clicked():
    global quickSearchList, quickSearchDeleted
    txt = QtBind.text(gui, txtBxSearch).strip()
    i = 0
    for qs in quickSearchList:
        if qs == txt:
            quickSearchList.remove(qs)
        i += 1
    quickSearchDeleted = True
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
    global currPage
    btn = buttonItems['{btn}']
    currPage = 0
    QtBind.setText(gui, txtBxSearch, QtBind.text(gui, btn).strip())
    '''
    exec(func)

# Called every 500ms
def event_loop():
    global searchText, configStamp, lastCountIn, lastPage, currPage
    txt = QtBind.text(gui, txtBxSearch)
    if searchText != txt or lastCountIn != countIn or lastPage != currPage:
        if lastPage == currPage:
            currPage = 0
        countItems(countIn, currPage)
    searchText = txt
    lastCountIn = countIn
    lastPage = currPage
    # update if config is changed
    stamp = os.stat(getConfigPath()).st_mtime
    if stamp != configStamp:
        loadConfig()
    configStamp = stamp

# Return the sox type as text, empty if none is found
def getSoXText(servername,level):
	if level < 101:
		if servername.endswith('A_RARE'):
			return '^Star'
		elif servername.endswith('B_RARE'):
			return '^Moon'
		elif servername.endswith('C_RARE'):
			return '^Sun'
	else:
		if servername.endswith('A_RARE'):
			return '^Nova'
		elif servername.endswith('B_RARE'):
			return '^Rare'
		elif servername.endswith('C_RARE'):
			return '^Legend'
		elif servername.endswith('SET_A'):
			return '^Egy A'
		elif servername.endswith('SET_B'):
			return '^Egy B'
	return ''

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
    global quickSearchDeleted
    data = {"QuickSearchList": quickSearchList}
    if len(quickSearchList) == 0 and not quickSearchDeleted:
        return
    with open(getConfigPath(), "w") as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))
        f.close()
    quickSearchDeleted = False

def countItems(countIn, page=0):
    global currPage, totalPages, pageLimit
    currPage = page
    clearLabels()
    items = []
    itemCounter = {}
    start = 13 # for not showing weapon and set parts
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
        elif countIn == 'All':
            # char items
            charItems = get_inventory()['items']
            if charItems is not None:
                iterator = 0
                for i in charItems:
                    if iterator < start:
                        iterator += 1
                    elif i is not None:
                        items.append(i)
            # storage items
            storageItems = get_storage()['items']
            if storageItems is not None:
                for i in storageItems:
                    if i is not None:
                        items.append(i)
            # guild storage items
            guildStorageItems = get_guild_storage()['items']
            if guildStorageItems is not None:
                for i in guildStorageItems:
                    if i is not None:
                        items.append(i)
            # pet items
            pets = get_pets()
            if pets != None:
                for k in pets:
                    pet = pets[k]
                    if pet['type'] == 'pick':
                        for i in pet['items']:
                            if i is not None:
                                items.append(i)
    except Exception as e:
        log('Error: ' + str(e))
        clearLabels('None')
        return
    # update title
    QtBind.setText(gui, lblTitle, 'ITEMS (' + countIn + ')')
    # count items
    i = 0
    txt = QtBind.text(gui, txtBxSearch)
    itemFound = False
    for item in items:
        if i < start and countIn == 'Inventory':
            i += 1
            continue
        if item != None:
            itemFound = True
            level = 0
            try:
                itemData = get_item_string(item['servername'])
                if itemData is not None:
                    level = itemData['level']
            except:
                log('err')
            race = '(CH)' if '_CH_' in item['servername'] else '(EU)'
            gender = ''
            if '_W_' in item['servername']:
                gender = '[F]'
            elif '_M_' in item['servername']:
                gender = '[M]'
            if str_in(txt, item['name']) or str_in(txt, item['servername']):
                # name = item['name'] + ' (+' + str(
                #     item['plus']) + ')' if '_CH_' in item['servername'] or '_EU_' in item['servername'] else item['name']
                name = item['name'] + ' ' + race + (' ' + gender if gender else '') + ' ' + getSoXText(item['servername'], level) + ' (+' + str(item['plus']) + ')' if '_CH_' in item['servername'] or '_EU_' in item['servername'] else item['name']
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
        itemString = key if count == -1 else key + ': <b style="color: green;">' + str(count) + '</b>'
        QtBind.setText(gui, labelItems[i], '<span style=\'font-family: Arial, "Helvetica Neue", Helvetica, sans-serif;\'>' + itemString + '</span>')
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

### COMMUNICATION WITH OTHER CHARACTERS IN LOCAL ###

####################################################


# check plugin folder is exists
if not os.path.exists(getPath()):
	# Creating plugin folder
	os.makedirs(getPath())
# load config
loadConfig()

log('Plugin: ['+pName+' v'+pVersion+'] successfully loaded')





# use it in conditions
def isProfileWizz():
    return get_profile() == 'wizz'

def isProfileBard():
    return get_profile() == 'bard'