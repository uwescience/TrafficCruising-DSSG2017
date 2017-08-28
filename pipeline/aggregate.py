import json
import pandas as pd

def aggregate(trip_list, write_path='app/static/data/aggregated.txt',
    chart_path_1='app/static/data/chart_data_fhv.json',
    chart_path_2='app/static/data/chart_data_cruising.json',
    intersections_path='data/intersections.csv',
    silent=True):
    """Combines paths by street segment in preparation for visualization.

    trip_list [list]: a list of dicts in JSON format.
    write_path [str]: path and filename for heatmap data.
    chart_path_1 [str]: path and filename for for-hire vehicle
        side plot data.
    chart_path_2 [str]: path and filename for cruising vehicle
        side plot data.
    intersections_path [str]: path to intersections.csv data file.
    silent [bool]: if True, does not print reports.

    Returns nothing."""

    if silent == False:
        print('Preparing to aggregate records.')

    # OPEN UP PATH TO WRITE TO JSON
    writefile = open(write_path, 'w')

    # OPEN UP PATH TO WRITE TO JSON
    chartfile1 = open(chart_path_1, 'w')

    # OPEN UP PATH TO WRITE TO JSON
    chartfile2 = open(chart_path_2, 'w')

    # READ IN INTERSECTIONS DATA
    intersections = pd.read_csv(intersections_path)

    # CREATE DICTIONARY TO STORE FREQUENCIES
    freq = {}

    # DIFFERENT VIEWS OF THE DATA
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
        'Saturday', 'Sunday']
    times = ['All','Morning', 'Midday', 'Evening']
    fhv = [True, False]
    labels = {True:"FHV", False:"Parking"}
    count = "count"

    data = [x for x in data if x['label'] == 'cruising']

    for subset in fhv:
        for day in days:
            for time in times:
                if time == 'All':
                    data_subset = [x for x in data if x['fhv'] == subset and x['weekday'] == day]
                else:
                    data_subset = [x for x in data if x['fhv'] == subset and x['weekday'] == day and x['timeofday'] == time]

                for hash in range(0, len(data_subset)):
                    numHits = len(data_subset[hash]['reduction']) # number of times to iterate through per hash
                    for iterator in range(0,numHits-1):
                        start = data_subset[hash]['reduction'][iterator]['IntersectionID'] # get starting IntersectionID
                        end = data_subset[hash]['reduction'][iterator+1]['IntersectionID'] # get ending IntersectionID
                        if start != end: # making sure that we do not store occurences where it is the same start to end
                            if (start, end) in freq:
                                if str(labels[subset]+"_"+day+"_"+time) in freq[(start,end)]:
                                    freq[(start,end)][str(labels[subset]+"_"+day+"_"+time)] = freq[(start,end)][str(labels[subset]+"_"+day+"_"+time)] + 1
                                else:
                                    freq[(start,end)][str(labels[subset]+"_"+day+"_"+time)] = 1
                            elif (end, start) in freq:
                                if str(labels[subset]+"_"+day+"_"+time) in freq[(end,start)]:
                                    freq[(end,start)][str(labels[subset]+"_"+day+"_"+time)] = freq[(end,start)][str(labels[subset]+"_"+day+"_"+time)] + 1
                                else:
                                    freq[(end,start)][str(labels[subset]+"_"+day+"_"+time)] = 1
                            else: # else add (start,end) and add the count for the given subset
                                freq[(start,end)] = {}
                                freq[(start,end)][str(labels[subset]+"_"+day+"_"+time)] = 1
    text = '[\n'
    for index, i in enumerate(freq.keys()):
        start_id, end_id = i
        start_lat = intersections['intersection_lat'][intersections.intersection == int(start_id)].values[0] # transform to lat
        start_lon = intersections['intersection_lon'][intersections.intersection == int(start_id)].values[0] # transform to lon
        end_lat = intersections['intersection_lat'][intersections.intersection == int(end_id)].values[0] # transform to lat
        end_lon = intersections['intersection_lon'][intersections.intersection == int(end_id)].values[0] # transform to lon
        for key in freq[i].keys():
            text = text + '{\n'
            text = text + '"label":"{}",\n"start_lat":{},\n"start_lon":{},\n"end_lat":{},\n"end_lon":{},\n"count":{}\n'.format(key,start_lat,start_lon,end_lat,end_lon,freq[i][key])
            text = text + "},\n"
    text = text[:len(text)-2]
    text = text + "\n]"
    data_json = json.loads(text)
    fhv = ["FHV", "Parking"]
    all_views = {}
    for f in fhv:
        for day in days:
            for time in times:
                output_dict = [x for x in data_json if x['label'] == str(f+"_"+day+"_"+time)]
                all_views[f,day,time] = json.dumps(output_dict)
    writefile.write(str(all_views))

    hours = range(0,24)
    text = "[\n"
    for day in days:
        for hour in hours:
            text = text + "{\n"
            text = text +'"day":"{}",\n"time":"{}",\n"count":{}\n'.format(day,("Jan 1, 1900 "+str(hour)+":00:00"),str(len([x for x in data if(x['weekday'] == day and x['hour'] == hour) and x['fhv'] == False])))
            text = text + "},\n"
    if(len(text)>5):
        text = text[0:len(text)-2]
    text = text + "]"
    chartfile1.write(text)
    text = "[\n"
    for day in days:
        for hour in hours:
            text = text + "{\n"
            text = text +'"day":"{}",\n"time":"{}",\n"count":{}\n'.format(day,("Jan 1, 1900 "+str(hour)+":00:00"),str(len([x for x in data if(x['weekday'] == day and x['hour'] == hour) and x['fhv'] == True])))
            text = text + "},\n"
    if(len(text)>5):
        text = text[0:len(text)-2]
    text = text + "]"
    chartfile2.write(text)
    chartfile1.close()
    chartfile2.close()

    if silent == False:
        print('Done aggregating records. Results written to app/static/data/')
