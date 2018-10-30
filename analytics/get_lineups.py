#---------------------IMPORTS---------------------------------------------------
#Standard default packages
import sys
import os #operating system, used for correct file paths

#File reading, writing and copying
import pandas as pd #sudo pip3 install pandas
import csv
from shutil import copyfile
import six.moves.cPickle as pickle

#Actual math and calculations
import itertools #used for 4-,3-,2-,1- man lineups

#Own helper functions
#import utils
import stat_type_lookups

#---------------------MACROS---------------------------------------------------
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(FILE_DIR, '..')
DATA_DIR = os.path.join(ROOT_DIR, 'data')
ENRICHED_FILENAME = 'PlayByPlay_enriched.csv' 
ENRICHED_FILEPATH = os.path.join(DATA_DIR, ENRICHED_FILENAME)
OVERWRITE_LINEUPS = 1 #If false, use existing pickle data for 5-man lineup


LINEUPS_PICKLE_NAMES = ['lineups_5.pkl', 'lineups_4.pkl', 'lineups_3.pkl', 
                            'lineups_2.pkl', 'lineups_1.pkl']
LINEUPS_CSV_NAMES = ['lineups_5.csv', 'lineups_4.csv', 'lineups_3.csv',
                         'lineups_2.csv', 'lineups_1.csv']
LINEUPS_PICKLE_PATHS, LINEUPS_CSV_PATHS  = [], []
for i in range(len(LINEUPS_PICKLE_NAMES)):
  LINEUPS_PICKLE_PATHS.append(os.path.join(DATA_DIR, LINEUPS_PICKLE_NAMES[i]))
  LINEUPS_CSV_PATHS.append(os.path.join(DATA_DIR, LINEUPS_CSV_NAMES[i]))

PLAYER_NAMES_COLS = ["Home.*Player1", "Home.*Player2", "Home.*Player3", 
                      "Home.*Player4", "Home.*Player5", 
                      "Away.*Player1", "Away.*Player2", "Away.*Player3", 
                      "Away.*4", "Away.*5"]

TIME_ON_COLS = ["Home.*ON1", "Home.*ON2", "Home.*ON3", "Home.*ON4", 
                "Home.*ON5", "Away.*ON1", "Away.*ON2", "Away.*ON3", 
                "Away.*ON4", "Away.*ON5"]

TEAM_NAMES_COLS = ["Home.*Team", "Away.*Team"]

STATS_HEADING = ['Lineup', 'Lineup Team', 'Opponent', 'Opponent Team',
                  'MIN', 'PTS','PPP', 'FGM', 'FGA', 'FG%', '2FGM', '2FGA', '2FG%',
                  '3FGM', '3FGA','3FG%', 'FTM', 'FTA', 'FT%', 'OREB', 'DREB', 
                  'REB', 'AST', 'PF', 'TO', 'STL', 'BLK','eFG%','TS%', 'ORB%','DRB%','OFF Poss','PTS Against', 'PPP Against',
                  'FGM Against', 'FGA Against', 'FG% Against', '2FGM Against', '2FGA Against', 
                  '2FG% Against', '3FGM Against', '3FGA Against', '3FG% Against', 'FTM Against',
                  'FTA Against', 'FT% Against', 'OREB Against', 'DREB Against', 'REB Against', 
                  'AST Against', 'PF Against', 'TO Against', 'STL Against', 'BLK Against',
                  'eFG% Against', 'TS% Against','ORB%  Against','DRB% Against','DEF Poss','+/-' ]


