import csv
import os
import pickle
import re
from pprint import pprint
from stat_type_lookups import *
from logger import *
from datetime import *
from heatmap_input_info import *
from heatmap_name_interpretor import *
from stat_classes import *

import sys
sys.path.insert(0, '../enrich')
from parse_to_yaml import *
from enrich_CSVs import *


class HeatmapGenerator:
    def __init__(self, inputInfoList = [HeatmapInputInfo()]):
        self.inputInfoList = inputInfoList
        
        self.data_path = '../data'
        self.pickleParser = PickleParser(self.data_path, False)

        # Delete old pickles
        self.pickleParser.RemovePicklesOfType(CSVTypes.Heatmap.value, '.csv')
        self.pickleParser.RemovePicklesOfType(CSVTypes.Heatmap.value, '.pickle')

        # Load pickles
        self.pg = self.pickleParser.LoadPickle(os.path.join(self.data_path, 'GameIDs.pickle'))
        self.ep = self.GetEnrichedPlayByPlay()

        self.Generate()
        self.SaveResults()

    def Generate(self):
        
        for inputInfo in self.inputInfoList:
            teams_checked = []
            filename = HeatmapNameInterpretor.GetFilenameFromInputInfo(inputInfo)
            self.InitOutputStatFiles(filename)

            for teamname in inputInfo.teams:
                team = Team(teamname)
                team.roster['TOTAL'].games_played = inputInfo.games
                for game in inputInfo.games:
                    team.roster['TOTAL'].ResetStatTimes()
                    activeTeams = [self.pg[str(game)]['Home Team'],
                                   self.pg[str(game)]['Away Team']]
                    # Make sure they're not the same team
                    if activeTeams[0] == activeTeams[1]: continue

                    away_offset = 0
                    if team.team == activeTeams[1]: away_offset = 5

                    last_sub_event_time = -1
                    for event in self.ep[str(game)]:
                        if int(event[PlayByPlayHeader.Quarter.value]) not in range(5): continue

                        if get_minute(event[PlayByPlayHeader.Time.value]) + \
                           (int(event[PlayByPlayHeader.Quarter.value])-1)*10 > \
                           last_sub_event_time:
                            last_sub_event_time = get_minute(event[PlayByPlayHeader.Time.value]) + \
                                                  (int(event[PlayByPlayHeader.Quarter.value])-1)*10

                            # Go through each player on the court, create player object for them
                            # and add them to team roster
                            team.roster['TOTAL'].Minutes.add_dist(event[PlayByPlayHeader.Quarter.value],
                                                                               event[PlayByPlayHeader.Time.value])
                            for player_idx in range(PlayByPlayHeader.HomePlayer1.value + away_offset,
                                                    PlayByPlayHeader.HomePlayer5.value + 1 + away_offset):
                                if not team.check_player(event[player_idx]):
                                    p = Player(event[player_idx], teamname)
                                    p.Minutes.add_dist(event[PlayByPlayHeader.Quarter.value],
                                                  event[PlayByPlayHeader.Time.value])
                                    p.games_played.append(game)
                                    team.add_player(p)
                                else:
                                    if game not in team.roster[event[player_idx]].games_played:
                                        team.roster[event[player_idx]].games_played.append(game)
                                    team.roster[event[player_idx]].Minutes.add_dist(event[PlayByPlayHeader.Quarter.value],
                                                                               event[PlayByPlayHeader.Time.value])

                        if event[PlayByPlayHeader.Player.value] in team.roster:
                            #team.roster[event[PlayByPlayHeader.Player.value]].Minutes.update()
                            team.roster[event[PlayByPlayHeader.Player.value]].Points.update(event)
                            team.roster[event[PlayByPlayHeader.Player.value]].Turnovers.update(event)
                            team.roster[event[PlayByPlayHeader.Player.value]].Rebounds.update(event)
                            team.roster[event[PlayByPlayHeader.Player.value]].Fouls.update(event)
                            team.roster[event[PlayByPlayHeader.Player.value]].Shots.update(event)
                            team.roster[event[PlayByPlayHeader.Player.value]].ThreePointers.update(event)
                            team.roster['TOTAL'].Points.update(event)
                            team.roster['TOTAL'].Turnovers.update(event)
                            team.roster['TOTAL'].Rebounds.update(event)
                            team.roster['TOTAL'].Fouls.update(event)
                            team.roster['TOTAL'].Shots.update(event)
                            team.roster['TOTAL'].ThreePointers.update(event)

                team.normalize_stats()
                team.write_results(self.data_path, filename)

    def InitOutputStatFiles(self, basename):
        for statname in stat_filenames.values():
            filename = os.path.join(self.data_path, statname + "_" + basename + ".csv")
            if os.path.exists(filename): os.remove(filename)
            with open(filename, 'w') as f:
                # Title (keys)
                title_str = 'Team,Player'
                for i in range(1,5):
                    for j in range(1,11):
                        title_str += ',Q'+str(i)+'-'+str(j)
                f.write(title_str)

    def GetEnrichedPlayByPlay(self):
        # Check to see if enriched play by play is populated
        # If not, re-serialize
        # Load results into self.p
        p = self.pickleParser.LoadPickle('PlayByPlay_enriched.pickle')
        if p == {}:
            self.pickleParser.SaveTypesToPickles(CSVTypes.Enriched.value)
            p = self.pickleParser.LoadPickle('PlayByPlay_enriched.pickle')
        return p

    def SaveResults(self):
        # Save new pickle 
        self.pickleParser.SaveTypesToPickles(CSVTypes.Heatmap.value)

        # Save results in logger file
        #newLogger = Logger(teams, games)
        #newLogger.print_current_logger()
        #newLogger.dump_logger()
        

    # Helper functions
    
    def ConvertToDate(self, date):
        if re.search('\d\d\d\d-\d\d-\d\d', date) == None: return None
        dateArray = date.split('-')
        if (int(dateArray[0]) <= 0 or int(dateArray[0]) >= 3000): return None
        if (int(dateArray[1]) < 1 or int(dateArray[1]) > 12): return None
        if (int(dateArray[2]) < 1 or int(dateArray[2]) > 31): return None
        return datetime.strptime(date, '%Y-%m-%d').date()


