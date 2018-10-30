import re
import csv
import os
import sys
import pickle
from pprint import pprint
from enum import Enum
sys.path.insert(0, '../heatmap')
sys.path.insert(0, '../tests')
from stat_type_lookups import *
from tester import *

# Types of files:
#   Fundamental files
#       - PlayByPlay.csv, GameIDs.csv, BoxscoreStats.csv
#       - Run after scraper
#       - Generate pickles right after
#   Enriched
#       - PlayByPlay_enriched.csv
#       - Run during enrich
#       - Generate pickle right after
#   Heatmap Stats
#       - *_heatmap.csv
#       - Run for relevent stats (can be all), for specific games and teams
#       - Generate pickles right after
#   Lineups
#       - lineups_*.csv
#       - That's up to Rossdan (assume it's his problem)

class CSVTypes(Enum):
    Fundamentals = 0
    Enriched = 1
    Heatmap = 2
    All = 3

class PickleParser:

    def __init__(self, root, verbose = False):
        self.root = root
        self.verbose = verbose
        
        # Lists of filenames
        self.fundamentalFiles = ['PlayByPlay.csv', 'GameIDs.csv', 'BoxscoreStats.csv']
        self.enrichedFiles = ['PlayByPlay_enriched.csv']
        self.statFiles = list(stat_filenames.values())
        for i in range(len(self.statFiles)):
            self.statFiles[i] += '_heatmap.csv'

    def IterateOverPickles(self, task):
        for subdir, dirs, fs in os.walk(self.root):
            for f in fs:
                filename = os.path.join(subdir, f)
                if task == 'save' and filename.endswith('.csv'):
                    self.Serialize(filename)
                elif task == 'remove' and filename.endswith('.pickle'):
                    if self.verbose: print("Removing file: {}".format(filename))
                    os.remove(filename)

    def SavePicklesInRoot(self):
        self.IterateOverPickles('save')

    def RemovePicklesFromRoot(self):
        self.IterateOverPickles('remove')

    def GetAllEnrichedFiles(self):
        allEnrichedFiles = list(self.enrichedFiles)
        for subdir, dirs, items in os.walk(self.root):
            for item in items:
                if re.match(".*PlayByPlay_enriched_game[\d]+\.csv", item):
                    allEnrichedFiles.append(item)
        return allEnrichedFiles

    def GetAllHeatmapFiles(self):
        allHeatmapFiles = list(self.statFiles)
        for subdir, dirs, items in os.walk(self.root):
            for item in items:
                if item.endswith("_heatmap.csv"):
                    allHeatmapFiles.append(item)
        return allHeatmapFiles

    def SaveTypesToPickles(self, types = []):
        if type(types) != list: types = [types]
        if types == [] or types == [CSVTypes.All.value]:
            self.SaveTypesToPickles([CSVTypes.Fundamentals.value,
                               CSVTypes.Enriched.value,
                               CSVTypes.Heatmap.value])
        if CSVTypes.Fundamentals.value in types:
            self.Remove(self.fundamentalFiles, '.pickle')
            self.Serialize(self.fundamentalFiles)
        if CSVTypes.Enriched.value in types:
            allEnrichedFiles = self.GetAllEnrichedFiles()
            self.Remove(allEnrichedFiles, '.pickle')
            self.Serialize(allEnrichedFiles)
        if CSVTypes.Heatmap.value in types:
            allEnrichedFiles = self.GetAllHeatmapFiles()
            self.Remove(allEnrichedFiles, '.pickle')
            self.Serialize(allEnrichedFiles)

    def RemovePicklesOfType(self, csvType, fileType):
        if fileType != '.csv': fileType = '.pickle'
        if csvType == CSVTypes.All.value:
            self.Remove([CSVTypes.Fundamentals.value,
                               CSVTypes.Enriched.value,
                               CSVTypes.Heatmap.value])
        if csvType == CSVTypes.Fundamentals.value:
            self.Remove(self.fundamentalFiles, fileType)
        if csvType == CSVTypes.Enriched.value:
            self.Remove(self.GetAllEnrichedFiles(), fileType)
        if csvType == CSVTypes.Heatmap.value:
            self.Remove(self.GetAllHeatmapFiles(), fileType)

    def Remove(self, files = [], fileType = '.pickle'):
        if type(files) == str: files = [files]
        for csvF in files:
            csvfilename = os.path.join(self.root, csvF)
            filename = str(os.path.splitext(csvfilename)[0]) + fileType
            if os.path.isfile(filename):
                if self.verbose: print("Removing file: {}".format(filename))
                os.remove(filename)

    def RemovePickles(self, inVal = None):
        if inVal == None:
            self.RemovePicklesFromRoot()
        else:
            self.RemovePicklesOfType(inVal, '.pickle')

    def Serialize(self, files = []):
        if type(files) == str: files = [files]
        for csvF in files:
            csvfilename = os.path.join(self.root, csvF)
            if not csvfilename.endswith('.csv') or not os.path.isfile(csvfilename):
                continue

            # Delete old pickle file of the same name if it exists
            filename = str(os.path.splitext(csvfilename)[0]) + '.pickle'
            if os.path.isfile(filename): os.remove(filename)

            x = {}
            header_flag = True
            keys = []
            last_gameID = -1

            manualAddID = "PlayByPlay.pickle" in filename or \
                          os.path.basename(csvfilename) in self.GetAllEnrichedFiles() or \
                          os.path.basename(csvfilename) in self.GetAllHeatmapFiles()

            with open(csvfilename,'rt') as f:
                reader = csv.reader(f, delimiter=',')
                for line in reader:
                    if header_flag:
                        header_flag = False
                        keys = line
                    else:
                        if manualAddID:
                            if line[0] != last_gameID: #New gameID
                                last_gameID = line[0]
                                x[line[0]] = []
                                x[line[0]].append(line[1:])
                            else:
                                x[line[0]].append(line[1:])
                        else:
                            x[line[0]] = {}
                            for i in range(1,len(line)):
                                x[line[0]][keys[i]] = line[i]

            if self.verbose: print("Dumping {} data, hold on".format(filename))
            with open(filename,'wb') as f:
                pickle.dump(x, f, pickle.HIGHEST_PROTOCOL)

    def LoadPickle(self, file = ''):
        filename = os.path.join(self.root, file)
        if not os.path.isfile(filename) or not filename.endswith('.pickle'):
            if self.verbose: print("Unable to find pickle file {}".format(filename))
            return dict()
        if self.verbose: print("Loading data from {}, hold on".format(filename))
        p = pickle.load( open( filename, "rb" ))
        return p
    