STATS_INDEX = { 'Lineup': 0,
                'Lineup Team': 1,
                'Opponent': 2,
                'Opponent Team': 3,
                'MIN': 4,
                'PTS': 5,
                'PPP': 6,
                'FGM': 7,
                'FGA': 8,
                'FG%': 9,
                '2FGM': 10,
                '2FGA': 11,
                '2FG%': 12,
                '3FGM': 13,
                '3FGA': 14,
                '3FG%': 15,
                'FTM': 16,
                'FTA': 17,
                'FT%': 18,
                'OREB': 19,
                'DREB': 20,
                'REB': 21,
                'AST': 22,
                'PF': 23,
                'TO': 24,
                'STL': 25,
                'BLK': 26,
                'eFG%': 27,
                'TS%': 28,
                'ORB%': 29,
                'DRB%': 30,
                'OFF Poss': 31,
                'PTS Against': 32,
                'PPP Against': 33,
                'FGM Against': 34,
                'FGA Against': 35,
                'FG% Against': 36,
                '2FGM Against': 37,
                '2FGA Against': 38,
                '2FG% Against': 39,
                '3FGM Against': 40,
                '3FGA Against': 41,
                '3FG% Against': 42,
                'FTM Against': 43,
                'FTA Against': 44,
                'FT% Against': 45,
                'OREB Against': 46,
                'DREB Against': 47,
                'REB Against': 48,
                'AST Against': 49,
                'PF Against': 50,
                'TO Against': 51,
                'STL Against': 52,
                'BLK Against': 53,
                'eFG% Against': 54,
                'TS% Against': 55,
                'ORB% Against': 56,
                'DRB% Against': 57,
                'DEF Poss': 58,
                '+/-': 59
}

Home_COLS = ["Home.*1", "Home.*2", "Home.*3", "Home.*4", "Home.*5"]
Away_COLS = ["Away.*1", "Away.*2", "Away.*3", "Away.*4", "Away.*5"]
CRUNCH_TIME={"Margin":5, "Mins":5}
FTM_FOR_POSS=False
#---------------------FUNCTIONS---------------------------------------------------
def performBoxstatLogic(lineup_hash, opponent, event, 
                          stat_col_map, active_team, lineup_team,
                          opponent_team, time_int):
  '''
  Perform logic for traditional boxscore stats.
  
  Args:
    lineup_hash: (hash) {opponent lineup (or aggregate): [array of stats]}
                  of ONE PARTICULAR LINEUP

    opponent: (str) key of lineup_hash consisting of opponent lineup or 
                aggregate data such as "Cleveland - Team" or simply "Total"

    event: (str) event name for a particular play 

    stat_col_map: (hash) {stat: index} maps name of stat to column index 
                    in stat array (important because stats out of order
                    like in a regular hash table look very messy)

    active_team: (boolean) True if lineup team is responsible for event.

    lineup_team: (str) Team of the lineup.

    opponent_team: (str) Team of the opposing lineup (or just 'Total')
    
    time_int: (float) time interval in mins since last event 

  Returns:
    None: All it does is update the lineup_hash. 
  '''
  
  #Team Info
  lineup_hash[opponent][stat_col_map['Lineup Team']] = lineup_team
  lineup_hash[opponent][stat_col_map['Opponent Team']] = opponent_team

  #Minutes
  lineup_hash[opponent][stat_col_map['MIN']] += time_int
  if event in stat_type_lookups.event_SUB:
    return

  #Points and +/-
  if event in stat_type_lookups.event_PTS:
    stat='PTS'
    if active_team:
      pm_factor = 1 #pm = plus-minus
    else:
      stat += ' Against'
      pm_factor = -1

    if event in stat_type_lookups.event_1PT:
      lineup_hash[opponent][stat_col_map[stat]] += 1
      lineup_hash[opponent][stat_col_map['+/-']] += pm_factor*1
    elif event in stat_type_lookups.event_2PT:
      lineup_hash[opponent][stat_col_map[stat]] += 2
      lineup_hash[opponent][stat_col_map['+/-']] += pm_factor*2
    else: #3PT
      lineup_hash[opponent][stat_col_map[stat]] += 3
      lineup_hash[opponent][stat_col_map['+/-']] += pm_factor*3
  
  #Field Goal Attempts
  if (event in stat_type_lookups.event_FGA):
    stat='FGA'
    if not active_team:
      stat+=' Against'
    lineup_hash[opponent][stat_col_map[stat]] += 1
    if event in stat_type_lookups.event_2FGA:
      stat='2FGA'
      if not active_team:
        stat+=' Against'        
      lineup_hash[opponent][stat_col_map[stat]] += 1
    else:
      stat='3FGA'
      if not active_team:
        stat+=' Against'        
      lineup_hash[opponent][stat_col_map[stat]] += 1    
    if event in stat_type_lookups.event_FGM:
      stat='FGM'
      if not active_team:
        stat+=' Against'
        lineup_hash[opponent][stat_col_map['DEF Poss']] += 1
      else:
        lineup_hash[opponent][stat_col_map['OFF Poss']] += 1        
      lineup_hash[opponent][stat_col_map[stat]] += 1
      if event in stat_type_lookups.event_2PT:
        stat='2FGM'
        if not active_team:
          stat+=' Against'        
        lineup_hash[opponent][stat_col_map[stat]] += 1
      else:
        stat='3FGM'
        if not active_team:
          stat+=' Against'        
        lineup_hash[opponent][stat_col_map[stat]] += 1

  #Free throws
  global FTM_FOR_POSS
  FTM_FOR_POSS=False #global var for possession count     
  if (event in stat_type_lookups.event_FTA):
    stat='FTA'
    if not active_team:
      stat+=' Against'    
    lineup_hash[opponent][stat_col_map[stat]] += 1
    if event in stat_type_lookups.event_FTM:
      FTM_FOR_POSS=True
      stat='FTM'
      if not active_team:
        stat+=' Against'      
      lineup_hash[opponent][stat_col_map[stat]] += 1
      
  #Rebounds
  if (event in stat_type_lookups.event_REB):
    stat='REB'
    if not active_team:
      stat+=' Against'      
    lineup_hash[opponent][stat_col_map[stat]] += 1
    if event in stat_type_lookups.event_OREB:
      stat='OREB'
      if not active_team:
        stat+=' Against'   
      lineup_hash[opponent][stat_col_map[stat]] += 1
    else:
      stat='DREB'
      if not active_team:
        stat+=' Against'    
        lineup_hash[opponent][stat_col_map['OFF Poss']] += 1
      else:
        lineup_hash[opponent][stat_col_map['DEF Poss']] += 1        
      lineup_hash[opponent][stat_col_map[stat]] += 1
  
  #Assists
  if (event in stat_type_lookups.event_AST):
    stat='AST'
    if not active_team:
      stat+=' Against'    
    lineup_hash[opponent][stat_col_map[stat]] += 1

  #Fouls
  if (event in stat_type_lookups.event_PF):
    stat='PF'
    if not active_team:
      stat+=' Against'    
    lineup_hash[opponent][stat_col_map[stat]] += 1

  #Turnovers
  if (event in stat_type_lookups.event_TO):
    stat='TO'
    if not active_team:
      stat+=' Against'    
      lineup_hash[opponent][stat_col_map['DEF Poss']] += 1
    else:
      lineup_hash[opponent][stat_col_map['OFF Poss']] += 1
    lineup_hash[opponent][stat_col_map[stat]] += 1

  #Steals
  if (event in stat_type_lookups.event_STL):
    stat='STL'
    if not active_team:
      stat+=' Against'    
    lineup_hash[opponent][stat_col_map[stat]] += 1

  #Blocks
  if (event in stat_type_lookups.event_BLK):
    stat='BLK'
    if not active_team:
      stat+=' Against'    
    lineup_hash[opponent][stat_col_map[stat]] += 1

  return


