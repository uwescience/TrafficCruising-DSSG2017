import networx as nx

def zipper_remover(trip_list, undirected_graph, directed_graph, silent=True):
    """ Trips with pedestrians walking the wrong way on a one-way street, 
        when routed on a directed graph create a zipper-like pattern with 
        an artificially inflated velocity. This function identifies and 
        removes these patterns.

        trip_list [list]: a list of dicts in JSON format.
        undirected_graph [Networkx graph object]: must be an undirected graph.
        directed_graph [Networkx graph object]: must be an undirected graph.
        silent [bool]: if True, prints reports.

        Returns a list of trips in json format"""

    if (silent == False):
        print('Preparing to remove zipper sequences for ' \
            + str(len(trip_list)) + ' trips.')

    loop_counter = 0
    loop_size = len(trip_list)

    for doc in trip_list:

        zipper_sequence = []
        loop_measure = 0;
        i = 0

        if silent == False:
            loop_counter = loop_counter + 1
            if loop_counter % 10000 == 0:
                print('Removing zipper sequences. Finished ' + str(loop_counter) \
                    + ' trips.')


        while (i < len(doc['reduction']) - 1):

            node_i = doc['reduction'][i]
            node_i_neighbors = undirected_graph.neighbors(int(node_i['IntersectionID']))


            array_of_neighbors = []

            if (node_i['sensor']!= None):
                array_of_neighbors.append(int(node_i['sequence']))
                for j in range(i+1, len(doc['reduction'])):

                    node_j = doc['reduction'][j]
                    if (node_j['sensor'] != None and node_i['IntersectionID'] != node_j['IntersectionID']):


                        node_j_neighbors = undirected_graph.neighbors(int(node_j['IntersectionID']))

                        nearest_neighbor_test = is_neighbor(undirected_graph, int(node_i['IntersectionID']), int(node_j['IntersectionID']))
                        shortest_path_length_undirected = nx.shortest_path_length(undirected_graph, source=int(node_i['IntersectionID']), target=int(node_j['IntersectionID']), weight='distance')
                        shortest_path_length_directed = nx.shortest_path_length(directed_graph, source=int(node_i['IntersectionID']), target=int(node_j['IntersectionID']), weight='distance')
                        if (abs(shortest_path_length_directed - shortest_path_length_undirected) < 2.0): directed_test = False
                        else: directed_test = True
                        neighbor_test = nearest_neighbor_test and directed_test
                        common_neighbors = np.intersect1d(node_j_neighbors, node_i_neighbors)
                        two_removed_neighbor_test = False

                        same_street_common_neighbor = None

                        if(len(common_neighbors) > 0 and not neighbor_test):

                            for neighbor in common_neighbors:
                                try:
                                    street_1 = directed_graph[int(node_i['IntersectionID'])][neighbor]['name']
                                except:

                                    street_1 = directed_graph[neighbor][int(node_i['IntersectionID'])]['name']

                                try:
                                    street_2 = directed_graph[neighbor][int(node_j['IntersectionID'])]['name']
                                except:
                                    street_2 = directed_graph[int(node_j['IntersectionID'])][neighbor]['name']

                                if (street_1 == street_2 and directed_test == True):

                                    two_removed_neighbor_test = True
                                    same_street_common_neighbor = neighbor

                                    break

                                else: pass
                                
                        if (neighbor_test or two_removed_neighbor_test):

                            array_of_neighbors.append(int(node_j['sequence']))
                            node_i = node_j
                            node_i_neighbors = undirected_graph.neighbors(int(node_i['IntersectionID']))
                            i = j


                        else:
                            i = i + 1
                            break
                    else:
                        i = i + 1
                        continue
            else :
                i = i + 1

            loop_measure = loop_measure + 1

            if (loop_measure > 2*len(doc['reduction'])):
                print('Something went wrong')
                print(doc['group'])
                break

            if (len(array_of_neighbors) > 2) :
                zipper_sequence.append(array_of_neighbors)

            if (len(array_of_neighbors) > 2) :

                pass

        zipper_sequence = reversed(zipper_sequence)


        for seq in (zipper_sequence):
            if (len(seq) < 2):
                break

            first_intersection = int(doc['reduction'][seq[0]]['IntersectionID'])
            last_intersection = int(doc['reduction'][seq[-1]]['IntersectionID'])
            total_distance = nx.shortest_path_length(undirected_graph,source=first_intersection, target=last_intersection,weight='distance')
            total_time = float(doc['reduction'][seq[-1]]['time']) - float(doc['reduction'][seq[0]]['time'])
            average_speed = total_distance/total_time
            seq = sorted(seq, reverse = True)


            if (average_speed < 5.0):
                for ctr in range(len(seq)-1):

                    node_1 = int(doc['reduction'][seq[ctr]]['IntersectionID']); node_0 = int(doc['reduction'][seq[ctr+1]]['IntersectionID'])
                    time_0 = float(doc['reduction'][seq[ctr+1]]['time'])
                    time_1 = float(doc['reduction'][seq[ctr]]['time'])
                    time_0_to_1 = time_1 - time_0


                    if (not is_neighbor(undirected_graph, node_0, node_1)):

                        shortest_path = nx.shortest_path(undirected_graph,source = node_0,target = node_1,weight='distance')
                        total_distance = nx.shortest_path_length(undirected_graph,source = node_0,target = node_1,weight='distance')
                        average_speed = total_distance/time_0_to_1
                        time = time_0 + float(total_distance/average_speed)

                        for ctr2 in range(seq[ctr]-1, seq[ctr+1],-1):
                            del doc['reduction'][ctr2]

                        node_to_add = {'IntersectionID' : str(shortest_path[1]), 'sensor':  None, 'strength' : None, 'time' : str(time)}
                        doc['reduction'].insert(seq[ctr+1]+1,node_to_add)

                    elif (is_neighbor(undirected_graph, node_0, node_1)):
 
                        for ctr2 in range(seq[ctr]-1, seq[ctr+1],-1):
                            del doc['reduction'][ctr2]


    if silent == False:
        print('Done removing zipper sequences. Returning list of length ' \
            + str(len(trip_list)) + '.')
        
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

    #neighbors.append(node1)

    if (node2 in neighbors): return True
    else: return False