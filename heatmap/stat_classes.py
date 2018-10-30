import os
import re
from abc import ABC, abstractmethod
from stat_type_lookups import *
from enum import Enum

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

class Player:
    def __init__(self, name, team):
        self.name = name
        self.team = team
        self.games_played = []

        self.Minutes = Minutes()
        self.Points = Points()
        self.Turnovers = Turnovers()
        self.Rebounds = Rebounds()
        self.Fouls = Fouls()
        self.Shots = Shots()
        self.ThreePointers = ThreePointers()

    def normalize(self):
        GP = len(self.games_played)
        if GP > 0:
            self.Minutes.normalize(GP)
            self.Points.normalize(GP)
            self.Turnovers.normalize(GP)
            self.Rebounds.normalize(GP)
            self.Fouls.normalize(GP)
            self.Shots.normalize(GP)
            self.ThreePointers.normalize(GP)
            
    def ResetStatTimes(self):
        self.Minutes.lastTime = -1
        self.Points.lastTime = -1
        self.Turnovers.lastTime = -1
        self.Rebounds.lastTime = -1
        self.Fouls.lastTime = -1
        self.Shots.lastTime = -1
        self.ThreePointers.lastTime = -1
        

class Team:
    def __init__(self, team):
        self.team = team
        self.roster = { 'TOTAL': Player('TOTAL', self.team) }

    def check_player(self, name):
        return name in self.roster

    def add_player(self, player):
        if not self.check_player(player.name):
            self.roster[player.name] = player
        #else:
        #    print('Invalid! ' + name + ' already on the team')

    def normalize_stats(self):
        for player in self.roster:
            self.roster[player].normalize()

    def write_results(self, dataPath, basename):
        for name, player in self.roster.items():
            player.Minutes.WriteOut(dataPath, basename, player.team, player.name)
            player.Points.WriteOut(dataPath, basename, player.team, player.name)
            player.Turnovers.WriteOut(dataPath, basename, player.team, player.name)
            player.Rebounds.WriteOut(dataPath, basename, player.team, player.name)
            player.Fouls.WriteOut(dataPath, basename, player.team, player.name)
            player.Shots.WriteOut(dataPath, basename, player.team, player.name)
            player.ThreePointers.WriteOut(dataPath, basename, player.team, player.name)
            

class Stat(ABC): 
    def __init__(self):
        # All data provided in the following logs used 10-minute quarters
        # Except for minute, logs are broken up into:
        #   x_log -> cumulative occurrences of x across timeslots of all games
        #   x_dist_log -> games in which x occurs in each timeslot
        #   ie if a player gets 2 layups in Q2 min:3,
        #       point_log[Q,M] += 4 and point_dist_log[Q,M] += 1
        self.stat = 0
        self.log = [0]*4*10
        self.dist_log = [0]*4*10
        self.eventList = []
        self.lastTime = -1
        super().__init__()
    
    @abstractmethod
    def add(self, quarter, time, value = 1):
        return NotImplemented

    @abstractmethod
    def add_dist(self, quarter, time, value = 1):
        return NotImplemented

    def update(self, event):
        if event[PlayByPlayHeader.Event.value] in self.eventList:
            self.add(event[PlayByPlayHeader.Quarter.value],
                     event[PlayByPlayHeader.Time.value])
            time = get_minute(event[PlayByPlayHeader.Time.value])\
                   + (int(event[PlayByPlayHeader.Quarter.value])-1)*10
            if time > self.lastTime:
                self.lastTime = time
                self.add_dist(event[PlayByPlayHeader.Quarter.value],
                              event[PlayByPlayHeader.Time.value])

    def normalize(self, gamesPlayed):
        if gamesPlayed > 0:
            for i in range(len(self.dist_log)):
                self.dist_log[i] = float(self.dist_log[i]/gamesPlayed)

    def outputWrite(self, dataPath, basename, teamname, playername):
        filename = os.path.join(dataPath, stat_filenames[self.stat] + "_" + \
                                basename + ".csv")
        out_str = '\n' + teamname + ',' + playername + ','
        with open(filename, 'a') as f: 
            out_str += ','.join([str(i) for i in self.log])
            f.write(out_str)

    def outputDistWrite(self, dataPath, basename, teamname, playername):
        filename = os.path.join(dataPath, stat_filenames[self.stat] + "_avg_" + \
                                basename + ".csv")
        out_str = '\n' + teamname + ',' + playername + ','
        with open(filename, 'a') as f: 
            out_str += ','.join([str(i) for i in self.dist_log])
            f.write(out_str)

    def WriteOut(self, dataPath, basename, teamname, playername):
        self.outputWrite(dataPath, basename, teamname, playername)
        self.outputDistWrite(dataPath, basename, teamname, playername)