def addMatchupEvent(lineups_hash, lineup, opponents, lineup_team,
                      opponent_team, event, event_team, time_int, addpossession=''):
  lineup_key = ";".join(lineup)
  opponents_key = ";".join(opponents)
  opponent_team_key = opponent_team + " - Total"

  #Never seen this lineup before
  if lineup_key not in lineups_hash: #never seen this lineup before
    lineups_hash[lineup_key] = {}
    this_lineup_hash = lineups_hash[lineup_key]
    this_lineup_hash[opponents_key] = [0 for _ in range(len(STATS_INDEX))]
    this_lineup_hash[opponent_team_key] = [0 for _ in range(len(STATS_INDEX))]
    lineups_hash[lineup_key]['Total']  = [0 for _ in range(len(STATS_INDEX))]

  #This lineup has existed, but first time facing opponent matchup
  elif opponents_key not in lineups_hash[lineup_key]:
    this_lineup_hash = lineups_hash[lineup_key]
    this_lineup_hash[opponents_key] = [0 for _ in range(len(STATS_INDEX))]
    if opponent_team_key not in this_lineup_hash: #Never faced team before
      this_lineup_hash[opponent_team_key] = \
        [0 for _ in range(len(STATS_INDEX))]

  #Update boxscore stats
  this_lineup_hash = lineups_hash[lineup_key]
  active_team = (event_team == lineup_team) 
  if addpossession:
    if addpossession==lineup_team:
      stat='DEF Poss'
    else:
      stat='OFF Poss'
    this_lineup_hash[opponents_key][STATS_INDEX[stat]] += 1
    this_lineup_hash[opponent_team_key][STATS_INDEX[stat]] += 1
    this_lineup_hash['Total'][STATS_INDEX[stat]] += 1
      

  performBoxstatLogic(this_lineup_hash, opponents_key, event, STATS_INDEX, 
                        active_team, lineup_team, opponent_team, time_int)
  performBoxstatLogic(this_lineup_hash, opponent_team_key, event, STATS_INDEX, 
                        active_team, lineup_team, opponent_team, time_int)
  performBoxstatLogic(this_lineup_hash, 'Total', event, STATS_INDEX, 
                        active_team, lineup_team, 'Total', time_int)

  return 


