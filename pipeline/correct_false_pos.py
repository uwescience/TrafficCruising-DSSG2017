import networkx as nx
import operator
import itertools as itt


def correct_false_pos(trip_list, graph, silent=True):

    """Removes in-line false positives.

    Due to excessive sensor range, travelers can be detected far away from their
    true location, even alternatingly on adjacent sensors while stopped between
    them, creating a "back-and-forth" (if on two-way street) or rapid looping
    (if on one-way) artifact. This removes that.

    trip_list [list]: a list of dicts in JSON format.
    graph [Networkx graph object]: must be a directed graph.
    silent [bool]: if True, does not print reports.

    Returns list of dicts in JSON format."""

    mapping = {1178349141:273628, 53072275:273153, 53072274:273606, 53213825:273603, 53142971:273158, 53205955:273100, 53072273:273636, 53160865:273595, 53160863:273155, 53160861:265078, 53160858:273095, 53160854:273099, 53160852:273083, 3618304999:273608, 53213824:273598, 53142969:273630, 53213415:273149, 53200378:273090, 53144265:273240, 53184114:273061, 53207667:273246, 53221907:273049, 53114228:273057, 2481926130:273601, 53213823:273594, 53205953:273104, 53213414:265082, 53144262:265074, 53142136:273668, 53207665:273107, 53221906:273106, 53187905:273103, 53213413:273620, 2053744124:273621, 53221905:273085, 53071891:273093, 53187904:265104, 53203467:273591, 53142966:273596, 53203466:265178, 53203465:265081, 53200375:273050, 53144260:265150, 53184111:273624, 53203464:273086, 53142130:265105, 53203463:265180, 53203462:265118, 53144742:273669, 53017297:265115, 53144257:273055, 53144734:273092, 53144733:273579, 53142127:273059, 53144731:273619, 53071880:273147, 53114264:273152, 53114263:273618, 53114262:273096, 53009977:273094, 53155726:265113, 53155724:273056, 53155723:265120}

    # newTablename = table_name + '_RBF'

    # cursor=r.table(table_name).run()
    # trip_list = list(cursor)

    if silent == False:
        print('Correcting false-positive artifacts for ' + str(len(trip_list)) \
            + ' trips.')

    for doc in trip_list:
        sensor_list = []; timestamps = []
        for i in range(0,len(doc['reduction'])):
            sensor_list.append(int(doc['reduction'][i]['sensor']))
            timestamps.append(int(round(float(doc['reduction'][i]['time']))))

        new_Intersection_list = remove_back_forth(graph, sensor_list, timestamps)

        for i in range(0,len(doc['reduction'])):
            doc['reduction'][i]['sensor'] = str(mapping[new_Intersection_list[i]])
            doc['reduction'][i]['IntersectionID'] = str(new_Intersection_list[i])


    # r.table_create(newTablename).run()
    # r.table(newTablename).insert(trip_list).run()
    # cursor.close()
    if silent == False:
        print('Done correcting. ' \
        + 'Returning list of length ' + str(len(trip_list)) + '.')
    # return newTablename
    return(trip_list)


def remove_back_forth(G, sample_list, time_stamps):

    '''Called by correct_false_pos; should not be called directly.'''

    mapping = {1178349141:273628, 53072275:273153, 53072274:273606, 53213825:273603, 53142971:273158, 53205955:273100, 53072273:273636, 53160865:273595, 53160863:273155, 53160861:265078, 53160858:273095, 53160854:273099, 53160852:273083, 3618304999:273608, 53213824:273598, 53142969:273630, 53213415:273149, 53200378:273090, 53144265:273240, 53184114:273061, 53207667:273246, 53221907:273049, 53114228:273057, 2481926130:273601, 53213823:273594, 53205953:273104, 53213414:265082, 53144262:265074, 53142136:273668, 53207665:273107, 53221906:273106, 53187905:273103, 53213413:273620, 2053744124:273621, 53221905:273085, 53071891:273093, 53187904:265104, 53203467:273591, 53142966:273596, 53203466:265178, 53203465:265081, 53200375:273050, 53144260:265150, 53184111:273624, 53203464:273086, 53142130:265105, 53203463:265180, 53203462:265118, 53144742:273669, 53017297:265115, 53144257:273055, 53144734:273092, 53144733:273579, 53142127:273059, 53144731:273619, 53071880:273147, 53114264:273152, 53114263:273618, 53114262:273096, 53009977:273094, 53155726:265113, 53155724:273056, 53155723:265120}
    mapping_inv = {v: k for k, v in mapping.items()}
    rr = []
    for i in range(len(sample_list)):
        rr.append(mapping_inv.get(int(sample_list[i])))
        # if mapping_inv.get(int(sample_list[i])) == None:
            # print(int(sample_list[i]))
    i = 0
    repeats = {}
    while i < len(rr)-1:
        if rr[i+1] in list(nx.all_neighbors(G, rr[i])):
            a = rr[i+1]
            b = rr[i]
            if (a,b) in repeats:
                repeats[(a,b)] += 1
            elif (b,a) in repeats:
                repeats[(b,a)] += 1
            else:
                repeats[(a,b)]=1
        i += 1
    repeats = {k:v for (k,v) in repeats.items() if v >= 3}

    if bool(repeats) == False:
        return rr
    else:
        time_stamps = [int(x) for x in time_stamps]
        repeating = []
        for key, val in repeats.items():
            c = [i for i, x in enumerate(rr) if x == key[0]]
            d = [i for i, x in enumerate(rr) if x == key[1]]
            repeating.extend(c)
            repeating.extend(d)
            repeating = sorted(repeating)
            sep_repeating = [list(map(operator.itemgetter(1), g)) for k,
                g in itt.groupby(enumerate(repeating), lambda x: x[0]-x[1])]

            for sr in sep_repeating:
                c_time = []
                d_time = []
                c1 = sorted(list(set(sr).intersection(c)))
                d1 = sorted(list(set(sr).intersection(d)))
                cc = [list(map(operator.itemgetter(1), g)) for k,
                    g in itt.groupby(enumerate(c1), lambda x: x[0]-x[1])]
                for ccc in cc:
                    start = min(ccc)
                    end = max(ccc)
                    c_time.append(time_stamps[end]-time_stamps[start])
                dd = [list(map(operator.itemgetter(1), g)) for k,
                    g in itt.groupby(enumerate(d1), lambda x: x[0]-x[1])]
                for ddd in dd:
                    start = min(ddd)
                    end = max(ddd)
                    d_time.append(time_stamps[end]-time_stamps[start])
                if (len(d_time) >= 1 and len(c_time) >= 2) or (len(d_time) >= 2 and len(c_time) >= 1):
                    if sum(d_time) > sum(c_time):
                        new_rr = rr[:min(sr)]+[key[1] if x==key[0] else x for x in rr[min(sr):max(sr)+1]]+rr[max(sr)+1:]
                    else:
                        new_rr = rr[:min(sr)]+[key[0] if x==key[1] else x for x in rr[min(sr):max(sr)+1]]+rr[max(sr)+1:]
                    rr = new_rr
                else:
                    rr = rr
        return rr