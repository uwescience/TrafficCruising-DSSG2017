## Description of Folders and Files

* **static**: contains javascript, css, and data files necessary to produce the web application
  * **css**: contains all stylesheets
    * main.css: styling for web app
  * **data**: contains all data necessary for web app
    * aggregated.txt: aggregated lat/lon pairs with count for given time
    * base_layer.js: assigns javascript variable to be plotted to show the grid of downtown Seattle
    * chart_data_cruising.json: data necessary to produce lower right chart of cruising volume for given day
    * chart_data_vhf.json: data necessary to produce lower right of cruising volume for a given day
    * intersections.js: assigns javascript variable to be plotted to show all the intersections of the grid
  * **javascript**: contains all javascript used in web app
    * addlisteners.js: sets buttons on page as active or non-active, redraws charts when resize, other minor features
    * chart.js: draws chart in lower right corner for traffic volume
    * drawmap.js: functions pertaining to main map on left side of screen
    * getdata.js: AJAX calls to python web framework to get data
* **templates**: contains template html file to be rendered by Flask app
* app.py: Flask web app

## Web Application Demo

<img src="../results/demo.gif">

## How To Use Web Application Demo

1. Clone github repository to local computer
2. Download Python 3.6 
3. Install required dependencies with the following command: "pip install Flask"
4. Navigate to app folder
5. From command line, type: "python app.py"
6. Open web browser to "localhost:5000"

