# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 17:13:32 2020

@author: Ahir
"""

import riotapicalls
import opggcalls
import dbcalls

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

def main():
    updateConstantsTest()
    dbcalls.printTables()
    
if __name__ == '__main__':
    main()