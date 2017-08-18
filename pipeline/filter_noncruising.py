def filter_noncruising(trip_list, keep_only_driving=True,
    keep_all_fhv=False, silent=True):

    # keep_list = np.repeat(0, len(trip_list))
    # for i in range(len(trip_list)):
    if keep_all_fhv == True:
        # if trip_list[i]['label'] == 'cruising' or \
        #     trip_list[i]['fhv'] == True:
        trip_list = list(filter(lambda x: x['label'] == 'cruising' or \
            x['fhv'] == True, trip_list))
            # keep_list[i] = 1
    else:
        trip_list = list(filter(lambda x: x['label'] == 'cruising', trip_list))
        # if trip_list[i]['label'] == 'cruising':
            # keep_list[i] = 1

    # trip = trip_list[0]
    # read = trip['reduction'][1]
    if keep_only_driving == True:
        for trip in trip_list:
            # duc = trip['reduction']
            # keep_list = np.repeat(0, len(duc))
            trip['reduction'] = list(filter(lambda x: 'mode' in x and \
                x['mode'] == 'driving', trip['reduction']))
            # for i in range(len(duc)):
                # if 'mode' in duc[i] and duc[i]['mode'] == 'driving':
                    # keep_list[i] = 1

    return trip_list