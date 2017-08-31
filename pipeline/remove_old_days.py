import rethinkdb as r
import datetime
import itertools as itt

def remove_old_days(db_name, older_than=8, silent=True):

    """Deletes old days (tables) from a database.

    db_name [str]: an existing RethinkDB database.
    older_than [int]: delete days before this number of days ago.
        Defaults to 8, which will keep one week of data in the database
        (remember, no data are collected for the current day).
    silent [bool]: if True, does not print reports.

    Returns nothing."""

    #get today's date and the last date to keep
    today_date = datetime.datetime.today()
    delete_before = (today_date - datetime.timedelta(days=older_than-1)).date()

    #get all dates in db and convert to date objects
    days_in_db = r.db(db_name).table_list().run()
    dts_in_db = [datetime.datetime.strptime(d, '%Y_%m_%d').date() \
        for d in days_in_db]

    #find out which ones need to go
    inds_to_delete = [d < delete_before for d in dts_in_db]
    days_to_delete = list(itt.compress(days_in_db, inds_to_delete))

    #delete them
    if days_to_delete:
        for d in days_to_delete:
            r.db(db_name).table_drop(d).run()

    if silent == False:
        delete_before_str = delete_before.strftime('%Y-%m-%d')
        print('Removed ' + str(len(days_to_delete)) \
            + ' days prior to ' + delete_before_str + '.')
