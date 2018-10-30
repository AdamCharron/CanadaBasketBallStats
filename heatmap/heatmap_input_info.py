import re
import sys
from enum import Enum
from datetime import *

sys.path.insert(0, '../enrich')
from convert_country_names import *
from parse_to_yaml import *


class PlayersOrTeams(Enum):
    Players = 0
    Teams = 1
    Both = 2

class HeatmapInputInfo:
    def __init__(self, teams = [], opponents = [],
                 games = [], tournaments = [], dates = ['', ''],
                 playersOrTeams = PlayersOrTeams.Both.value):
        self.teams = teams
        self.opponents = opponents 
        self.games = games
        self.tournaments = tournaments
        self.dates = dates
        self.playersOrTeams = playersOrTeams

        self.defaultStartDate = '1900-01-01'
        self.defaultEndDate = '2200-01-01'

        self.dataPath = '../data'
        self.pickleParser = PickleParser(self.dataPath, False)
        self.GetGameIDPickle()
        
        self.teamGameDict = self.GetGamesPerTeam()

    def GetGameIDPickle(self):
        # Check to see if GameIDs is populated. If not, re-serialize
        # Load results into self.p
        self.p = self.pickleParser.LoadPickle('GameIDs.pickle')
        if self.p == {}:
            self.pickleParser.Serialize('GameIDs.csv')
            self.pickleParser.SaveTypesToPickles(CSVTypes.Enriched.value)
            self.p = self.pickleParser.LoadPickle('GameIDs.pickle')

    def GetValidTeams(self, teamList):
        # If no country was selected, select all
        # Also handle countries that are listed, but never in any games
        if len(teamList) == 0:
            teamList = list(LOOKUP_ABBREV.keys())
            for t in NOT_IN_GAMES_ABBREV:
                teamList.remove(t)
        return list(map(lambda x: LOOKUP_ABBREV[x], teamList))

    def GetValidDates(self):
        # Add in date range
        if not isinstance(self.dates, list) or len(self.dates) != 2 or \
           not isinstance(self.dates[0], str) or \
           not isinstance(self.dates[0], str):
            raise ValueError("Invalid date format. Needs to be in two element array")
            return
        if (self.dates[0] in ['', None]): self.dates[0] = self.defaultStartDate
        if (self.dates[1] in ['', None]): self.dates[1] = self.defaultEndDate
        if (self.dates != []):
            startDate = self.ConvertToDate(self.dates[0])
            endDate = self.ConvertToDate(self.dates[1])
            if (startDate == None or endDate == None):
                raise ValueError("Invalid date format. Needs to be YYYY-MM-DD")
                return
            elif (startDate > endDate):
                raise ValueError("Start date must be before end date")
                return
        self.dates = [self.ConvertToDate(self.dates[0]),
                      self.ConvertToDate(self.dates[1])]

    def GetValidDisplay(self):
        # Manage playersOrTeams
        self.playersOrTeams = max(min(self.playersOrTeams, 2), 0)
        self.showPlayers = self.DisplaysPlayers(self.playersOrTeams)
        self.showTeams = self.DisplaysTeams(self.playersOrTeams)

    def GetValidGames(self):
        # Pick all games that are within the dates, in the tournaments,
        # and part of the selected subset of games. For each criteria,
        # if they are empty, select all applicable
        temp_g = []
        
        for game, value in self.p.items():
            gameDate = self.ConvertToDate(value['Date'].replace('/', '-'))
            if ((self.games == [] or int(game) in self.games) and \
                (self.tournaments == [] or value['Tournament'] in self.tournaments) and \
                (self.dates == [] or (self.dates[0] <= gameDate and gameDate <= self.dates[1])) and \
                (value['Home Team'] in self.teams or value['Away Team'] in self.teams) and \
                (value['Home Team'] in self.opponents or value['Away Team'] in self.opponents)):
                temp_g.append(int(game))
        self.games = list(set(temp_g))
        
        # Sort the list to have a final clean list of str games (for easy indexing)
        self.games.sort()
        self.games = list(map(lambda x: str(x), self.games))

    def GetGamesPerTeam(self):
        self.teams = self.GetValidTeams(self.teams)
        self.opponents = self.GetValidTeams(self.opponents)
        self.GetValidDates()
        self.GetValidDisplay()
        self.GetValidGames()

        tempDict = {}
        for team in self.teams:
            tempDict[team] = self.games
        return tempDict

    def ConvertToDate(self, date):
        if re.search('\d\d\d\d-\d\d-\d\d', date) == None: return None
        dateArray = date.split('-')
        if (int(dateArray[0]) <= 0 or int(dateArray[0]) >= 3000): return None
        if (int(dateArray[1]) < 1 or int(dateArray[1]) > 12): return None
        if (int(dateArray[2]) < 1 or int(dateArray[2]) > 31): return None
        return datetime.strptime(date, '%Y-%m-%d').date()

    def DisplaysPlayers(self, playersOrTeams):
        return playersOrTeams != 1

    def DisplaysTeams(self, playersOrTeams):
        return playersOrTeams != 0

    def PrintSelf(self):
        print("\nPrinting Self: ")
        print("Teams:        ", self.teams)
        print("Opponents:    ", self.opponents)
        print("Games:        ", self.games)
        print("Tournaments:  ", self.tournaments)
        print("Dates:        ", self.dates)
        print("Display:      ", self.playersOrTeams)
        #print("TeamGameDict: ", self.teamGameDict)


if __name__=='__main__':
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

    for inputInfo in inputInfoList:
        inputInfo.PrintSelf()
