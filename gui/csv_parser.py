import csv
from pprint import pprint


def csv_to_dict(path):
    # Read through the heatmap CSV and output a dict representation of it
    d = {}
    with open(path, 'r') as f:
        # Start by gathering all the fields for later use
        titles = f.readline().split(',')
        titles.pop(0)
        print(titles)

        for line in f:
            x = line.strip().split(',')
            # x[0] = country name
            # x[1] = player name
            # x[2] = Q1 - minute 1
            # x[3] = Q1 - minute 2
            # ...
            # x[41] = Q4 - minute 10
            if x[0] not in d:
                d[x[0]] = {}
            if x[1] not in d[x[0]]:
                d[x[0]][x[1]] = []
            d[x[0]][x[1]] = x[2:]
    
    return d


if __name__=='__main__':
    path = '../data/minutes_heatmap.csv'
    print(csv_to_dict(path))
