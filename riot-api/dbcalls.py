# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 16:14:03 2020

@author: Ahir
"""

import sqlite3
import json

DB = sqlite3.connect("riotapi.db") #connect to our database
cursor = DB.cursor()

def initializeDB():
    """
    Should never be called, but this was used to initalize the riotapi.db file
    """
    global DB, cursor
    
    cursor.execute("DROP TABLE accounts")
    DB.commit()
    #hard coded numbers are the max sizes for the respective field, with extra padding just in case
    create_accounts = """
    CREATE TABLE accounts (
    profileIconId int,
    name VARCHAR(16),
    puuid VARCHAR(128),
    summonerLevel int,
    accountId VARCHAR(128),
    id VARCHAR(128),
    revisionDate bigint,
    data TEXT
    );
    """
    cursor.execute(create_accounts)
    DB.commit()
    
    cursor.execute("DROP TABLE matches")
    DB.commit()
    create_matches = """
    CREATE TABLE matches (
    gameId int,
    gameCreation bigint,
    mapId int,
    queueId int,
    seasonId int,
    gameDuration int,
    gameMode VARCHAR(32),
    gameType VARCHAR(32),
    platformId VARCHAR(8),
    gameVersion VARCHAR(32),
    p1 VARCHAR(128), p2 VARCHAR(128), p3 VARCHAR(128), p4 VARCHAR(128), p5 VARCHAR(128),
    p6 VARCHAR(128), p7 VARCHAR(128), p8 VARCHAR(128), p9 VARCHAR(128), p10 VARCHAR(128),
    data TEXT
    );
    """
    cursor.execute(create_matches)
    DB.commit()    
    
    cursor.execute("DROP TABLE champions")
    DB.commit()
    create_champions = """
    CREATE TABLE champions (
    version VARCHAR(16),
    id VARCHAR(32),
    name VARCHAR(32),
    key int,
    partype VARCHAR(16),
    armor float,
    armorperlevel float,
    attackdamage float,
    attackdamageperlevel float,
    attackrange int,
    attackspeed float,
    attackspeedperlevel float,
    crit float,
    critperlevel float,
    hp float,
    hpperlevel float,
    hpregen float,
    hpregenperlevel float,
    movespeed int,
    mp float,
    mpperlevel float,
    mpregen float,
    mpregenperlevel float,
    spellblock float,
    spellblockperlevel float,
    title VARCHAR(64),
    data TEXT
    );
    """
    cursor.execute(create_champions)
    DB.commit() 
    
    cursor.execute("DROP TABLE items")
    DB.commit()
    #buildPath would normally be "from" but that's a keyword in SQL
    create_items = """
    CREATE TABLE items (
    version VARCHAR(16),
    colloq VARCHAR(64),
    depth int,
    baseCost int,
    purchasable int,
    sellCost int,
    totalCost int,
    name VARCHAR(128),
    number int,
    data TEXT
    );
    """
    cursor.execute(create_items)
    DB.commit() 
    
    cursor.execute("DROP TABLE sSpells")
    DB.commit()
    create_sSpells = """
    CREATE TABLE sSpells (
    version VARCHAR(16),
    name VARCHAR(32),
    cd int,
    key int,
    data TEXT
    );
    """
    cursor.execute(create_sSpells)
    DB.commit() 
    
initializeDB()
    
def printTable(tableName):
    global DB, cursor
    cmd = "SELECT * from " + tableName
    cursor.execute(cmd)
    results = cursor.fetchall()
    print((str)(len(results)) + " " + tableName + ":")
    for r in results:
        print(r)
    
def printTables():
    """
    Purely a debug method
    """    
    #printTable("accounts")
    #printTable("matches")
    printTable("champions")
    
#printTables()
        
"""
Table update method for dynamic data that changes per patch (champions, items, sSpells)
"""

def checkForUpdates(versions):
    updatesNeeded = [False,False,False]    #[champions,items,sSpells]
    global DB, cursor
    
    #champions
    cmd = "SELECT version from champions"
    cursor.execute(cmd)
    champVersion = cursor.fetchone()
    if(not versions["champion"] == champVersion):
        updatesNeeded[0] = True
    
    #items   
    cmd = "SELECT version from items"
    cursor.execute(cmd)
    itemVersion = cursor.fetchone()
    if(not versions["item"] == itemVersion):
        updatesNeeded[1] = True
        
    #sSpells
    cmd = "SELECT version from sSpells"
    cursor.execute(cmd)
    sSpellsVersion = cursor.fetchone()
    if(not versions["summoner"] == sSpellsVersion):
        updatesNeeded[2] = True
    
    return updatesNeeded
        
"""
Methods for adding a record to the database
"""  

def addAccountToDB(account):
    if(not account):  #account wasn't found, don't do anything
        return -1
    if(fetchAccountByPuuid(account["puuid"])):  #account is already in the database, don't do anything
        return 0
    global DB, cursor
    formatStr = """
    INSERT INTO accounts (profileIconId, name, puuid, summonerLevel, accountId, id, revisionDate, data)
    VALUES ({icon},"{name}","{puuid}",{level},"{accId}","{summId}",{date},?);
    """
    cmd = formatStr.format(icon=account["profileIconId"],name=(account["name"].lower()),
                           puuid=account["puuid"],level=account["summonerLevel"],
                           accId=account["accountId"],summId=account["id"],date=account["revisionDate"])
    data = json.dumps(account)
    cursor.execute(cmd,(data,))
    DB.commit()
    return 1

def addMatchToDB(match):
    if(not match):    #match wasn't found, don't do anything
        return -1
    if(fetchMatch(match["gameId"])):
        return 0
    global DB, cursor
    formatStr = """
    INSERT INTO matches (gameId, gameCreation, mapId, queueId, seasonId, gameDuration, gameMode, 
    gameType, platformId, gameVersion, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, data) 
    VALUES ({gid},{gC},{mid},{qid},{sid},{gD},"{gM}","{gT}", 
    "{pid}","{gV}","{p1}","{p2}","{p3}","{p4}","{p5}","{p6}","{p7}","{p8}","{p9}","{p10}",?);
    """
    p = []
    m = match
    data = json.dumps(m)
    assert len(m["participantIdentities"]) == 10, "there are not 10 players?"
    for i in range(0,len(m["participantIdentities"])):    #guarantee summId's added in order
        p.append(m["participantIdentities"][i]["player"]["summonerId"])
    assert len(p) == 10, "did not find 10 players"
    cmd = formatStr.format(gid=m["gameId"],gC=m["gameCreation"],mid=m["mapId"],qid=m["queueId"],
                           sid=m["seasonId"],gD=m["gameDuration"],gM=m["gameMode"],
                           gT=m["gameType"],pid=m["platformId"],gV=m["gameVersion"],
                           p1=p[0],p2=p[1],p3=p[2],p4=p[3],p5=p[4],p6=p[5],p7=p[6],
                           p8=p[7],p9=p[8],p10=p[9])
    cursor.execute(cmd,(data,))
    DB.commit()
    return 1
    
"""
Methods for updating existing records in the database
"""

def updateAccountName(name,puuid):
    global DB, cursor
    cmd = "UPDATE accounts SET name = \"" + name.lower() + "\" WHERE puuid = \"" + puuid + "\""
    cursor.execute(cmd)
    DB.commit()
    
def updateChamps(champs,version):
    global DB, cursor
    print("updating champs in dbcalls.py")
    cursor.execute("DELETE FROM champions;")
    formatStr = """
    INSERT INTO champions (version, id, name, key, partype, 
    armor, armorperlevel, attackdamage, attackdamageperlevel, attackrange, attackspeed, 
    attackspeedperlevel, crit, critperlevel, hp, hpperlevel, hpregen, hpregenperlevel, 
    movespeed, mp, mpperlevel, mpregen, mpregenperlevel, spellblock, spellblockperlevel, 
    title, data) VALUES ("{v}","{iD}","{n}",{k},"{pT}",{arm},{armPL},{ad},{adPL},{ar},{aS},
    {aspl},{c},{cPL},{hp},{hpPL},{hpR},{hpRPL},{ms},{mp},{mpPL},{mpR},{mpRPL},{mr},{mrPL},"{t}",?);
    """
    for c in champs:
        print(c["id"])
        s = c["stats"]
        cmd = formatStr.format(v=version,iD=c["id"],n=c["name"].lower(),k=c["key"],pT=c["partype"],arm=s["armor"],
                               armPL=s["armorperlevel"],ad=s["attackdamage"],adPL=s["attackdamageperlevel"],
                               ar=s["attackrange"],aS=s["attackspeed"],aspl=s["attackspeedperlevel"],
                               c=s["crit"],cPL=s["critperlevel"],hp=s["hp"],hpPL=s["hpperlevel"],
                               hpR=s["hpregen"],hpRPL=s["hpregenperlevel"],ms=s["movespeed"],mp=s["mp"],
                               mpPL=s["mpperlevel"],mpR=s["mpregen"],mpRPL=s["mpregenperlevel"],
                               mr=s["spellblock"],mrPL=s["spellblockperlevel"],t=c["title"])
        data = json.dumps(c)
        cursor.execute(cmd,(data,))
    DB.commit()
    return 0
    
def updateItems(items):
    return 0

def updateSpells(spells):   #summoner spells
    return 0

"""
Methods for querying the database for records
"""

def fetchChamp(cmd):
    global cursor
    cursor.execute(cmd)
    result = cursor.fetchall()
    assert not len(result) > 1, "more than one champ with the same identifier"
    if(not result):
        print("did not find champion")
        return {}
    else:
        return json.loads(result[0][0])

def fetchChampByName(name):
    cmd = "SELECT data FROM champions WHERE name = " + "\"" + name.lower() + "\""
    return fetchChamp(cmd)
    
def fetchChampByKey(key):
    cmd = "SELECT data FROM champions WHERE key = " + (str)(key)
    return fetchChamp(cmd)

def fetchMatch(gameId):
    global cursor
    cmd = "SELECT * FROM matches WHERE gameId = " + (str)(gameId)
    cursor.execute(cmd)
    result = cursor.fetchall()
    assert not len(result) > 1, "more than one of the same gameId"
    if(not result): #if result is empty
        print("did not find match")
        return {}
    else:
        return matchTupleToMatchDict(result[0])
    
def matchTupleToMatchDict(matchTuple):
    assert len(matchTuple) == 23, "matchTuple is of the incorrect length"
    matchDict = {}
    matchDict["gameId"] = matchTuple[0]
    matchDict["gameCreation"] = matchTuple[1]
    matchDict["mapId"] = matchTuple[2]
    matchDict["queueId"] = matchTuple[3]
    matchDict["seasonId"] = matchTuple[4]
    matchDict["gameDuration"] = matchTuple[5]
    matchDict["gameMode"] = matchTuple[6]
    matchDict["gameType"] = matchTuple[7]
    matchDict["platformId"] = matchTuple[8]
    matchDict["gameVersion"] = matchTuple[9]
    matchDict["p1"] = matchTuple[10]
    matchDict["p2"] = matchTuple[11]
    matchDict["p3"] = matchTuple[12]
    matchDict["p4"] = matchTuple[13]
    matchDict["p5"] = matchTuple[14]
    matchDict["p6"] = matchTuple[15]
    matchDict["p7"] = matchTuple[16]
    matchDict["p8"] = matchTuple[17]
    matchDict["p9"] = matchTuple[18]
    matchDict["p10"] = matchTuple[19]
    matchDict["participants"] = json.loads(matchTuple[20])
    matchDict["teams"] = json.loads(matchTuple[21])
    matchDict["participantIdentities"] = json.loads(matchTuple[22])
    return matchDict

def fetchAccount(cmd):
    global cursor
    cursor.execute(cmd)
    result = cursor.fetchall()
    assert not len(result) > 1, "more than one of the same identifier"
    if(not result): #if result is empty
        return {}
    else:
        return json.loads(result[0][0])
    
def accTupleToAccDict(accTuple):
    assert len(accTuple) == 8, "accTuple is of the incorrect length"
    accDict = {}
    accDict["profileIconId"] = accTuple[0]
    accDict["name"] = accTuple[1]
    accDict["puuid"] = accTuple[2]
    accDict["summonerLevel"] = accTuple[3]
    accDict["accountId"] = accTuple[4]
    accDict["id"] = accTuple[5]
    accDict["revisionDate"] = accTuple[6]
    return accDict
    
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
    cmd = "SELECT data FROM accounts WHERE name = \"" + name.lower() + "\""
    return fetchAccount(cmd)