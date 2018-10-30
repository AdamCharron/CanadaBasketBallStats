# For stats
s_MINUTES = 0
s_POINTS = 1
s_TURNOVERS = 2
s_REBOUNDS = 3
s_BLOCK = 4
s_FOUL = 5
s_SHOT_ATTEMPTS = 6
s_3_POINTERS = 7
s_MINUTES_AVERAGE = 10
s_POINTS_AVERAGE = 11
s_TURNOVERS_AVERAGE = 12
s_REBOUNDS_AVERAGE = 13
s_BLOCK_AVERAGE = 14
s_FOUL_AVERAGE = 15
s_SHOT_ATTEMPTS_AVERAGE = 16
s_3_POINTERS_AVERAGE = 17

stat_filenames = {
    s_MINUTES : "minutes",
    s_POINTS : "points",
    s_TURNOVERS : "turnovers",
    s_REBOUNDS : "rebounds",
    s_BLOCK : "blocks",
    s_FOUL : "fouls",
    s_SHOT_ATTEMPTS : "shot_attempts",
    s_3_POINTERS : "three_pointers",
    s_MINUTES_AVERAGE : "minutes_avg",
    s_POINTS_AVERAGE : "points_avg",
    s_TURNOVERS_AVERAGE : "turnovers_avg",
    s_REBOUNDS_AVERAGE : "rebounds_avg",
    s_BLOCK_AVERAGE : "blocks_avg",
    s_FOUL_AVERAGE : "fouls_avg",
    s_SHOT_ATTEMPTS_AVERAGE : "shot_attempts_avg",
    s_3_POINTERS_AVERAGE : "three_pointers_avg"
    }

# Lookup for which events in the enriched PlayByPlay constitute which stats

#Points events
event_1PT = ["1st free throw made",
                      "1st of 1 free throw made",
                      "1st of 2 free throw made",
                      "1st of 2 free throws made",
                      "1st of 3 free throw made",
                      "1st of 3 free throws made",
                      "2nd of 2 free throws made",
                      "2nd of 3 free throws made",
                      "3rd of 3 free throws made",
                      "free throw made"]

event_2PT = ["2pt jump shot made",
                       "2pt shot made",
                       "alley oop made",
                       "dunk made",
                       "layup made",
                       "tip in made"]

event_3PT = ["3pt jump shot made", "3pt shot made"]

event_PTS = event_1PT + event_2PT + event_3PT

#Shot attempts events
event_FGM = event_2PT + event_3PT

event_2FGA = ["2pt jump shot made",
              "2pt jump shot missed",
              "2pt shot made",
              "2pt shot missed",
              "alley oop made",
              "alley oop missed",
              "dunk made",
              "dunk missed",
              "layup made",
              "layup missed",
              "tip in made",
              "tip in missed"]

event_3FGA = ["3pt jump shot made",
              "3pt jump shot missed",
              "3pt shot made",
              "3pt shot missed"]

event_FGA = event_2FGA + event_3FGA

#Free throws events
event_FTM = event_1PT

event_FT_missed = [ "1st free throw missed",
                    "1st of 1 free throw missed",
                    "1st of 2 free throw missed",
                    "1st of 2 free throws missed",
                    "1st of 3 free throws missed",
                    "2nd of 2 free throws missed",
                    "2nd of 3 free throws missed",
                    "3rd of 3 free throws missed",
                    "free throw missed"]

event_FTA = event_FTM + event_FT_missed

#Rebounds events
event_OREB = ["offensive rebound", "team offensive rebound"]
event_DREB = ["defensive rebound", "team defensive rebound"]
event_REB = event_OREB + event_DREB

#Other events
event_AST = ["made the assist"]

event_PF = ["Bench: technical foul", #What counts as "Personal Foul"?
            "Coach: technical foul",
            "disqualifying foul",
            "offensive foul",
            "offensive foul; 1 free throw awarded",
            "offensive foul; 2 free throws awarded",
            "personal foul",
            "personal foul; 1 free throw awarded",
            "personal foul; 2 free throws awarded",
            "personal foul; 3 free throws awarded",
            "technical foul",
            "technical foul; 1 free throw awarded",
            "technical foul; 2 free throws awarded",
            "technical foul; 3 free throws awarded",
            "unsportsmanlike foul",
            "unsportsmanlike foul; 1 free throw awarded",
            "unsportsmanlike foul; 2 free throws awarded"]

event_TO = ["turnover",
            "turnover; 3 seconds violation",
            "turnover; 5 seconds violation",
            "turnover; backcourt violation",
            "turnover; bad pass",
            "turnover; ball handling",
            "turnover; goaltending",
            "turnover; irregular dribble (ball handling)",
            "turnover; out of bounds",
            "turnover; travelling",
            "team turnover; 24 seconds violation",
            "team turnover; 8 seconds violation"]

event_STL = ["steal"]

event_BLK = ["blocked the shot"]

event_SUB = [ "Substitution in", 
              "Substitution out", 
              "Substitution: replaces"]
