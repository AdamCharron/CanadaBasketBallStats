import csv
import os
import pickle
import re
from pprint import pprint
from stat_type_lookups import *
from REFORMATTING_logger import *
from datetime import *
from HeatmapInputInfo import *

import sys
sys.path.insert(0, '../enrich')
from convert_country_names import *
from parse_to_yaml import *
from enrich_CSVs import *


# For Play-By-Play pickle
class PlayByPlayHeader(Enum):
    Quarter = 0
    Time = 1
    HomeScore = 2
    AwayScore = 3
    Team = 4
    Number = 5
    Player = 6
    Event = 7
    PlayersOnCourt = 8
    HomePlayer1 = 9
    HomePlayer2 = 10
    HomePlayer3 = 11
    HomePlayer4 = 12
    HomePlayer5 = 13
    AwayPlayer1 = 14
    AwayPlayer2 = 15
    AwayPlayer3 = 16
    AwayPlayer4 = 17
    AwayPlayer5 = 18
    HomePlayerTimeOn1 = 19
    HomePlayerTimeOn2 = 20
    HomePlayerTimeOn3 = 21
    HomePlayerTimeOn4 = 22
    HomePlayerTimeOn5 = 23
    AwayPlayerTimeOn1 = 24
    AwayPlayerTimeOn2 = 25
    AwayPlayerTimeOn3 = 26
    AwayPlayerTimeOn4 = 27
    AwayPlayerTimeOn5 = 28
    HomeTeamName = 29
    AwayTeamName = 30

'''
class GameIDHeader(Enum):
    GameID = 0
    Tournament = 1
    Date = 2
    Round = 3
    Location = 4
    HomeTeam = 5
    AwayTeam = 6
    HomeFinalScore = 7
    AwayFinalScore = 8
'''

# Paths
data_path = '../data'
gameid_pickle_file = os.path.join(data_path, 'GameIDs.pickle')
enriched_playbyplay_pickle_file = os.path.join(data_path, 'PlayByPlay_enriched.pickle')
heatmap_pickle = os.path.join(data_path, 'minutes_heatmap.pickle')


class Player:
    def __init__(self, name, team):
        self.name = name
        self.team = team
        self.games_played = []

        # All data provided in the following logs used 10-minute quarters
        # Except for minute, logs are broken up into:
        #   x_log -> cumulative occurrences of x across timeslots of all games
        #   x_dist_log -> games in which x occurs in each timeslot
        #   ie if a player gets 2 layups in Q2 min:3,
        #       point_log[Q,M] += 4 and point_dist_log[Q,M] += 1
        self.minute_log = [0]*4*10  
        self.point_log = [0]*4*10
        self.turnover_log = [0]*4*10
        self.rebound_log = [0]*4*10
        self.block_log = [0]*4*10
        self.foul_log = [0]*4*10
        self.shot_log = [0]*4*10
        self.three_pointer_log = [0]*4*10
        self.point_dist_log = [0]*4*10
        self.turnover_dist_log = [0]*4*10
        self.rebound_dist_log = [0]*4*10
        self.block_dist_log = [0]*4*10
        self.foul_dist_log = [0]*4*10
        self.shot_dist_log = [0]*4*10
        self.three_pointer_dist_log = [0]*4*10

    # Cumulative - total stats in each minute
    def add_points(self, quarter, minute, points):
        # Increment player's point total for that minute
        self.point_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += points

    def add_turnovers(self, quarter, minute):
        # Increment player's turnover total for that minute
        self.turnover_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_rebounds(self, quarter, minute):
        # Increment player's rebound total for that minute
        self.rebound_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_block(self, quarter, minute):
        # Increment player's block total for that minute
        self.block_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_foul(self, quarter, minute):
        # Increment player's foul total for that minute
        self.foul_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_shot_attempts(self, quarter, minute):
        # Increment player's shot attempt total for that minute
        self.shot_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_3_pointers(self, quarter, minute):
        # Increment player's 3 pointer total for that minute
        self.three_pointer_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1


    # Dist - for occurrence of a stat type in each minute
    def add_minutes(self, quarter, minute):
        # Increment player's presence on the court for that minute
        self.minute_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_dist_points(self, quarter, minute):
        # Increment player's point total for that minute
        self.point_dist_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_dist_turnovers(self, quarter, minute):
        # Increment player's turnover total for that minute
        self.turnover_dist_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_dist_rebounds(self, quarter, minute):
        # Increment player's rebound total for that minute
        self.rebound_dist_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_dist_block(self, quarter, minute):
        # Increment player's block total for that minute
        self.block_dist_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_dist_foul(self, quarter, minute):
        # Increment player's foul total for that minute
        self.foul_dist_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_dist_shot_attempts(self, quarter, minute):
        # Increment player's shot attempt total for that minute
        self.shot_dist_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1

    def add_dist_3_pointers(self, quarter, minute):
        # Increment player's 3 pointer total for that minute
        self.three_pointer_dist_log[get_minute(minute) - 1 + 10*(int(quarter)-1)] += 1


