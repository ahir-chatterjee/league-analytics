# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 16:14:03 2020

@author: Ahir
"""

import pymysql
import json
import time
import os

global DB, cursor
hst=""
dbname=""
u=""
pw=""
if(os.path.exists("secrets.txt")):
    with open("secrets.txt",'r') as openFile:
        secrets = json.loads(openFile.read())
        hst = secrets["db_host"]
        dbname = secrets["db_name"]
        u = secrets["db_user"]
        pw = secrets["db_pw"]

DB = pymysql.connect(host=hst,user=u,password=pw,database=dbname) #connect to our database
cursor = DB.cursor()
print("Database connected to!")

def createAccountsTable():
    #cursor.execute("DROP TABLE accounts")
    #DB.commit()
    #hard coded numbers are the max sizes for the respective field, with extra padding just in case
    #removed summonericon and summonerlevel, as neither are relevant for looking up
    create_accounts = """
    CREATE TABLE IF NOT EXISTS accounts (
    name VARCHAR(16),
    puuid VARCHAR(128),
    accountId VARCHAR(64),
    id VARCHAR(64),
    revisionDate bigint,
    data JSON
    );
    """
    cursor.execute(create_accounts)
    DB.commit()
    
def createMatchesTable():
    #cursor.execute("DROP TABLE matches")
    #DB.commit()
    #uses summIds (account["id"]) to store p1-p10
    create_matches = """
    CREATE TABLE IF NOT EXISTS matches (
    gameId bigint,
    gameCreation bigint,
    mapId int,
    queueId int,
    seasonId int,
    gameDuration bigint,
    gameMode VARCHAR(16),
    gameType VARCHAR(16),
    platformId VARCHAR(4),
    gameVersion VARCHAR(16),
    p1 VARCHAR(64), p2 VARCHAR(64), p3 VARCHAR(64), p4 VARCHAR(64), p5 VARCHAR(64),
    p6 VARCHAR(64), p7 VARCHAR(64), p8 VARCHAR(64), p9 VARCHAR(64), p10 VARCHAR(64),
    data JSON
    );
    """
    cursor.execute(create_matches)
    DB.commit()   
    
def createTimelinesTable():
    #cursor.execute("DROP TABLE timelines")
    #DB.commit()
    #uses summIds (account["id"]) to store p1-p10
    create_timelines = """
    CREATE TABLE IF NOT EXISTS timelines (
    gameId bigint,
    data JSON
    );
    """
    cursor.execute(create_timelines)
    DB.commit()
    
def createChampionsTable():
    #cursor.execute("DROP TABLE champions")
    #DB.commit()
    create_champions = """
    CREATE TABLE IF NOT EXISTS champions (
    ky int,
    version VARCHAR(16),
    id VARCHAR(32),
    name VARCHAR(32),
    partype VARCHAR(16),
    armor decimal,
    armorperlevel decimal,
    attackdamage decimal,
    attackdamageperlevel decimal,
    attackrange int,
    attackspeed decimal,
    attackspeedperlevel decimal,
    crit decimal,
    critperlevel decimal,
    hp decimal,
    hpperlevel decimal,
    hpregen decimal,
    hpregenperlevel decimal,
    movespeed int,
    mp decimal,
    mpperlevel decimal,
    mpregen decimal,
    mpregenperlevel decimal,
    spellblock decimal,
    spellblockperlevel decimal,
    title VARCHAR(64),
    data JSON
    );
    """
    cursor.execute(create_champions)
    DB.commit() 
    
def createItemsTable():
    #cursor.execute("DROP TABLE items")
    #DB.commit()
    create_items = """
    CREATE TABLE IF NOT EXISTS items (
    version VARCHAR(16),
    colloq VARCHAR(64),
    depth int,
    baseCost int,
    purchasable int,
    sellCost int,
    totalCost int,
    onSR int,
    name VARCHAR(64),
    number int,
    data JSON
    );
    """
    cursor.execute(create_items)
    DB.commit()
    
def createSpellsTable():
    #cursor.execute("DROP TABLE sSpells")
    #DB.commit()
    create_sSpells = """
    CREATE TABLE IF NOT EXISTS sSpells (
    version VARCHAR(16),
    name VARCHAR(32),
    cd int,
    ky int,
    onSR int,
    data JSON
    );
    """
    cursor.execute(create_sSpells)
    DB.commit() 
    
def createRunesTable():
    #cursor.execute("DROP TABLE runes")
    #DB.commit()
    create_runes = """
    CREATE TABLE IF NOT EXISTS runes (
    id int,
    ky VARCHAR(16),
    name VARCHAR(16),
    data JSON
    );
    """
    cursor.execute(create_runes)
    DB.commit()
    
def createTeamsTable():
    #cursor.execute("DROP TABLE teams")
    #DB.commit()
    #25 summonerIds and 25 names to account for way more than possible accounts on a team
    create_teams = """
    CREATE TABLE IF NOT EXISTS teams (
    date VARCHAR(16),
    name VARCHAR(32),
    id1 VARCHAR(64),id2 VARCHAR(64),id3 VARCHAR(64),id4 VARCHAR(64),id5 VARCHAR(64),
    id6 VARCHAR(64),id7 VARCHAR(64),id8 VARCHAR(64),id9 VARCHAR(64),id10 VARCHAR(64),
    id11 VARCHAR(64),id12 VARCHAR(64),id13 VARCHAR(64),id14 VARCHAR(64),id15 VARCHAR(64),
    id16 VARCHAR(64),id17 VARCHAR(64),id18 VARCHAR(64),id19 VARCHAR(64),id20 VARCHAR(64),
    id21 VARCHAR(64),id22 VARCHAR(64),id23 VARCHAR(64),id24 VARCHAR(64),id25 VARCHAR(64),
    n1 VARCHAR(16),n2 VARCHAR(16),n3 VARCHAR(16),n4 VARCHAR(16),n5 VARCHAR(16),
    n6 VARCHAR(16),n7 VARCHAR(16),n8 VARCHAR(16),n9 VARCHAR(16),n10 VARCHAR(16),
    n11 VARCHAR(16),n12 VARCHAR(16),n13 VARCHAR(16),n14 VARCHAR(16),n15 VARCHAR(16),
    n16 VARCHAR(16),n17 VARCHAR(16),n18 VARCHAR(16),n19 VARCHAR(16),n20 VARCHAR(16),
    n21 VARCHAR(16),n22 VARCHAR(16),n23 VARCHAR(16),n24 VARCHAR(16),n25 VARCHAR(16),
    accounts JSON
    );
    """
    cursor.execute(create_teams)
    DB.commit()

def initializeDB():
    """
    Should never be called other than on initialization, but this was used to initalize the riotapi.db file
    """
    createAccountsTable()
    createMatchesTable()
    createChampionsTable()
    createItemsTable()
    createSpellsTable()
    createRunesTable()  
    createTeamsTable()
    createTimelinesTable()
    
def printTable(tableName):
    cmd = "SELECT COUNT(*) from " + tableName
    cursor.execute(cmd)
    results = cursor.fetchall()
    print((str)(results[0][0]) + " " + tableName)
    
def printTables():
    """
    Purely a debug method. Probably no longer works on AWS
    """    
    cmd = "SHOW TABLES"
    cursor.execute(cmd)
    results = cursor.fetchall()
    for name in results:
        printTable(name[0])
        
"""
Table update method for dynamic data that changes per patch (champions, items, sSpells)
"""

def checkForUpdates(versions):
    updatesNeeded = [False,False,False]    #[champions,items,sSpells]
    
    #champions
    cmd = "SELECT version from champions"
    cursor.execute(cmd)
    champVersion = cursor.fetchone()
    if(not champVersion == None):
        champVersion = champVersion[0]
        if(not versions["champion"] == champVersion):
            updatesNeeded[0] = True
    else:
        updatesNeeded[0] = True
    
    #items   
    cmd = "SELECT version from items"
    cursor.execute(cmd)
    itemVersion = cursor.fetchone()
    if(not itemVersion == None):
        itemVersion = itemVersion[0]
        if(not versions["item"] == itemVersion):
            updatesNeeded[1] = True
    else:
        updatesNeeded[1] = True
        
    #sSpells
    cmd = "SELECT version from sSpells"
    cursor.execute(cmd)
    sSpellsVersion = cursor.fetchone()
    if(not sSpellsVersion == None):
        sSpellsVersion = sSpellsVersion[0]
        if(not versions["summoner"] == sSpellsVersion):
            updatesNeeded[2] = True
    else:
        updatesNeeded[2] = True
    
    return updatesNeeded
        
"""
Methods for adding a record to the database
"""  

def addTeamToDB(name,accounts): #DOES NOT WORK FOR NOW, ABORT
    if(not name or not accounts):   #passed useless data
        return -1
    now = time.localtime()
    date = (str)(now.tm_mon) + "-" + (str)(now.tm_mday) + "-" + (str)(now.tm_year)  #dd/mm/yyyy
    if(fetchTeam(name,date)):
        cmd = "DELETE FROM teams WHERE name = " + "\"" + name.lower() + "\" AND date = \"" + date + "\""
        cursor.execute(cmd)
    formatStr = """
    INSERT INTO teams (date, name, id1, id2, id3, id4, id5, id6, id7, id8, id9, id10, id11, 
    id12, id13, id14, id15, id16, id17, id18, id19, id20, id21, id22, id23, id24, id25, n1, n2, 
    n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13, n14, n15, n16, n17, n18, n19, n20, n21, n22, 
    n23, n24, n25, accounts) VALUES ("{d}","{n}",?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
    """
    cmd = formatStr.format(d=date,n=name)
    playersInfo = []
    for num in range(0,50):
        i = num%25
        account = {"name":"","id":""}
        if(i < len(accounts)):
            account = accounts[i]
        if(num < 25):
            playersInfo.append(account["id"])
        else:
            playersInfo.append(account["name"])
    playersInfo.append(json.dumps(accounts))
    playersInfo = tuple(playersInfo)
    cursor.execute(cmd,playersInfo)
    DB.commit()
    return 1

def addAccountToDB(account):
    if(not "puuid" in account):  #account wasn't found, don't do anything
        return -1
    if(fetchAccountByPuuid(account["puuid"])):  #account is already in the database, don't do anything
        return 0
    formatStr = """
    INSERT INTO accounts (`name`, `puuid`, `accountId`, `id`, `revisionDate`, `data`)
    VALUES ("{n}","{puuid}","{accId}","{summId}",{date},'{d}');
    """
    name = account["name"].lower()
    name = name.replace(" ","")
    cmd = formatStr.format(n=name,
                           puuid=account["puuid"],
                           accId=account["accountId"],
                           summId=account["id"],
                           date=account["revisionDate"],
                           d=json.dumps(account))    
    cursor.execute(cmd)
    DB.commit()
    return 1

def addTimelineToDB(timeline,gameId):
    if(not timeline):
        return -1
    if(fetchTimeline(gameId)):
        return 0
    formatStr = """
    INSERT INTO timelines (`gameId`, `data`) VALUES ({gId},'{d}');
    """
    cmd = formatStr.format(gId=gameId,d=json.dumps(timeline))
    cursor.execute(cmd)
    DB.commit()
    return 1

def addMatchToDB(match):
    if(not "gameId" in match):    #match wasn't found, don't do anything
        return -1
    if(fetchMatch(match["gameId"])):    #match was already in the database
        return 0
    formatStr = """
    INSERT INTO matches (`gameId`, `gameCreation`, `mapId`, `queueId`, 
    `seasonId`, `gameDuration`, `gameMode`, 
    `gameType`, `platformId`, `gameVersion`, `p1`, `p2`, `p3`, `p4`, `p5`,
    `p6`, `p7`, `p8`, `p9`, `p10`, `data`) 
    VALUES ({gid},{gC},{mid},{qid},{sid},{gD},"{gM}","{gT}", 
    "{pid}","{gV}","{p1}","{p2}","{p3}","{p4}","{p5}","{p6}","{p7}","{p8}","{p9}","{p10}",'{d}');
    """
    p = []
    m = match
    assert len(m["participantIdentities"]) == 10, "there are not 10 players?"
    for i in range(0,len(m["participantIdentities"])):    #guarantee summId's added in order
        p.append(m["participantIdentities"][i]["player"]["summonerId"])
    assert len(p) == 10, "did not find 10 players"
    cmd = formatStr.format(gid=m["gameId"],gC=m["gameCreation"],mid=m["mapId"],qid=m["queueId"],
                           sid=m["seasonId"],gD=m["gameDuration"],gM=m["gameMode"],
                           gT=m["gameType"],pid=m["platformId"],gV=m["gameVersion"],
                           p1=p[0],p2=p[1],p3=p[2],p4=p[3],p5=p[4],p6=p[5],p7=p[6],
                           p8=p[7],p9=p[8],p10=p[9],d=json.dumps(m))
    cursor.execute(cmd)
    DB.commit()
    return 1
    
"""
Methods for updating existing records in the database
"""

def updateAccountName(name,puuid):
    name = name.lower()
    name = name.replace(" ","")
    account = fetchAccountByPuuid(puuid)
    assert account, "account must be in the database for this method to be called"
    account["name"] = name
    data = json.dumps(account)
    formatStr = "UPDATE accounts SET `name` = \"" + name + "\", `data` = '{d}' WHERE `puuid` = \"" + puuid + "\""
    cmd = formatStr.format(d=json.dumps(account))
    cursor.execute(cmd)
    DB.commit()
    
def updateChamps(champs,version):
    cursor.execute("DELETE FROM champions;")
    formatStr = """
    INSERT INTO champions (`version`, `id`, `name`, `ky`, `partype`, 
    `armor`, `armorperlevel`, `attackdamage`, `attackdamageperlevel`, `attackrange`, `attackspeed`, 
    `attackspeedperlevel`, `crit`, `critperlevel`, `hp`, `hpperlevel`, `hpregen`, `hpregenperlevel`, 
    `movespeed`, `mp`, `mpperlevel`, `mpregen`, `mpregenperlevel`, `spellblock`, `spellblockperlevel`, 
    `title`, `data`) VALUES ("{v}","{iD}","{n}",{k},"{pT}",{arm},{armPL},{ad},{adPL},{ar},{aS},
    {aspl},{c},{cPL},{hp},{hpPL},{hpR},{hpRPL},{ms},{mp},{mpPL},{mpR},{mpRPL},{mr},{mrPL},"{t}",'{d}');
    """
    for c in champs:
        s = c["stats"]
        cmd = formatStr.format(v=version,iD=c["id"],n=c["name"].lower(),k=c["key"],pT=c["partype"],arm=s["armor"],
                               armPL=s["armorperlevel"],ad=s["attackdamage"],adPL=s["attackdamageperlevel"],
                               ar=s["attackrange"],aS=s["attackspeed"],aspl=s["attackspeedperlevel"],
                               c=s["crit"],cPL=s["critperlevel"],hp=s["hp"],hpPL=s["hpperlevel"],
                               hpR=s["hpregen"],hpRPL=s["hpregenperlevel"],ms=s["movespeed"],mp=s["mp"],
                               mpPL=s["mpperlevel"],mpR=s["mpregen"],mpRPL=s["mpregenperlevel"],
                               mr=s["spellblock"],mrPL=s["spellblockperlevel"],t=c["title"],d=json.dumps(c))
        cursor.execute(cmd)
    DB.commit()
    
def updateItems(items,version):
    cursor.execute("DELETE FROM items;")
    formatStr = """
    INSERT INTO items (`version`, `colloq`, `baseCost`, `purchasable`, `sellCost`, `totalCost`, `onSR`, 
    `name`, `number`, `data`) VALUES ("{v}","{c}",{bC},{p},{sC},{tC},{SR},"{name}","{num}",'{d}');
    """
    for n in items:
        i = items[n]
        gold = i["gold"]
        purchasable = 1 if i["gold"]["purchasable"] else 0
        onSR = 1 if i["maps"]["11"] else 0
        cmd = formatStr.format(v=version,c=i["colloq"],bC=gold["base"],p=purchasable,
                               sC=gold["sell"],tC=gold["total"],SR=onSR,name=i["name"],num=n,d=json.dumps(items[n]))
        cursor.execute(cmd)
    DB.commit()

def updateSpells(spells,version):   #summoner spells
    cursor.execute("DELETE FROM sSpells;")
    formatStr = """
    INSERT INTO sSpells (`version`, `name`, `cd`, `ky`, `onSR`, `data`) 
    VALUES ("{v}","{n}",{cd},{k},{onSR},'{d}');
    """
    for summ in spells:
        s = spells[summ]
        SR = 1 if "CLASSIC" in s["modes"] else 0
        cmd = formatStr.format(v=version,n=s["name"],cd=s["cooldownBurn"],k=s["key"],onSR=SR,d=json.dumps(spells[summ]))
        cursor.execute(cmd)
    DB.commit()
    
def updateRunes(runes):
    cursor.execute("DELETE FROM runes;")
    formatStr = """
    INSERT INTO runes (`id`, `ky`, `name`, `data`) 
    VALUES ({iD},"{k}","{n}",'{d}');
    """
    for tree in runes:
        cmd = formatStr.format(iD=tree["id"],k=tree["key"],n=tree["name"],d=json.dumps(tree))
        cursor.execute(cmd)
        for slot in tree["slots"]:
            for rune in slot["runes"]:
                cmd = formatStr.format(iD=rune["id"],k=rune["key"],n=rune["name"],d=json.dumps(rune))
                cursor.execute(cmd)
    DB.commit()

"""
Methods for querying the database for records
"""

def fetchTeam(name,date):
    cmd = "SELECT accounts FROM teams WHERE name = " + "\"" + name.lower() + "\" AND date = \"" + date + "\""
    cursor.execute(cmd)
    result = cursor.fetchall()
    assert not len(result) > 1, "more than one team with the same name AND date"
    if(not result):
        return []
    else:
        return json.loads(result[0][52])

def fetchChamp(cmd):
    cursor.execute(cmd)
    result = cursor.fetchall()
    assert not len(result) > 1, "more than one champ with the same identifier"
    if(not result):
        return {}
    else:
        return json.loads(result[0][0])

def fetchChampByName(name):
    cmd = "SELECT data FROM champions WHERE name = " + "\"" + name.lower() + "\""
    return fetchChamp(cmd)
    
def fetchChampByKey(ky):
    cmd = "SELECT data FROM champions WHERE ky = " + (str)(ky)
    return fetchChamp(cmd)

def fetchAllItems():
    cmd = "SELECT data, number FROM items"
    cursor.execute(cmd)
    result = cursor.fetchall()
    itemDict = {}
    for i in range(0,len(result)):
        data = json.loads(result[i][0])
        data["num"] = result[i][1]
        itemDict[data["name"]] = data
    return itemDict

def fetchItem(cmd):
    cursor.execute(cmd)
    result = cursor.fetchall()
    assert not len(result) > 1, "more than one item with the same identifier"
    if(not result):
        return {}
    else:
        return json.loads(result[0][0])

def fetchItemByName(name):
    cmd = "SELECT data FROM items WHERE name = " + "\"" + name.lower() + "\""
    return fetchItem(cmd)

def fetchItemByNumber(num):
    if(num == 0):
        return {}
    cmd = "SELECT data FROM items WHERE number = " + (str)(num)
    return fetchItem(cmd)

def fetchRune(cmd):
    cursor.execute(cmd)
    result = cursor.fetchall()
    assert not len(result) > 1, "more than one rune with the same identifier"
    if(not result):
        return {}
    else:
        return json.loads(result[0][0])

def fetchRuneByName(name):
    cmd = "SELECT data FROM runes WHERE name = " + "\"" + name.lower() + "\""
    return fetchRune(cmd)

def fetchRuneById(ky):
    cmd = "SELECT data FROM runes WHERE id = " + (str)(ky)
    return fetchRune(cmd)

def fetchTimeline(gameId):
    cmd = "SELECT data FROM timelines WHERE gameId = " + (str)(gameId)
    cursor.execute(cmd)
    result = cursor.fetchall()
    assert not len(result) > 1, "more than one of the same gameId"
    if(not result):
        return {}
    else:
        return json.loads(result[0][0])

def fetchMatch(gameId):
    cmd = "SELECT data FROM matches WHERE gameId = " + (str)(gameId)
    cursor.execute(cmd)
    result = cursor.fetchall()
    assert not len(result) > 1, "more than one of the same gameId"
    if(not result): #if result is empty
        return {}
    else:
        return json.loads(result[0][0])
    
def fetchAccountsBySummId(summIds):
    summIds.sort()
    cmd = "SELECT data FROM accounts WHERE" #ORDER BY guarantees that they will be sorted in summIds order
    for summId in summIds:
        cmd += " id = \"" + summId + "\" OR"
    cmd = cmd[:len(cmd)-2]  #get rid of the last "OR"
    cmd += "ORDER BY id;"
    cursor.execute(cmd)
    results = cursor.fetchall()
    accounts = []
    for r in results:
        account = json.loads(r[0])
        summIds.remove(account["id"])
        accounts.append(account)
    return (accounts,summIds)

def fetchAccount(cmd):
    cursor.execute(cmd)
    result = cursor.fetchall()
    assert not len(result) > 1, "more than one of the same identifier"
    if(not result): #if result is empty
        return {}
    else:
        return json.loads(result[0][0])
    
def fetchAccountByPuuid(puuid):
    cmd = "SELECT data FROM accounts WHERE puuid = \"" + puuid + "\""
    return fetchAccount(cmd)

def fetchAccountByAccId(accId):
    cmd = "SELECT data FROM accounts WHERE accountId = \"" + accId + "\""
    return fetchAccount(cmd)

def fetchAccountBySummId(summId):
    cmd = "SELECT data FROM accounts WHERE id = \"" + summId + "\""
    return fetchAccount(cmd)

def fetchAccountByName(name):
    name = name.lower()
    name = name.replace(" ","")
    cmd = "SELECT data FROM accounts WHERE name = \"" + name + "\""
    return fetchAccount(cmd)

def fetchMatchesByAccount(account):
    formatStr = """SELECT data FROM matches WHERE p1 = "{sId}" OR p2 = "{sId}" OR 
    p3 = "{sId}" OR p4 = "{sId}" OR p5 = "{sId}" OR p6 = "{sId}" OR 
    p7 = "{sId}" OR p8 = "{sId}" OR p9 = "{sId}" OR p10 = "{sId}" ORDER BY gameCreation; 
    """
    cmd = formatStr.format(sId=account["id"])
    cursor.execute(cmd)
    results = cursor.fetchall()
    if(not results):    #if result is empty
        return []
    else:
        matches = []
        for match in results:
            matches.append(json.loads(match[0]))
        return matches
    
def fetchMatchesByName(name):
    account = fetchAccountByName(name)
    if(account):
        return fetchMatchesByAccount(fetchAccountByName(name))
    else:
        return {}
    
def fetchAllMatchIds():
    cmd = "SELECT gameId FROM matches"
    cursor.execute(cmd)
    results = cursor.fetchall()
    return results
    
"""
Delete methods
"""

def deleteAccount(name):
    cmd = "DELETE FROM accounts WHERE name = " + "\"" + name + "\""
    try:
        cursor.execute(cmd)
    except:
        cmd = "DELETE FROM accounts WHERE name = ?"
        cursor.execute(cmd,(name,))
    
"""
Generally useful methods built on top of the database calls
"""

def translateChamp(ky):
    champ = fetchChampByKey(ky)
    return champ["name"]

def translateItem(num):
    item = fetchItemByNumber(num)
    if(item):
        return item["name"]
    else:
        return (str)(num)
    
def translateRune(ky):
    rune = fetchRuneById(ky)
    if(rune):
        return rune["name"]
    else:
        return ""
    
def updateAccounts():
    cmd = "SELECT name, data FROM accounts"
    cursor.execute(cmd)
    results = cursor.fetchall()
    count = 0
    for account in results:
        name = account[0]
        name = name.lower()
        name = name.replace(" ","")
        d = json.loads(account[1])
        accName = d["name"]
        if(len(name) > 18):
            print("deleting account because name is too damn long")
            deleteAccount(name)
        elif(not name == accName):
            count += 1
            #print("Found an account to update! From " + accName + " to " + name)
            updateAccountName(name,d["puuid"])
    return count

printTables()