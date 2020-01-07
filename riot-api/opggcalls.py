# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 14:04:10 2019

@author: ahirc
"""

import riotapicalls
import dbcalls
import time

def getNamesFromOpgg(opgg):
    split = opgg.split("query=")    #we only care about the part after query=, which is in split[1]
    if(len(split) < 2):    #passed an invalid op.gg link
        return []
    names = split[1].split("%2C")   #each name is separated by %2C
    finalNames = [] #store our final names here
    
    for name in names:
        #handle all the special characters in the name.
        #assertion: a special character is always in the format "%__%__", where "__" is in hex (ex. %C3%B2)
        
        #construct variables
        n = name
        index = n.find('%')
        finalName = ""
        lastIndex = -1  #we need to know how the final name string needs to be concatenated, so keep track of the last special character
        
        while(not(index == -1)):
            char = n[index:index+6] #isolate the special character string
            char = translateChar(char)  #translate the string into a single char
            finalName += n[:index]  #add the previous characters before the special char to the finalName
            finalName += char #add the special char to the finalName
            #reconstruct variables
            n = n[index+6:] 
            lastIndex = index
            index = n.find('%')
            
        #handle the final cases
        if(lastIndex == -1):
            #there were no special characters, the name is just the name
            finalName = name
        else:
            #there was at least one special character, add the last part after the last special character
            finalName += n
            
        finalNames.append(finalName)    #append the finalName to the array of them
    return finalNames
    
def translateChar(char):
    hexInts = [int(char[1:3],16), int(char[4:],16)] #isolate the first set and decode them, then isolate the second set and decode them
    specChar = bytes(hexInts) #turn the hexInts into bytes so we can decode them and return them in utf8 format
    return specChar.decode('utf8')

"""
Below are helper methods for createScoutingReport()
"""

def findParticipantId(match,summId):
    for p in match["participantIdentities"]:
        if(p["player"]["summonerId"] == summId):
            return p["participantId"]
    return -1

def addInfo(d,pData):
    champ = dbcalls.translateChamp(pData["championId"])
    win = 1 if pData["stats"]["win"] else 0
    
    #champion info
    if champ in d:
        d[champ]["matches"] += 1
        d[champ]["wins"] += win
    else:
        d[champ] = {"matches":1,"wins":win,"items":{},"lanes":{},"runes":{}}
    
    #items info (per champion)
    for num in range(0,7):
        itemNum = pData["stats"]["item"+(str)(num)]
        item = dbcalls.translateItem(itemNum)
        if(not item == ""): #ensures we don't add empty inventory slots to the items dict, or outdated items
            items = d[champ]["items"]
            if item in items:
                items[item] += 1
            else:
                items[item] = 1
                
    #lane info (per champion)
    lane = pData["timeline"]["lane"]
    lanes = d[champ]["lanes"]
    if lane in lanes:
        lanes[lane] += 1
    else:
        lanes[lane] = 1
        
    #rune info (per champion)
    for num in range(0,6):
        runeNum = pData["stats"]["perk"+(str)(num)]
        rune = dbcalls.translateRune(runeNum)
        runes = d[champ]["runes"]
        if(not rune == ""): #ensures we don't add outdated runes that will cause an error
            if rune in runes:
                runes[rune] += 1
            else:
                runes[rune] = 1

def analyzeMatches(matches,account):
    recent = {}
    aggregate = {}
    summId = account["id"]
    now = time.time()*1000 #in milliseconds
    for match in matches:
        pId = findParticipantId(match,summId)
        assert not pId == -1, "player was not in their own game: " + (str)(match["gameId"]) + " | " + (str)(account["name"])
        pData = match["participants"][pId-1]
        msPerWeek = 604800*1000 #milliseconds per week
        if(now-match["gameCreation"] < msPerWeek*4):   #if the match was within two weeks ago, it is "recent"
            addInfo(recent,pData)
        addInfo(aggregate,pData)
    analysis = {"recent":recent,"aggregate":aggregate}
    return analysis

def createReport(accounts):
    allAnalysis = []
    for account in accounts:
        if(account):    #if the account is a valid account
            name = account["name"]
            print("Retrieving all ranked matches from \"" + name + "\"...")
            matches = riotapicalls.getAllRankedMatchesByAccount(account)
            print((str)(len(matches)) + " ranked matches retrieved from \"" + name + "\".")
            analysis = analyzeMatches(matches,account)
            allAnalysis.append(analysis)
        else:
            print("Invalid account given.")
    return allAnalysis

def createScoutingReport(teamName,opgg):
    print("Creating scouting report for " + teamName + "...")
    names = getNamesFromOpgg(opgg)
    accounts = riotapicalls.getAccountsByNames(names)
    dbcalls.addTeamToDB(teamName,accounts)
    createReport(accounts)
    print("Scouting report created for " + teamName)
    
#test = analyzeMatches(dbcalls.fetchMatchesByName("CrusherCake"),dbcalls.fetchAccountByName("CrusherCake"))
    
#createScoutingReport("UC Irvine","https://na.op.gg/multi/query=duongpro%2Ckimdown%2Cthecookie%2Cdescraton%2Cyoungbin")
#createScoutingReport("TAMU","https://na.op.gg/multi/query=crecious%2Ctheholyslurp%2Cnatey67%2Cimbiglou%2Cmrblackpanda%2Ckshuna")
#createScoutingReport("NC State - Varsity","https://na.op.gg/multi/query=jast%2Canonymouspi%2Cdrbeat%2Clok%C3%AE%2Cbobtimer%2Cwolfskullrider%2Cpeachbeltprodigy%2Calextheclown")
#createScoutingReport("St. Edward's Varsity","https://na.op.gg/multi/query=darkakemi%2Cgeschickt%2Cviserys%2Ct%C3%BBrtl%C4%99%2Cvenomouslizard%2Ca%C5%BEura%2Csirpopencoc%2Ccallistus")
#createScoutingReport("University of Ottawa","https://na.op.gg/multi/query=yoken%2Cxpsionicsx%2Cmidianehokage%2Croronoazary%2Copenbackpack%2Cdigitalotus")
#createScoutingReport("Ryerson Rams","https://na.op.gg/multi/query=swiftah%2Cdead420%2Cruel%2Cayami%2Cleur%2Csubjoint%2Cgroszak%2Chugedarshanfan%2Cfk")
#createScoutingReport("York University","https://na.op.gg/multi/query=lnvent%2Cspin%2Cscrandor%2Cmishaeats%2Cgrubfoot%2Cmonka%2Ccabstract%2Cchickendelivery")