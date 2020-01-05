# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 21:22:15 2019

@author: ahirc
"""

import riotapicalls
import opggcalls

def main():
    while(True):
        cmd = input("Enter command (use \"help\" for a list of commands): ")
        cmds = cmd.split()
        if(cmds[0] == "break"):
            break
        else:
            handleCmd(cmds)
        
def handleCmd(cmds):
    cmd = cmds[0].lower()   #main command
    cmdList = [["help"],
               ["opggScout", "teamName", "opgg"],
               ["namesFromOpgg", "opgg"],
               ["downloadRankedGames", "[name1,name2,...,nameN]"]]   #a list of all the commands supported
    if(cmd == "help"):
        #print out all of the commands from cmdList and their arguments (if any)
        print("Here is a list of commands and their parameters that they take:")
        for c in cmdList:
            if(len(c) == 1):    #takes no parameters
                print(c[0])
            else:
                print(c[0] + ":",end=' ')
                for i in range(1,len(c)):
                    if(i == len(c)-1):
                        print(c[i])
                    else:
                        print(c[i],end=', ')
    elif(cmd == "opggScout"):
        #creates a scouting report from the given opgg. see opggcalls.opggScout for more details
        if(len(cmds) != 3):
            invalidParameterLength(3,len(cmds))
        else:
            opggcalls.createScoutingReport(cmds[1],cmds[2])
    elif(cmd == "namesfromopgg"):
        #grabs all of the summoner names from a given opgg. see opggcalls.getNamesFromOpgg
        if(len(cmds) != 2):
            invalidParameterLength(2,len(cmds))
        else:
            print(opggcalls.getNamesFromOpgg(cmds[1]))
    elif(cmd == "downloadrankedgames"):
        #downloads the ranked games from the supplied names
        if(len(cmds) == 1):
            invalidParameterLength("any number of",len(cmds))
        else:
            for i in range(1,len(cmds)):
                name = cmds[i]
                account = riotapicalls.getAccountByName(name)
                riotapicalls.getAllRankedMatchesByAccount(account)  #saves them into a file called name.txt, with a "version" of the season
    else:
        print("Command not recognized. Try \"help\" for a list of recognized commands.")
        
def invalidParameterLength(expected,actual):
    print("Expected " + (str)(expected) + " parameters, receieved " + (str)(actual-1) + " parameters.")
    
if __name__ == '__main__':
    main()