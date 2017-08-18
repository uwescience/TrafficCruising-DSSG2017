import tzlocal
import networkx as nx
import calendar

def add_features(trip_list, graph, silent=True):

    """Populates each trip document with features used for classification and
    visualization.

    trip_list [list]: a list of dicts in JSON format.
    graph [Networkx graph object]: must be a directed graph.
    silent [bool]: if True, does not print reports.

    Returns list of dicts in JSON format."""

    #cursor = r.table(tablename).run()
    #trip_list = list(cursor)
    if silent == False:
        print('Preparing to add features for ' + str(len(trip_list)) \
            + ' trips. This step is a doozy.')

    #get local timezone
    tzone = tzlocal.get_localzone()

    loop_counter = 0
    loop_size = len(trip_list)
    for doc in trip_list:

        if silent == False:
            loop_counter = loop_counter + 1
            if loop_counter % 10000 == 0:
                print('Adding features. Finished ' + str(loop_counter) \
                    + ' trips.')

        # doc_id = doc['id']
        total_time_taken = float(doc['reduction'][-1]['time'])-float(doc['reduction'][0]['time'])
        total_distance = 0
        max_speed = 0;
        doc['reduction'][0]['sequence'] = '0'
        hit_total = []
        list_of_intersections = [int(doc['reduction'][0]['IntersectionID'])]
        speeds = []
        stops_0_to_2_mins = 0
        stops_2_to_5_mins = 0
        stops_5_to_10_mins = 0
        stops_10_to_15_mins = 0
        stops_15_mins_and_over = 0
        number_of_times_crossed = 0

        shortest_distance = nx.shortest_path_length(graph,source=int(doc['reduction'][0]['IntersectionID']), target=int(doc['reduction'][-1]['IntersectionID']),weight='distance')
        for i in range(1,len(doc['reduction'])):
            node_0 = int(doc['reduction'][i-1]['IntersectionID'])
            node_1 = int(doc['reduction'][i]['IntersectionID'])
            list_of_intersections.append(int(doc['reduction'][i]['IntersectionID']))

            time_0 = float(doc['reduction'][i-1]['time']); time_1 = float(doc['reduction'][i]['time'])
            if ((time_1 - time_0)==0):
                time_1 = time_0 + 0.01
                # print(doc['group'])
            distance = float(nx.shortest_path_length(graph,source=node_0,target=node_1,weight='distance'))
            doc['reduction'][i]['distance'] = str(distance)
            doc['reduction'][i]['velocity'] = str(distance/(time_1 - time_0))
            doc['reduction'][i]['sequence'] = str(i)
            if (distance/(time_1 - time_0) > max_speed): max_speed = distance/(time_1 - time_0)
            total_distance = total_distance + distance
            stop_time = 0
            if (float(doc['reduction'][i]['velocity']) != 0.0):
                speeds.append(float(doc['reduction'][i]['velocity']))
                hit_total.append(int(node_1))
            elif (float(doc['reduction'][i]['velocity']) == 0.0):
                stop_time = time_1 - time_0


        l = range(len(doc['reduction']))

        rreduc = [doc['reduction'][i] for i in l if doc['reduction'][i]['sensor'] is not None]

        l = range(len(rreduc)) #can fix this down the road to improve cleanliness

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
        #big_stops = [ind for ind, item in enumerate(rep_durs) if item >= stop_dur*60]

        for stop_time in rep_durs:
            if (0 < stop_time < 120): stops_0_to_2_mins = stops_0_to_2_mins + 1

            elif (120 <= stop_time < 300) : stops_2_to_5_mins = stops_2_to_5_mins + 1

            elif (300 <= stop_time < 600) : stops_5_to_10_mins = stops_5_to_10_mins + 1

            elif (600 <= stop_time < 900) : stops_10_to_15_mins = stops_10_to_15_mins + 1

            elif (stop_time >= 900) : stops_15_mins_and_over = stops_15_mins_and_over + 1

        list_of_intersections = set(list_of_intersections)

        try:
            for intersection in list_of_intersections:
                if (hit_total.count(intersection) > 1):
                    number_of_times_crossed = number_of_times_crossed + hit_total.count(intersection) - 1
        except:
            print(str(loop_counter - 1))
        doc['speed_max'] = str(max_speed)
        doc['duration_of_trip'] = str(total_time_taken)
        doc['distance_total'] = str(total_distance)
        doc['distance_shortest'] = str(shortest_distance)
        doc['speed_average'] = str(total_distance/total_time_taken)
        doc['distance_ratio'] = str(shortest_distance/total_distance)
        doc['speed_standard_deviation'] = str(np.std(speeds))
        doc['stops_0_to_2_mins'] = str(stops_0_to_2_mins)
        doc['stops_2_to_5_mins'] = str(stops_2_to_5_mins)
        doc['stops_5_to_10_mins'] = str(stops_5_to_10_mins)
        doc['stops_10_to_15_mins'] = str(stops_10_to_15_mins)
        doc['stops_15_mins_and_over'] = str(stops_15_mins_and_over)
        doc['number_of_times_crossed'] = str(number_of_times_crossed)


        #add temporal details that will be used in the final plot:
        #convert timestamps to datetimes
        tstamps = [doc['reduction'][i]['time'] for i in range(len(doc['reduction']))]
        datetimes = [pd.to_datetime(tstamps[i],
            unit='s').tz_localize('UTC').tz_convert(tzone)
            for i in range(len(tstamps))]

        #get weekday and date
        doc['weekday'] = calendar.day_name[datetimes[0].weekday()]
        doc['date'] = datetimes[0].strftime('%Y-%m-%d')

        #bin this trip into a certain hour and time of day
        hours = [datetimes[i].hour for i in range(len(tstamps))]
        hour_set = set(hours)
        proportion_of_hours = (len(hour_set) + 1) / 24
        primary_hour = max(hour_set, key=hours.count)
        doc['hour'] = primary_hour
        doc['hour_proportion'] = proportion_of_hours
        doc['timeofday'] = pd.cut([primary_hour,primary_hour], [-1,5,10,15,20,23],
            labels=['Predawn','Morning','Midday','Evening','Night'])[0]

    if silent == False:
        print('Done adding features. Returning list of length ' \
            + str(len(trip_list)) + '.')

    return trip_list