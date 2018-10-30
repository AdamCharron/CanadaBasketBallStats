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

'''
Utils file to hold helper functions for the scraper.py file.
'''

def getSoup(link):
  '''
  Keep polling a website url until HTML content is extracted.

  Args:
    link: url string of website page to extract HTML from

  Returns:
    BeautifulSoup Object containing HTML extracted from website
  '''
  nolink=True
  while nolink:               
    res=requests.get(link, verify=False) #Don't check certificates
    try:
      res.raise_for_status()
      nolink=False
    except requests.exceptions.HTTPError: #http request has errors
      pass           
    except requests.exceptions.Timeout: #too long to connect
      pass
    except requests.exceptions.TooManyRedirects: #tried to connect repeatedly
      pass
    except requests.exceptions.ChunkedEncodingError: #broken connection; retry
      pass
    except requests.exceptions.RequestException as e:  #all other exceptions
      print (e)
  return BeautifulSoup(res.text,'lxml')

def formatdate(d,MONTHS):
  '''
  Args:
    d: string
       day, month and year separated by a space. Month is in words
    MONTHS: dictionary
      dictionary mapping month names to numbers
  '''
  day,month,year=d.split(' ')  
  month=MONTHS[month]
#  print(datetime.datetime(int(year),month,int(day)))
  return datetime.datetime(int(year),month,int(day))

def formatdatenoyear(d, MONTHS, year):
  '''
  Args:
    d: string
       day and month separated by a space. Month is in words
    MONTHS: dictionary
      dictionary mapping month names to numbers
    year: string
       4 digit year
    
  '''  
  month, day=d.split(' ')
  month=MONTHS[month]
#  print(datetime.datetime(int(year),month,int(day)))
  return datetime.datetime(int(year),month,int(day))

def cleanString(string):
  ''''
  Don't actually know what this does.

  Args:
    string: don't know

  Returns:
    "Cleaned string"?
  '''
  return unidecode(normalize('NFKD',string))


def getGameData(Soup):
  ''''
  Yea Jamal just fill this in later.

  Args:
    Soup: BeautifulSoup Object containing all HTML data from a webpage

  Returns:
    relevant info
  '''
  #Extract basic box score data only
  gamedata = Soup.find(class_='module__header-scores')

  Round=gamedata.find(class_='phase-info').text.strip().replace('\n',' - ')
  if '[' in Round:
    Round=Round[:Round.find('[')].strip()
      
  location_soup = gamedata.find(class_='location')
  location = cleanString(location_soup.text.strip()) if location_soup else ""

  hometeam=gamedata.find(class_='team-A').text.strip()
  awayteam=gamedata.find(class_='team-B').text.strip()
  score=gamedata.find(class_='final-score').text.strip()
  homescore,awayscore =score.split('\n')
  
  game_info = {"round": Round,
               "location": location, 
               "home_team": hometeam, 
               "away_team": awayteam, 
               "home_score": homescore,
               "away_score": awayscore}
  return game_info 


def getPlayData(play):
  ''''
  Yea Jamal just fill this in later.

  Args:
    Soup: BeautifulSoup Object containing all HTML data from a webpage

  Returns:
    relevant info
  '''
  time=play.find(class_='occurrence-info').text.split('\r')
  quarter=time[0].strip().strip('Q')
  if quarter[:2]=="OT":
    quarter=int(quarter[2:])+4
  clock=time[-1].strip()

  number=''
  player=play.find(class_='athlete-name')
  if player != None:
    player=player.text.strip()
    player=cleanString(player)
    number=play.find(class_='bib').text
  #if '-' in player[:player.find('#')]:
   # player=player[player.find(' ')+1:]
    #  number=player[:player.find(' ')].strip('#')
     # player=player[player.find(' ')+1:]        

  homescore=play.find(class_='score-A').text
  awayscore=play.find(class_='score-B').text

  #player=player[player.find(' ')+1:]
  
  event=play.find(class_='action-description').text.strip()    
  team=play['class'][1][-1]

  play_info = {"quarter": quarter, 
               "clock": clock,
               "home_score": homescore,
               "away_score": awayscore,
               "team": team,
               "number": number,
               "player": player,
               "event": event}
  return play_info 