def minuteInterval(cur_time, last_time):
  def parseInputTime(input_time):
    quarter, time = input_time.split('-')
    minute, second = time.split(':')
    return int(quarter), float(minute), float(second)
  last_quarter, last_min, last_sec = parseInputTime(last_time)
  cur_quarter, cur_min, cur_sec = parseInputTime(cur_time)

  #Current time is in separate quarter than last event
  if cur_quarter > last_quarter:
    if cur_min > 5: #In quarters 1-4, 10-mins 
      quarter_start_seconds = 10*60 #in s
    else: #In overtime, 5-mins
      quarter_start_seconds = 5*60
    sec_in_last_quarter = last_min*60 + last_sec
    sec_in_cur_quarter = quarter_start_seconds - (cur_min*60 + cur_sec)
    return (sec_in_last_quarter + sec_in_cur_quarter)/60
  
  time_int = ((last_min*60 + last_sec) - (cur_min*60 + cur_sec))/60
  return time_int

def swapValues(val1, val2):
  return val2, val1

def extractLineups(N, enriched_PbP_file, players_cols, teams_cols,
                    pkl_save_file, show_progress_steps = 1000, 
                    onlycrunchtime=False, crunch_time=CRUNCH_TIME):
  '''
  Extract all N-man lineups from enriched Play-by-Play file. Use 
  each lineup name as a key in a hash. Save hash into pickle 
  file for later use.

  Args:
    N: (int) number of players in each lineup combination to analyze

    enriched_PbP_file: (string) csv file of Play-by-Play data containing 
                          additional columns indicating which players 
                          are on the court

    players_cols: (array) column header names (or regular expression of 
                    column header names) to indicate which elements we need 
                    to extract from enriched_PbP_file in order to get player 
                    data

    teams_cols: (array) column header names (or regex of column names)
                  to indicate which columns to get the home and away team
                  names

    pkl_save_file: (string) save lineup_hash into a pickle for easy access

    show_progress_steps: (int) print progress every time we process this many 
                          rows in the csvfile data (default = 1000)

  Returns:
    lineups_hash: hash whose keys are the names of the N-player lineup sorted 
  '''
  if not os.path.isfile(enriched_PbP_file):
    print("Error: Could not find enriched file: {}".format(enriched_PbP_file))
    sys.exit()
  
  #Read in lineup data
  lineups_hash = {}
  enriched_PbP_df = pd.read_csv(enriched_PbP_file, sep=",")
  
  def getElementFromColRegex(row_df, col_regex):
    element_df = row_df.filter(regex=(col_regex))
    element_txt = str(element_df.iloc[0]) #Filtered row so only one column
    return element_txt.strip()
  
  if onlycrunchtime:
    def defCrunchTime(crunch_time):
      def isCrunchTime(event_time, homescore, awayscore):
        quarter, time = event_time.split('-')
        minute, second = time.split(':')     
        time_crit, score_crit =False, False
        if int(quarter) >= 4 and int(minute) < crunch_time['Mins']:
          time_crit=True
        if abs(homescore-awayscore) <= crunch_time['Margin']:
          score_crit=True
        return time_crit, score_crit 
      return isCrunchTime
    isCrunchTime=defCrunchTime(crunch_time)
    firstcrunchtimeevent=True
  
  
  #Extract data row-by-row
  last_gameID = 0
  for idx, row in enriched_PbP_df.iterrows():
    #Sort players alphabetically to form 5-player lineup
    home_5 = []
    away_5 = []
    for col in players_cols:
      player = getElementFromColRegex(row, col)
      if "Home" in col:
        home_5.append(player)
      else:
        away_5.append(player)
    home_5.sort()
    away_5.sort()

    #Get all combinations from 5-man lineup for N-man lineup
    home_N = list(itertools.combinations(home_5, N))
    away_N = list(itertools.combinations(away_5, N))
    
    #Extract event, event team, home team, away team
    event = str(row['Event']).strip()
    event_team = str(row['Team']).strip()
    if not event: #blank event
      continue
    for col in teams_cols:
      if "Home" in col:
        home_team = getElementFromColRegex(row, col)
      else:
        away_team = getElementFromColRegex(row, col)
    
    #Update minutes
    gameID = str(row['Game ID']).strip()
    if gameID != last_gameID:
      last_home_N = home_N[:] #Splicing to copy by value
      last_away_N = away_N[:]
      last_event_time = '1-10:00'
      last_gameID = gameID
      if onlycrunchtime:
        firstcrunchtimeevent=True

    event_time = str(row['Quarter']).strip() + "-" + str(row['Time']).strip()
    
    #check if crunchtime
    if onlycrunchtime:
      time_crit, score_crit = isCrunchTime(event_time, row["Home Score"], row["Away Score"])
      if not time_crit:
        continue
      elif not score_crit: #meets time criteria but not score criteria
        if not firstcrunchtimeevent: #it's a play to push the score out of score criteria so add stats one last time
          firstcrunchtimeevent=True
          time_int = minuteInterval(event_time, last_event_time)
        else: #never was in crunchtime
          continue
      elif firstcrunchtimeevent: #if first event in crunchtime then no time interval
        time_int=0.0
        firstcrunchtimeevent=False
      else:
        time_int = minuteInterval(event_time, last_event_time)
    else:
      time_int = minuteInterval(event_time, last_event_time)
    
    last_event_time = event_time
   
    #If event is a substitution then add minutes played for preceding lineup
    if (event in stat_type_lookups.event_SUB):
      if (time_int == 0):
        continue #Don't bother saving if lineup has no meaningful stat
      else:
        if event_team == home_team:
          home_N, last_home_N = swapValues(home_N, last_home_N) 
        else:
          away_N, last_away_N = swapValues(away_N, last_away_N) 

    #Update boxscore stats for both lineups (1 for each team) 
    global FTM_FOR_POSS
    addpossession=''
    if FTM_FOR_POSS and (event not in stat_type_lookups.event_FTA):
      FTM_FOR_POSS=False
      addpossession=event_team #event_team gets defensive possession
                               #Assumption is that play after made freethrow is by non shooting team
    
    #Add event to lineups_hash for N-man lineup against 5-man opponent
    for i in range(len(home_N)):  
      addMatchupEvent(lineups_hash, home_N[i], away_5, home_team,
                        away_team, event, event_team, time_int, addpossession=addpossession)
      addMatchupEvent(lineups_hash, away_N[i], home_5, away_team,
                        home_team, event, event_team, time_int, addpossession=addpossession)
   
    #Show progress on terminal
    if (idx+1)%show_progress_steps == 0:
      print("Done {}/{} rows...".format(idx+1, enriched_PbP_df.shape[0] + 1))

  print("Done all rows! Extracted {} unique {}-man lineups".\
          format(len(lineups_hash), N))

  with open(pkl_save_file,'wb') as fd:
    pickle.dump(lineups_hash, fd, pickle.HIGHEST_PROTOCOL)
    print("Results saved into {}".format(pkl_save_file))

  return lineups_hash


