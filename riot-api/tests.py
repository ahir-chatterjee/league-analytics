# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 17:13:32 2020

@author: Ahir
"""

import riotapicalls
import opggcalls
import dbcalls
import time
import createScoutingReport
import findRelatedAccounts

def getAccountTests():
    name = "arf ARF AwOoÒwÓo"
    name = name.lower() #lowercase for case sensitivity
    
    account = riotapicalls.getAccountByName(name)
    assert account["name"].lower() == name, "getAccountByName from server/db: " + account["name"] + " vs " + name
    account = riotapicalls.getAccountByAccId(account["accountId"])
    assert account["name"].lower() == name, "getAccountByAccId from db: " + account["name"] + " vs " + name
    account = riotapicalls.getAccountByPuuid(account["puuid"])
    assert account["name"].lower() == name, "getAccountByPuuid from db: " + account["name"] + " vs " + name
    account = riotapicalls.getAccountBySummId(account["id"])
    assert account["name"].lower() == name, "getAccountBySummId from db: " + account["name"] + " vs " + name
    account = riotapicalls.getAccountByName(name)
    assert account["name"].lower() == name, "getAccountByName from db: " + account["name"] + " vs " + name
    
    print("passed getAccountTests")
    
def getNamesFromOpggTest():
    opgg = "https://na.op.gg/multi/query=yellowbumblebee%2Cvelocityone%2Carfarfawoo%C3%B2w%C3%B3o%2Cpoopsers%2Cmelllo%2Cas%C3%B8nder%2Ccelsiusheat%2Cigthethigh%2Cnoodlz%2Ccrushercake%2Cra%C3%AFlgun"
    names = ["yellowbumblebee","velocityone","arfARFAwOoÒwÓo","poopsers","melllo","ASønder","celsiusheat","igthethigh","noodlz","crushercake","RaÏlgun"]
    for i in range(0,len(names)):
        names[i] = names[i].lower() #lowercase for case sensitivity
    
    opggNames = opggcalls.getNamesFromOpgg(opgg)
    for name in names:
        assert name in opggNames, name + " is not present in " + (str)(opggNames)
    
    print("passed getNamesFromOpggTest")
    
def updateConstantsTest():
    riotapicalls.updateConstants()
    
def fetchMatchesByNameTest():
    matches1 = dbcalls.fetchMatchesByName("CrusherCake")
    account = riotapicalls.getAccountByName("mello mental")
    matches2 = dbcalls.fetchMatchesByAccount(account)
    assert len(matches1) > 900, "didn't get CrusherCake ranked matches"
    assert len(matches2) > 0, "didn't get mello mental ranked matches"
    
def getNamesFromOpggTest2():
    opgg = "https://na.op.gg/multi/query=shorthop%2Cwinst%C3%B3n%2Cthisnamethough%2Cautolocksaber%2Cuwochim%2Carfarfawoo%C3%B2w%C3%B3o%2Cblazednova%2Cloyal%2Cra%C3%AFlgun"
    correctNames = ["shorthop","blazednova","loyal","autolocksaber","Winstón","thisnamethough","uwochim","arfARFAwOoÒwÓo","RaÏlgun"]
    names = opggcalls.getNamesFromOpgg(opgg)
    for name in correctNames:
        if name.lower() not in names:
            print(name + " not found.")

def createScoutingReportTest():
    start = time.time()
    report2 = createScoutingReport("Maryville University","https://na.op.gg/multi/query=niles%2CMUIconic%2CMUWolfe%2CValue%2C1Shady%2CJulien1%2Ckindjungle%2Chybridzz%2Cevanrl%2CCIyde")
    report = createScoutingReport("University of Southern California","https://na.op.gg/multi/query=lofirelax%2Cherking%2Cuschovz%2Cusctechsupport%2Cpo%C4%B1%2Cusckamdono%2Cusc5050352")
    report3 = createScoutingReport("Grand Canyon University","https://na.op.gg/multi/query=siglere%2CNovawolf%2CPlumberMario%2C4bidden%2CGCUQuicksands%2CSwagnar")
    end = time.time()
    elapsedTime = (end-start)/60
    return elapsedTime,report,report2,report3

def findRelatedAccountsTest():
    #names = ["Noodlz","keep it mello","Poopsers","Celsius HEAT","YellowBumbleBee","arf ARF AwOoÒwÓo","IG TheThigh"]
    #names = ["duong pro","kim down","the cookie","descraton","youngbin"]
    #names = ["spøøky","mistystumpey","andybendy","rovex","nintendudex","nme toysoldier"]
    #names = ["i am nightshade","móónlight","súnlight","really big meme","argentumsky","dylaran"]
    #names = ["barbecueribs","ino1","easy 10","scherb","lyo"]
    #names = ["the jons","vinnyhuan","golden kiwi","smelp","sharpe","lunarly","0aks"]    #having trouble with Nova Bot (Texas)
    names = opggcalls.getNamesFromOpgg("https://na.op.gg/multi/query=celsiusheat%2Cigthethigh%2Carfarfawoo%C3%B2w%C3%B3o%2Cpoopsers%2Cnoodlz%2Cra%C3%AFlgun%2Cyellowbumblebee%2Cvelocityone%2Ckeepitmello%2Cas%C3%B8nder")
    start = time.time()
    accounts = []
    for name in names:
        account = riotapicalls.getAccountByName(name)
        accounts.append(account)
    #print(accounts)
    susAccounts = findRelatedAccounts(accounts)
    end = time.time()
    elapsedTime = end-start
    return elapsedTime,susAccounts,accounts,names

def downloadTimelines():
    matchIds = dbcalls.fetchAllMatchIds()
    for matchId in matchIds:
        riotapicalls.getMatchTimeline(matchId[0])

def downloadATonOfStuff():
    dbcalls.printTables()
    print("Downloading timelines")
    riotapicalls.downloadTimelines()
    print("updating accounts")
    dbcalls.updateAccounts()

def main():
    api = riotapicalls.getAccountByName("Gl in Lotteria")
    db = dbcalls.fetchAccountByPuuid(api["puuid"])
    return api,db
    
variables = main()