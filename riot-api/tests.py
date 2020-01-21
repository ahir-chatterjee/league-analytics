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
#from roleml import roleml

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
    #report = createScoutingReport.createScoutingReport("UT Austin","https://na.op.gg/multi/query=noodlz%2Cra%C3%AFlgun%2Ckeepitmello%2Cpoopsers%2Clpoklpok%2Carfarfawoo%C3%B2w%C3%B3o%2Ccelsiusheat")
    #report = createScoutingReport.createScoutingReport("Waterloo","https://na.op.gg/multi/query=barbecueribs%2Cino1%2Ceasy10%2Cscherb%2Clyo")
    #report2 = createScoutingReport.createScoutingReport("Maryville University","https://na.op.gg/multi/query=niles%2CMUIconic%2CMUWolfe%2CValue%2C1Shady%2Csleeptimego%2Ckindjungle%2Chybridzz%2Cevanrl%2CCIyde")
    gcu = opggcalls.stichIntoMulti(["https://na.op.gg/summoner/userName=siglere","https://na.op.gg/summoner/userName=Novawolf","https://na.op.gg/summoner/userName=PlumberMario","https://na.op.gg/summoner/userName=4bidden","https://na.op.gg/summoner/userName=GCU+Quicksands","https://na.op.gg/summoner/userName=Swagnar"])
    report3 = createScoutingReport.createScoutingReport("Grand Canyon University",gcu)
    #hiddens = createScoutingReport.createScoutingReport("h","https://na.op.gg/multi/query=gavita%2Cbotcait%2Cdaddyowo%2Cggevosnore%2Cadebolaoluwa%2Cthejawsofdeath%2Caut1stanuser")
    end = time.time()
    elapsedTime = (end-start)/60
    return [elapsedTime,report3]#,report2,report3]

def findRelatedAccountsTest():
    #names = ["Noodlz","keep it mello","Poopsers","Celsius HEAT","arf ARF AwOoÒwÓo","lpoklpok","raïlgun"]
    #names = ["duong pro","kim down","the cookie","descraton","youngbin"]
    #names = ["spøøky","mistystumpey","andybendy","rovex","nintendudex","nme toysoldier"]
    #names = ["i am nightshade","móónlight","súnlight","really big meme","argentumsky","dylaran"]
    names = ["barbecueribs","ino1","easy 10","scherb","lyo"]
    #names = ["the jons","vinnyhuan","golden kiwi","smelp","sharpe","lunarly","0aks"]    #having trouble with Nova Bot (Texas)
    #names = ['lofirelax', 'herking', 'uschovz', 'usctechsupport', 'poı', 'usckamdono', 'usc5050352', 'joejacko', 'gtinybear', 'hey i miss u']#opggcalls.getNamesFromOpgg("https://na.op.gg/multi/query=lofirelax%2Cherking%2Cuschovz%2Cusctechsupport%2Cpo%C4%B1%2Cusckamdono%2Cusc5050352")
    #names = opggcalls.getNamesFromOpgg("https://na.op.gg/multi/query=crecious%2Cimbiglou%2Ctheholyslurp%2Cnatey67%2Ckshuna%2Cmrblackpanda")
    #names = opggcalls.getNamesFromOpgg("https://na.op.gg/multi/query=niles%2CMUIconic%2CMUWolfe%2CValue%2C1Shady%2Csleeptimego%2Ckindjungle%2Chybridzz%2Cevanrl%2CCIyde")
    names = opggcalls.getNamesFromOpgg("https://na.op.gg/multi/query=gavita%2Cbotcait%2Cdaddyowo%2Cggevosnore%2Cadebolaoluwa%2Cthejawsofdeath%2Caut1stanuser")
    start = time.time()
    accounts = []
    for name in names:
        account = riotapicalls.getAccountByName(name)
        accounts.append(account)
    #print(accounts)
    susAccounts = findRelatedAccounts.findRelatedAccounts(accounts)
    end = time.time()
    elapsedTime = (end-start)/60
    return [elapsedTime,susAccounts,accounts,names]

def downloadTimelines():
    matchIds = dbcalls.fetchAllMatchIds()
    for matchId in matchIds:
        riotapicalls.getMatchTimeline(matchId[0])

def downloadATonOfStuff():
    dbcalls.printTables()
    print("Downloading timelines")
    downloadTimelines()
    print("updating accounts")
    dbcalls.updateAccounts()
    
def roleMLTest():
    id1 = 3260726596
    id2 = 3261268214
    m1 = riotapicalls.getMatch(id1)
    t1 = riotapicalls.getMatchTimeline(id1)
    m2 = riotapicalls.getMatch(id2)
    t2 = riotapicalls.getMatchTimeline(id2)
    #p1 = roleml.roleml.predict(m1,t1)
    #p2 = roleml.roleml.predict(m2,t2)
    return

def createMultiTest():
    names = ['lofirelax', 'herking', 'uschovz', 'usctechsupport', 'poı', 'usckamdono', 'usc5050352', 'joejacko', 'gtinybear', 'hey i miss u']
    return opggcalls.createMultiFromNames(names)

def downloadAccountsByOpgg(opgg):
    names = opggcalls.getNamesFromOpgg(opgg)
    accounts = riotapicalls.getAccountsByNames(names)
    for account in accounts:
        print(account["name"])
        riotapicalls.getAllRankedMatchesByAccount(account)

def main():
    #return findRelatedAccountsTest()
    print(opggcalls.stichIntoMulti(["https://na.op.gg/summoner/userName=siglere","https://na.op.gg/summoner/userName=Novawolf","https://na.op.gg/summoner/userName=PlumberMario","https://na.op.gg/summoner/userName=4bidden","https://na.op.gg/summoner/userName=GCU+Quicksands","https://na.op.gg/summoner/userName=Swagnar"]))
    return createScoutingReportTest()
    #downloadAccountsByOpgg("https://na.op.gg/multi/query=ac%CB%86130%2Chornyandgiad%2Clungair%2Cdustinchang%2Csatanoncoke%2Cjudochess%2Cloopsers%2Cmellomental%2Clickitloveit%2Cboostedmememonke%2Cmelllo")
    
accs = main()