if __name__== '__main__':

    # HeatmapInputInfo(stat to generate
    #                   list of teams (default all),
    #                   list of opponent teams (default all),
    #                   list of games (default all),
    #                   list of tournaments (default all),
    #                   date bounds [start, end] (default all),
    #                   players and/or teams enum (default all))

    '''
    inputInfoList = [HeatmapInputInfo(['CAN'],
                                      ['ISV'],
                                      [],
                                      ['2019 WorldCup Americas Qualifiers'],
                                      ['2018-01-01', ''],
                                      PlayersOrTeams.Both.value),
                     HeatmapInputInfo(['USA', 'PUR'],
                                      ['CUB'],
                                      [],
                                      ['2019 WorldCup Americas Qualifiers'],
                                      ['', ''],
                                      PlayersOrTeams.Both.value)
                     ]

    # Canada [496, 522]
    # USA, Puerto Rico [491, 503, 512, 518]
    for inputInfo in inputInfoList:
        print(inputInfo.stat)
        print(inputInfo.teamGameDict)
        print(inputInfo.teams)
        print(inputInfo.games)
        print(inputInfo.tournaments)
        print(inputInfo.dates)
        print(inputInfo.playersOrTeams)
    '''
    

    inputInfoList = [HeatmapInputInfo(['CAN'],
                                      ['ISV'],
                                      [],
                                      ['2019 WorldCup Americas Qualifiers'],
                                      ['2018-01-01', ''],
                                      PlayersOrTeams.Both.value)]

    #main_heatmap(inputInfoList)
    HeatmapGenerator(inputInfoList)
    inputInfoList[0].PrintSelf()