def getMostRecentGameInfo(gamefile, 
                            csv_delimiter=',', print_info=False):
  ''''
  Gets the most recently played date and game_ID from the game IDs csv.
  If the file doesn't exist, "most recent" date is initialized 
  to 1800 and game_ID initialized to 1.

  Args:
    filename: str
      file path of game id csv file 

    csv_delimiter: str
      string used to separate elements in rows (default = ',')

    print_info: boolean

  Returns:
    last_dates_hash: hash{tournament_name: datetime.date}
      dates of most recently played game date for each tournament

    game_ID: int
      ID of the most recently played game
  '''
  last_dates_hash = {}
  try: #2 possible errors: 1) csvfile doesn't exist; 2) csvfile has no data
    df = pd.read_csv(gamefile, sep=csv_delimiter)
    df.set_index('Game ID', inplace=True)

    #Get last date for each tournament
    last_entries_df = df.groupby('Tournament', as_index=False)\
                                      ['Date'].max()
    for idx, row in last_entries_df.iterrows():
      date_str = row['Date']
      date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
      name = row['Tournament']
      last_dates_hash[name] = date
    if print_info:
      print('\nLast rows extracted:\n{}; \n'.format(last_entries_df))

    #Get GameID from last row
    last_row = df.tail(1)
    game_ID = int(last_row.index.tolist()[0])

  except:
    game_ID = 0
    if print_info:
      print('\nCould not extract last row of {}\n'.format(gamefile))

  return last_dates_hash, game_ID
                   

def writeHeadingsIfNeeded(game_file,
                          play_file,
                          boxscore_file,
                          game_heading,
                          play_heading,
                          boxscore_heading):
  '''
  If files don't exist, write headings as the first row.
  
  '''
  def writeHeading(filepath, header):
    if not os.path.isfile(filepath):
      print("Could not find {}! Writing header...".format(filepath))
      fd = open(filepath,'w', newline='')
      csv.writer(fd).writerow(header)
      fd.close()
    return
  
  writeHeading(game_file, game_heading)
  writeHeading(play_file, play_heading)
  writeHeading(boxscore_file, boxscore_heading)
  return


def saveBackUpIfExists(game_filepath, play_filepath, boxscore_filepath):
  '''
  If files exist, record the current date as YYYY_MM_DD_hh_mm and
  save it as filename_[date].[extension]
  
  Args:
    game_filepath: string
      file which contains game_file data

    play_filepath: string
      file which contains play_file data

    boxscore_filepath: string
      file which contains boxscore_file data
  
  Returns:
    None

  '''
  timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
  
  def saveBackUp(filepath, timestamp):
    if not os.path.isfile(filepath):
      return
    filename, extension = os.path.splitext(filepath)
    new_filepath = filename + "_" + timestamp + extension
    print("Copying file {} to {} ...".format(filepath, new_filepath))
    copyfile(filepath, new_filepath)
    return
  
  saveBackUp(game_filepath, timestamp)
  saveBackUp(play_filepath, timestamp)
  saveBackUp(boxscore_filepath, timestamp)
  return

def getTournamentNamesAndURLS(tournament_root_dir, url_filename,
                                name_filename):
  '''
  Args:
    tournament_root_dir: string
      directory containing tournament info files

    url_filename: string
      name of file containing tournament urls (1 for each line)

    name_filename: string
      name of file containing tournament names (1 for each line)
  
  Returns:
    tournament_info: array[tuple(name,url)]
      array of tuples containing tournament (name, url)
  '''
  urls_filepath = os.path.join(tournament_root_dir, 
                                        url_filename)
  names_filepath = os.path.join(tournament_root_dir, 
                                        name_filename)

  #Check that tournament info files exist
  if not os.path.exists(tournament_root_dir):
    print(("Tournament info folder ({}) does not exist! Please make one "
            "and put your ({}) and ({}) files in there.").\
            format(tournament_root_dir, url_filename, 
                    name_filename))
    sys.exit()
  elif not os.path.isfile(urls_filepath):
    print(("Tournament schedule URL file ({}) does not exist within folder "
            "({}). Please add it into the folder.").\
            format(url_filename, tournament_root_dir))
    sys.exit()
  elif not os.path.isfile(names_filepath):
    print(("Tournament name file ({}) does not exist within tournament "
            "info folder ({}). Please add it to folder.").\
            format(name_filename, tournament_root_dir))
    sys.exit()
  
  #Read the tournament names and urls line by line
  def readLinesToArray(filepath):
    array = []
    with open(filepath, 'r') as fd:
      for line in fd:
        line = line.strip()
        if line: #Not an empty string
          array.append(line)
    return array

  names = readLinesToArray(names_filepath)
  urls = readLinesToArray(urls_filepath)

  if len(names) != len(urls):
    print(("Number of tournament names and urls in {} and {} do not match! "
            "Please ensure the names and urls match in the correct order.").\
            format(name_filename, url_filename))
    sys.exit()
  
  #Create and return tournament info hash
  tournament_info = []
  for name, url in zip(names,urls):
    tournament_info.append((name, url))

  return tournament_info



