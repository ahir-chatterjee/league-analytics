# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 21:22:15 2019

@author: ahirc
"""

import xlsxwriter
import riotapicalls
import opggcalls
import createScoutingReport


def main():
    while (True):
        cmd = input("Enter command (use \"help\" for a list of commands): ")
        cmds = cmd.split()
        if (cmds[0] == "break"):
            break
        else:
            handleCmd(cmds)


def handleCmd(cmds):
    cmd = cmds[0].lower()  # main command
    cmdList = [["help"],
               ["opggScout", "teamName", "opgg"],
               ["namesFromOpgg", "opgg"],
               ["downloadRankedGames", "[name1,name2,...,nameN]"]]  # a list of all the commands supported
    if (cmd == "help"):
        # print out all of the commands from cmdList and their arguments (if any)
        print("Here is a list of commands and their parameters that they take:")
        for c in cmdList:
            if (len(c) == 1):  # takes no parameters
                print(c[0])
            else:
                print(c[0] + ":", end=' ')
                for i in range(1, len(c)):
                    if (i == len(c) - 1):
                        print(c[i])
                    else:
                        print(c[i], end=', ')
    elif (cmd == "opggscout"):
        # creates a scouting report from the given opgg. see opggcalls.opggScout for more details
        if (len(cmds) != 3):
            invalidParameterLength(3, len(cmds))
        else:
            team_name = cmds[1]
            opgglink = cmds[2]
            report_dict = createScoutingReport.createScoutingReport(team_name, opgglink)
            build_excel_sheet(report_dict, team_name)

    elif (cmd == "namesfromopgg"):
        # grabs all of the summoner names from a given opgg. see opggcalls.getNamesFromOpgg
        if (len(cmds) != 2):
            invalidParameterLength(2, len(cmds))
        else:
            print(opggcalls.createMultiFromNames(cmds[1]))
    elif (cmd == "downloadrankedgames"):
        # downloads the ranked games from the supplied names
        if (len(cmds) == 1):
            invalidParameterLength("any number of", len(cmds))
        else:
            for i in range(1, len(cmds)):
                name = cmds[i]
                account = riotapicalls.getAccountByName(name)
                riotapicalls.getAllRankedMatchesByAccount(
                    account)  # saves them into a file called name.txt, with a "version" of the season
    else:
        print("Command not recognized. Try \"help\" for a list of recognized commands.")


def invalidParameterLength(expected, actual):
    print("Expected " + (str)(expected) + " parameters, receieved " + (str)(actual - 1) + " parameters.")


def build_excel_sheet(scouting_dict, team_name=''):
    example = {'players': {'Hamski': {'recent': {'lanes': {}}, 'aggregate': {'lanes': {}}, 'champPool': []},
                           'CrusherCake': {'recent': {'lanes': {}}, 'aggregate': {'lanes': {}}, 'champPool': []}
                           }}
    scout_book = xlsxwriter.Workbook('ScoutInfo' + team_name + '.xlsx')
    for player_name, scout_info in scouting_dict['players'].items():
        curr_player_sheet = scout_book.add_worksheet(player_name)
        set_sheet_titles(curr_player_sheet, player_name)
        for i in range(1, len(scout_info[player_name]['champPool'])):
            curr_player_sheet.write(i, 0, scout_info[player_name]['champPool'][i])
        for i in range(1, len(scout_info[player_name]['recent']['lanes'].values())):
            curr_player_sheet.write(i, 1, scout_info[player_name]['recent']['lanes'].values()[i])
        for i in range(1, len(scout_info[player_name]['aggregate']['lanes'].values())):
            curr_player_sheet.write(i, 2, scout_info[player_name]['aggregate']['lanes'].values()[i])
    scout_book.close()


def set_sheet_titles(sheet, player_name):
    sheet.write(0, 0, 'Champ Pool')
    sheet.write(0, 1, 'Recent Lanes')
    sheet.write(0, 2, 'Aggregate Lanes')
    sheet.write(0, 4, 'Player: ' + player_name)


if __name__ == '__main__':
    main()
