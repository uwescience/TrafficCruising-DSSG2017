def filter_short_trips(trip_list, unique_sensor_count, silent=True):

    """Removes trips too short to be identifiable as cruising.

    trip_list [list]: a list of dicts in JSON format.
    unique_sensor_count [int]: trips with fewer than this number of hits on
        unique sensors will be filtered out.
    silent [bool]: if True, does not print reports.

    Returns list of dicts in JSON format."""

    if silent == False:
        print('Filtering short trips. Scanning ' + str(len(trip_list)) \
            + ' trips.')

    keep_inds = []
    for i in range(len(trip_list)):
        doc = trip_list[i]
        sensor_list = [doc['reduction'][j]['sensor'] for j in range(len(doc['reduction']))]
        if len(set(sensor_list)) >= unique_sensor_count-1:
            keep_inds.append(i)


    trip_list = [trip_list[i] for i in keep_inds]


    if silent == False:

        print('Done filtering trips with < ' + str(unique_sensor_count) \
            + ' unique sensor hits. Returning list of length ' \
            + str(len(trip_list)) + '.')


    return(trip_list)