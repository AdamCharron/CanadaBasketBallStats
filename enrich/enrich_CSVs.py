import os
import sys
sys.path.insert(0, '../tests')
from pprint import pprint
from enum import Enum
from convert_country_names import *
from parse_to_yaml import *
from tester import *
from time import sleep

class PlayByPlayPickle(Enum):
    # For Play-By-Play pickle
    #p_GAME_ID = '0'
    p_QUARTER = 0
    p_TIME = 1
    p_HOME_SCORE = 2
    p_AWAY_SCORE = 3
    p_TEAM = 4
    p_NUMBER = 5
    p_PLAYER = 6
    p_EVENT = 7

'''
class GameIDPickle(Enum):
    # For GameID pickle
    pg_GAME_ID = 0
    pg_TOURNAMENT = 1
    pg_DATE = 2
    pg_ROUND = 3
    pg_LOCATION = 4
    pg_HOME_TEAM = 5
    pg_AWAY_TEAM = 6
    pg_HOME_FINAL_SCORE = 7
    pg_AWAY_FINAL_SCORE = 8
'''

class OutFileHandler:
    def __init__(self, filename):
        self.out_filename = filename
        self.out_file = open(self.out_filename,'w')
        self.Write('Game ID,Quarter,Time,Home Score,Away Score,Team,Number,Player,Event,Players on Court,HomePlayer1,HomePlayer2,HomePlayer3,HomePlayer4,HomePlayer5,AwayPlayer1,AwayPlayer2,AwayPlayer3,AwayPlayer4,AwayPlayer5,HomePlayerTimeON1,HomePlayerTimeON2,HomePlayerTimeON3,HomePlayerTimeON4,HomePlayerTimeON5,AwayPlayerTimeON1,AwayPlayerTimeON2,AwayPlayerTimeON3,AwayPlayerTimeON4,AwayPlayerTimeON5,Home Team Name, Away Team Name')

    def Write(self, inputObj):
        self.out_file.write(str(inputObj) + '\n')

    def Close(self):
        self.out_file.close()
        

