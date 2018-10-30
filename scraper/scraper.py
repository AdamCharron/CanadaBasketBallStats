#---------------------IMPORTS---------------------------------------------------
#Standard default packages
import sys
import os #operating system, used for correct file paths

#File reading, writing and copying
import pandas as pd #sudo pip3 install pandas
import csv
from shutil import copyfile

#Website scraping
import requests
from bs4 import BeautifulSoup #sudo apt-get install python3-bs4

#Formatting text
from unicodedata import normalize
from unidecode import unidecode
import re #regular expressions
#import datefinder #sudo pip3 install datefinder
import datetime

#Own helper functions
import utils

#---------------------MACROS---------------------------------------------------
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(FILE_DIR, '../data')
GAME_FILE_PATH = os.path.join(RESULTS_PATH, 'GameIDs.csv')
PLAY_FILE_PATH = os.path.join(RESULTS_PATH, 'PlayByPlay.csv')
BOXSCORE_FILE_PATH = os.path.join(RESULTS_PATH, 'BoxscoreStats.csv')

GAME_FILE_HEADING = ['Game ID', 'Tournament', 'Date', 'Round', 'Location',
                      'Home Team', 'Away Team', 'Home Final Score', 
                      'Away Final Score']

PLAY_FILE_HEADING = ['Game ID', 'Quarter', 'Time', 'Home Score', 'Away Score',
                      'Team', 'Number', 'Player', 'Event']

BOXSCORE_FILE_HEADING = ['Game ID', 'Team', 'Number', 'Name', 'MIN', 'PTS', 
                          'FGM', 'FGA', '2FGM', '2FGA', '3FGM', '3FGA', 'FTM', 
                          'FTA', 'OREB', 'DREB', 'REB', 'AST', 'PF', 'TO', 
                          'STL', 'BLK', '+/-']

TOURNAMENT_INFO_PATH = os.path.join(FILE_DIR, 'tournament_info')
TOURNAMENT_URLS_FILE = 'schedule_URLs.txt'
TOURNAMENT_URLS_PATH = os.path.join(TOURNAMENT_INFO_PATH, 
                                      TOURNAMENT_URLS_FILE)
TOURNAMENT_NAMES_FILE = 'names.txt'
TOURNAMENT_NAMES_PATH = os.path.join(TOURNAMENT_INFO_PATH, 
                                      TOURNAMENT_NAMES_FILE)

OTHER_FORMAT_LINKS={
'http://www.fiba.basketball/afrobasketqualifiers/2017/fullschedule',
'http://www.fiba.basketball/asiacup/2017/seaba/fullschedule',
'http://www.fiba.basketball/asiacup/2017/eaba/fullschedule',
'http://www.fiba.basketball/asiacup/2017/waba/fullschedule',
'http://www.fiba.basketball/basketballworldcup/2019/european-qualifiers/fullschedule#tab=Past',
'http://www.fiba.basketball/basketballworldcup/2019/americas-qualifiers/fullschedule#tab=Past',
'http://www.fiba.basketball/basketballworldcup/2019/african-qualifiers/fullschedule#tab=Past',
'http://www.fiba.basketball/basketballworldcup/2019/asian-qualifiers/fullschedule#tab=Past'
}

MONTHS={'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6,
        'July':7, 'August':8, 'September':9, 'October':10, 'November':11,
        'December':12}

