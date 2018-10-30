#Baller Boys Basketball Matchup Tool
A basketball lineups tool used to evaluate the performance
of various lineup combinations from FIBA Play-by-Play data.

#Overview
This project has 4 main parts:

1) Web scraping: Pull data from tournament URLs
2) Enrichment and validation: Add more detailed info in Play-by-Play events. Verify data integrity.
3.1) Matchup Analytics: Main part of the tool. Display stats for each lineup that exist and how they performed against other opponent lineups. 
3.2) Individual Analytics: Various analytics of individuals such as heatmaps.
4) User Interface: Ability to use tool and selectively parse results.

#Packages and Dependencies
From scraper/scraper.py:
1) Python3
2) pandas (version '0.23.0')
3) csv (version '1.0')
4) requests (version '2.18.4')
5) bs4 (version '4.6.0')

From analytics/get_lineups.py
1) six (version '1.11.0')
