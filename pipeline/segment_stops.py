import numpy as np
import itertools as itt

def segment_stops(trip_list, stop_dur=10, append_tag=True, retain_stops=True,
    silent=True):

    """Splits trips if there are sufficiently large stops.

    trip_list [list]: a list of dicts in JSON format.
    stop_dur [int]: duration of stops (in minutes) that will be used
        to split trips.
    append_tag [bool]: should trips that get split have tags
        (_S0, _S1, _S2, etc.) appended to their hashes?
    retain_stops [bool]: if True, all mid-stop reads will be included with the
        segments before and after the stop
    silent [bool]: if True, does not print reports.

    You'll want to rerun filter_short_trips after using this function.
    Does not work on routed data.
    Returns list of dicts in JSON format."""

    if silent == False:
        print('Segmenting trips before and after stops > ' \
            + str(stop_dur) + ' minutes. Processing '+ str(len(trip_list)) \
            + ' trips.')

    #find hashes with multiple trips and identify where to split them
    splits = []
    for j in range(len(trip_list)):

        #sort reduction by time (just to be on the safe side)
        reduc = trip_list[j]['reduction']
        l = range(len(reduc))
        time_order = np.argsort([reduc[i]['time'] for i in l])
        rreduc = [reduc[i] for i in time_order]

        #get times and intersection IDs associated with sensor reads
        times = [rreduc[i]['time'] for i in l]
        hit_ids = [rreduc[i]['IntersectionID'] for i in l] #get list of intersections

        #identify stops that are >= stop_dur minutes (big stops)
        hits_per_sensor = [sum(1 for _ in gp) for x, gp in itt.groupby(hit_ids)] #get run lengths
        repeat_sensors = [ind for ind, item in enumerate(hits_per_sensor) if item > 1] #which run lengths > 1?
        cs = np.cumsum(hits_per_sensor) #used to find stop endpoints
        rep_end_inds = [cs[i]-1 for i in repeat_sensors] #indices of final times for sensors with repeats
        hits_per_repeat = [hits_per_sensor[i] for i in repeat_sensors]
        rep_start_inds = list(map(lambda x, y : x - y + 1, rep_end_inds, hits_per_repeat))
        rep_durs = [int(times[rep_end_inds[i]]) - int(times[rep_start_inds[i]]) for i in range(len(rep_end_inds))]
        big_stops = [ind for ind, item in enumerate(rep_durs) if item >= stop_dur*60]

        #find the temporal endpoints of big stops, and the location
        stop_bounds = [(times[rep_start_inds[i]], times[rep_end_inds[i]],
                       hit_ids[i]) for i in big_stops]

        #if there are any, add the whole doc to new list, along with segment bounds
        if len(stop_bounds):
            splits.append([trip_list[j], stop_bounds])

    if silent == False:
        print('Found ' + str(len(splits)) \
            + ' trips that need to be segmented.')

    #for each trip that needs to be split, create a list of integer categories
    #representing which reads will be allocated to each new segment
    break_schemes = [None] * len(splits) #create a list to hold lists of segment #s
    for i in range(len(splits)): #for each trip that needs to be split
        reads = splits[i][0]['reduction'] #get the reads
        break_schemes[i] = np.repeat(0, len(reads)) #assign all reads 0

        for j in range(len(splits[i][1])): #for each time the trip needs to be segmented
            stop_beginning = int(splits[i][1][j][0]) #get the moment they stopped
            stop_end = int(splits[i][1][j][1]) #and the moment they started moving again

            for k in range(len(reads)): #for each read
                read_time = int(reads[k]['time'])

                if read_time > stop_beginning and read_time < stop_end: #does the read take place mid-stop?
                    break_schemes[i][k] = -j - 1 #then mark it as a negative segment number
                elif read_time >= stop_end: #does it follow the stop?
                    break_schemes[i][k] = j + 1 #then assign it a positive segment number

    if silent == False:
        print('Determined splitting scheme.')

    #now do the actual splitting
    segs = []
    for i in range(len(break_schemes)): #for all trips that need to be split
        scheme = list(map(int, break_schemes[i])) #convert scheme to int
        hsh = splits[i][0]['group'] #get the original hash
        moving_segs = set([abs(scheme[i]) for i in range(len(scheme))])
        for j in moving_segs: #for each new trip...
            if retain_stops == True: #if you want to keep reads taken during stops...
                jj = (j, -j, -(j+1)) #include the trip and the full stop on either side
                seg = [splits[i][0]['reduction'][k] for k in range(len(scheme)) if scheme[k] in jj]
            else: #otherwise keep the trip and the stop boundaries on either side
                seg = [splits[i][0]['reduction'][k] for k in range(len(scheme)) if scheme[k] == j]

            if append_tag == True: #label each new trip with a unique tag if desired
                newhash = hsh + '_S' + str(j)
                segs.append({'group':newhash,'reduction':seg})
            elif append_tag == False:
                segs.append({'group':hsh,'reduction':seg})
            else:
                raise ValueError("arg 'append_tag' must be logical")


    #filter segmented trip_list from list
    ids = set([splits[i][0]['id'] for i in range(len(splits))])
    preseg_removed = [trip_list[i] for i in range(len(trip_list)) if trip_list[i]['id'] not in ids]

    #append segmented trip_list to list and upload to the new table
    out = preseg_removed + segs
    # r.table(table_name).insert(out).run()

    # cursor.close() #see todo list
    # return table_name
    if silent == False:
        print('Done with stop segmentation. Returning list of length ' \
            + str(len(out)) + '. Now use filter_short_trips.')

    return out
