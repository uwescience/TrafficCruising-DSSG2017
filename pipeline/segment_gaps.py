import numpy as np


def segment_gaps(trip_list, undir_graph, gap_dur=10, append_tag=True,
    split_neighbors_too=True, label_fhvs=True, fhv_gap_thresh=4, silent=True):

    """Splits trips if there are sufficiently large gaps in read times.

    trip_list [list]: a list of dicts in JSON format.
    undir_graph [Networkx graph object]: should be an UNdirected graph.
    gap_dur [int]: duration of gaps (in minutes) that will be used
        to split trips.
    append_tag [bool]: should trips that get split have tags
        (_G0, _G1, _G2, etc.) appended to their hashes?
    split_neighbors_too [bool]: if the intersection after a gap is a
        neighbor of the one before, should the trip be split?
    label_fhvs [bool]: should for-hire vehicles be labeled as such?
    silent [bool]: if True, does not print reports.
    fhv_gap_thresh [int]: the number of gaps of gap_dur duration above which
        a traveler will be labeled as a for-hire vehicle if label_fhvs is True.
        Defaults to 4.

    You'll want to rerun filter_short_trips after using this function.
    Does not work on routed data.
    Returns list of dicts in JSON format."""

    if silent == False:
        print('Segmenting trips before and after gaps > ' \
            + str(gap_dur) + ' minutes. Processing '+ str(len(trip_list)) \
            + ' trips.')

    #convert rethinkdb table to list
    # trip_list = list(r.table(table_name).run())

    #if labeling for-hire vehicles, label all trips as non-fhvs to begin
    if label_fhvs == True:

        for i in range(len(trip_list)):
            trip_list[i]['fhv'] = False

    #find hashes with multiple trips and identify where to split them
    splits = []
    for j in range(len(trip_list)):

        #sort reduction by time (just to be on the safe side)
        reduc = trip_list[j]['reduction']
        l = range(len(reduc))
        time_order = np.argsort([reduc[i]['time'] for i in l])
        rreduc = [reduc[i] for i in time_order]

        #create list of hits with sensor reads (no interpolated points) [deprecated]
        # rreduc = [sreduc[i] for i in l if sreduc[i]['sensor'] is not None]

        #get durations between sensor reads (gaps)
        times = [rreduc[i]['time'] for i in l]
        gaps = list(np.diff(list(map(int, times))))

        #get indices of gaps >= gap_dur minutes (big gaps)
        big_gaps = [ind for ind, item in enumerate(gaps) if item >= gap_dur*60]

        #get intersection ids on either side of each big gap, and the time before the gap
        hit_ids = [rreduc[i]['IntersectionID'] for i in l] #get list of intersections
        gap_bounds = [(hit_ids[i], hit_ids[i+1], times[i]) for i in big_gaps]

        #if intersections are not directly connected, and not identical, assume a new
        #trip began after that gap. record any times after which this reduction needs to be segmented.
        #Or, if they are directly connected and split_neighbors_too is True, still split.
        split_times = []
        for k in range(len(gap_bounds)): #for each gap
            node1 = int(gap_bounds[k][0]) #pre-gap intersection
            node2 = int(gap_bounds[k][1]) #post-gap intersection

            #if we want to treat leave node and return node as separate trips
            #only when they are unconnected and not the same...
            if split_neighbors_too == False:
                try:
                    con = undir_graph[node1][node2] #test if node1 and node2 are connected
                except KeyError: #if not...
                    con = 'not connected'
                finally:
                    if con == 'not connected' and node1 != node2: #and if nodes aren't identical...
                        split_times.append(int(gap_bounds[k][2])) #then this counts as a separate trip

            #if we want to treat leave node and return node as separate trips
            #whether they're connected or not (but they still can't be the same)
            else:
                if node1 != node2: #split as long as return node != leave node
                    split_times.append(int(gap_bounds[k][2]))

        if split_times: #now, if there are any split times
            splits.append([trip_list[j], split_times]) #append doc and its split times to list

    if silent == False:
        print('Identified ' + str(len(splits)) \
            + ' trips that need to be segmented.')

    #for each trip that needs to be split, create a list of integer categories
    #representing which reads will be allocated to each new segment
    break_schemes = [None] * len(splits) #create a list to hold lists of segment #s
    for i in range(len(splits)): #for each trip that needs to be split
        reads = splits[i][0]['reduction'] #get the reads
        break_schemes[i] = np.repeat(0, len(reads)) #assign all reads 0

        for j in range(len(splits[i][1])): #for each necessary segmentation
            break_time = splits[i][1][j] #get the break time

            for k in range(len(reads)): #for each read
                read_time = int(reads[k]['time'])
                if read_time > break_time: #does the read take place after the break time?
                    break_schemes[i][k] = j + 1 #then assign it a new segment number

    if silent == False:
        print('Determined splitting scheme.')

    #label for-hire vehicles if desired
    if label_fhvs == True:

        #get number of gaps > gap_dur
        ngaps = [len(i[1]) for i in splits]

        for i in range(len(ngaps)): #for each trip with gaps

            #if there are more than fhv_gap_thresh gaps over gap_dur duration...
            if ngaps[i] > fhv_gap_thresh:

                #get # sensors and # total reads
                nsens = len(set([r['sensor'] for r in splits[i][0]['reduction']]))
                nreads = len(splits[i][0]['reduction'])

                if nreads / nsens < 6: #if dispersion ratio is under 6
                    splits[i][0]['fhv'] = True #assume not a bus and label as fhv

    #now do the actual splitting
    segs = []
    for i in range(len(break_schemes)): #for all trips that need to be split
        scheme = list(map(int, break_schemes[i])) #convert scheme to int
        # np.array([list(map(int, break_schemes[i])) for i in range(len(break_schemes))])
        hsh = splits[i][0]['group'] #get the original hash
        fhv_status = splits[i][0]['fhv'] #get the fhv status

        # [index for index, item in enumerate(splits) if item[0]['group']=='0847f823a678fbe15841177253f972f9bc4e0ecbca9852b9c2529c649789551e']

        for j in set(scheme): #split trips
            seg = [splits[i][0]['reduction'][k] for k in range(len(scheme)) if scheme[k] == j]

            if append_tag == True:
                newhash = hsh + '_G' + str(j)
                if label_fhvs == True:
                    segs.append({'group':newhash, 'fhv':fhv_status,
                        'reduction':seg})
                else:
                    segs.append({'group':newhash, 'reduction':seg})
            elif append_tag == False:
                if label_fhvs == True:
                    segs.append({'group':hsh, 'fhv':fhv_status,
                        'reduction':seg})
                else:
                    segs.append({'group':hsh,'reduction':seg})
            else:
                raise ValueError("arg 'append_tag' must be logical")

    #remove the input table from the database if desired
    # if overwrite_table == True:
        # r.table_drop(table_name).run()

    #create a new table for segmented trip_list
    # table_name = table_name + '_GSEG'
    # r.table_create(table_name).run()

    #filter pre-segmented trips from list
    ids = set([splits[i][0]['id'] for i in range(len(splits))])
    preseg_removed = [trip_list[i] for i in range(len(trip_list)) if trip_list[i]['id'] not in ids]

    #append post-segmented trips to list and upload to the new table
    out = preseg_removed + segs
    # r.table(table_name).insert(out).run()

    # cursor.close() #see todo list
    if silent == False:
        print('Done with gap segmentation. Returning list of length ' \
            + str(len(out)) + '. Now use filter_short_trips.')
    # return table_name

    return out