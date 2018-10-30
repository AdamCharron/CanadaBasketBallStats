import os
import pickle

# Path and filename of the pickle log file
#logger_file_path = './heatmap_search_log.pickle'
logger_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heatmap_search_log.pickle')

class Logger:
    def __init__(self, teams = [], opponents = [], games = [], verbose = False):
        self.filename = logger_file_path
        self.verbose = verbose
        self.log = {}
        self.start_log()
        if len(teams) > 0: self.add_teams(teams)
        if len(opponents) > 0: self.add_opponents(opponents)
        if len(games) > 0: self.add_games(games)

    def start_log(self):
        self.log['teams'] = []
        self.log['opponents'] = []
        self.log['games'] = []

    def add_teams(self, teams):
        if isinstance(teams, str): teams = [teams]
        for t in teams:
            if t not in self.log['teams']:
                self.log['teams'].append(t)

    def add_opponents(self, opponents):
        if isinstance(opponents, str): opponents = [opponents]
        for t in opponents:
            if t not in self.log['opponents']:
                self.log['opponents'].append(t)

    def add_games(self, games):
        if isinstance(games, str): games = [games]
        if isinstance(games, int): games = [int(games)]
        for g in games:
            if str(g) not in self.log['games']:
                self.log['games'].append(str(g))

    def overwrite_teams(self, teams):
        self.log['teams'] = []
        self.add_teams(teams)

    def overwrite_opponents(self, opponents):
        self.log['opponents'] = []
        self.add_opponents(opponents)

    def overwrite_games(self, games):
        self.log['games'] = []
        self.add_games(games)

    def dump_logger(self):
        with open(self.filename,'wb') as f:
            pickle.dump(self.log, f, pickle.HIGHEST_PROTOCOL)

    def load_last_logger(self):
        p = self.get_last_logger()
        if p == None: return
        for country in p['teams']:
            self.add_teams(country)
        for country in p['opponents']:
            self.add_opponents(country)
        for game in p['games']:
            self.add_games(game)

    def get_last_logger(self):
        if self.verbose: print("Loading data from {}, hold on".format(self.filename))
        if os.path.isfile(self.filename):
            return pickle.load( open( self.filename, "rb" ))
        return None

    def print_current_logger(self):
        print(self.get_current_logger())

    def get_current_logger(self):
        return self.log


if __name__ == '__main__':
    
    # Load the last logger results
    oldLogger = Logger()
    oldLogger.load_last_logger()
    oldLogger.print_current_logger()

    # Create new logger that stores the following teams and games
    teams = ['CAN', 'USA', 'SOM']
    opponents = ['BRA']
    games = [2,5,12]
    newLogger = Logger(teams, opponents, games)
    newLogger.print_current_logger()
    newLogger.dump_logger()
