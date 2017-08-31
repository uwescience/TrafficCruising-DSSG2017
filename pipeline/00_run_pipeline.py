import rethinkdb as r
import pipeline_main as pl
import os
import datetime
import time
import warnings
warnings.filterwarnings("ignore")

#set working directory to top level of git repo
os.chdir('/home/ubuntu/RUN_PIPELINE_HERE/TrafficCruising-DSSG2017') #AWS path

#load API key from environment variable
key = os.environ['ACYC']

#connect to database
r.connect(host='localhost', port=28015).repl() #local

#generate directed and undirected graphs
graphs = pl.graph_generator('data/nodes.geojson')

#select a database (existing or not) to write records to
db = 'example'

#delete old records that might be cluttering the database
pl.remove_old_days(db_name=db, older_than=8, silent=True)

#pull new records from Acyclica
pl.retrieve_records(api_key=key,
    sensor_path='data/IntersectionToSensor.csv',
    db_name=db, #omitting end_date here so it defaults to today
    start_date='prev_week', json_chunk_size=5e3, verbosity=2)

#loop through each day stored in the database
for tname in r.db(db).table_list().run():

    #extract day as list of dicts
    dat = list(r.db(db).table(tname).run())

    #initial cleaning and segmenting
    dat = pl.segment_gaps(dat, graphs[1], gap_dur=15, append_tag=True,
       split_neighbors_too=True, label_fhvs=True, silent=False)
    dat = pl.filter_short_trips(dat, unique_sensor_count=4, silent=False)
    dat = pl.filter_spurs(dat, filter_time=7, silent=False)
    dat = pl.correct_false_pos(dat, graphs[1], silent=False)
    dat = pl.filter_spurs(dat, filter_time=7, silent=False)
    dat = pl.filter_short_trips(dat, unique_sensor_count=4, silent=False)

    #no use for this at present, but could fit into future pipeline designs
    # segment_stops(trip_list, stop_dur=10, append_tag=True, retain_stops=True,
       # silent=False)

    #routing and further cleaning
    dat = pl.router(dat, graphs[1], silent=False)
    dat = pl.remove_zippers(dat, graphs[0], graphs[1], silent=False)
    dat = pl.filter_short_trips(dat, unique_sensor_count=4, silent=False)

    #feature creation and classification
    dat = pl.add_features(dat, graphs[1], silent=False)
    dat = pl.label_modes(dat, silent=False)
    dat = pl.classify(dat, algorithm='gradient_boosting_classifier',
        silent=False)

    #remove all but cruisers and FHVs, segment driving portions, write to db
    dat = pl.filter_noncruising(dat, keep_only_driving=False,
        keep_all_fhv=True, silent=False)
    dat = pl.segment_driving(dat, silent=False)
    pl.jumbo_write_json(dat, db_name=db + '_out',
        table_name=tname, chunk_size=5000, silent=False)

#pull all days from database, aggregate for visualization in app
dat = pl.combine_days(db + '_out', silent=False)
pl.aggregate(dat, silent=False)
