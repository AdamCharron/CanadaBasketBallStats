from tkinter import *
from pprint import pprint
from csv_parser import *
from simple_grid import *

import sys
sys.path.insert(0, '../enrich')
sys.path.insert(0, '../heatmap')
from convert_country_names import *
from parse_to_yaml import *
from enrich_CSVs import *
from minute_heatmap import *
from stat_type_lookups import *
from logger import *
from heatmap_name_interpretor import *

data_path = '../data'
defaultStartDate = '1900-01-01'
defaultEndDate = '2200-01-01'


def DisplayPlayers(playersOrTeams):
    return playersOrTeams != 1

def DisplayTeams(playersOrTeams):
    return playersOrTeams != 0

def pre_checks(stat, inputInfo):
    # This function checks if all required stats and countries are present in pickles
    # If not, if runs the main minute_heatmap.py function to get them
    #   This automatically dumps when it's done

    abbrev_teams = list(map(lambda x: LOOKUP_FULLNAME[x], inputInfo.teams))
    
    # Find pickle corresponding to the chosen stat
    pickle_path = stat_filenames[stat] + '_' + \
                  HeatmapNameInterpretor.GetFilenameFromInputInfo(inputInfo) + ".pickle"

    # Dump pickle if needed
    # Can exit this function once that's done
    if not os.path.isfile(os.path.join(data_path,pickle_path)):
        print("File {} not found - re-serializing now.".format(pickle_path))
        pickleParser = PickleParser(data_path, True)
        pickleParser.SaveTypesToPickles(CSVTypes.Heatmap.value)
        return

    # See if anything changed since the last heatmap call
    #logger = Logger(teams, games)
    #last_log = logger.get_last_logger()
    #if last_log == None:
    #    main_heatmap(abbrev_teams, games)
    #    return
    #for country in abbrev_teams:
    #    if country not in last_log['teams']:
    #        main_heatmap(abbrev_teams, games)
    #        return
    #games.sort()
    #last_log['games'].sort()
    #if games != last_log['games']:
    #    main_heatmap(abbrev_teams, games)
    #    return


def create_full_grid(stat, inputInfo):

    # Load pickle
    pickle_path = stat_filenames[stat] + '_' + \
                  HeatmapNameInterpretor.GetFilenameFromInputInfo(inputInfo) + ".pickle"
    pickleParser = PickleParser(data_path, True)
    p = pickleParser.LoadPickle(pickle_path)
    
    # Combine all data rows into one 2d array for visualization
    grid = []
    players = []
    for country, val in p.items():
        if country not in inputInfo.teams: continue
        for player in val:
            #print(player)
            players.append([player[0], country])
            grid.append(player[1:])
            #print(player[1:])

    # Convert the grid to floats
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            grid[i][j] = float(grid[i][j])

    return players, grid
   

def launch_gui(inputInfoList = [], statList = []):
    if (inputInfoList == [] or statList == [] or
        len(inputInfoList) != len(statList)):
        print("Invalid list entries")
        return

    players = []
    games = []
    grid = []
    for i in range(len(statList)):
        pre_checks(statList[i], inputInfoList[i])
        playersTemp, gridTemp = create_full_grid(statList[i], inputInfoList[i])
        players.append(playersTemp)
        grid.append(gridTemp)

    visualize(inputInfoList, grid, players, statList)


if __name__ == '__main__':
    '''
    This is the main file for the gui for minutes heatmaps.

    These two function calls will assemble the heatmaps of players from all
    teams entered in the list below.

    Colours are assigned by giving out red, blue, green, gold to the first 4
    teams, then randomly giving a colour from the COLORS list in colours.py.
    This is not ideal, but since there's no scroll functionality (that I know of),
    using more than 4 teams should never happen since not all the results would
    be viewable.
    
    This will delete and recreate csv's and pickles for all code-generated csv's
    (enriched play-by-play, heatmap minutes, etc), so may take a few seconds to
    complete all preprocessing.
    '''

    # Teams to test this for
    #   If empty list ( [] ), all teams
    #   Otherwise, it will make the heatmap for all teams in the list
    #teams = []     # For all teams
    #teams = ['CAN', 'USA']
    teams = ['CAN']
    #teams = "CAN"

    # Games to test this for
    #   If empty list ( [] ), all games
    #   Otherwise, it will make the heatmap for all games in the list
    games = []     # For all games
    #games = [265, 269, 487, 493, 618]

    # Tournaments to test this for
    #   If empty list ( [] ), all tournaments
    #   Otherwise, it will make the heatmap for all tournaments in the list
    #tournaments = []    # For all tournaments
    tournaments = ['2019 WorldCup Americas Qualifiers']

    # Dates, in the form [start, end]
    #   Each date is YYYY-MM-DD as a string
    #   Empty list (or list of empty strings) is all days
    #   ['', '<date>'] is all games until a certain date
    #   ['<date>', ''] is all games since a certain date
    # dates = []
    #dates = ['2017-08-29', '2018-06-30']
    dates = ['2018-01-01', '']

    # Players or Teams
    #   PlayersOrTeams.Both     or
    #   PlayersOrTeams.Players  or
    #   PlayersOrTeams.Teams
    playersOrTeams = PlayersOrTeams.Both.value

    # Uncomment to select the stat to evaluate
    #stat = s_POINTS
    #stat = s_TURNOVERS
    #stat = s_REBOUNDS
    #stat = s_BLOCK
    #stat = s_FOUL
    #stat = s_SHOT_ATTEMPTS
    #stat = s_3_POINTERS
    stat = s_MINUTES_AVERAGE
    #stat = s_POINTS_AVERAGE
    #stat = s_TURNOVERS_AVERAGE
    #stat = s_REBOUNDS_AVERAGE
    #stat = s_BLOCK_AVERAGE
    #stat = s_FOUL_AVERAGE
    #stat = s_SHOT_ATTEMPTS_AVERAGE
    #stat = s_3_POINTERS_AVERAGE

    # Uncomment the following line to intentionally re-generate the enriched CSV
    #get_time_logs()

    # Uncomment the following line to intentionally re-generate pickles
    #main_heatmap()

    # Run the actual GUI
    #launch_gui(stat, teams)
    #launch_gui(stat, teams, games, tournaments)
    #launch_gui(stat, teams, games, tournaments, dates, playersOrTeams)

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

    HeatmapGenerator(inputInfoList)

    statList = [s_POINTS,
                s_POINTS_AVERAGE,
                s_MINUTES_AVERAGE]
    
    launch_gui(inputInfoList, statList)

