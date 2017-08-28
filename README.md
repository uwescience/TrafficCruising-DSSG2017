# Traffic Cruising Data Science for Social Good Project

## Description

A substantial portion of urban traffic can result from [drivers searching for parking spaces](http://shoup.bol.ucla.edu/CruisingForParkingAccess.pdf) and [waiting for (or traveling between) passengers](http://schallerconsult.com/rideservices/unsustainable.htm), in the case of for-hire vehicles. These sources of congestion are known collectively as *traffic cruising*, and are thought to be major contributors to traffic congestion in downtown Seattle. However, the magnitude and location of traffic cruising are poorly understood. By analyzing traffic sensor data, we devised a system for visualizing temporally- and spatially-explicit variations in the intensity of traffic cruising across Seattle's Central Business District. We use a series of heuristics and algorithms to estimate vehicle routes from anonymous data. We then describe each route with calculated metadata, by which we label it as either demonstrating cruising behavior or not, based on a semi-supervised machine learning approach. Finally, we create an interactive heat map of downtown Seattle that can be used to visualize magnitudes of each type of traffic cruising behavior.

This research has the potential to help transportation agencies, technology companies, and car companies predict the availability of parking and more accurately direct travelers with online, mobile, and connected tools, thereby reducing congestion impacts, emissions, and fuel costs.

## Web Application Demo

<img src="results/demo.gif">

## Description of Folders

* **analysis**: contains code for supporting tasks carried out throughout the process of building the pipeline.
* **app**: contains code for the web application to visualize the aggregated data.
* **data**: contains supporting data necessary at different steps in pipeline.
* **models**: contains analysis for different machine learning approaches.
* **pipeline**: contains code for our process of transforming the data to a usable format.
* **results**: contains final papers, presentations, and images.

## How To Use Web Application Demo

1. Clone github repository to local computer
2. Download Python 3.6 
3. Install required dependencies with the following command: "pip install Flask"
4. Navigate to app folder
5. From command line, type: "python app.py"
6. Open web browser to "localhost:5000"

## Team Members

**DSSG Fellows**
* Brett Bejcek, The Ohio State University
* Anamol Pundle, University of Washington
* Orysya Stus, University of California, San Diego
* Michael Vlah, University of Washington

**Data Science Leads**
* Valentina Staneva, eScience Institute
* Vaughn Iverson, eScience Institute

**Project Lead**
* Steve Barham, Seattle Department of Transportation
