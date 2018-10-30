from heatmap_input_info import *

import sys
sys.path.insert(0, '../enrich')
from convert_country_names import *

class HeatmapNameInterpretor:
    @classmethod
    def GetFilenameFromInputInfo(self, inputInfo):
        #statStr = stat_filenames[inputInfo.stat]
        teams = list(inputInfo.teams)
        if teams != []:
            for i in range(len(teams)):
                teams[i] = LOOKUP_FULLNAME[teams[i]]
        teamStr = '-'.join(teams)
        
        opponents = list(inputInfo.opponents)
        if opponents != []:
            for i in range(len(opponents)):
                opponents[i] = LOOKUP_FULLNAME[opponents[i]]
        opponentsStr = '-'.join(opponents)
        
        gameStr = '-'.join(inputInfo.games)
        tournamentStr = '-'.join(inputInfo.tournaments)
        datesStr = inputInfo.dates[0].strftime("%Y.%m.%d") + "-" + \
                   inputInfo.dates[1].strftime("%Y.%m.%d")
        displayStr = str(inputInfo.playersOrTeams)
        return teamStr  + "_" + opponentsStr + "_" + gameStr  + \
               "_" + tournamentStr  + "_" + datesStr + "_heatmap"

    @classmethod
    def GetInputInfoFromFilename(self, filename):
        array = filename.split('_')

        #stat = list(stat_filenames.keys())[list(stat_filenames.values()).index(array[0])]
        teams = array[0].split('-')
        opponents = array[1].split('-')
        games = array[2].split('-')
        if games != []:
            for i in range(len(games)):
                games[i] = int(games[i])

        tournaments = array[3].split('-')

        dates = array[4].split('-')
        if dates[0] != '': dates[0] = dates[0].replace('.', '-')
        if dates[1] != '': dates[1] = dates[1].replace('.', '-')
        
        return HeatmapInputInfo(teams, opponents, games, tournaments,
                                dates, display)


if __name__== '__main__':

    inputInfo = HeatmapInputInfo(['CAN'],
                                 ['ISV'],
                                 [],
                                 ['2019 WorldCup Americas Qualifiers'],
                                 ['2018-01-01', ''],
                                 PlayersOrTeams.Both.value)

    inputInfo.PrintSelf()
    a = HeatmapNameInterpretor.GetFilenameFromInputInfo(inputInfo)
    print("\nFilename: ", a)
    HeatmapNameInterpretor.GetInputInfoFromFilename(a).PrintSelf()


    inputInfo = HeatmapInputInfo()
    inputInfo.PrintSelf()
