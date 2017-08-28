import numpy as np
import pandas as pd
from sklearn.externals import joblib

def classify(trip_list, algorithm='gradient_boosting_classifier', silent=True):

    """Classifies trips as either cruising or not cruising.

    Classification proceeds by one of three algorithms trained previously on
    one week of labeled data under a "semi-supervised" learning framework.
    Details can be found in the main documentation.

    trip_list [list]: a list of dicts in JSON format.
    algorithm [str]: one of 'logistic_regression',
        'gradient_boosting_classifier' or 'decision_tree' (the default). The
        non-default options may provide more reasonable output in cases where
        artifacts show up in the heatmap (e.g. very low or very high cruising
        rates). More details in the main docs.
    silent [bool]: if True, does not print reports.

    Returns list of dicts in JSON format."""


    metadata = pd.DataFrame(trip_list)
    metadata = metadata.reset_index(drop=True)
    index_hash_mapping = dict(zip(list(metadata.index), list(metadata['group'])))

    if silent == False:
        print('Classifying ' + str(len(metadata)) + ' trips.')

    # Remove unneeded columns
    del metadata['group']
    del metadata['id']
    del metadata['reduction']
    del metadata['hour']
    del metadata['timeofday']
    del metadata['weekday']
    del metadata['date']
    # # These features would not provide additional information gain
    del metadata['distance_shortest']
    del metadata['distance_total']
    del metadata['duration_of_trip']
    del metadata['fhv']
    metadata = metadata.astype(float)
    metadata['speed_average'] = metadata['speed_average']*2.23694
    metadata['speed_max'] = metadata['speed_max']*2.23694
    metadata['speed_standard_deviation'] = metadata['speed_standard_deviation']*2.23694

    # Determine which paths are not_cruising
    not_cruising = []
    not_cruising.extend(list(metadata[(metadata['time_percentage_driving'] == 0) & (metadata['time_percentage_bogus'] == 0)].index))
    not_cruising.extend(list(metadata['time_percentage_walking'][metadata['time_percentage_walking'] == 100].index))
    not_cruising = list(set(not_cruising))
    metadata1 = metadata[~metadata.index.isin(not_cruising)]
    #Get data where threshold == 1  --> not cruising
    not_cruising_threshold = 1
    not_cruising.extend(list(metadata1[metadata1['distance_ratio'] == not_cruising_threshold].index))
    metadata1 = metadata[~metadata.index.isin(not_cruising)]

    # Determine which paths are cruising
    cruising_threshold = 0.3
    cruising = list(metadata1[metadata1['distance_ratio'] < cruising_threshold].index)

    # Create known and unknown datasets as well as training set from known dataset
    not_cruising_data = metadata[metadata.index.isin(not_cruising)]
    not_cruising_data['label'] = 'not_cruising'
    cruising_data = metadata[metadata.index.isin(cruising)]
    cruising_data['label'] = 'cruising'
    knowns = pd.concat([not_cruising_data, cruising_data])
    unknowns = metadata[(~metadata.index.isin(not_cruising)) & (~metadata.index.isin(cruising))]
    del knowns['distance_ratio']
    del unknowns['distance_ratio']

    # Choose model of interest
    if algorithm == 'decision_tree':
        model = joblib.load('models/decision_tree.pkl')
    elif algorithm == 'logistic_regression':
        model = joblib.load('models/logistic_regression.pkl')
    elif algorithm == 'gradient_boosting_classifier':
        model = joblib.load('models/gradient_boosting_classifier.pkl')
    else: pass

    # Predict based on model chosen
    y_unknown_pred = model.predict(unknowns)
    predicted_cruising = y_unknown_pred[y_unknown_pred == 1].sum()/unknowns.shape[0]*100.0
    rev_dic = {1: 'cruising', 0: 'not_cruising'}
    y_unknown_pred = [rev_dic[n] if n in rev_dic else n for n in y_unknown_pred]
    unknowns['label'] = y_unknown_pred
    knowns['predicted'] = 'False'
    unknowns['predicted'] = 'True'
    all_labeled = pd.concat([knowns, unknowns]).rename(index=index_hash_mapping)
    add_type = dict(zip(list(all_labeled.index), list(all_labeled['predicted'])))
    add_label = dict(zip(list(all_labeled.index), list(all_labeled['label'])))

    for i in range(len(trip_list)):
        trip_list[i]['predicted'] = add_type.get(trip_list[i]['group'])
        trip_list[i]['label'] = add_label.get(trip_list[i]['group'])

    if silent == False:
        print('Total number of cruising vehicles: ', int((unknowns.shape[0] * predicted_cruising/100.0) + len(cruising)))
        print('Total % of cruising vehicles: ', round(100.0*((unknowns.shape[0] * predicted_cruising/100.0) + len(cruising))/metadata.shape[0], 2),'%')

    return trip_list
