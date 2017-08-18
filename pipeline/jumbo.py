import pandas as pd
import numpy as np
import gc
import rethinkdb as r
import operator
import itertools as itt
import requests
import datetime
import time
import os
import io
import math


def jumbo_write_json(data, table_name, chunk_size=5000, silent=True):

    '''Write big JSON lists to RethinkDB.

    Essential for datasets that are larger than 100,000 docs (ReQL max write).
    Often necessary even for smaller ones.

    data [list]: a list of dicts in JSON format.
    table_name [str]: an existing RethinkDB table.
    chunk_size [int or float of form BASEeEXP]: input list will be broken into
        chunks of this size. If you encounter memory use issues, reduce this
        value.
    silent [bool]: if True, does not print reports.

    Must be connected to a RethinkDB instance before using this.'''

    if chunk_size > 1e5:
        raise(Exception('Maximum JSON chunk_size is 100,000.'))

    #determine list length, number of chunks, and remainder
    list_length = len(data)
    chunk_size = int(chunk_size) #max array length for a ReQL write is 100k; but that uses too much mem
    nchunks = math.ceil(list_length / chunk_size)
    rem = list_length % chunk_size

    if silent == False:
        print('Writing list of ' + str(list_length) + ' trips to table "' \
            + table_name + '".')

    #digest data and write to RethinkDB
    for i in range(nchunks):
        s = i * chunk_size #chunk_start

        if i == nchunks - 1 and rem != 0:
            e = s + rem + 1
        else:
            e = (i+1) * chunk_size

        if silent == False:
            print('Writing trips ' + str(s) + '-' + str(e - 1) + '.')

        #write chunk to rethink (some data may be lost in case of power failure)
        r.table(table_name).insert(data[s:e]).run(durability='soft',
            noreply=False)

    if silent == False:
        ndocs = r.table(table_name).count().run()
        print('Table "' + table_name + '" now contains ' + str(ndocs) \
            + ' trips.')


def jumbo_write_df(df, table_name, df_chunk_size=5e5,
    json_chunk_size=5e3, verbosity=1):

    '''Write big pandas dataframes to RethinkDB.

    Essential for datasets that are larger than 100,000 rows (ReQL max write).
    Often necessary even for smaller ones.

    df [pandas DataFrame]: nuff said.
    table_name [str]: an existing RethinkDB table.
    df_chunk_size [int or float of form BASEeEXP]: input df will be broken into
        chunks of this many rows. If you encounter memory use issues, reduce
        this value first. Maximum accepted value is 1,000,000.
    json_chunk_size [int or float of form BASEeEXP]: input list passed to
        jumbo_write_json will be broken into chunks of this size. If you
        encounter memory use issues, reduce this value second. Maximum
        accepted value is 100,000 (ReQL write limit).
    verbosity [int]: determines the number of reports that will be printed.
        0 = no reports
        1 = reports from this function only
        2 = reports from this function and subroutine jumbo_write_json.

    Calls jumbo_write_json.
    Must be connected to a RethinkDB instance before using this.'''

    if df_chunk_size > 1e6:
        raise(Exception('Maximum df_chunk_size is 1,000,000.'))
    if json_chunk_size > 1e5:
        raise(Exception('Maximum json_chunk_size is 100,000. This size is \
            rarely a good idea.'))

    #set verbosity for jumbo_write_json
    sil = False if verbosity == 2 else True

    if verbosity > 0:
        print('Preparing ' + str(len(df)) + '-row DataFrame for database.')

    # json_list = []
    while len(df): #runs as long as rows remain in the dataframe

        #take a chunk of the dataframe and convert to json list
        l = min(len(df), int(df_chunk_size)) #get the first chunk_size lines, or all the rest if fewer
        chunk = df.iloc[0:l] #subset them from the df
        df = df.drop(df.index[0:l]) #drop those lines
        json_list = chunk.to_dict('records')

        if verbosity > 0:
            print('Converting chunk of ' + str(l) + ' rows to JSON format.')

        # s_buf = io.StringIO() #create string buffer
        # chunk.to_csv(s_buf, index=False) #send chunk as csv to buffer
        # s_buf.seek(0) #reset buffer to first position
        # json_list = list(csv.DictReader(s_buf)) #read csv into json list
        # s_buf.close() #close string buffer

        #free up some memory
        del(chunk)
        gc.collect() #remove all vars no longer referenced to free a bit more

        #open connection to null device for banishing unneeded outputs
        black_hole = open(os.devnull, 'w')
        # black_hole = [json_list[i].pop('', None) for i in range(len(json_list))]
        # black_hole = [json_list[i].pop('Unnamed: 0', None) for i in range(len(json_list))]

        #sort by hash.
        json_list = sorted(json_list, key=operator.itemgetter('hash'))

        #group json list by hash and remove hash from each reduction
        jl2 = []
        for hsh, red in itt.groupby(json_list, key=operator.itemgetter('hash')):
            red = list(red)
            black_hole = [red[i].pop('hash', None) for i in range(len(red))]
            jl2.append({'group':hsh, 'reduction':red})
        del(json_list)

        if verbosity > 0:
            print('Finished grouping chunk by hash. Passing list of length ' \
                + str(len(jl2)) + ' to jumbo_write_json.')

        #write list to rethink
        jumbo_write_json(data=jl2, table_name=table_name,
            chunk_size=json_chunk_size, silent=sil)
        del(jl2)

    if verbosity > 0:
        ndocs = r.table(table_name).count().run()
        print('Finished writing day of records. Wrote ' + str(ndocs) \
            + ' docs to table "' + table_name + '".')


