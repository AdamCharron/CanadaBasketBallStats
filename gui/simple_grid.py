'''
Based on code from:
https://stackoverflow.com/questions/29267532/heat-map-from-data-points
'''

import sys
sys.path.insert(0, '../enrich')
sys.path.insert(0, '../heatmap')
from tkinter import *
from colours import *
from stat_type_lookups import *
from convert_country_names import *
import random
import re


class ScrollEvent:
    def __init__(self, canvas):
        self.canvas = canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def assign_colour(country_list):
    colour_assignment = {}
    colour_list = ['red3', 'medium blue', 'dark green', 'gold4']
    colours = list(COLORS)
    while country_list != []:
        # The first 4 countries will use the colour list provided in order
        # Using more than 4 countries is unlikely due to visual space, but
        # in the event that more than 4 are used, colours from colours.py will
        # be randomly selected (not the most robust, but wasn't about to hardcode
        # the order of >100 colours for different countries
        if colour_list != []:
            c = colour_list.pop(0)
            colour_assignment[country_list.pop(0)] = c
            colours.remove(c)
        else:
            if colours == []: 
                # If we run out of colours in total (extremely unlikely), then
                # just replenish the colours list from the array in colours.py
                colours = list(COLORS)
            rand_int = random.randint(0,len(colours)-1)
            c = colours[rand_int]
            colour_assignment[country_list.pop(0)] = c
            colours.remove(c)
    return colour_assignment

def compute_colours(root, value, minval, maxval, start_colour, end_colour):
    (r1,g1,b1) = root.winfo_rgb(start_colour)
    (r2,g2,b2) = root.winfo_rgb(end_colour)
    #limit = 1
    limit = maxval-minval
    r_ratio = float(r2-r1) / limit
    g_ratio = float(g2-g1) / limit
    b_ratio = float(b2-b1) / limit

    nr = int(r1 + (r_ratio * value))
    ng = int(g1 + (g_ratio * value))
    nb = int(b1 + (b_ratio * value))
    return "#%4.4x%4.4x%4.4x" % (nr,ng,nb)

def visualize(inputInfoList, heat_map, players, stats, numeric_display_flag = True):
    root = Tk()
    start_colour = "white"

    f = Frame(root)
    f.pack(fill=BOTH)
    c = Canvas(f)

    # Get longest name in the players list
    char_offset = -1
    for p in players:
        char_offset = max(char_offset,
                          max(list(map(lambda x: \
                                       len(x[0][0] + \
                                           x[0].split(' ')[len(x[0].split(' '))-1]), p))))
    char_offset += 6
    offset = 9*char_offset

    for i in range(len(players)):

        # Set up bounds
        heat_min = min(min(temp for temp in row) for row in heat_map[i])
        heat_max = max(max(temp for temp in row) for row in heat_map[i])
        width, height = 1300, 22*len(players[i])

        # Fix up the player names being used
        for j in range(len(players[i])):
            if players[i][j][0] == "TOTAL": continue
            players[i][j][0] = players[i][j][0][0] + '. ' + \
                            players[i][j][0].split(' ')[len(players[i][j][0].split(' '))-1]

        frame = Frame(c)
        frame.pack(fill=BOTH)

        label = Label(frame,
                      text="{} Heatmap for {} against {} in games {}".format(
                          stat_filenames[stats[i]],
                          ', '.join(inputInfoList[i].teams),
                          ', '.join(inputInfoList[i].opponents),
                          ', '.join(inputInfoList[i].games)))
        label.pack()

        # Assign colours for each country
        colour_assignment = assign_colour(inputInfoList[i].teams)

        # Create canvas
        canvas = Canvas(frame, width=width + offset, height=height)
        scroller = ScrollEvent(canvas)
        rect_width = (width - offset) // 40
        rect_height = (height-len(players[i])-1) // len(heat_map[i])

        # Create timeline
        timeline = ''
        for j in range(1,5):
            timeline += 'Q' + str(j) + ' '*int(3.18*rect_width)
        canvas.create_text(int(2.7*offset), 0, text=timeline, anchor="nw", font=('Helvetica', '8'))

        for y, row in enumerate(heat_map[i]):
            # Determine shapes and positions of names
            x0, y0 = offset, (y+1) * rect_height
            y1 = y0 + rect_height-1
            country = players[i][y][1]
            player = "({}) {}".format(LOOKUP_FULLNAME[country], players[i][y][0])

            # Change colour depending on the team
            #end_colour = "red3"
            end_colour = colour_assignment[country]

            canvas.create_text(x0, (y0+y1)/2, text=player)
            for x, num in enumerate(row):
                # Determine shapes and positions of data entries
                x0, y0 = x * rect_width + 2*offset, (y+1) * rect_height
                x1, y1 = x0 + rect_width-1, y0 + rect_height-1
                colour = compute_colours(root, num, heat_min, heat_max, start_colour, end_colour)
                canvas.create_rectangle(x0, y0, x1, y1, fill=colour, width=0)
                if numeric_display_flag:
                    canvas.create_text(((x0+x1)/2, (y0+y1)/2), text="%.2f"%num, font=('Helvetica', '8'))

        # Add quarter borders
        y_range = [rect_height, len(players[i]) * rect_height + rect_height-1]
        for i in range(1,4):
            x = 10 * i * rect_width + 2*offset
            canvas.create_line(x, y_range[0], x, y_range[1], width=2)

        # Scroll bars
        vbar=Scrollbar(frame,orient=VERTICAL)
        vbar.pack(side=RIGHT,fill=Y)
        vbar.config(command=canvas.yview)
        canvas.configure(scrollregion = canvas.bbox("all"))
        canvas.pack(fill=BOTH)

    s = ScrollEvent(c)
    v=Scrollbar(c,orient=VERTICAL)
    v.pack(side=RIGHT,fill=Y)
    v.config(command=c.yview)
    c.configure(scrollregion = c.bbox("all"))
    c.pack(fill=BOTH)

    root.mainloop()   