#---------------------MAIN---------------------------------------------------
if __name__ == '__main__':
                           
  print('Started running...')
  
  #Initialize results files and copy current version into timestamped copy
  if not os.path.exists(RESULTS_PATH):
    os.makedirs(RESULTS_PATH)
  utils.saveBackUpIfExists(GAME_FILE_PATH, PLAY_FILE_PATH, BOXSCORE_FILE_PATH)
  utils.writeHeadingsIfNeeded(GAME_FILE_PATH, PLAY_FILE_PATH, 
                              BOXSCORE_FILE_PATH, GAME_FILE_HEADING,
                              PLAY_FILE_HEADING, BOXSCORE_FILE_HEADING)

  #Get gameID, last gamedate for each tournament, tournament urls+names
  last_dates_hash, game_ID = utils.getMostRecentGameInfo(GAME_FILE_PATH, ',', 
                                                        print_info=True)
  tournament_info = utils.getTournamentNamesAndURLS(TOURNAMENT_INFO_PATH, 
                                TOURNAMENT_URLS_FILE, TOURNAMENT_NAMES_FILE)

  #Get all the gamedates and associated gamelink URLs for each tournament
  GameLinks=[]
  TOURNAMENT_NAMES = []
  for i, (name, link) in enumerate(tournament_info):
    print("Extracting info from link {}/{}: {} ...".\
      format(i+1,len(tournament_info), link))
    TOURNAMENT_NAMES.append(name)
    tourney_date_and_games_tuples = []
    
    #Get gamedates, check if > last_dates_hash
      #If new date, create list of (date, [gameURLs]) for each tournament 
    Soup = utils.getSoup(link)
    GameDays = Soup.findAll(class_='day_content')
    firstdate=None
    for day in GameDays:
      d = day.find(class_='section_header').text.strip()
      
      #some tournamnets have duplicates
      if firstdate==None:
        firstdate=d
      elif firstdate==d:
        break

      if len(d.split(' '))==3: #make sure date is complete
          gamedate=utils.formatdate(d[:d.find('\n')], MONTHS)
      else:
          tourneyyear=re.search('20[12][0-9]',link).group(0)
          gamedate=utils.formatdatenoyear(d[:d.find('\n')], MONTHS, tourneyyear)        
      
      #Check to make sure gamedate is more recent than what we already have
        #We need to be careful of the previous scrape happening in the middle
        #of the day, with some games already finished and others not started
        
      if (name in last_dates_hash) and (gamedate <= last_dates_hash[name]):
        print("\tSkipping because gamedate: {} <= last saved: {} ...".\
                format(gamedate.strftime('%Y/%m/%d'), 
                        last_dates_hash[name].strftime('%Y/%m/%d')))
        continue
      
      #Add in array containing game urls
      if link in OTHER_FORMAT_LINKS:
        games = day.findAll(class_='score_list')
        gamelinks_for_date = []        
        for j in games:
          for l in j.findAll('a'):
            if (l['href'] != '#') and (l.find(class_='score')):
              if l['href'] not in gamelinks_for_date:
                gamelinks_for_date.append(l['href']) #Jamal update this so that
          #it doesn't find all games (only those with gamdate > last_saved)
        tourney_date_and_games_tuples.append((gamedate, gamelinks_for_date))
      else:
        Gameboxes = day.findAll(class_=['score_cell odd','score_cell even'])
        tourney_date_and_games_tuples.append((
          gamedate, [i['href'] for i in Gameboxes])) #Jamal update this so that
          #it doesn't find all games (only those with gamdate > last_saved)
        
    GameLinks.append(tourney_date_and_games_tuples)
      
  print("Collected all the tournament links!")
 
  
  #Beging extracting data from links and writing into csv files
  with open(GAME_FILE_PATH,'a',newline='') as gamefile:
    gamewriter=csv.writer(gamefile)

    with open(PLAY_FILE_PATH,'a',newline='') as playfile:
      playwriter=csv.writer(playfile)

      with open(BOXSCORE_FILE_PATH,'a',newline='') as boxscorefile:
        boxwriter=csv.writer(boxscorefile)

        #Go through each tournament
        for i, date_and_games_tuples in enumerate(GameLinks):
          tournamentname = TOURNAMENT_NAMES[i]
          print("\n\nWriting for tournament {}/{}: {} ...".format(i+1,
            len(GameLinks), tournamentname))

          if not date_and_games_tuples:
            print("No updated games for this tournament, skipping...")
            continue
          
          #Go through each date, and then each game_url for that date
          for j, (date, game_urls) in enumerate(date_and_games_tuples):
            date = date.strftime('%Y/%m/%d')
            print("Extracting new gamedate info {}/{}: {}".format(j+1,
              len(date_and_games_tuples), date))
            print(len(game_urls), "games:", game_urls)
            if not game_urls: #No games for gamedate
              continue
            for game_url in game_urls:
              print("\t{} ...".format(game_url)) 
              if game_url == '#':
                continue
  
              Soup = utils.getSoup('http://www.fiba.basketball'+ game_url)
              if Soup.find(
                class_=['action-item x--team-B','action-item x--team-A']#if no play by play
              ) == None:
                continue
             
              #Add new game entry to gameID csv file 
              game_ID+=1
              game_info = utils.getGameData(Soup)
              game_entry = [
                game_ID,
                tournamentname,
                date,
                game_info['round'],
                game_info['location'],
                game_info['home_team'],
                game_info['away_team'],
                game_info['home_score'],
                game_info['away_score']
              ]
              gamewriter.writerow(game_entry)
              
              
              #Boxscore info starts here
              boxscoreURL=Soup.find(class_='custom_tab_title tabs').findAll('li')[3]['data-ajax-url']
              boxsoup= utils.getSoup('http://www.fiba.basketball'+boxscoreURL)
          
              Boxscores= boxsoup.findAll(class_=['box-score_team-A','box-score_team-B'])
              if Boxscores==[]:
                continue #  Game still in progress ROSSDAN MAKE SURE THIS GAME GETS SCRAPED AGAIN
              Team=game_info["home_team"]
              starters={game_info["home_team"]:[], game_info["away_team"]:[]}
              for boxscore in Boxscores:
                
                rows=boxscore.findAll('tr')
                for row in rows:
                  data=[]
                  for val in row.find_all('td'):
                      if val.find(class_='bold'):
                          data.append(val.find(class_='bold').text.encode('utf8').decode('utf8'))
                      else:
                          data.append(val.text.encode('utf8').decode('utf8'))
      
                  if len(data) not in (17,18):
                      continue
                  if data[0]=='Team/Coaches':
                      continue
              
                  data[1]= utils.cleanString(data[1])
                  

                  if data[0]=='Totals':
                      data.insert(0,Team)
                      
                  if row['class']==['x--player-is-starter']:
                    starters[Team].append((data[1],data[0])) #name, number
                    
                    
                  mins=data[2]
                  if len(mins)>5:
                      data[2]=mins[:mins.rfind(':')]
                  for k in (7,6,5,4):
                      data[k]=data[k].strip()[:data[k].strip().find('\n')]
                      makes,attempts=data[k].split('/')
                      data[k]=attempts
                      data.insert(k,makes)
                  data.pop(-1)
                  data.insert(0,Team)
                  data.insert(0,game_ID)
                  boxwriter.writerow(data)
  
                #Now repeat the same process for the away team
                if len(starters[Team])!=5:
                  print(Team+ "has "+ str(len(starters[Team])) + " starters")
                  
                Team=game_info["away_team"]              
              
              
              
              #Soup = utils.getSoup('http://www.fiba.basketball'+game_url+'#tab=play_by_play,q1')
              
              
              #Begin writing the play-by play data
              Plays=Soup.findAll(class_=['action-item x--team-B','action-item x--team-A'])
              previousscore=(0,0)
              firstplay=None
              for j in range(len(Plays)):
                play = Plays[-1-j] #plays are in reverse order
                if play == firstplay:
                  break #website gives 2 copies of the game. Break after first                       
                
                play_info = utils.getPlayData(play)
                
                
                
                if j==0 and ('Substitution in' != play_info['event']): #Start of game and no substitutions
                  for team in starters:
                    for player in starters[team]:
                      play_entry = [
                        game_ID,
                        1,    #quarter
                        '10:00', #time
                        0, #score
                        0,  #score
                        team,
                        player[1], #number
                        player[0], #name
                        'Substitution in',
                      ]
                      playwriter.writerow(play_entry)
                                          
                
                if play_info['event'] == '':
                  print("Blank event", game_url, play_info['quarter'], 
                          play_info['clock'], j)##################################################################
                if play_info['team'] == 'A':
                  play_info['team'] = game_info['home_team']
                else:
                  play_info['team'] = game_info['away_team']
                    
                if (play_info['home_score'], play_info['away_score']) == ('',''):
                  (play_info['home_score'], play_info['away_score']) = previousscore
                else:
                  previousscore=(play_info['home_score'], play_info['away_score'])
                
                #Have to do this becuase some names have commans in them...
                if play_info['player']:
                  temp = play_info['player'].split(",")
                  play_info['player'] = "".join(temp)

                if play_info['event'] != 'Substitution: replaces':
                  play_entry = [
                    game_ID,
                    play_info['quarter'],
                    play_info['clock'],
                    play_info['home_score'],
                    play_info['away_score'],
                    play_info['team'],
                    play_info['number'],
                    play_info['player'],
                    play_info['event'],
                  ]
                  playwriter.writerow(play_entry)
                
                if j==0:
                  firstplay=play
