#########################################################
##            CRUISING TEAM 2017 @ DSSG                ##
##                                                     ##
##    Flask web application to visualize aggregated    ##
##                       heatmap.                      ##
##                                                     ##
##                code by Brett Bejcek                 ##
#########################################################

import json # working with json files
from flask import Flask # working with Flask
from flask import request
from flask import render_template
from flask import jsonify

## DATA NEEDED TO RUN APPLICATION
with open('static/data/aggregated.txt','r') as handle: # this data is aggregated for type of cruising, day, and time of day
    data = eval(handle.read())
with open('static/data/chart_data_cruising.json','r') as handle2: # this data is for the chart in the lower right corner [only cruising]
    chart_data_cruising = json.load(handle2)
with open('static/data/chart_data_fhv.json','r') as handle3: # this data is for the chart in the lower right corner [only for hire vehicles]
    chart_data_vhf = json.load(handle3)

app = Flask(__name__) # creates a new instantiation

@app.route("/")
def start():
    return render_template("home.html") # returns the home page

@app.route('/data/<string:fhv>/<string:day>/<string:time>', methods= ['GET']) #returns the data for leaflet plotting
def return_data(fhv, day, time):
    return(data[(fhv,day,time)])

@app.route('/legend/<string:fhv>/<string:day>/<string:time>', methods= ['GET']) #returns the legend for the map
def return_legend(fhv, day, time):
    counts = []
    percentiles = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9] # different percentiles for legend
    results = []
    result = json.loads(data[(fhv,day,time)])
    for i in result:
        counts.append(i['count'])
    counts.sort()
    length = len(counts)
    for i in range(len(percentiles)):
        results.append(counts[int(percentiles[i]*length)]) # getting the 0th,10th,20th,...,90th percentiles of the data
    results[0] = 0
    return(json.dumps(results))

@app.route('/chart_data_vhf/<string:day>/<string:time>', methods= ['GET']) # returns data for lower right chart when the for hire vehicle button is selected
def return_small_chart_data_vhf(day, time):
    output_dict = [x for x in chart_data_vhf if x['day'] == day]
    if(time == 'All'):
        start = "Jan 01, 1900 00:00:00"
        end = "Jan 01, 1900 23:00:00"
    elif(time == 'Morning'):
        start = "Jan 01, 1900 06:00:00"
        end = "Jan 01, 1900 10:00:00"
    elif(time == 'Midday'):
        start = "Jan 01, 1900 10:00:00"
        end = "Jan 01, 1900 16:00:00"
    else:
        start = "Jan 01, 1900 16:00:00"
        end = "Jan 01, 1900 20:00:00"
    for entry in output_dict:
        entry['start'] = start
        entry['end'] = end
    output_json = json.dumps(output_dict)
    return(output_json)

@app.route('/chart_data_cruising/<string:day>/<string:time>', methods= ['GET']) #  returns data for lower right chart when parking button is selected
def return_small_chart_data_cruising(day, time):
    output_dict = [x for x in chart_data_cruising if x['day'] == day]
    if(time == 'All'):
        start = "Jan 01, 1900 00:00:00"
        end = "Jan 01, 1900 23:00:00"
    elif(time == 'Morning'):
        start = "Jan 01, 1900 06:00:00"
        end = "Jan 01, 1900 10:00:00"
    elif(time == 'Midday'):
        start = "Jan 01, 1900 10:00:00"
        end = "Jan 01, 1900 16:00:00"
    else:
        start = "Jan 01, 1900 16:00:00"
        end = "Jan 01, 1900 20:00:00"
    for entry in output_dict:
        entry['start'] = start
        entry['end'] = end
    output_json = json.dumps(output_dict)
    return(output_json)

if __name__ == "__main__":
    app.run()
