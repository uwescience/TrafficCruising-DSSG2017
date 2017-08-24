
############ oi, this file is temporary and unusable at the moment.
#it will be replaced by Anamol's pipeline
#caller when he returns from his trip #############








import rethinkdb as r
import pipeline as pl
import os
import json
import datetime
import time
import warnings
warnings.filterwarnings("ignore")

from importlib import reload
reload(a)

#cd ~/git/dssg/cruising/data/large_files/testing
#rethinkdb import -f nobackforth_corrected_paths_Dijkstra_JSON1494284400.json --format json --table test.hash
#rethinkdb import -f JSON1494284400.json --format json --table test.hash

#set working directory; load API key and rethinkdb password
os.chdir('/home/mike/git/dssg/cruising')
key = os.environ['ACYC']
# pw = os.environ['DSSG_RETHINKDB']
#connect to database
r.connect(host='localhost', port=28015, db='test').repl() #local
# conn = r.connect(host='ec2-54-190-85-124.us-west-2.compute.amazonaws.com',  #remote
#     user='admin', port='28015', db='test', password=pw).repl()
# conn.server()

# r.table_list().run()

#generate directed and undirected graphs
graphs = a.graph_generator('data/nodes.geojson')
# s = pd.read_csv('data/large_files/Acyclica_sensors_CBD.csv')
# s = pd.read_csv('/home/mike/git/dssg/cruising/data/IntersectionToSensor.csv')

tnames = ['jul31','aug1','aug2','aug3','aug4','aug5','aug6']
end_dates = ['2017-07-31','2017-08-01','2017-08-02','2017-08-03','2017-08-04','2017-08-05','2017-08-06']
# tables_to_drop = r.db('preclassify').table_list().run()
# for tab in tables_to_drop:
    # dat = list(r.db('preclassify').table(tab).run())
    # print(r.db('final').table(tab).count().run())
    # r.db('final').table_create(tab).run()
# r.db('final').table_drop('jul31').run()
for date in range(len(tnames)):

    tname = tnames[date]
    # a.retrieve_records(api_key=key,
    #     sensor_path='data/IntersectionToSensor.csv',
    #     table_name=tname, end_date=end_dates[date],
    #     start_date=None, json_chunk_size=5e3, verbosity=2)
    # endDate='2017-08-04'; startDate='2017-08-03'

#    dat = list(r.db('test').table(tname).run())
    # r.db('final').table_create(tname).run()

    # dat = list(r.db('test').table('jul31').limit(1000).run())

#    dat = a.segment_gaps(dat, graphs[1], gap_dur=15, append_tag=True,
#        split_neighbors_too=True, label_fhvs=True, silent=False)
#    dat = a.filter_short_trips(dat, unique_sensor_count=4, silent=False)
#    dat = a.filter_spurs(dat, filter_time=7, silent=False)
#    dat = a.correct_false_pos(dat, graphs[1], silent=False)
#    dat = a.filter_spurs(dat, filter_time=7, silent=False)
#    dat = a.filter_short_trips(dat, unique_sensor_count=4, silent=False)
#    # segment_stops(trip_list, stop_dur=10, append_tag=True, retain_stops=True,
#        # silent=False)
#    dat = a.router(dat, graphs[1], silent=False)
#    dat = a.remove_zippers(dat, graphs[0], graphs[1])
#    dat = a.filter_short_trips(dat, unique_sensor_count=4, silent=False)
#    dat = a.add_features(dat, graphs[1], silent=False)
#    dat = a.label_modes(dat, silent=False)
#    a.jumbo_write_json(dat, 'preclassify', tname, chunk_size=5000, silent=False)
    dat = list(r.db('preclassify').table(tname).run())
    dat = a.classify(dat, algorithm='gradient_boosting_classifier', silent=False)
    dat = a.filter_noncruising(dat, keep_only_driving=False,
        keep_all_fhv=True, silent=False)
    dat = a.segment_driving(dat, silent=False)
    # for i in tnames:
    #     r.db('brief_out').table_create(i).run()
        # r.db('brief').table(i).insert(r.db('test').table(i).limit(1000).run()).run()
    r.db('final').table(tname).insert(dat).run()

# dat = a.classify(dat, 'decision_tree', silent=False)
# dat = a.classify(dat, silent=False)
# x = []
# c = b = []
# for i in range(len(dat2)):
#     for j in range(1,len(dat2[i]['reduction'])):
#         x.append(dat2[i]['reduction'][j]['strength'])
# for i in range(len(x)):
#     b.append(type(x[i]))
# all(b[i] == float for i in range(len(b)))
# set(b)
# dat2[0]
# for i in x:
#     if i >= 0:
#         c = c+1
#     if i < 0:
#         b = b+1
# import matplotlib.pyplot as plt
# p = plt.hist(x, bins=1000)
# plt.ylim(0,100)
# plt.xlim(0,1000)
# plt.show()

# with open('/home/mike/Desktop/untracked/one_week/'+tname+'.json', 'w') as data_file:
#     json.dump(dat, data_file)
#     data_file.close()
del(dat)
dat = a.combine_days('final', silent=False)
# dat = a.combine_days('final', silent=False)

with open('/home/mike/Desktop/untracked/week_withDispRatioAndHour.json', 'w') as data_file:
    json.dump(dat, data_file)
    data_file.close()
