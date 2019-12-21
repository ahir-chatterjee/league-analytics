# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 14:04:10 2019

@author: ahirc
"""

import riotapicalls

def getNamesFromOpgg(opgg):
    opgg = "https://na.op.gg/multi/query=arfarfawoo%C3%B2w%C3%B3o%2Cpoopsers%2Cloopsers%2Cra%C3%AFlgun%2Clickitloveit"
    split = opgg.split("query=")
    names = split[1].split("%2C")
    print(names)
    finalNames = []
    for name in names:
        n = name
        index = n.find('%')
        finalName = ""
        lastIndex = -1
        while(not(index == -1)):
            char = n[index:index+6]
            char = translateChar(char)
            finalName += n[:index]
            finalName += char
            n = n[index+6:]
            lastIndex = index
            index = n.find('%')
        if(lastIndex == -1):
            finalName = name
        else:
            finalName += n[lastIndex-2:]
        finalNames.append(finalName)
    print(finalNames)
    
def translateChar(char):
    string = "\\x" + char[1:3] + "\\x" + char[4:]
    b = (bytes)(string)
    print(b.decode('utf8'))
    return '!'

#print(b'\xC3\xB2'.decode('utf8'))
#print("ò".encode('utf8'))    
#print("ò".encode('utf8').decode('utf8'))
getNamesFromOpgg("")