def performAggregateBoxStatLogic(values, stat_col_map):
  '''
  Similar to the other function performBoxstatLogic except uses entire
  data from lineups after "counting" events (ex: FG, FGA) have already
  been tallied to get stats such as shooting % and points-per-possession.

  Args:
    values: (array) contains stat values of ONE PARTICULAR LINEUP 
                          against ONE PARTICULAR OPPONENT

    stat_col_map: (hash) {stat: index} maps name of stat to column index 
                    in stat array (important because stats out of order
                    like in a regular hash table look very messy)
  Returns:
    None: All it does is update the stat_array. 
  '''

  for stat in ("FG", "2FG", "3FG", "FT"):
    if values[stat_col_map[stat+'A']]!=0:
      values[stat_col_map[stat+'%']]=round(100*values[stat_col_map[stat+'M']] / values[stat_col_map[stat+'A']])
    else:
      values[stat_col_map[stat+'%']]=0
    if values[stat_col_map[stat+'A Against']]!=0:
      values[stat_col_map[stat+'% Against']]=round(100*values[stat_col_map[stat+'M Against']] / values[stat_col_map[stat+'A Against']])
    else:
      values[stat_col_map[stat+'% Against']]=0
      
  #Points per possession
  if values[stat_col_map['OFF Poss']]!=0:
    values[stat_col_map['PPP']] = round(values[stat_col_map['PTS']]  / values[stat_col_map['OFF Poss']], 3) 
  else:
    values[stat_col_map['PPP']] = 0
  if values[stat_col_map['DEF Poss']] !=0:
    values[stat_col_map['PPP Against']] = round(values[stat_col_map['PTS Against']]  / values[stat_col_map['DEF Poss']], 3 )
  else:
    values[stat_col_map['PPP Against']] =0
    
  #Add RB%
  if (values[stat_col_map['DREB']] + values[stat_col_map['OREB Against']])!=0:
    values[stat_col_map['DRB%']] = round( 100*values[stat_col_map['DREB']] / (values[stat_col_map['DREB']] + values[stat_col_map['OREB Against']]) )
    values[stat_col_map['ORB% Against']] = round( 100*values[stat_col_map['OREB Against']] / (values[stat_col_map['OREB Against']] + values[stat_col_map['DREB']]) ) 
  else:
    values[stat_col_map['DRB%']] = 0
    values[stat_col_map['ORB% Against']] =0
  if (values[stat_col_map['OREB']] + values[stat_col_map['DREB Against']]) !=0:
    values[stat_col_map['ORB%']] = round( 100*values[stat_col_map['OREB']] / (values[stat_col_map['OREB']] + values[stat_col_map['DREB Against']]) )
    values[stat_col_map['DRB% Against']] = round( 100*values[stat_col_map['DREB Against']] / (values[stat_col_map['DREB Against']] + values[stat_col_map['OREB']]) )
  else:
    values[stat_col_map['ORB%']] =0
    values[stat_col_map['DRB% Against']]=0

  #Add efg% and ts%
  for team in (""," Against"):
    if values[stat_col_map['FGA'+team]]!=0:
      values[stat_col_map['eFG%'+team]] = round(100*(values[stat_col_map['FGM'+team]] +0.5*values[stat_col_map['3FGM'+team]]) / values[stat_col_map['FGA'+team]] ) #eFG%
      values[stat_col_map['TS%'+team]] = round(100*values[stat_col_map['PTS'+team]] / (2*(values[stat_col_map['FGA'+team]]+ (0.47*values[stat_col_map['FTA'+team]]) ) ) ) #TS%
    else:
        values[stat_col_map['eFG%'+team]] = 0 #eFG%
        if values[stat_col_map['FTA'+team]]!=0:
            values[stat_col_map['TS%'+team]] = round(100*values[stat_col_map['PTS'+team]] / (2*(values[stat_col_map['FGA'+team]]+ (0.47*values[stat_col_map['FTA'+team]]) ) ) ) #TS%
        else:
            values[stat_col_map['TS%'+team]] = 0 #TS% 
          
  for stat in ("MIN","OFF Poss", "DEF Poss"): #round possible decimal values
    values[stat_col_map[stat]]=round(values[stat_col_map[stat]])

  return