class Team:
    def __init__(self, team):
        self.team = team
        self.roster = {}

    def check_player(self, name):
        return name in self.roster

    def add_player(self, player):
        if not self.check_player(player.name):
            self.roster[player.name] = player
        #else:
        #    print('Invalid! ' + name + ' already on the team')

    def normalize_stats(self):
        for player in self.roster:
            if self.roster[player].games_played == []: return 
            for entry in range(len(self.roster[player].minute_log)):
                self.roster[player].minute_log[entry] /= len(self.roster[player].games_played)
                self.roster[player].point_dist_log[entry] /= len(self.roster[player].games_played)
                self.roster[player].turnover_dist_log[entry] /= len(self.roster[player].games_played)
                self.roster[player].rebound_dist_log[entry] /= len(self.roster[player].games_played)
                self.roster[player].block_dist_log[entry] /= len(self.roster[player].games_played)
                self.roster[player].foul_dist_log[entry] /= len(self.roster[player].games_played)
                self.roster[player].shot_dist_log[entry] /= len(self.roster[player].games_played)
                self.roster[player].three_pointer_dist_log[entry] /= len(self.roster[player].games_played)


def ConvertToDate(date):
    if re.search('\d\d\d\d-\d\d-\d\d', date) == None: return None
    dateArray = date.split('-')
    if (int(dateArray[0]) <= 0 or int(dateArray[0]) >= 3000): return None
    if (int(dateArray[1]) < 1 or int(dateArray[1]) > 12): return None
    if (int(dateArray[2]) < 1 or int(dateArray[2]) > 31): return None
    return datetime.strptime(date, '%Y-%m-%d').date()

            
def get_minute(time):
    if re.search('\d\d?:\d\d', time) == None: return None
    minute = int(re.sub(':\d\d', '', time))
    if minute > 10 or minute < 0: return None
    if minute == 10: return 1
    return 10 - minute


def get_countrys_games(team, ep, pg):

    # Find all candidate games in which the team plays (as home or away)
    candidate_games = []
    for game, info in pg.items():
        #if LOOKUP_ABBREV[team] == info['Home Team'] or LOOKUP_ABBREV[team] == info['Away Team']:
        if team == info['Home Team'] or team == info['Away Team']:
            candidate_games.append(int(game))
    
    # Find all games (of the candidate ones) with enriched info (valid substitutions)
    games = []
    for game in candidate_games:
        if str(game) in ep.keys():
            games.append(int(game))

    print(team)
    print(sorted(games))
    return sorted(games)


def init_output_stats():
    # Write the heatmap to a CSV
    for filename in list(stat_filenames.values()):
        output_file = os.path.join(data_path, filename + "_heatmap.csv")
        f = open(output_file, 'w')

        # Title (keys)
        title_str = 'Team,Player'
        for i in range(1,5):
            for j in range(1,11):
                title_str += ',Q'+str(i)+'-'+str(j)
        f.write(title_str)
        f.close()