class Minutes(Stat):
    def __init__(self):
        super().__init__()
        self.stat = s_MINUTES

    def add(self, quarter, time, value = 1):
        pass

    def add_dist(self, quarter, time, value = 1):
        self.dist_log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

    def WriteOut(self, dataPath, basename, teamname, playername):
        self.outputDistWrite(dataPath, basename, teamname, playername)

class Points(Stat):
    def __init__(self):
        super().__init__()
        self.stat = s_POINTS
        self.eventList = [event_name_1_POINT, event_name_2_POINTS, event_name_3_POINTS]

    def add(self, quarter, time, value = 1):
        self.log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

    def add_dist(self, quarter, time, value = 1):
        self.dist_log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

    def update(self, event):
        newTime = False
        time = get_minute(event[PlayByPlayHeader.Time.value]) + \
                   (int(event[PlayByPlayHeader.Quarter.value])-1)*10
        for i in range(3):
            if event[PlayByPlayHeader.Event.value] in self.eventList[i]:
                self.add(event[PlayByPlayHeader.Quarter.value],
                         event[PlayByPlayHeader.Time.value], i+1)
                if time > self.lastTime:
                    newTime = True
                    self.add_dist(event[PlayByPlayHeader.Quarter.value],
                                  event[PlayByPlayHeader.Time.value])
        if (newTime): self.lastTime = time

class Turnovers(Stat):
    def __init__(self):
        super().__init__()
        self.stat = s_TURNOVERS
        self.eventList = event_name_TURNOVERS

    def add(self, quarter, time, value = 1):
        self.log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

    def add_dist(self, quarter, time, value = 1):
        self.dist_log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

class Rebounds(Stat):
    def __init__(self):
        super().__init__()
        self.stat = s_REBOUNDS
        self.eventList = event_name_REBOUNDS

    def add(self, quarter, time, value = 1):
        self.log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

    def add_dist(self, quarter, time, value = 1):
        self.dist_log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

class Blocks(Stat):
    def __init__(self):
        super().__init__()
        self.stat = s_BLOCK
        self.eventList = event_name_BLOCK

    def add(self, quarter, time, value = 1):
        self.log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

    def add_dist(self, quarter, time, value = 1):
        self.dist_log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

class Fouls(Stat):
    def __init__(self):
        super().__init__()
        self.stat = s_FOUL
        self.eventList = event_name_FOUL

    def add(self, quarter, time, value = 1):
        self.log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

    def add_dist(self, quarter, time, value = 1):
        self.dist_log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

class Shots(Stat):
    def __init__(self):
        super().__init__()
        self.stat = s_SHOT_ATTEMPTS
        self.eventList = event_name_SHOT_ATTEMPTS

    def add(self, quarter, time, value = 1):
        self.log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

    def add_dist(self, quarter, time, value = 1):
        self.dist_log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

class ThreePointers(Stat):
    def __init__(self):
        super().__init__()
        self.stat = s_3_POINTERS
        self.eventList = event_name_3_POINTS

    def add(self, quarter, time, value = 1):
        self.log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value

    def add_dist(self, quarter, time, value = 1):
        self.dist_log[get_minute(time) - 1 + 10*(int(quarter)-1)] += value


def get_minute(time):
    if re.search('\d\d?:\d\d', time) == None: return None
    minute = int(re.sub(':\d\d', '', time))
    if minute > 10 or minute < 0: return None
    if minute == 10: return 1
    return 10 - minute


if __name__ == '__main__':
    a = Points()
    b = Points()
    c = Minutes()

    a.add(1,'10:00', 5)
    a.add(3,'01:00')
    b.add(4,'04:00', 2)
    c.add(4,'02:00', 1)
    a.add_dist(1,'10:00')
    a.add_dist(3,'01:00')
    b.add_dist(4,'04:00')
    c.add_dist(4,'02:00')

    print('\nBefore normalization:')
    print(a.log)
    print(b.log)
    print(c.log)
    print('')
    print(a.dist_log)
    print(b.dist_log)
    print(c.dist_log)

    a.normalize(4)
    c.normalize(4)
    b.normalize(4)

    print('\nAfter normalization:')
    print(a.log)
    print(b.log)
    print(c.log)
    print('')
    print(a.dist_log)
    print(b.dist_log)
    print(c.dist_log)