def retrieve_records(api_key, sensor_path, table_name,
    end_date=(datetime.datetime.strptime(time.strftime('%Y-%m-%d'),
        '%Y-%m-%d') - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
    start_date=None, json_chunk_size=5e3, verbosity=1):

    '''Pull records from Acyclica's API and write to RethinkDB.

    api_key [str]: the 41-character alphanumeric key you were given by Acyclica.
        Should be read in from an environment variable, encrypted if possible.
    sensor_path [str]: the path to Acyclica_sensors_CBD.csv
        (should be fetched automatically once we package this thing).
    table_name [str]: the name of the RethinkDB table that will be written. If
        a table of the same name already exists, it will be overwritten.
    end_date [str]: a date string of the form 'YYYY-MM-DD' specifying the last
        day of data to pull from Acyclica. Defaults to yesterday.
    start_date [str]: a date string of the form 'YYYY-MM-DD' specifying the first
        day of data to fetch from Acyclica. Defaults to None, which means only
        end_date will be fetched. Set this to 'prev_week' to fetch the full week
        starting 8 days ago and ending yesterday.
    json_chunk_size [int or float of form BASEeEXP]: lists passed to
        jumbo_write_json will be broken into chunks of this size. No need to
        modify unless you encounter memory use issues, in which case you should
        first try reducing the default value of 5,000.
    df_chunk_size [int or float of form BASEeEXP]: DataFrames passed to
        jumbo_write_df will be broken into chunks of this many rows.
        No need to modify unless you encounter memory use issues, in which
        case you should next try reducing the default value of 500,000.
    verbosity [int]: determines the number of reports that will be printed.
        0 = no reports
        1 = reports from this function only
        2 = more reports from this function and from subroutine
            jumbo_write_json.

    Calls jumbo_write_df, which calls jumbo_write_json.
    Must be connected to a RethinkDB instance before using this.

    Pull at minimum 1 day and at maximum 1 week of data in increments of 1
    day.'''

    #start timing
    start_time = time.time()

    #check for size limit errors
    # if df_chunk_size > 1e6:
    #     raise(Exception('Maximum df_chunk_size is 1,000,000.'))
    if json_chunk_size > 1e5:
        raise(Exception('Maximum json_chunk_size is 100,000. This size is \
            rarely a good idea.'))

    #check for end_date format error
    try:
        nul = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except:
        raise(Exception('end_date must be of the form "YYYY-MM-DD".'))

    #set appropriate start dates based on input
    if start_date == 'prev_week':
        start_date = (datetime.datetime.strptime(end_date,
            '%Y-%m-%d') - datetime.timedelta(days=6)).strftime('%Y-%m-%d')
    elif start_date is None:
        start_date = end_date
    else: pass

    #check for start_date format error
    try:
        nul = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    except:
        raise(Exception('start_date must be of the form "YYYY-MM-DD".'))

    #add 23 h, 59 m, and 59 s to the end date (to grab the whole day)
    end_date = datetime.datetime.strptime(end_date,
        '%Y-%m-%d') + datetime.timedelta(hours=23, minutes=59, seconds=59)

    #convert datetime objects to unix time
    start_unix = int(time.mktime(datetime.datetime.strptime(start_date,
        '%Y-%m-%d').timetuple()))
    end_unix = int(time.mktime(end_date.timetuple()))

    #make sure the user isn't trying to grab more than a week of data, and that
    #end is after start
    if end_unix - start_unix > 604800:
        raise(Exception('Please specify a range of dates no greater than one week.'))
    if end_unix - start_unix < 0:
        raise(Exception('end_date must be later than start date.'))

    #determine how many days have been selected
    dif = end_unix - start_unix
    ndays = math.ceil(dif / (24 * 3600))

    #get sensor data
    sensors = pd.read_csv(sensor_path)
    # sensors = sensors.drop(['name', 'short_name','latitude','longitude'], axis=1)
    sensors.columns = ['IntersectionID','sensor']
    sensor_list = list(sensors['sensor'])

    if verbosity > 0:
        print('Preparing to acquire data for ' + str(ndays) + ' day(s) and ' \
            + str(len(sensor_list)) + ' sensors.')

    #remove tables and create them anew
    try:
        r.table_drop(table_name).run()

        if verbosity > 0:
            print('Table "' + table_name + '" already existed and has ' \
                + 'been deleted.')
    except: pass
    finally:
        r.table_create(table_name).run()

        if verbosity > 0:
            print('Created table "' + table_name + '".')

    #request and process one day at a time (roughly 5-10m records acquired per day)
    day_start_unix = start_unix
    for day in range(ndays):

        print('Acquiring records for day ' + str(day + 1) + ' of ' \
            + str(ndays) + '. May take several minutes.')

        #get endpoints for each iteration and (re)instantiate dataframe
        day_end_unix = day_start_unix + (23 * 3600) + 3599
        df = pd.DataFrame(columns=['Timestamp','MAC Hash','Strength','Serial'])

        #request and preprocess each sensor separately
        for i in range(len(sensor_list)):

            # sensorID = sensor_list[1]
            URL = "https://cr.acyclica.com/datastream/device/csv/time/" \
                + api_key + "/" + str(sensor_list[i]) + "/" \
                + str(day_start_unix) + "/" + str(day_end_unix)

            #get raw web content and read into a dataframe
            items = requests.get(URL).content
            newdf = pd.read_csv(io.StringIO(items.decode('utf-8')),
                usecols=['Timestamp','MAC Hash','Strength','Serial'])

            #round timestamp to nearest second
            newdf['Timestamp'] = newdf['Timestamp'].round().astype('int')

            #drop repeated reads within 1s, keeping read with highest strength
            strmaxes = newdf.groupby(['Timestamp',
                'MAC Hash'])['Serial'].transform(max)
            newdf = newdf[newdf['Serial'] == strmaxes]

            #append to main dataframe
            df = df.append(newdf, ignore_index=True)

            if verbosity == 2:
                if i + 1 in [15,30,45]:
                    print('Got data for ' + str(i + 1) + ' of ' \
                        + str(len(sensor_list)) \
                        + ' sensors. So far there are ' + str(len(df)) \
                        + ' reads for day ' + str(day + 1) + '.')

        del(newdf)

        # df = pd.read_csv('/home/mike/Desktop/untracked/aug5_df_justAfterAppending.csv')
        # print('WARNING: STILL READING LOCAL DATAFRAME FROM CSV')

        #drop repeated reads again, keeping read with highest strength
        strmaxes = df.groupby(['Timestamp',
            'MAC Hash'])['Serial'].transform(max)
        df = df[df['Serial'] == strmaxes]

        pre_filt_len = str(len(df))
        if verbosity > 0:
            print('Found ' + pre_filt_len + ' sensor reads for day ' \
                + str(day + 1) + '. Cleaning those now.')

        # df.to_csv('/home/mike/Desktop/untracked/aug5_df_justAfterAppending.csv', index=False)

        json_list = df_to_json_etc(df, verbosity, pre_filt_len, sensors)

        if verbosity > 0:
            print('Converted DataFrame to JSON list and grouped by hash. ' \
                + 'Passing list of length ' + str(len(json_list)) \
                + ' to jumbo_write_json.')

        # json_list = json_list[0:11000]

        #set verbosity for jumbo_write_json
        sil = False if verbosity == 2 else True

        #write list to rethink
        # while len(json_list): #runs as long as rows remain in the dataframe
        #
        #     #take a chunk of the dataframe and convert to json list
        #     l = min(len(df), int(df_chunk_size)) #get the first chunk_size lines, or all the rest if fewer
        #     chunk = df.iloc[0:l] #subset them from the df
        #     df = df.drop(df.index[0:l]) #drop those lines
        #     json_list = chunk.to_dict('records')

            # if verbosity > 0:
            #     print('Converting chunk of ' + str(l) + ' rows to JSON format.')

        jumbo_write_json(data=json_list, table_name=table_name,
            chunk_size=json_chunk_size, silent=sil)

    # if verbosity > 0:
    #     ndocs = r.table(table_name).count().run()
    #     print('Finished writing day of records. Wrote ' + str(ndocs) \
    #         + ' docs to table "' + table_name + '".')

        # insert df into table as JSON (calls subroutine jumbo_write_json)
        # jumbo_write_df(df=df, table_name=table_name,
        #     df_chunk_size=df_chunk_size, json_chunk_size=json_chunk_size,
        #     verbosity=verbosity)

        #increment day
        day_start_unix = day_start_unix + (24 * 3600)

    if verbosity > 0:
        run_time = round((time.time() - start_time) / 60, 2)
        print('Finished writing all records for ' + str(ndays) + ' day(s) ' \
            + 'in ' + str(run_time) + ' minutes.')


def df_to_json_etc(df, verbosity, pre_filt_len, sensors):

    '''Called by retrieve_records. Not called directly.'''

    #drop duplicates again, just in case
    df = df.drop_duplicates(subset=['Timestamp', 'MAC Hash', 'Serial'],
        keep='first')

    #drop hashes with < 4 unique sensor hits
    unique_rows = df[['MAC Hash','Serial']].drop_duplicates()
    hit_counts = unique_rows['MAC Hash'].value_counts()
    low_hit_hashes = hit_counts.index[hit_counts < 4]
    df = df[-df['MAC Hash'].isin(low_hit_hashes)]

    if verbosity > 0:
        print('Cleaned duplicates and short trips. Got rid of ' \
            + str(int(pre_filt_len) - len(df)) + ' reads.')

    #convert columns back to int after appending changed them to float.
    #somehow pandas still has this bug from 2014
    df[['Timestamp', 'Strength', 'Serial']] = \
        df[['Timestamp', 'Strength', 'Serial']].astype('int')

    # len(df)
    # unique_rows = df[['hash','sensor']].drop_duplicates()
    # hit_counts = unique_rows['hash'].value_counts()
    # low_hit_hashes = hit_counts.index[hit_counts < 4]
    # df = df[-df['hash'].isin(low_hit_hashes)]

    #rename columns; merge sensor IDs; convert all columns to strings
    df.columns = ['time','hash','strength','sensor']
    df = pd.merge(df, sensors, on='sensor')
    df.astype('str')

    #convert to json format
    json_list = df.to_dict('records')

    del(df)
    gc.collect() #remove all vars no longer referenced to free a bit more

    #open connection to null device for banishing unneeded outputs
    black_hole = open(os.devnull, 'w')

    #sort by hash.
    json_list = sorted(json_list, key=operator.itemgetter('hash'))

    #group json list by hash and remove hash from each reduction
    jl2 = []
    for hsh, red in itt.groupby(json_list, key=operator.itemgetter('hash')):
        red = list(red)
        black_hole = [red[i].pop('hash', None) for i in range(len(red))]
        jl2.append({'group':hsh, 'reduction':red})
    del(json_list)

    return jl2