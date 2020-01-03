# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 16:14:03 2020

@author: Ahir
"""

import sqlite3

DB = sqlite3.connect("riotapi.db") #connect to our database

def initializeDB():
    """
    Should never be called, but this was used to initalize the riotapi.db file
    """
    global DB
    cursor = DB.cursor()
    
    #hard coded numbers are the max sizes for the respective field, with extra padding just in case
    create_accounts = """
    CREATE TABLE accounts (
    profileIconId int,
    name VARCHAR(16),
    puuid VARCHAR(100),
    summonerLevel int,
    accountId VARCHAR(100),
    id VARCHAR(100),
    revisionDate bigint);
    """
    cursor.execute(create_accounts)
    DB.commit()
    
    #oh boy here we go. time to put the match data here
    
def printTables():
    """
    Purely a debug method
    """
    global DB
    cursor = DB.cursor()
    
    cmd = "SELECT * from accounts"
    cursor.execute(cmd)
    results = cursor.fetchall()
    for r in results:
        print(r)
    
def addAccountToDB(account):
    if(len(account) == 0):  #account wasn't found, don't do anything
        return -1
    if(fetchAccountByPuuid(account["puuid"])):  #account is already in the database, don't do anything
        return 0
    global DB
    cursor = DB.cursor()
    formatStr = """
    INSERT INTO accounts (profileIconId, name, puuid, summonerLevel, accountId, id, revisionDate)
    VALUES ({icon},"{name}","{puuid}",{level},"{accId}","{summId}",{date});
    """
    cmd = formatStr.format(icon=account["profileIconId"],name=(account["name"].lower()),puuid=account["puuid"],level=account["summonerLevel"],
                           accId=account["accountId"],summId=account["id"],date=account["revisionDate"])
    cursor.execute(cmd)
    DB.commit()
    return 1

def updateAccountName(name,puuid):
    global DB
    cursor = DB.cursor()
    cmd = "UPDATE accounts SET name = \"" + name.lower() + "\" WHERE puuid = \"" + puuid + "\""
    cursor.execute(cmd)
    DB.commit()
    
def accListToAccDict(accList):
    #misnomer, it's actually a tuple not a list
    assert len(accList) == 7, "accList is of the incorrect length"
    accDict = {}
    accDict["profileIconId"] = accList[0]
    accDict["name"] = accList[1]
    accDict["puuid"] = accList[2]
    accDict["summonerLevel"] = accList[3]
    accDict["accountId"] = accList[4]
    accDict["id"] = accList[5]
    accDict["revisionDate"] = accList[6]
    return accDict

def fetchAccount(cmd):
    global DB
    cursor = DB.cursor()
    cursor.execute(cmd)
    result = cursor.fetchall()
    assert not len(result) > 1, "more than one of the same identifier"
    if(len(result) == 0):
        return {}
    else:
        return accListToAccDict(result[0])
    
def fetchAccountByPuuid(puuid):
    cmd = "SELECT * FROM accounts WHERE puuid = \"" + puuid + "\""
    return fetchAccount(cmd)

def fetchAccountByAccId(accId):
    cmd = "SELECT * FROM accounts WHERE accountId = \"" + accId + "\""
    return fetchAccount(cmd)

def fetchAccountBySummId(summId):
    cmd = "SELECT * FROM accounts WHERE id = \"" + summId + "\""
    return fetchAccount(cmd)

def fetchAccountByName(name):
    cmd = "SELECT * FROM accounts WHERE name = \"" + name.lower() + "\""
    print(cmd)
    return fetchAccount(cmd)
    