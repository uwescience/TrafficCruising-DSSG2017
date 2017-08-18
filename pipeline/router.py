import networkx as nx

def router(trip_list, graph, silent=True):

    """Fills in trip routes based on the most likely (shortest) path.

    Paths are determined by sequential use of Dijkstra's Shortest Path algorithm
    on a directed graph.

    trip_list [list]: a list of dicts in JSON format.
    graph [Networkx graph object]: must be a directed graph.
    silent [bool]: if True, does not print reports.

    Returns list of dicts in JSON format."""

    if silent == False:
        print('Preparing to route ' + str(len(trip_list)) + ' trips.')

    if nx.is_directed(graph) == True: directed = True
    elif nx.is_directed(graph) == False: directed = False

    # newTablename = table_name + '_RTD'

    # cursor = r.table(table_name).run()
    # trip_list = list(cursor)
    loop_counter = 0
    loop_size = len(trip_list)
    for doc in trip_list:

        if silent == False:
            loop_counter = loop_counter + 1
            if loop_counter % 10000 == 0:
                print('Routing. Finished ' + str(loop_counter) \
                    + ' trips.')

        all_points_to_add = []

        for i in range(len(doc['reduction'])):
            node_i = int(doc['reduction'][i]['IntersectionID'])
            time_i = int(round(float(doc['reduction'][i]['time'])))
            points_to_add = []

            if directed == True and i < len(doc['reduction']) - 1:
                neighb_test = is_successor(graph, int(doc['reduction'][i+1]['IntersectionID']), node_i)
            elif directed == False and i < len(doc['reduction']) - 1:
                neighb_test = is_neighbor(graph, int(doc['reduction'][i+1]['IntersectionID']), node_i)
            else: pass

            if (i < len(doc['reduction']) - 1 and not neighb_test):

                total_time = float(int(doc['reduction'][i+1]['time']) - time_i)

                shortest_path = nx.shortest_path(graph, source = node_i,
                    target = int(doc['reduction'][i+1]['IntersectionID']),
                    weight='distance')
                total_distance = nx.shortest_path_length(graph, source = node_i,
                    target = int(doc['reduction'][i+1]['IntersectionID']),
                    weight='distance')
                try:
                    average_speed = total_distance/total_time
                except:
                    from pprint import pprint
                    raise(Exception(pprint(doc)))

                shortest_path = shortest_path[1:-1]

                for node_j in shortest_path:

                    time = float(time_i) + float(nx.shortest_path_length(graph,source = node_i,target = node_j,weight='distance')/average_speed)

                    points_to_add.append({'IntersectionID' : str(node_j), 'sensor':  None, 'strength' : None, 'time' : str(time)})

                all_points_to_add.append((i+1,points_to_add))

        all_points_to_add.sort(reverse=True)
        for paths in all_points_to_add:
            i=0
            for points in paths[1]:
                doc['reduction'].insert(paths[0]+i,points)

                i = i + 1

        for i in range(len(doc['reduction'])):
            doc['reduction'][i]['sequence'] = str(i)

    # r.table_create(newTablename).run()
    # r.table(newTablename).insert(trip_list).run()
    # cursor.close()
    if silent == False:
        print('Done routing. Returning list of length ' \
            + str(len(trip_list)) + '.')
    # return newTablename

    return trip_list


def is_successor(graph, node2, node1):

    """Is node 2 the successor of node 1 on a directed graph?"""

    successors = graph.successors(node1)
    successors.append(node1)
    if (node2 in successors): return True
    else: return False


def is_neighbor(graph, node2, node1):

    """Is node 2 a neighbor of node 1 (on an undirected graph)?"""

    neighbors = graph.neighbors(node1)

    if (node2 in neighbors): return True
    else: return False