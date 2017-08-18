def filter_noncruising(trip_list, keep_only_driving=False,
    keep_all_fhv=True, silent=True):
    """Removes trips labeled as 'not_cruising' after classification.
    
    trip_list [list]: a list of dicts in JSON format.
    keep_only_driving [bool]: should segments not identified
        as 'driving' be dropped from all trips? This should
        always be set to False unless modifications have been
        made to the heatmap code. Use the function segment_driving
        instead.
    keep_all_fhv [bool]: should for-hire vehicles be included in
        the output regardless of whether they're displaying cruising
        behavior?
    silent [bool]: if True, does not print reports.
    
    Returns list of dicts in JSON format."""

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