if __name__=='__main__':

    # Init
    pickleParser = PickleParser('../data', False)

    #################################################################
    ######################### Tests + demos #########################
    #################################################################
    t = Tester()

    # Load empty pickle
    print("Test 1")
    t.Assert("Load empty pickle", pickleParser.LoadPickle('') == {})

    # Remove empty pickle
    print("Test 2")
    pickleParser.Remove('')
    t.Assert("Delete empty pickle", True)
    
    # Create and remove a file (csv and pickle)
    print("Test 3")
    tempFileName = os.path.join(pickleParser.root, 'test.csv')
    with open(tempFileName,'w') as f: f.write('')
    pickleParser.Remove(tempFileName, '.csv')
    t.Assert("Delete csv", not os.path.isfile(tempFileName))
    
    tempFileName = os.path.join(pickleParser.root, 'test.pickle')
    with open(tempFileName,'w') as f: f.write('')
    pickleParser.Remove(tempFileName)
    t.Assert("Delete pickle", not os.path.isfile(tempFileName))
  
    # Load == Serialize for a file
    print("Test 4")
    serializeTestFile = 'turnovers_avg_heatmap'
    initialRead = pickleParser.LoadPickle(serializeTestFile + '.pickle')
    pickleParser.Serialize(serializeTestFile + '.csv')
    rewriteAndRead = pickleParser.LoadPickle(serializeTestFile + '.pickle')
    t.Assert("Seralize == Load for pickle reading", initialRead == rewriteAndRead)

    # Delete stats pickles
    print("Test 5")
    pickleParser.RemovePicklesOfType(CSVTypes.Heatmap.value, '.pickle')
    t.Assert("Delete stats pickles",
             all(not os.path.isfile(os.path.join(pickleParser.root, str(os.path.splitext(x)[0]) + '.pickle')) for x in pickleParser.statFiles))

    # Delete enriched pickle
    print("Test 6")
    pickleParser.RemovePicklesOfType(CSVTypes.Enriched.value, '.pickle')
    t.Assert("Delete enriched pickles",
             all(not os.path.isfile(os.path.join(pickleParser.root, str(os.path.splitext(x)[0]) + '.pickle')) for x in pickleParser.GetAllEnrichedFiles()))
    
    # Delete fundamental pickles
    print("Test 7")
    pickleParser.RemovePicklesOfType(CSVTypes.Fundamentals.value, '.pickle')
    t.Assert("Delete fundamental pickles",
             all(not os.path.isfile(os.path.join(pickleParser.root, str(os.path.splitext(x)[0]) + '.pickle')) for x in pickleParser.fundamentalFiles))
    
    # Pickles created during fundamentals serialization
    print("Test 8")
    pickleParser.SaveTypesToPickles(CSVTypes.Fundamentals.value)
    t.Assert("Pickles created during fundamentals serialization",
             all(os.path.isfile(os.path.join(pickleParser.root, str(os.path.splitext(x)[0]) + '.pickle')) for x in pickleParser.fundamentalFiles))

    # Pickles created during enriched serialization
    print("Test 9")
    pickleParser.SaveTypesToPickles(CSVTypes.Enriched.value)
    t.Assert("Pickles created during enriched serialization",
             all(os.path.isfile(os.path.join(pickleParser.root, str(os.path.splitext(x)[0]) + '.pickle')) for x in pickleParser.GetAllEnrichedFiles()))
    
    # Pickles created during stat serialization
    print("Test 10")
    pickleParser.SaveTypesToPickles(CSVTypes.Heatmap.value)
    t.Assert("Pickles created during stat serialization",
             all(os.path.isfile(os.path.join(pickleParser.root, str(os.path.splitext(x)[0]) + '.pickle')) for x in pickleParser.GetAllHeatmapFiles()))

    # Delete all pickles from dir
    print("Test 11")
    pickleParser.RemovePicklesFromRoot()
    t.Assert("Delete all pickles from dir",
             all(not os.path.isfile(os.path.join(pickleParser.root, str(os.path.splitext(x)[0]) + '.pickle'))
                 for x in pickleParser.statFiles + pickleParser.enrichedFiles + pickleParser.fundamentalFiles))
    
    # All pickles created from dir
    print("Test 12")
    pickleParser.SavePicklesInRoot()
    t.Assert("All pickles created from dir",
             all(os.path.isfile(os.path.join(pickleParser.root, str(os.path.splitext(x)[0]) + '.pickle'))
                 for x in pickleParser.GetAllHeatmapFiles() + pickleParser.GetAllEnrichedFiles() + pickleParser.fundamentalFiles))

    print('\n')
    t.ShowResults()

    print("\nNote: There is a chance this failed because of setup. \n" + \
          "I'm very lazy and don't want to create files for the sole purpose of testing," + \
          "so just make sure to copy the files from ../_backup_data into ../data" + \
          "and see if it still works then.")

    #################################################################
    #################################################################