def output_stats(team):
    # Write the heatmaps for each stat to CSVs
    for flag in [True, False]:
            
        for filename in list(stat_filenames.values()):
            if flag == filename.endswith("_avg"): continue

            # Only deal with dist for minutes. No sum tracker for total minutes
            if filename == "minutes_heatmap.csv": continue

            output_file = os.path.join(data_path, filename + "_heatmap.csv")
            print("Writing to {}".format(output_file))

            f = open(output_file, 'a')
            for player in team.roster:

                # Select the log based on the file type
                log_of_interest = []
                if flag:
                    if "points" in filename: log_of_interest = team.roster[player].point_log
                    if "turnovers" in filename: log_of_interest = team.roster[player].turnover_log
                    if "rebounds" in filename: log_of_interest = team.roster[player].rebound_log
                    if "blocks" in filename: log_of_interest = team.roster[player].block_log
                    if "fouls" in filename: log_of_interest = team.roster[player].foul_log
                    if "shot_attempts" in filename: log_of_interest = team.roster[player].shot_log
                    if "three_pointers" in filename: log_of_interest = team.roster[player].three_pointer_log

                else:
                    if "minutes" in filename: log_of_interest = team.roster[player].minute_log
                    if "points" in filename: log_of_interest = team.roster[player].point_dist_log
                    if "turnovers" in filename: log_of_interest = team.roster[player].turnover_dist_log
                    if "rebounds" in filename: log_of_interest = team.roster[player].rebound_dist_log
                    if "blocks" in filename: log_of_interest = team.roster[player].block_dist_log
                    if "fouls" in filename: log_of_interest = team.roster[player].foul_dist_log
                    if "shot_attempts" in filename: log_of_interest = team.roster[player].shot_dist_log
                    if "three_pointers" in filename: log_of_interest = team.roster[player].three_pointer_dist_log

                # Fill the appropriate CSV with the contents of that log 
                out_str = '\n' + team.team + ',' + team.roster[player].name
                for m in range(len(log_of_interest)):
                    out_str += ',' + str(log_of_interest[m])
                #print(out_str)
                f.write(out_str)
            f.close()


def update_time(quarter, time, event_time):
    if get_minute(time) + (int(quarter)-1)*10 > event_time:
        event_time = get_minute(time) + (int(quarter)-1)*10
    return event_time
            

