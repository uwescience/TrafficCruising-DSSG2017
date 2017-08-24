#########################################################
##            CRUISING TEAM 2017 @ DSSG                ##
##                                                     ##
##   CODE TO CALCULATE SENSOR-TO-SENSOR DISTRIBUTIONS  ##
##                                                     ##
##                code by Brett Bejcek                 ##
#########################################################

import json
import pandas as pd

# FILE PATHS
JSON_PATH = "JSON1494284400_PF_MR.json" # path to json file of prefiltered, multiples removed data
WRITE_JSON_PATH = "distributions.json" # path to output distributions

# READ IN JSON DATA -- eventually replaced with call from
with open(JSON_PATH, 'r') as handle:
    data = json.load(handle)

# OPEN UP PATH TO WRITE TO JSON
jsonfile = open(WRITE_JSON_PATH, 'w')

# CREATE DICTIONARY TO STORE FREQUENCIES
freq = {}

# COUNTING FREQUENCIES IN DATA
for hash in range(0, len(data)):
    numHits = len(data[hash]['reduction']) # number of times to iterate through per hash
    for iterator in range(0,numHits-1):
        start = data[hash]['reduction'][iterator]['sensor'] # get starting IntersectionID
        end = data[hash]['reduction'][iterator+1]['sensor'] # get ending IntersectionID
        time = int(data[hash]['reduction'][iterator+1]['time']) - int(data[hash]['reduction'][iterator]['time'])
        path = (start, end)
        if start != end: # making sure that we do not store occurences where it is the same start to end
            if path in freq: # if it exists, add one
                freq[path].append(time)
            else: # else add it to the dictionary as one
                freq[path] = [time]

length = len(freq.keys()) # iterating through to write JSON file
text = '[\n' # store all as text because if you process line by line, it puts the wrong output
for index, i in enumerate(freq.keys()):
    (start, end) = i
    length_2 = len(freq[i])
    time_list = []
    for j in range(0,length_2):
        time = freq[i][j]
        time_list.append(int(time))
    text = text + '{\n'
    text = text + '"start":{},\n"end":{},\n"times":{},\n'.format(start,end,time_list)
    if index != (length - 1):
        text = text + '},\n'
    else:
        text = text + '}'
text = text + ']'

jsonfile.write(text) # write the JSON file
jsonfile.close() # close the stream
