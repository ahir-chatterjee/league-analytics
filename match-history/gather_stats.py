# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 12:44:30 2020

@author: Ahir
"""

from bs4 import BeautifulSoup
import requests
import json
import os
import xlwt
from selenium import webdriver
import time

def createCStats(players):
    cStats = []
    for player in players:
        name = player.find('div',attrs={"class" : "champion-nameplate-name"}).text
        name = name[1:len(name)-1]
        cStats.append({"champion":name})
    return cStats

def scrapeMHData(MHurl):
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")
    url = MHurl
    driver = webdriver.Chrome(executable_path = DRIVER_BIN)
    driver.get(url)
    input("Press enter to continue after logging in: ") #temporary fix to log-in issue
    time.sleep(3)
    
    content = BeautifulSoup(driver.page_source,"html.parser")
    general = {}
    count = 0
    divs = content.find('div',attrs={"class" : "default-2-3"}).findAll('div')
    for div in divs:
        if(count == len(divs)-2):
            general["time"] = div.text
        elif(count == len(divs)-1):
            general["date"] = div.text
        count += 1
    scoreboard = content.find('div',attrs={"class" : "gs-container gs-no-gutter"})
    general["result"] = scoreboard.find('div',attrs={"class" : "game-conclusion"}).text.strip()
    stats = content.find('table',attrs={"class" : "table table-bordered"})
    players = scoreboard.findAll('li')
    
    cStats = createCStats(players)
    
#    headerRow = stats.find('tr',attrs={"class" : "grid-header-row"})
#    data = headerRow.findAll('td')
#    for d in data:
#        #print(d)
#        div = d.find('div')
#        div = div.find('div')
#        if(div is not None):
#            div = div.find('div')
#            print(div["data-rg-id"])
    
    rows = stats.findAll('tr')
    for row in rows:
        if(row.has_attr("class") and not row["class"][0] == "view" and not row["class"][0] == "grid-header-row"):
            data = row.findAll('td')
            i = 0
            statName = ""
            for d in data:
                #if(d.has_attr("class") and d["class"][0] == "grid-label"):
                    #print()
                #print(d.text)
                if(statName == ""):
                    statName = d.text
                else:
                    cStats[i][statName] = d.text
                    i += 1
    
    driver.close()
    return {"cStats":cStats, "general":general}

def initializeSheet(ws):
    num = 0
    ws.write(num,0,"Date")
    ws.write(num,1,"W/L")
    ws.write(num,2,"Game Time")
    ws.write(num,5,"Champion")
    ws.write(num,7,"Kills")
    ws.write(num,8,"Deaths")
    ws.write(num,9,"Assists")
    ws.write(num,13,"KDA")
    ws.write(num,19,"CS")
    ws.write(num,21,"CSPM")
    ws.write(num,23,"Gold Earned")
    ws.write(num,27,"GPM")
    ws.write(num,29,"Damage Dealt")
    ws.write(num,33,"DPM")
    ws.write(num,35,"Wards Placed")
    ws.write(num,37,"Control Wards Purchased")
    ws.write(num,39,"Wards Destroyed")
    ws.write(num,41,"WPM")
    ws.write(num,43,"DMG/Gold")
    ws.write(num,3,"Team Kills")
    ws.write(num,4,"Enemy Team Kills")
    ws.write(num,6,"Opposing Champion")
    ws.write(num,10,"Kill Delta")
    ws.write(num,11,"Death Delta")
    ws.write(num,12,"Assist Delta")
    ws.write(num,14,"KDA Delta")
    ws.write(num,15,"KP%")
    ws.write(num,16,"KP% Delta")
    ws.write(num,17,"Death Share")
    ws.write(num,18,"Death Share Delta")
    ws.write(num,20,"CS Delta")
    ws.write(num,22,"CSPM Delta")
    ws.write(num,24,"Gold Delta")
    ws.write(num,25,"Gold Share")
    ws.write(num,26,"Gold Share Delta")
    ws.write(num,28,"GPM Delta")
    ws.write(num,30,"Damage Delta")
    ws.write(num,31,"Damage Share")
    ws.write(num,32,"Damage Share Delta")
    ws.write(num,34,"DPM Delta")
    ws.write(num,36,"Wards Placed Delta")
    ws.write(num,38,"Control Wards Purchased Delta")
    ws.write(num,40,"Wards Destroyed Delta")
    ws.write(num,42,"WPM Delta")
    ws.write(num,44,"DMG/Gold Delta")
    ws.write(num,45,"DMG/Gold Share")
    ws.write(num,46,"DMG/Gold Share Delta")
    ws.write(num,47,"DMG Share/Gold Share")  
    ws.write(num,48,"DMG Share/Gold Share Delta")
    
def writeStatsSheet(urls,teamName):
    wb = xlwt.Workbook()
    sheets = {}
    for num, url in enumerate(urls, start=1):
        MHData = scrapeMHData(url)
        general = MHData["general"]
        cStats = MHData["cStats"]
        for champ in cStats:
            champ["player"] = input("Who played " + champ["champion"] + "? ") #can write skip to not log this player
        
        print()
        general["kills1"] = 0
        general["kills2"] = 0
        general["gold1"] = 0
        general["gold2"] = 0
        general["dmg1"] = 0
        general["dmg2"] = 0
        count = 0
        for champ in cStats:
            kda = champ["KDA"].split("/")
            champ["CS"] = (float)(champ["Minions Killed"])
            if(not champ["Neutral Minions Killed"] == "-"):
                champ["CS"] += (float)(champ["Neutral Minions Killed"])
            champ["kills"] = (float)(kda[0])
            champ["deaths"] = (float)(kda[1])
            champ["assists"] = (float)(kda[2])
            champ["Gold Earned"] = (float)(champ["Gold Earned"].split("k")[0])*1000
            champ["Total Damage to Champions"] = (float)(champ["Total Damage to Champions"].split("k")[0])*1000
            champ["Wards Placed"] = (float)(champ["Wards Placed"])
            if(champ["Control Wards Purchased"] == '-'):
                champ["Control Wards Purchased"] = 0
            else:
                champ["Control Wards Purchased"] = (float)(champ["Control Wards Purchased"])
            if(champ["Wards Destroyed"] == '-'):
                champ["Wards Destroyed"] = 0
            else:
                champ["Wards Destroyed"] = (float)(champ["Wards Destroyed"])
            champ["Wards Destroyed"] = float(champ["Wards Destroyed"])
            if(champ["deaths"] == 0):
                champ["KDA"] = champ["kills"] + champ["assists"]
            else:
                champ["KDA"] = ((champ["kills"] + champ["assists"])/champ["deaths"])
            if(count < 5): #simple way to check for blue vs red side
                general["kills1"] += champ["kills"]
                general["gold1"] += champ["Gold Earned"]
                general["dmg1"] += champ["Total Damage to Champions"]
            else:
                general["kills2"] += champ["kills"]
                general["gold2"] += champ["Gold Earned"]
                general["dmg2"] += champ["Total Damage to Champions"]
            count += 1
            
        #roles = ["Top","Jungle","Mid","Bot","Support"]
        count = 0
        for champ in cStats: #this part of the code is hard coded and fairly bad. Could be vastly improved in the future
            if not champ["player"] == "skip": #if this is a player we actually care about stat-tracking
                ws = sheets.get(champ["player"]) #check if we've already made a sheet for this player
                if(not ws): #if no sheet exists, make one and then store it
                    ws = wb.add_sheet(champ["player"])
                    sheets[champ["player"]] = ws
                    initializeSheet(ws)
                ws.write(num,0,general["date"])
                gameTime = (float)(general["time"].split(":")[0])+ ((float)(general["time"].split(":")[1]))/60
                ws.write(num,2,gameTime)
                ws.write(num,5,champ["champion"])
                ws.write(num,7,champ["kills"])
                ws.write(num,8,champ["deaths"])
                ws.write(num,9,champ["assists"])
                ws.write(num,13,champ["KDA"])
                ws.write(num,19,champ["CS"])
                ws.write(num,21,champ["CS"]/gameTime)
                ws.write(num,23,champ["Gold Earned"])
                ws.write(num,27,champ["Gold Earned"]/gameTime)
                ws.write(num,29,champ["Total Damage to Champions"])
                ws.write(num,33,champ["Total Damage to Champions"]/gameTime)
                ws.write(num,35,champ["Wards Placed"])
                ws.write(num,37,champ["Control Wards Purchased"])
                ws.write(num,39,champ["Wards Destroyed"])
                ws.write(num,41,(float)(champ["Wards Placed"])/gameTime)
                ws.write(num,43,(champ["Total Damage to Champions"]/champ["Gold Earned"]))
                if(count < 5): #simple way to swap teams
                    oppChamp = cStats[count+5]
                    if(general["result"] == "VICTORY"):
                        ws.write(num,1,"W")
                    else:
                        ws.write(num,1,"L")
                    ws.write(num,3,general["kills1"])
                    ws.write(num,4,general["kills2"])
                    ws.write(num,6,oppChamp["champion"])
                    ws.write(num,10,champ["kills"]-oppChamp["kills"])
                    ws.write(num,11,champ["deaths"]-oppChamp["deaths"])
                    ws.write(num,12,champ["assists"]-oppChamp["assists"])
                    ws.write(num,14,champ["KDA"]-oppChamp["KDA"])
                    ws.write(num,15,(champ["kills"]+champ["assists"])/general["kills1"])
                    ws.write(num,16,((champ["kills"]+champ["assists"])/general["kills1"])-((oppChamp["kills"]+oppChamp["assists"])/general["kills2"]))
                    ws.write(num,17,(champ["deaths"]/general["kills2"]))
                    ws.write(num,18,(champ["deaths"]/general["kills2"])-(champ["deaths"]/general["kills1"]))
                    ws.write(num,20,champ["CS"]-oppChamp["CS"])
                    ws.write(num,22,(champ["CS"]/gameTime)-(oppChamp["CS"]/gameTime))
                    ws.write(num,24,champ["Gold Earned"]-oppChamp["Gold Earned"])
                    ws.write(num,25,champ["Gold Earned"]/general["gold1"])
                    ws.write(num,26,(champ["Gold Earned"]/general["gold1"])-(oppChamp["Gold Earned"]/general["gold2"]))
                    ws.write(num,28,(champ["Gold Earned"]/gameTime)-(oppChamp["Gold Earned"]/gameTime))
                    ws.write(num,30,champ["Total Damage to Champions"]-oppChamp["Total Damage to Champions"])
                    ws.write(num,31,(champ["Total Damage to Champions"]/general["dmg1"]))
                    ws.write(num,32,(champ["Total Damage to Champions"]/general["dmg1"])-(oppChamp["Total Damage to Champions"]/general["dmg2"]))
                    ws.write(num,34,(champ["Total Damage to Champions"]/gameTime)-(oppChamp["Total Damage to Champions"]/gameTime))
                    ws.write(num,36,champ["Wards Placed"]-oppChamp["Wards Placed"])
                    ws.write(num,38,champ["Control Wards Purchased"]-oppChamp["Control Wards Purchased"])
                    ws.write(num,40,champ["Wards Destroyed"]-oppChamp["Wards Destroyed"])
                    ws.write(num,42,((float)(champ["Wards Placed"])/gameTime)-((float)(oppChamp["Wards Placed"])/gameTime))
                    ws.write(num,44,(champ["Total Damage to Champions"]/champ["Gold Earned"])-(oppChamp["Total Damage to Champions"]/oppChamp["Gold Earned"]))
                    ws.write(num,45,(champ["Total Damage to Champions"]/(champ["Gold Earned"]/general["gold1"])))
                    ws.write(num,46,(champ["Total Damage to Champions"]/(champ["Gold Earned"]/general["gold1"]))-(oppChamp["Total Damage to Champions"]/(oppChamp["Gold Earned"]/general["gold2"])))
                    ws.write(num,47,((champ["Total Damage to Champions"]/general["dmg1"])/(champ["Gold Earned"]/general["gold1"])))  
                    ws.write(num,48,((champ["Total Damage to Champions"]/general["dmg1"])/(champ["Gold Earned"]/general["gold1"]))-((oppChamp["Total Damage to Champions"]/general["dmg2"])/(oppChamp["Gold Earned"]/general["gold2"])))
                else:
                    oppChamp = cStats[count-5]
                    if(general["result"] == "DEFEAT"):
                        ws.write(num,1,"W")
                    else:
                        ws.write(num,1,"L")
                    ws.write(num,3,general["kills2"])
                    ws.write(num,4,general["kills1"])
                    ws.write(num,6,oppChamp["champion"])
                    ws.write(num,10,champ["kills"]-oppChamp["kills"])
                    ws.write(num,11,champ["deaths"]-oppChamp["deaths"])
                    ws.write(num,12,champ["assists"]-oppChamp["assists"])
                    ws.write(num,14,champ["KDA"]-oppChamp["KDA"])
                    ws.write(num,15,(champ["kills"]+champ["assists"])/general["kills2"])
                    ws.write(num,16,((champ["kills"]+champ["assists"])/general["kills2"])-((oppChamp["kills"]+oppChamp["assists"])/general["kills1"]))
                    ws.write(num,17,(champ["deaths"]/general["kills1"]))
                    ws.write(num,18,(champ["deaths"]/general["kills1"])-(champ["deaths"]/general["kills2"]))
                    ws.write(num,20,champ["CS"]-oppChamp["CS"])
                    ws.write(num,22,(champ["CS"]/gameTime)-(oppChamp["CS"]/gameTime))
                    ws.write(num,24,champ["Gold Earned"]-oppChamp["Gold Earned"])
                    ws.write(num,25,champ["Gold Earned"]/general["gold2"])
                    ws.write(num,26,(champ["Gold Earned"]/general["gold2"])-(oppChamp["Gold Earned"]/general["gold1"]))
                    ws.write(num,28,(champ["Gold Earned"]/gameTime)-(oppChamp["Gold Earned"]/gameTime))
                    ws.write(num,30,champ["Total Damage to Champions"]-oppChamp["Total Damage to Champions"])
                    ws.write(num,31,(champ["Total Damage to Champions"]/general["dmg2"]))
                    ws.write(num,32,(champ["Total Damage to Champions"]/general["dmg2"])-(oppChamp["Total Damage to Champions"]/general["dmg1"]))
                    ws.write(num,34,(champ["Total Damage to Champions"]/gameTime)-(oppChamp["Total Damage to Champions"]/gameTime))
                    ws.write(num,36,champ["Wards Placed"]-oppChamp["Wards Placed"])
                    ws.write(num,38,champ["Control Wards Purchased"]-oppChamp["Control Wards Purchased"])
                    ws.write(num,40,champ["Wards Destroyed"]-oppChamp["Wards Destroyed"])
                    ws.write(num,42,((float)(champ["Wards Placed"])/gameTime)-((float)(oppChamp["Wards Placed"])/gameTime)) 
                    ws.write(num,44,(champ["Total Damage to Champions"]/champ["Gold Earned"])-(oppChamp["Total Damage to Champions"]/oppChamp["Gold Earned"]))   
                    ws.write(num,45,(champ["Total Damage to Champions"]/(champ["Gold Earned"]/general["gold2"])))
                    ws.write(num,46,(champ["Total Damage to Champions"]/(champ["Gold Earned"]/general["gold2"]))-(oppChamp["Total Damage to Champions"]/(oppChamp["Gold Earned"]/general["gold1"])))
                    ws.write(num,47,((champ["Total Damage to Champions"]/general["dmg2"])/(champ["Gold Earned"]/general["gold2"])))  
                    ws.write(num,48,((champ["Total Damage to Champions"]/general["dmg2"])/(champ["Gold Earned"]/general["gold2"]))-((oppChamp["Total Damage to Champions"]/general["dmg1"])/(oppChamp["Gold Earned"]/general["gold1"])))    
            count += 1
    wb.save(teamName + ".xls")
    
urls = ["https://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/3529291963/42055489?tab=overview",
        "https://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/3529292291/42055489?tab=overview",
        "https://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/3529258460/42055489?tab=overview",
        "https://matchhistory.na.leagueoflegends.com/en/#match-details/NA1/3529518239/42055489?tab=overview"]
writeStatsSheet(urls,"Best Coast Invitational 2020")