def compute_team_stats(team_list, games):
    teams_checked = []
    init_output_stats()

    # Load pickles (dumps if they are needed)
    if not os.path.isfile(gameid_pickle_file): dump(data_path, 'GameIDs.csv')
    if not os.path.isfile(enriched_playbyplay_pickle_file): dump(data_path, 'PlayByPlay_enriched.csv')

    pg = load_pickle(gameid_pickle_file)
    ep = load_pickle(enriched_playbyplay_pickle_file)

    for teamname in team_list:
        # Go through all teams in the inputted list
        if teamname in teams_checked: continue
        teams_checked.append(teamname)

        # Go through all games, increment players' playtime for all players
        temp_games_list = get_countrys_games(teamname, ep, pg)
        games_list = []
        for g in temp_games_list:
            if games == [] or str(g) in games:
                games_list.append(g)
                
        team = Team(teamname)
        for game in range(len(games_list)):

            # Determine if the team is home or away
            #if LOOKUP_ABBREV[teamname] == pg[str(games_list[game])]['Home Team']: away_offset = 0
            #elif LOOKUP_ABBREV[teamname] == pg[str(games_list[game])]['Away Team']: away_offset = 5
            if teamname == pg[str(games_list[game])]['Home Team']: away_offset = 0
            elif teamname == pg[str(games_list[game])]['Away Team']: away_offset = 5

            g_events = games_list[int(game)]
            last_sub_event_time = -1
            last_point_event_time = -1
            last_3pt_event_time = -1
            last_turnover_event_time = -1
            last_rebound_event_time = -1
            last_block_event_time = -1
            last_foul_event_time = -1
            last_shot_event_time = -1
            for event in ep[str(g_events)]:
                if int(event[PlayByPlayHeader.Quarter.value]) not in range(5): continue
                if get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10 > last_sub_event_time:
                    last_sub_event_time = get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10

                    # Go through each player on the court, create player object for them and add them to team roster
                    for player_idx in range(PlayByPlayHeader.HomePlayer1.value + away_offset, PlayByPlayHeader.HomePlayer5.value + 1 + away_offset):
                        if not team.check_player(event[player_idx]):
                            #print('New for ' + event[player_idx] + ' at '+ event[PlayByPlayHeader.Quarter.value] + '-' + event[PlayByPlayHeader.Time.value])
                            p = Player(event[player_idx], teamname)
                            p.add_minutes(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])
                            p.games_played.append(games_list[game])
                            team.add_player(p)
                        else:
                            #print('Updating ' + event[player_idx] + ' at '+ event[PlayByPlayHeader.Quarter.value] + '-' + event[PlayByPlayHeader.Time.value])
                            if games_list[game] not in team.roster[event[player_idx]].games_played:
                                team.roster[event[player_idx]].games_played.append(games_list[game])
                            team.roster[event[player_idx]].add_minutes(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])

                # Add occurrence of a stat type in that minute
                # Make sure that the player is in the roster first
                # (avoid blank players from team events)
                            

                # Add other stats for the player performing the event
                        
                # First see if that player is in the roster
                # If not, skip. This is designed to catch errors/blanks since
                # everyone performing an event should already be on the roster as
                # per the block directly above
                #print('[' + team.team + '] ' + event[PlayByPlayHeader.Player.value] + ' ' + str(event[PlayByPlayHeader.Player.value] in team.roster) + ' ' + event[PlayByPlayHeader.Quarter.value] + '-' + event[PlayByPlayHeader.Time.value] + ' - ' + event[PlayByPlayHeader.Event.value])
                if event[PlayByPlayHeader.Player.value] not in team.roster: continue

                # Points
                if event[PlayByPlayHeader.Event.value] in event_name_1_POINT:
                    #print('1pt: ' + event[PlayByPlayHeader.Player.value] + ' ' + event[PlayByPlayHeader.Quarter.value] + ':' + event[PlayByPlayHeader.Time.value] + ' - ' + event[PlayByPlayHeader.Event.value])
                    team.roster[event[PlayByPlayHeader.Player.value]].add_points(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value], 1)
                    if get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10 > last_point_event_time:
                        last_point_event_time = get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10
                        team.roster[event[PlayByPlayHeader.Player.value]].add_dist_points(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])
                if event[PlayByPlayHeader.Event.value] in event_name_2_POINTS:
                    #print('2pts: ' + event[PlayByPlayHeader.Player.value] + ' ' + event[PlayByPlayHeader.Quarter.value] + ':' + event[PlayByPlayHeader.Time.value] + ' - ' + event[PlayByPlayHeader.Event.value])
                    team.roster[event[PlayByPlayHeader.Player.value]].add_points(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value], 2)
                    if get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10 > last_point_event_time:
                        last_point_event_time = get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10
                        team.roster[event[PlayByPlayHeader.Player.value]].add_dist_points(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])
                if event[PlayByPlayHeader.Event.value] in event_name_3_POINTS:
                    # 3 pointers
                    #print('3pts: ' + event[PlayByPlayHeader.Player.value] + ' ' + event[PlayByPlayHeader.Quarter.value] + ':' + event[PlayByPlayHeader.Time.value] + ' - ' + event[PlayByPlayHeader.Event.value])
                    team.roster[event[PlayByPlayHeader.Player.value]].add_points(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value], 3)
                    if get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10 > last_point_event_time:
                        last_point_event_time = get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10
                        team.roster[event[PlayByPlayHeader.Player.value]].add_dist_points(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])
                    team.roster[event[PlayByPlayHeader.Player.value]].add_3_pointers(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])
                    if get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10 > last_3pt_event_time:
                        last_3pt_event_time = get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10
                        team.roster[event[PlayByPlayHeader.Player.value]].add_dist_3_pointers(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])

                # Turnovers
                if event[PlayByPlayHeader.Event.value] in event_name_TURNOVERS:
                    #print('turnover: ' + event[PlayByPlayHeader.Player.value] + ' ' + event[PlayByPlayHeader.Quarter.value] + ':' + event[PlayByPlayHeader.Time.value] + ' - ' + event[PlayByPlayHeader.Event.value])
                    team.roster[event[PlayByPlayHeader.Player.value]].add_turnovers(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])
                    if get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10 > last_turnover_event_time:
                        last_turnover_event_time = get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10
                        team.roster[event[PlayByPlayHeader.Player.value]].add_dist_turnovers(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])

                # Rebounds
                if event[PlayByPlayHeader.Event.value] in event_name_REBOUNDS:
                    #print('rebound: ' + event[PlayByPlayHeader.Player.value] + ' ' + event[PlayByPlayHeader.Quarter.value] + ':' + event[PlayByPlayHeader.Time.value] + ' - ' + event[PlayByPlayHeader.Event.value])
                    team.roster[event[PlayByPlayHeader.Player.value]].add_rebounds(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])
                    if get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10 > last_rebound_event_time:
                        last_rebound_event_time = get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10
                        team.roster[event[PlayByPlayHeader.Player.value]].add_dist_rebounds(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])

                # Blocked Shots
                if event[PlayByPlayHeader.Event.value] in event_name_BLOCK:
                    #print('block: ' + event[PlayByPlayHeader.Player.value] + ' ' + event[PlayByPlayHeader.Quarter.value] + ':' + event[PlayByPlayHeader.Time.value] + ' - ' + event[PlayByPlayHeader.Event.value])
                    team.roster[event[PlayByPlayHeader.Player.value]].add_block(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])
                    if get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10 > last_block_event_time:
                        last_block_event_time = get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10
                        team.roster[event[PlayByPlayHeader.Player.value]].add_dist_block(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])

                # Fouls
                if event[PlayByPlayHeader.Event.value] in event_name_FOUL:
                    #print('foul: ' + event[PlayByPlayHeader.Player.value] + ' ' + event[PlayByPlayHeader.Quarter.value] + ':' + event[PlayByPlayHeader.Time.value] + ' - ' + event[PlayByPlayHeader.Event.value])
                    team.roster[event[PlayByPlayHeader.Player.value]].add_foul(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])
                    if get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10 > last_foul_event_time:
                        last_foul_event_time = get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10
                        team.roster[event[PlayByPlayHeader.Player.value]].add_dist_foul(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])

                # Shot Attempts
                if event[PlayByPlayHeader.Event.value] in event_name_SHOT_ATTEMPTS:
                    #print('shot: ' + event[PlayByPlayHeader.Player.value] + ' ' + event[PlayByPlayHeader.Quarter.value] + ':' + event[PlayByPlayHeader.Time.value] + ' - ' + event[PlayByPlayHeader.Event.value])
                    team.roster[event[PlayByPlayHeader.Player.value]].add_shot_attempts(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])
                    if get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10 > last_shot_event_time:
                        last_shot_event_time = get_minute(event[PlayByPlayHeader.Time.value]) + (int(event[PlayByPlayHeader.Quarter.value])-1)*10        
                        team.roster[event[PlayByPlayHeader.Player.value]].add_dist_shot_attempts(event[PlayByPlayHeader.Quarter.value], event[PlayByPlayHeader.Time.value])

        team.normalize_stats()
        output_stats(team)


