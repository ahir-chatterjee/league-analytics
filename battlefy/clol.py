# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 14:04:09 2020

@author: Ahir
"""

from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
import time

global base
base = "https://battlefy.com/college-league-of-legends/"

def getSouthUrl():
    south = "2020-south-conference/5de98edc4c23d0180a4e77ae/stage/5e23ad236cbf7a66ba401ca9/"
    return base + south

def getNorthUrl():
    north = "2020-north-conference/5de98dd4196d1311d9e6edbd/stage/5e23b6e395e72856dac06997/"
    return base + north

def getMatchesTableForWeek(url,week):
    bUrl = url + "bracket/" + (str)(week)
    driver = webdriver.Chrome(executable_path='C:/bin/chromedriver.exe')
    driver.get(bUrl)
    time.sleep(4)   #give the driver time to load
    content = BeautifulSoup(driver.page_source,"html.parser")
    bsTable = content.find('table',attrs={"class" : "bfy-table bfy-table-hover"})
    driver.close()
    table = {}
    for row in bsTable.findAll('tr'):
        cols = row.findAll('td')
        rowNum = -1
        if(cols):
            rowNum = (int)((cols[0].text).strip())
            table[rowNum] = {}
            table[rowNum]["match"] = row["class"][1][6:]
        for col in range(1,len(cols)):
            td = cols[col]
            if(col == 1): #date/time
                table[rowNum]["date"] = td.text.strip()
            if(col == 3): #team1 and victory/defeat
                table[rowNum]["team1"] = td.text.strip()
            if(col == 4): #result (2-0,2-1,1-2)
                table[rowNum]["result"] = td.text.strip()
            if(col == 5): #team2 and victory/defeat
                #winner/loser will contain the name of the team that won/was defeated
                table[rowNum]["team2"] = td.text.strip()
                table[rowNum]["winner"] = table[rowNum]["team2"] if "winner" in td["class"] else table[rowNum]["team1"]
                table[rowNum]["loser"] = table[rowNum]["team1"] if table[rowNum]["team2"] in table[rowNum]["winner"] else table[rowNum]["team2"]
    return table

def getMatchData(url):
    driver = webdriver.Chrome(executable_path='C:/bin/chromedriver.exe')
    driver.get(url)
    time.sleep(4)   #give the driver time to load
    content = BeautifulSoup(driver.page_source,"html.parser")
    matchStats = content.find('div',attrs={"class" : "end-of-game game-stats clearfix"})
    driver.close()
    if(matchStats == None):
        print("Forfeit match detected.")
        return {"ff":True}
    matchData = {"bans0":{},"bans1":{}}
    banLists = matchStats.findAll('div',attrs={"class" : "ban-list"})
    for bans in banLists:
        banTeam = ""
        if bans["ng-if"] == "stats.teams[0].teamStats.bans":
            banTeam = "bans0"
        else:
            banTeam = "bans1"
            
        localBans = {}
        for ban in bans.findAll("li"):
            imgSrc = ban.find('img')["src"]
            champ = imgSrc[imgSrc.rfind("/")+1:imgSrc.rfind(".")]
            banNum = ban.find('p').text.strip()
            localBans[banNum] = champ
        if "6" in localBans:
            matchData[banTeam]["1"] = [localBans["2"],localBans["4"],localBans["6"]]
            matchData[banTeam]["2"] = [localBans["1"],localBans["3"]]
        else:
            matchData[banTeam]["1"] = [localBans["1"],localBans["3"],localBans["5"]]
            matchData[banTeam]["2"] = [localBans["2"],localBans["4"]]
    return matchData
        
def scrapeMatchesForWeek(url,week):
    table = getMatchesTableForWeek(getSouthUrl(),4)
    matches = []
    for match in table:
        mUrl = getSouthUrl() + "match/" + match["match"]
        matches.append(getMatchData(mUrl))

#matchInfo = scrapeMatchesForWeek()
#table = getMatchesTableForWeek(getSouthUrl(),4)
#getMatchData("https://battlefy.com/college-league-of-legends/2020-south-conference/5de98edc4c23d0180a4e77ae/stage/5e23ad236cbf7a66ba401ca9/match/5e4190c86caf8e107c1f9f3a")
url = getSouthUrl() + "match/5e4190c86caf8e107c1f9f3a"
data = getMatchData(url)
