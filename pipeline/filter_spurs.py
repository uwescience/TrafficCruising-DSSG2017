def filter_spurs(trip_list, filter_time, silent=True):

    """Filters false positive sensor reads and arranges trips by timestamp.

    trip_list [list]: a list of dicts in JSON format.
    filter_time [int]: Of two successive reads within this amount of time,
        the one with the weaker signal will be filtered out.
    silent [bool]: if True, does not print reports.

    Returns list of dicts in JSON format."""


    if silent == False:
        print('Filtering spurs. Scanning ' + str(len(trip_list)) \
            + ' trips.')

    for doc in trip_list:

        #round and convert times to integers. then sort by time.
        red = doc['reduction']
        for i in range(len(red)):
            red[i]['time'] = int(round(float(red[i]['time'])))
        red = sorted(red, key=lambda k: k['time'])
        doc['reduction'] = red #replace the actual reduction

        indices_to_delete = []

        for i in range(len(red)-1):

            timestamp_i = int(red[i]['time'])
            sensor_i = int(red[i]['sensor'])
            strength_i = int(red[i]['strength'])
            if (abs(timestamp_i - int(red[i+1]['time'])) <= filter_time and  sensor_i != int(red[i+1]['sensor'])):
                if (strength_i >= int(red[i+1]['strength'])): indices_to_delete.append(i+1)
                elif (strength_i < int(red[i+1]['strength'])): indices_to_delete.append(i)

        indices_to_delete = list(set(indices_to_delete))
        for i in sorted(indices_to_delete, reverse=True):
            del(doc['reduction'][i])


    if silent == False:

        print('Done filtering spurs. Returning list of length ' \
            + str(len(trip_list)) + '.')

    return(trip_list)