def team_stats(teamname = [], games = []):
    # Create heat maps for selected countries
    # If no team names given, do it for all
    if teamname == "" or teamname == []:
        teamname = []
        for country in LOOKUP_FULLNAME:
            teamname.append(country)
    elif isinstance(teamname, str):
        teamname = [LOOKUP_ABBREV[teamname]]
    else:
        teamname = list(map(lambda x: LOOKUP_ABBREV[x], teamname))
    #compute_team_stats(teamname)
    #print(list(map(lambda x: LOOKUP_ABBREV[x], teamname)))
    compute_team_stats(teamname, games)


def remove_stat_files():
    # Delete old pickle files for each stat
    for stat in stat_filenames:
        filename = os.path.join(data_path, stat_filenames[stat] + '_heatmap')
        if os.path.isfile(filename+'.csv'):
            print("Deleting old {} file to create new one".format(filename))
            os.remove(filename+'.csv')
        if os.path.isfile(filename+'.pickle'): os.remove(filename+'.pickle')



def GetGamesPerTeam(inputInfo):

    # If no country was selected, select all
    # Also handle countries that are listed, but never in any games
    if len(inputInfo.teams) == 0:
        teams = list(LOOKUP_ABBREV.keys())
        for t in NOT_IN_GAMES_ABBREV:
            teams.remove(t)
    if isinstance(teams, str): teams = [teams]
    teams = list(map(lambda x: LOOKUP_ABBREV[x], teams))

    


def main_heatmap(inputInfoList = HeatmapInputInfo()):


    for inputInfo in inputInfoList:
        print(inputInfo.teamGameDict)

    return


    pickleParser = PickleParser('../data', True)
    
    # Delete old pickles
    pickleParser.RemovePicklesOfType(CSVTypes.Heatmap.value, '.csv')
    pickleParser.RemovePicklesOfType(CSVTypes.Heatmap.value, '.pickle')

    # Run example 1: Use one country
    team_stats(teams, games)

    # Run example 2: Go through all teams
    #team_stats()
  
    # Save new pickle 
    pickleParser.SaveTypesToPickles(CSVTypes.Heatmap.value)

    # Save results in logger file
    newLogger = Logger(teams, games)
    newLogger.print_current_logger()
    newLogger.dump_logger()


if __name__== '__main__':

    # HeatmapInputInfo( list of teams (default all),
    #                   list of games (default all),
    #                   list of tournaments (default all),
    #                   date bounds [start, end] (default all),
    #                   players and/or teams enum (default all))
    inputInfoList = [HeatmapInputInfo(['CAN'],
                                  [],
                                  ['2019 WorldCup Americas Qualifiers'],
                                  ['2018-01-01', ''],
                                  PlayersOrTeams.Both.value)]

    main_heatmap(inputInfoList)