def getOneManLessLineups(larger_lineups_hash, show_progress_steps = 10000):
  '''
  Given hash containing lineups of N players in key, get all lineup
  combinations containing N-1 players. If N<=1, return empty hash.

  Args:
    larger_lineups_hash: hash whose keys are the sorted names of the 
                          N-player lineups 

    show_progress_steps: print progress every time we process this many 
                          entries in the lineups hash (default = 10,000)

  Returns:
    smaller_lineups_hash: hash whose keys are the names of the (N-1)-player 
                            lineup sorted. If N<=1, this is empty.
  '''
  smaller_lineups_hash = {}
  for i, lineup_key in enumerate(larger_lineups_hash):
    #Check that lineup hash given has at least two people
    more_players = lineup_key.split(";") #Contains players in (N+1)-lineups
    N = len(more_players)
    if N <= 1:
      print("Can't extract lineups of less than 1-person")
      return
    
    #Add new subset combinations to result
    for j in range(N):
      subset_players = more_players[:j] + more_players[j+1:] #already sorted
      smaller_lineup_key = ';'.join(subset_players)
      if smaller_lineup_key in smaller_lineups_hash: #lineup data already exists
        for key, val in larger_lineups_hash[lineup_key].items(): #merge dicts
          if key in smaller_lineups_hash[smaller_lineup_key]:
            smaller_lineups_hash[smaller_lineup_key][key] = val
          else:
            smaller_lineups_hash[smaller_lineup_key][key] = val
      else:
        smaller_lineups_hash[smaller_lineup_key] = larger_lineups_hash[lineup_key] 

    #Show progress on terminal
    if (i+1)%show_progress_steps == 0:
      print("Done {}/{} {}-man lineups ...".\
              format(i+1, len(larger_lineups_hash), N))

  return smaller_lineups_hash


