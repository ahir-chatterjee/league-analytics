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
    
    print("passed getAccount tests")    

def main():
    downloadAccount()
    
if __name__ == '__main__':
    main()