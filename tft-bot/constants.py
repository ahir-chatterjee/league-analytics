# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 15:28:10 2020

@author: Ahir
"""

'''
Tier 1 = 29 units
Tier 2 = 22 units
Tier 3 = 16 units
Tier 4 = 12 units
Tier 5 = 10 units
'''

#items
components = ['belt'  , 'bow'        , 'cloak'      , 'gloves'     , 'rod'       , 'spat'      , 'sword'      , 'tear'     , 'vest']

items = [['warmogs'   ,'zzrot'       ,'zephyr'     ,'trap claw'   ,'morello'    ,'protector'  ,'zeke'        ,'redemption','red buff'],
         ['zzrot'     ,'rfc'         ,'runaan'     ,'last whisper','guinsoo'    ,'infiltrator','giant slayer','stattik'   ,'titan'],
         ['zephyr'    , 'runaan'     ,'dragon claw','quicksilver' ,'ionic spark','celestial'  ,'bt'          ,'chalice'   ,'disarm'],
         ['trap claw' ,'last whisper','quicksilver','thief gloves','gauntlet'   ,'dark star'  ,'ie'          ,'justice'   ,'shroud'],
         ['morello'   ,'guinsoo'     ,'ionic spark','gauntlet'    ,'dcap'       ,'demolition' ,'gunblade'    ,'ludens'    ,'locket'],
         ['protector' ,'infiltrator' ,'celestial'  ,'dark star'   ,'demolition' ,'fon'        ,'blademaster' ,'star guard','rebel'],
         ['zeke'      ,'giant slayer','bt'         ,'ie'          ,'gunblade'   ,'blademaster','deathblade'  ,'shojin'    ,'ga'],
         ['redemption','stattik'     ,'chalice'    ,'justice'     ,'ludens'     ,'star guard' ,'shojin'      ,'seraph'    ,'fh'],
         ['red buff'  ,'titan'       ,'disarm'     ,'shroud'      ,'locket'     ,'rebel'      ,'ga'          ,'fh'        ,'thorn']]

def combineItems(item1,item2):
    assert item1 in components and item2 in components, "both items must be components"
    return items[components.index(item1)-1][components.index(item2)-1]

def isItem(item):
    if(item in components):
        return True
    for row in items:
        if(item in row):
            return True
    return False