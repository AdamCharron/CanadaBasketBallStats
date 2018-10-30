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

event_name_1_POINT = ["1st free throw made",
                      "1st of 1 free throw made",
                      "1st of 2 free throw made",
                      "1st of 2 free throws made",
                      "1st of 3 free throw made",
                      "1st of 3 free throws made",
                      "1st of 3 free throws missed",
                      "2nd of 2 free throws made",
                      "2nd of 3 free throws made",
                      "3rd of 3 free throws made",
                      "free throw made"]

event_name_2_POINTS = ["2pt jump shot made",
                       "2pt shot made",
                       "alley oop made",
                       "dunk made",
                       "layup made",
                       "tip in made"]

event_name_3_POINTS = ["3pt jump shot made", "3pt shot made"]

event_name_TURNOVERS = ["turnover",
                        "turnover; 3 seconds violation",
                        "turnover; 5 seconds violation",
                        "turnover; backcourt violation",
                        "turnover; bad pass",
                        "turnover; ball handling",
                        "turnover; goaltending",
                        "turnover; irregular dribble (ball handling)",
                        "turnover; out of bounds",
                        "turnover; travelling"]
                        
event_name_REBOUNDS = ["offensive rebound", "defensive rebound"]
event_name_BLOCK = ["blocked the shot"]

event_name_FOUL = ["disqualifying foul",
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


event_name_SHOT_ATTEMPTS = ["2pt jump shot made",
                            "2pt jump shot missed",
                            "2pt shot made",
                            "2pt shot missed",
                            "3pt jump shot made",
                            "3pt jump shot missed",
                            "3pt shot made",
                            "3pt shot missed",
                            "alley oop made",
                            "alley oop missed",
                            "dunk made",
                            "dunk missed",
                            "layup made",
                            "layup missed",
                            "tip in made",
                            "tip in missed"]
