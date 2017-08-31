import rethinkdb as r

def combine_days(db_name, silent=True):

    """Combines days of data into one JSON list.

    db_name [str]: an existing RethinkDB database.
    silent [bool]: if True, does not print reports.


    Reads all tables in the given database into memory
    and returns them as a list of dicts."""

    indiv_days = r.db(db_name).table_list().run()

    if len(indiv_days) > 7:
        raise(Exception('Database contains more than 7 days of data:\n' \
            + str(indiv_days) + '\n\nDelete days by connecting to ' \
            + 'RethinkDB from python (and running `r.table_drop(<tablen' \
            + 'ame>).run()`, without backticks. See docs for more info.'))

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
