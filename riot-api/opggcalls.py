# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 14:04:10 2019

@author: ahirc
"""

import riotapicalls
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
            #there was at least one special character, do some voodoo magic to create the proper name
            finalName += n[lastIndex-2:]
            
        finalNames.append(finalName)    #append the finalName to the array of them
    return finalNames
    
def translateChar(char):
    hexInts = [int(char[1:3],16), int(char[4:],16)] #isolate the first set and decode them, then isolate the second set and decode them
    specChar = bytes(hexInts) #turn the hexInts into bytes so we can decode them and return them in utf8 format
    return specChar.decode('utf8')

def createScoutingReport(teamName,opgg):
    names = getNamesFromOpgg(opgg)
    accounts = riotapicalls.getAccountsByNames(names)
    now = time.localtime()
    timeString = (str)(now.tm_mon) + "-" + (str)(now.tm_mday) + "-" + (str)(now.tm_year)
    riotapicalls.saveFile(teamName+" "+timeString+".txt",accounts,time.asctime(time.localtime(time.time())))
    for account in accounts:
        summName = account["name"]
        print(summName)
        riotapicalls.getAllRankedMatchesByAccount(account)
    
#createScoutingReport("UT Austin","https://na.op.gg/multi/query=poopsers%2Cvelocityone%2Cigthethigh%2Carfarfawoo%C3%B2w%C3%B3o%2Cloopsers%2Cyellowbumblebee%2Cnoodlz%2Csumochess%2Cas%C3%B8nder%2Ccrushercake%2Cra%C3%AFlgun")
#check Tanner (VelocityOne). Games downloaded are far too low