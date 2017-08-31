# Pipeline instructions
There is already an AMI on AWS called CruisingPipeline_image. This image is set up and ready to go. If you're working locally, follow the instructions below. None of this has been tested on Windows, but it all works on OS X Yosemite and Ubuntu 14.04.
1. Install [RethinkDB](https://www.rethinkdb.com/docs/install/).
1. Start RethinkDB with `rethinkdb`. This will occupy your terminal until you close it with [ctrl]+c. If you're working remotely, use `rethinkdb &`. Once it loads, press [enter] to get your prompt back and keep working.
   + NOTICE: RethinkDB will store data in whichever directory you're in when you call `rethinkdb`. Data will be saved in a new subdirectory called rethinkdb_data. To access the same data each time you use RethinkDB, make sure you always run `rethinkdb` from the same directory.
1. Use pip to install networkx, rethinkdb, geopy, and tzlocal (e.g. `pip install networkx`). If you aren't using an Anaconda installation of Python, you'll need numpy, pandas, and a few other modules that are not part of the standard library. Errors will let you know if there are others. Install them with pip.
1. Make sure you have the most recent version of this repository. Assuming you cloned it, that can be done with `git pull origin master`.
1. If you have an Acyclica API key, store it as an environment variable (This step has been done on the AMI. You just have to put the real key inside the text file, which is in the home directory.)
   1. Write the key to a text file called, e.g. "acyclica_api.txt" (should be outside of any public version-controlled repo)
   1. Restrict user permissions to that file with `chmod 700 acyc_key.txt`.
   1. Append `export ACYC=$(cat <path>/acyc_key.txt)` to your shell run commands file. If you're using bash, this is usually called `.bashrc`, and it can usually be found in your home directory (as a hidden file). Change <path> to the actual path to the text file you created.
   1. Execute your run commands file, either with something like `. .bashrc` or by closing and reopening your terminal. If you already have `00_run_pipeline.py` open, you may have to close and reopen it too.
1. `00_run_pipeline.py` is set up to pull the last week of data (ending yesterday) from Acyclica, run each day through the standard series of filters, segmenters, router, and annotaters. If you'd like to modify the pipeline, you'll learn more about it in the next section. Change the working directory path near the top. It should point to the top level of the project folder (AKA git repo).
1. Save changes to `00_run_pipeline.py`. Run it with `python 00_run_pipeline.py`.
   + NOTICE: the pipeline is not currently set up to clean up old records. In other words, days of data pulled from Acyclica and run through the pipeline will accumulate within the database and probably cause problems with the visualization. We're working on this.
1. Results will be saved in the app directory. See readme file there for more. If you're using AWS, viewing the results may not be straightforward, as they'll be available on localhost, but localhost will be accessible via by a terminal window. We're working on this.

# Pipeline functions
Although there is a default arrangement of these functions in __00_run_pipeline.py__, many arrangements are possible. Some functions can be omitted or used with different arguments. Still others are as of now deprecated or have no proper context. The idea was to have a set of malleable tools for the eventual user to incorporate in modular fashion, to their own ends.

## graph_generator
__Creates directed and undirected graphs of downtown Seattle.__

### args
  + *path* [str]: path to nodes.geojson

Returns an list of Networkx graph objects: undirected graph (index 0) and
directed graph (index 1).

## retrieve_records
__Pull records from Acyclica's API and write to RethinkDB.__

  + *api_key* [str]: the 41-character alphanumeric key you were given by Acyclica.
    Should be read in from an environment variable, encrypted if possible.
  + *sensor_path* [str]: the path to Acyclica_sensors_CBD.csv
    (should be fetched automatically once we package this thing).
  + *db_name* [str]: the name of the RethinkDB database that will be populated.
  + *end_date* [str]: a date string of the form 'YYYY-MM-DD' specifying the last
    day of data to pull from Acyclica.
    + default = yesterday
  + *start_date* [str]: a date string of the form 'YYYY-MM-DD' specifying the first
    day of data to fetch from Acyclica. Defaults to None, which means only
    end_date will be fetched. Set this to 'prev_week' to fetch the full week
    starting 8 days ago and ending yesterday.
    + default = None
  + *json_chunk_size* [int or float of form BASEeEXP]: lists passed to
    jumbo_write_json will be broken into chunks of this size. No need to
    modify unless you encounter memory use issues, in which case you should
    first try reducing the default value of 5000.
    + default = 5000
  + *verbosity* [int]: determines the number of reports that will be printed.
    0 = no reports
    1 = reports from this function only
    2 = more reports from this function and from subroutine jumbo_write_json.
    + default = 1

Calls jumbo_write_json.
Must be connected to a RethinkDB instance before using this.

Pull at minimum 1 day and at maximum 1 week of data in increments of 1
day.

## remove_old_records
__Deletes old days (tables) from a database.__

### args
  + *db_name* [str]: an existing RethinkDB database.
  + *older_than* [int]: delete days before this number of days ago.
        Default value will keep one week of data in the database
        (remember, no data are collected for the current day).
    + default = 8
  + *silent* [bool]: if True, does not print reports.
    + default = True

Returns nothing.

## segment_gaps
__Splits trips if there are sufficiently large gaps in read times.__

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *undir_graph* [Networkx graph object]: should be an UNdirected graph.
  + *gap_dur* [int]: duration of gaps (in minutes) that will be used
    to split trips.
    + default = 10
  + *append_tag* [bool]: should trips that get split have tags
    (\_G0, \_G1, \_G2, etc.) appended to their hashes?
    + default = True
  + *split_neighbors_too* [bool]: if the intersection after a gap is a
    neighbor of the one before, should the trip be split?
    + default = True  
  + *label_fhvs* [bool]: should for-hire vehicles be labeled as such?
    + default = True
  + *silent* [bool]: if True, does not print reports.
    + default = True
  + *fhv_gap_thresh* [int]: the number of gaps of gap_dur duration above which
    a traveler will be labeled as a for-hire vehicle if label_fhvs is True.
    + default = 4

You'll want to rerun filter_short_trips after using this function.

Does not work on routed data.

Returns list of dicts in JSON format.

## segment_stops
__Splits trips if there are sufficiently large stops__

There is currently no use for this function, but it could be useful under future pipeline arrangements.

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *stop_dur* [int]: duration of stops (in minutes) that will be used
      to split trips.
    + default = 10
  + *append_tag* [bool]: should trips that get split have tags
      (\_S0, \_S1, \_S2, etc.) appended to their hashes?
    + default = True
  + *retain_stops* [bool]: if True, all mid-stop reads will be included with the
      segments before and after the stop
    + default = True
  + *silent* [bool]: if True, does not print reports.
    + default = True

You'll want to rerun filter_short_trips after using this function.

Does not work on routed data.

Returns list of dicts in JSON format.

## filter_short_trips
__Removes trips too short to be identifiable as cruising.__

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *unique_sensor_count* [int]: trips with fewer than this number of hits on
    unique sensors will be filtered out.
    + default = 4
  + *silent* [bool]: if True, does not print reports.
    + default = True

Returns list of dicts in JSON format.

## filter_spurs
__Filters false positive sensor reads and arranges trips by timestamp.__

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *filter_time* [int]: Of two successive reads within this amount of time,
      the one with the weaker signal will be filtered out.
  + *silent* [bool]: if True, does not print reports.
    + default = True

Returns list of dicts in JSON format.

## correct_false_pos
__Removes in-line false positives.__

Due to excessive sensor range, travelers can be detected far away from their
true location, even alternatingly on adjacent sensors while stopped between
them, creating a "back-and-forth" (if on two-way street) or rapid looping
(if on one-way) artifact. This removes that.

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *graph* [Networkx graph object]: must be a directed graph.
  + *silent* [bool]: if True, does not print reports.
    + default = True

Returns list of dicts in JSON format.

## router
__Fills in trip routes based on the most likely (shortest) path.__

Paths are determined by sequential use of Dijkstra's Shortest Path algorithm
on a directed graph.

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *graph* [Networkx graph object]: must be a directed graph.
  + *silent* [bool]: if True, does not print reports.
    + default = True

Returns list of dicts in JSON format.

## remove_zippers
__Corrects zig-zag artifact produced by movement against one-way traffic.__

Trips with pedestrians walking the wrong way on a one-way street,
when routed on a directed graph create a zipper-like pattern with
an artificially inflated velocity. This function identifies and
removes these patterns.

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *undirected_graph* [Networkx graph object]: must be an undirected graph.
  + *directed_graph* [Networkx graph object]: must be an undirected graph.
  + *silent* [bool]: if True, prints reports.
    + default = True

Returns a list of trips in json format

## add_features
__Populates each trip document with features used for classification and
  visualization.__

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *graph* [Networkx graph object]: must be a directed graph.
  + *silent* [bool]: if True, does not print reports.
    + default = True

Returns list of dicts in JSON format.

## label_modes
__Labels trip segments by likely mode of travel.__

Labels are "chilling" if traveler is stationary, "walking" if slow,
"driving" if fast, and "bogus" if too fast to be real.

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *silent* [bool]: if True, does not print reports.

Returns list of dicts in JSON format.

## classify
__Classifies trips as either cruising or not cruising.__

Classification proceeds by one of three algorithms trained previously on
one week of labeled data under a "semi-supervised" learning framework.
Details can be found in the main documentation.

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *algorithm* [str]: one of 'logistic_regression',
      'gradient_boosting_classifier' or 'decision_tree'. The
      non-default options may provide more reasonable output in cases where
      artifacts show up in the heatmap (e.g. very low or very high cruising
      rates). More details in the main docs.
    + default = 'gradient_boosting_classifier'
  + *silent* [bool]: if True, does not print reports.
    + default = True

Returns list of dicts in JSON format.

## filter_noncruising
__Removes trips labeled as 'not_cruising' after classification.__

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *keep_only_driving* [bool]: should segments not identified
      as 'driving' be dropped from all trips? This should
      always be set to False unless modifications have been
      made to the heatmap code. Use the function segment_driving
      instead.
    + default = False
  + *keep_all_fhv* [bool]: should for-hire vehicles be included in
      the output regardless of whether they're displaying cruising
      behavior?
    + default = True
  + *silent* [bool]: if True, does not print reports.
    + default = True

Returns list of dicts in JSON format.

## segment_driving
__Isolates driving portions of trips.__

For each trip, identifies all segments where the traveler
was identified as 'driving' (versus 'walking', etc.), and
separates them as if they're individual trips. This is
necessary for the heatmap to work properly.

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *silent* [bool]: if True, does not print reports.
    + default = True

Returns list of dicts in JSON format.

## combine_days
__Combines days of data into one JSON list.__

### args
  + *db_name* [str]: an existing RethinkDB database
  + *silent* [bool]: if True, does not print reports.
    + default = True

Reads all tables in the given database into memory
and returns them as a list of dicts.

## aggregate
__Combines paths by street segment in preparation for visualization.__

### args
  + *trip_list* [list]: a list of dicts in JSON format.
  + *write_path* [str]: path and filename for heatmap data.
    + default = 'app/static/data/aggregated.txt'
  + *chart_path_1* [str]: path and filename for for-hire vehicle
      side plot data.
    + default = 'app/static/data/chart_data_fhv.json'
  + *chart_path_2* [str]: path and filename for cruising vehicle
      side plot data.
    + default = 'app/static/data/chart_data_cruising.json'
  + *intersections_path* [str]: path to intersections.csv data file.
    + default = 'data/intersections.csv'
  + *silent* [bool]: if True, does not print reports.
    + default = True

Returns nothing.

## jumbo_write_df
__Write big pandas dataframes to RethinkDB.__

Essential for datasets that are larger than 100,000 rows (ReQL max write).
Often necessary even for smaller ones.

### args
  + *df* [pandas DataFrame]: 'nuff said.
  + *db_name* [str]: a RethinkDB database, existing or not.
  + *table_name* [str]: a RethinkDB table, existing or not.
  + *df_chunk_size* [int or float of form BASEeEXP]: input df will be broken into
    chunks of this many rows. If you encounter memory use issues, reduce
    this value first. Maximum accepted value is 1,000,000.
    + default = 5e5
  + *json_chunk_size* [int or float of form BASEeEXP]: input list passed to
    jumbo_write_json will be broken into chunks of this size. If you
    encounter memory use issues, reduce this value second. Maximum
    accepted value is 100,000 (ReQL write limit).
    + default = 5=3
  + *verbosity* [int]: determines the number of reports that will be printed.
    0 = no reports
    1 = reports from this function only
    2 = reports from this function and subroutine jumbo_write_json.
    + default = 1

Calls jumbo_write_json.
Must be connected to a RethinkDB instance before using this.


## jumbo_write_json
__Write big JSON lists to RethinkDB.__

Essential for datasets that are larger than 100,000 docs (ReQL max write).
Often necessary even for smaller ones.

### args
  + *data* [list]: a list of dicts in JSON format.
  + *db_name* [str]: a RethinkDB database, existing or not.
  + *table_name* [str]: a RethinkDB table, existing or not.
  + *chunk_size* [int or float of form BASEeEXP]: input list will be broken into
    chunks of this size. If you encounter memory use issues, reduce this
    value.
    + default = 5000
  + *silent* [bool]: if True, does not print reports.
    + default = True

Must be connected to a RethinkDB instance before using this.

---
# Internal functions

## df_to_json_etc
Called by retrieve_records. Not called directly.

## is_successor
Called by router. Not called directly.

## is_neighbor
Called by router and remove_zippers. Not called directly.

## removes_back_forth
Called by correct_false_pos. Not called directly.
