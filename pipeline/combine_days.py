import rethinkdb as r

def combine_days(db_name, silent=True):

    """Combines days of data into one JSON list.

    db_name [str]: an existing RethinkDB database.
    silent [bool]: if True, does not print reports.

    WARNING: This function can use a *lot* of RAM. If you try to use it on
    a week of data for which filter_noncruising and segment_driving have not
    been run, you may consume all available RAM and mandate a forced shutdown
    of your computer. To avoid this, either omit combine_days in the pipeline
    and just leave each day separate, run the aforementioned filtering/segmenting
    steps before using this function, or run the pipeline on the EC2 instance,
    which has 15GB of RAM. If you're on a Unix machine, you can also prevent memory
    throttling with the shell command `ulimit -v <kB to allocate>`, where eg `5000000`
    would allocate 5GB of RAM and raise a Python memory error before throttling would
    occur. First you'd want to check how much memory is actually available with
    `free -m`, where the second row of the "free" column is the total amount of
    available memory in MB.
    
    Reads all tables in the given database into memory
    and returns them as a list of dicts."""

    indiv_days = r.db(db_name).table_list().run()

    if len(indiv_days) > 7:
        raise(Exception('Database contains more than 7 days of data. ' \
            + 'Run remove_old_days to prevent memory throttling.'))

    if len(indiv_days) == 0:
        raise(Exception("Database contains no tables. Either you're" \
            + "connected to the wrong database, the pipeline hasn't" \
            + "been run yet, or the pipeline is broken."))

    if silent == False:
        print('Combining ' + str(len(indiv_days)) + ' days of trips.')

    combined = []
    for i in range(len(indiv_days)):

        if silent == False:
            print('Appending day ' + str(i + 1) + ' of ' \
                + str(len(indiv_days)) + '.')

        temp = list(r.db(db_name).table(indiv_days[i]).run())
        combined.extend(temp)

    return combined
