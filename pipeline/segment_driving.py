import itertools as itt


def segment_driving(trip_list, silent=True):

    if silent == False:
        print('Separating driving portions of trips.')

    driving_list = []
    for doc in trip_list:
        modes = [doc['reduction'][i]['mode'] for i in range(1,
            len(doc['reduction']))]
        # import itertools as itt
        mode_rle = [(sum(1 for _ in gp), x) for x, gp in itt.groupby(modes)]
        dind = 0
        for i in range(len(mode_rle)):
            dind = dind + mode_rle[i][0]
            if mode_rle[i][1] == 'driving':
                newtrip = dict((k, doc[k]) for k in doc if k != 'reduction')
                newtrip['reduction'] = []
                if i == 0 and modes[0] == 'driving':
                    doc['reduction'][0]['mode'] = 'driving'
                    newtrip['reduction'].append(doc['reduction'][0])
                newtrip['reduction'].extend(doc['reduction'][(dind- \
                    (mode_rle[i][0]-1)):(dind+1)])
                driving_list.append(newtrip)
                # driving_list.append({all_but_reduc,
                    # 'reduction':dat[0]['reduction'][(dind-(mode_rle[i][0]-1)):(dind+1)]})

    return driving_list