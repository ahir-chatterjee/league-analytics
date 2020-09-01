# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 15:01:47 2020

@author: Ahir
"""

import constants

'''
Tier 1 = 29 units
Tier 2 = 22 units
Tier 3 = 16 units
Tier 4 = 12 units
Tier 5 = 10 units
'''

class GameState:
    
    #initialization methods
    
    def setNames(self,names):
        assert len(names) == len(self.others), "incorrect number of names passed in: " + (str)(len(names))
        for i in range(0,len(names)):
            self.others[i]["name"] = names[i]
            
    def __init__(self,galaxy,names):
        self.units = []
        self.shop = []
        self.level = 1
        self.xp = 0
        self.gold = 2
        self.streak = 0
        self.items = []
        self.others = [{"name":"","units":[]},
                        {"name":"","units":[]},
                        {"name":"","units":[]},
                        {"name":"","units":[]},
                        {"name":"","units":[]},
                        {"name":"","units":[]},
                        {"name":"","units":[]}]
        if(galaxy == "med"):
            self.hp = 125   #if we're in the medium legends galaxy
            for player in self.others:
                player["hp"] = 125
        else:
            self.hp = 100
            for player in self.others:
                player["hp"] = 100
        self.setNames(names)
            
    #item methods
    def addItems(self,items):
        for item in items:
            if(constants.isItem(item)):
                self.items.append(item)
            else:
                print(item + " is invalid.")
            
    def combineItems(self,item1,item2):
        if item1 in self.items:
            self.items.remove(item1)
        if item2 in self.items:
            self.items.remove(item2)
        self.items.append(constants.combineItems(item1,item2))
        
    #unit methods
    def addUnits(self,units):
        for 
            
gs = GameState("none",["a","b","c","d","e","f","g"])