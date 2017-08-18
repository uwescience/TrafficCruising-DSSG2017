def label_modes(trip_list, silent=True):
    """Labels trip segments by likely mode of travel.

    Labels are "chilling" if traveler is stationary, "walking" if slow,
        "driving" if fast, and "bogus" if too fast to be real.

    trip_list [list]: a list of dicts in JSON format.
    silent [bool]: if True, does not print reports.

    Returns list of dicts in JSON format."""


    if silent == False:
        print('Preparing to label modes of travel for ' \
            + str(len(trip_list)) + ' trips.')

    loop_counter = 0
    loop_size = len(trip_list)
    for doc in trip_list:

        if silent == False:
            loop_counter = loop_counter + 1
            if loop_counter % 10000 == 0:
                print('Labeling modes. Finished ' + str(loop_counter) \
                    + ' trips.')

        time_spent_driving = 0
        time_spent_walking = 0
        time_spent_chilling = 0
        time_spent_bogus = 0
        for i in range(1,len(doc['reduction'])):
            if (float(doc['reduction'][i]['velocity']) >= 2.3):
                doc['reduction'][i]['mode'] = 'driving'

            elif (float(doc['reduction'][i]['velocity']) < 2.3 and float(doc['reduction'][i]['velocity']) > 0):
                doc['reduction'][i]['mode'] = 'walking'

            elif (float(doc['reduction'][i]['velocity']) == 0.0):
                doc['reduction'][i]['mode'] = 'chilling'

            if (float(doc['reduction'][i]['velocity']) > 22.22):
                doc['reduction'][i]['mode'] = 'bogus'


        for i in range(1,len(doc['reduction']) - 1):
            path_length = 0

            if (doc['reduction'][i]['mode'] == 'driving'):
                for j in range(i+1,len(doc['reduction'])):
                    last_intersection_id = doc['reduction'][j]['IntersectionID']
                    if (doc['reduction'][j]['mode'] == 'walking'): path_length = path_length + 1
                    elif (doc['reduction'][j]['mode'] == 'driving' or doc['reduction'][j]['mode'] == 'bogus'): break

                if (path_length > 5 or last_intersection_id == doc['reduction'][i]['IntersectionID']):
                    for k in range(i+1,j):
                        if (doc['reduction'][k]['mode'] != 'chilling'): doc['reduction'][k]['mode'] = 'walking'
                else :
                    for k in range(i+1,j):
                        if (doc['reduction'][k]['mode'] != 'chilling'): doc['reduction'][k]['mode'] = 'driving'

            if (doc['reduction'][i]['mode'] == 'driving'): time_spent_driving = time_spent_driving + float(doc['reduction'][i]['time']) - float(doc['reduction'][i-1]['time'])
            elif (doc['reduction'][i]['mode'] == 'walking'): time_spent_walking = time_spent_walking + float(doc['reduction'][i]['time']) - float(doc['reduction'][i-1]['time'])
            elif (doc['reduction'][i]['mode'] == 'chilling'): time_spent_chilling = time_spent_chilling + float(doc['reduction'][i]['time']) - float(doc['reduction'][i-1]['time'])
            elif (doc['reduction'][i]['mode'] == 'bogus'): time_spent_bogus = time_spent_bogus + float(doc['reduction'][i]['time']) - float(doc['reduction'][i-1]['time'])

        if (doc['reduction'][-1]['mode'] == 'driving'): time_spent_driving = time_spent_driving + float(doc['reduction'][-1]['time']) - float(doc['reduction'][-2]['time'])
        elif (doc['reduction'][-1]['mode'] == 'walking'): time_spent_walking = time_spent_walking + float(doc['reduction'][-1]['time']) - float(doc['reduction'][-2]['time'])
        elif (doc['reduction'][-1]['mode'] == 'chilling'): time_spent_chilling = time_spent_chilling + float(doc['reduction'][-1]['time']) - float(doc['reduction'][-2]['time'])
        elif (doc['reduction'][-1]['mode'] == 'bogus'): time_spent_bogus = time_spent_bogus + float(doc['reduction'][-1]['time']) - float(doc['reduction'][-2]['time'])


        duration_of_trip = float(doc['duration_of_trip'])
        doc['time_percentage_driving'] = str(time_spent_driving/duration_of_trip*100)
        doc['time_percentage_walking'] = str(time_spent_walking/duration_of_trip*100)
        doc['time_percentage_chilling'] = str(time_spent_chilling/duration_of_trip*100)
        doc['time_percentage_bogus'] = str(time_spent_bogus/duration_of_trip*100)

    if silent == False:
        print('Done labeling mode of travel. Returning list of length ' \
            + str(len(trip_list)) + '.')

    return trip_list