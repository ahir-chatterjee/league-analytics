# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 14:04:10 2019

@author: ahirc
"""

def stichIntoMulti(opggs):
    multi = "https://na.op.gg/multi/query="
    for opgg in opggs:
        if("/summoner/" in opgg):   #single opgg
            split = opgg.split("userName=")
            parts = split[1].split('+')
            name = ""
            for part in parts:
                name += part
            multi += name + "%2C"
        elif("/multi/" in opgg):    #multi opgg
            split = opgg.split("query=")
            names = split[1]
            multi += names + "%2C"
    multi = multi[:len(multi)-3]    #get rid of the last extraneous "%2C" in the multi
    return multi

def createMultiFromNames(names):
    multi = "https://na.op.gg/multi/query="
    for name in names:
        name = name.lower()
        name = name.replace(" ","")
        multi += name + "%2C"
    multi = multi[:len(multi)-3]
    return multi

def getNamesFromMulti(opgg):
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