#---------------------MAIN---------------------------------------------------
if __name__ == '__main__':
                           
  print('Started running...')

  #Extracting N-man lineups
  for (i, N) in enumerate(range(5,0,-1)):
    print("\nExtracting {}-man lineups ...".format(N))
    if (OVERWRITE_LINEUPS) or (not os.path.isfile(LINEUPS_PICKLE_PATHS[i])):
      lineups_N = extractLineups(N, ENRICHED_FILEPATH, PLAYER_NAMES_COLS, 
                                      TEAM_NAMES_COLS, LINEUPS_PICKLE_PATHS[i], 
                                      show_progress_steps = 1000,
                                      onlycrunchtime=False, 
                                      crunch_time=CRUNCH_TIME)
    else:
      lineups_N = pickle.load(open(LINEUPS_PICKLE_PATHS[i], 'rb'))

    #Write data to CSV
    print("\n Writing pickle data to CSV file ...")
    num_lineups = len(lineups_N)
    with open(LINEUPS_CSV_PATHS[i],'w',newline='') as lineup_file:
      lineup_writer = csv.writer(lineup_file)
      lineup_writer.writerow(STATS_HEADING)

      for j, (lineup, lineup_hash) in enumerate(lineups_N.items()):
        for (opponent, stats) in lineup_hash.items():
          stats = list(stats)
          stats[STATS_INDEX['Lineup']] = str(lineup)
          stats[STATS_INDEX['Opponent']] = str(opponent)
          
          #Add percentage and per-minute stats
          performAggregateBoxStatLogic(stats, STATS_INDEX) 
         
          lineup_writer.writerow(stats)

        #Show progress on terminal
        if (j+1)%100 == 0:
          print("Done {}/{} {}-man lineups ...".format(j+1, num_lineups, N))

    print("Done {}-man lineups! Results saved in {}".
            format(N, LINEUPS_CSV_PATHS[i]))

  print("\n--------------------\nFinished main.")

#  print(lineups_5)
  
  #Extracting remaining lineups for subset of players
#  print("\nExtracting 4-man lineups ...")
#  lineups_4 = getOneManLessLineups(lineups_5, show_progress_steps = 10000)
#  print("\nExtracting 3-man lineups ...")
#  lineups_3 = getOneManLessLineups(lineups_4, show_progress_steps = 10000)
#  print("\nExtracting 2-man lineups ...")
#  lineups_2 = getOneManLessLineups(lineups_3, show_progress_steps = 10000)
#  print("\nExtracting 1-man (individual) lineups ...")
#  lineups_1 = getOneManLessLineups(lineups_2, show_progress_steps = 10000)
#
#  #Print final results
#  print("\nTotal number of lineups:")
#  print("5-man: {}".format(len(lineups_5)))
#  print("4-man: {}".format(len(lineups_4)))
#  print("3-man: {}".format(len(lineups_3)))
#  print("2-man: {}".format(len(lineups_2)))
#  print("1-man: {}".format(len(lineups_1)))


#  for i, (player, info) in enumerate(lineups_1.items()):
#    print(i, player, info, "\n")