class CSVEnricher:
    def __init__(self):
        self.__root_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.__gameID_pickle_file = os.path.join(self.__root_dir, "GameIDs.pickle")
        self.__playbyplay_pickle_file = os.path.join(self.__root_dir, "PlayByPlay.pickle")
        self.__gameID_csv_file = os.path.join(self.__root_dir, "GameIDs.csv")
        self.__playbyplay_csv_file = os.path.join(self.__root_dir, "PlayByPlay.csv")
        self.__out_filename = os.path.splitext(self.__playbyplay_pickle_file)[0] + '_enriched.csv'        
        self.__out_picklename = os.path.splitext(self.__playbyplay_pickle_file)[0] + '_enriched.pickle'
        self.__out_filename_game_template = self.__out_filename.replace('.csv', '_game')

        self.home_game_log = []
        self.away_game_log = []
        self.home_on_court = []
        self.away_on_court = []
        self.event_num = 0

        self.__pickleParser = PickleParser(self.__root_dir)
        self.Enrich()

    def SetUpFiles(self):
        # Delete old pickle for enriched CSV
        self.__pickleParser.RemovePicklesOfType(CSVTypes.Enriched.value, '.csv')
        self.__pickleParser.RemovePicklesOfType(CSVTypes.Enriched.value, '.pickle')
        self.__pickleParser.RemovePicklesOfType(CSVTypes.Heatmap.value, '.csv')
        self.__pickleParser.RemovePicklesOfType(CSVTypes.Heatmap.value, '.pickle')

        # Create prerequisite pickles (GameIDs and PlayByPlay) before starting
        if not os.path.isfile(self.__gameID_pickle_file): self.__pickleParser.Serialize(self.__gameID_csv_file)
        if not os.path.isfile(self.__playbyplay_pickle_file): self.__pickleParser.Serialize(self.__playbyplay_csv_file)
        
        self.pg = self.__pickleParser.LoadPickle(self.__gameID_pickle_file)
        self.p = self.__pickleParser.LoadPickle(self.__playbyplay_pickle_file)

        self.outFileHandler = OutFileHandler(self.__out_filename)

    def GetReleventGames(self):
        games = []
        # Only started tracking substitutions in game 118
        for key, value in self.p.items():
            for j in range(len(value)):
                if "Substitution" in value[j][int(PlayByPlayPickle.p_EVENT.value)]:
                    games.append(int(key))
                    break
        return sorted(games)

    def GetHomeAway(self, game):
        home_team = self.pg[str(game)]['Home Team']
        away_team = self.pg[str(game)]['Away Team']
        return home_team, away_team

    def ConvertTime(self, time):
        time = time.split(":")
        return int(time[0])*60 + int(time[1])

    def SubstitutionIn(self, event, on_court):
        if event[PlayByPlayPickle.p_PLAYER.value] not in list(map(lambda x: x[0], on_court)):
            on_court.append(list([event[PlayByPlayPickle.p_PLAYER.value], int(event[PlayByPlayPickle.p_QUARTER.value]), event[PlayByPlayPickle.p_TIME.value]]))
        
    def SubstitutionOut(self, event, on_court):
        prev_key = []
        to_remove = None
        for i in range(len(on_court)):
            # Assuming that no issues happen and no multiple subs in or out of the same player at once
            if on_court[i][0] == event[PlayByPlayPickle.p_PLAYER.value]:
                if prev_key == []:
                    prev_key = on_court[i][1:]
                    to_remove = i
                elif prev_key[0] < int(event[PlayByPlayPickle.p_QUARTER.value]):
                    on_court.pop(i)
                elif prev_key[0] == int(event[PlayByPlayPickle.p_QUARTER.value]) and convert_time(prev_key[1]) > convert_time(event[PlayByPlayPickle.p_TIME.value]):
                    on_court.pop(i)
        if to_remove != None:
            on_court.pop(to_remove)

    def InferredSubstitution(self, event, on_court):
        if len(event[PlayByPlayPickle.p_PLAYER.value]) == 0: return
        if event[PlayByPlayPickle.p_PLAYER.value] not in list(map(lambda x: x[0], on_court)):
            on_court.append(list([event[PlayByPlayPickle.p_PLAYER.value], int(event[PlayByPlayPickle.p_QUARTER.value]), event[PlayByPlayPickle.p_TIME.value]]))

    def WriteEventOutput(self, game, event_num, home_on_court, away_on_court, home_team, away_team):
        on_court_list = ['']*23
        player_count = 1
        on_court_list[0] = str(len(home_on_court)+ len(away_on_court))
        on_court_list[21] = home_team
        on_court_list[22] = away_team
        if (len(home_on_court) == 5 and len(away_on_court) == 5):
            for player in home_on_court:
                on_court_list[player_count] = player[0]
                on_court_list[player_count+10] = str(player[1]) + '-' + player[2]
                player_count += 1
            for player in away_on_court:
                on_court_list[player_count] = player[0]
                on_court_list[player_count+10] = str(player[1]) + '-' + player[2]
                player_count += 1
            out_str = self.p[str(game)][event_num] + on_court_list
            self.outFileHandler.Write(str(game) + ',' + ','.join(out_str))
            self.gameOutFileHandler.Write(str(game) + ',' + ','.join(out_str))
        
    def Enrich(self):
        self.SetUpFiles()
        self.releventGames = self.GetReleventGames()        
        for game in self.releventGames:
            home_team, away_team = self.GetHomeAway(game)
            if home_team == "" or away_team == "":
                print("UNEXPECTED ISSUE ENCOUNTERED: Missing team names in a game")
                continue

            gameFileName = self.__out_filename_game_template + str(game) + '.csv'
            self.gameOutFileHandler = OutFileHandler(gameFileName)
            
            home_on_court = []
            away_on_court = []
            event_num = 0

            for event in self.p[str(game)]:
                if event[PlayByPlayPickle.p_EVENT.value] == "Substitution in":
                    if event[PlayByPlayPickle.p_TEAM.value] == home_team:
                        self.SubstitutionIn(event, home_on_court)
                    else:
                        self.SubstitutionIn(event, away_on_court)
                elif event[PlayByPlayPickle.p_EVENT.value] == "Substitution out":
                    if event[PlayByPlayPickle.p_TEAM.value] == home_team:
                        self.SubstitutionOut(event, home_on_court)
                    else:
                        self.SubstitutionOut(event, away_on_court)
                        

                # For events that are not substitution, but contain players who aren't in the lineup
                # Only dealing with when < 10 players on the court now
                elif len(home_on_court)+ len(away_on_court) < 10:
                    if event[PlayByPlayPickle.p_TEAM.value] == home_team:
                        self.InferredSubstitution(event, home_on_court)
                    if event[PlayByPlayPickle.p_TEAM.value] == away_team:
                        self.InferredSubstitution(event, away_on_court)

                self.WriteEventOutput(game, event_num, home_on_court, away_on_court, home_team, away_team)
                event_num += 1

            # Close game file handler, and create pickle
            self.gameOutFileHandler.Close()
            self.__pickleParser.Serialize(gameFileName)

        # Create pickle
        self.outFileHandler.Close()
        self.__pickleParser.Serialize(self.__out_filename)
        
    
if __name__=='__main__':

    CSVEnricher()

    #################################################################
    ######################### Tests + demos #########################
    #################################################################
    t = Tester()
    pickleParser = PickleParser('../data')

    # Load empty pickle
    emptyGames = {}
    allPickleResults = pickleParser.LoadPickle('PlayByPlay_enriched.pickle')
    t.Assert("Non-empty all Enrich CSV results", allPickleResults != {})
    for gameF in pickleParser.GetAllEnrichedFiles()[1:]:        
        game = os.path.basename(gameF).replace('PlayByPlay_enriched_game', '').replace('.csv', '')
        gameFile = gameF.replace('.csv', '.pickle')
        gamePickleResults = pickleParser.LoadPickle(gameFile)

        # Catch blank games (invalid substitution numbers from website)
        missingFromAll = game not in allPickleResults.keys()
        missingFromLocal = game not in gamePickleResults.keys()
        if not missingFromAll and not missingFromLocal:
            t.Assert("Game {} CSV matches all Enrich".format(game),
                     game in allPickleResults.keys() and
                     game in gamePickleResults.keys() and
                     allPickleResults[game] == gamePickleResults[game])
        else:
            emptyGames[game] = [missingFromAll, missingFromLocal]

    print('\n')
    t.ShowResults()

    if emptyGames != {}:
        print('\nSome enriched files for games were empty.' + \
              'This implies no points with 5 players on the court for both' + \
              'teams from the info pulled from FIBA\'s website:')
        for k, v in emptyGames.items():
            if v == [True, True]: print("Game {} was in neither enriched csv".format(k))
            elif v == [True, False]: print("Game {} was not in full enriched play-by-play csv".format(k))
            elif v == [False, True]: print("Game {} was not in enriched play-by-play csv for only that game".format(k))
        
    #################################################################
    #################################################################

