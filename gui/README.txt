minute_heatmap_gui.py is the main file for the gui for minutes heatmaps.
Running it will generate a heatmap of minutes player for all players in 
the list at the bottom of the file.

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

Other files are useful external pieces of code:
    - colours.py, (NEEDED) which provides the list of all available colours for the heatmap boxes.
    - simple_grid.py, (NEEDED) which contains the code to visualize the heatmap