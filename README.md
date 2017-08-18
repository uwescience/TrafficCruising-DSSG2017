# DSSG2017-TrafficSensors

## Description

Vehicle cruising (individuals looking for parking and for-hire vehicles operating without a passenger) is a major contributor to traffic congestion in downtown Seattle. Still, the magnitude and location of vehicle cruising is poorly understood. To get a better understanding of where vehicles cruise, we propose a framework for using traffic sensor data. We generate most likely paths traversed through filtering out unrealistic behavior and incorporating routing. We break up individual trips via segmentation in terms of time and method of transportation. After segmentation, we introduce metadata to describe the trip and use a semi-supervised machine learning approach to label the data. Ultimately, we create an interactive heat map of downtown Seattle that can be used to visualize the relative levels of cruising.

This research has the potential to help transportation agencies, technology companies, and car companies predict the availability of parking and more accurately direct travelers with online, mobile, and connected tools, thereby reducing congestion impacts, emissions, and fuel costs.

## Web Application Demo

<img src="results/demo.gif">

## Description of Folders
* analysis: contains code for supporting tasks carried out throughout the process of building the pipeline.
* app: contains code for the web application to visualize the aggregated data.
* pipeline: contains code for our process of transforming the data to a usable format.

## Team Members

**Project Lead**
* Steve Barham, Data Scientist, Seattle Department of Transportation

**Data Science Leads**
* Valentina Staneva
* Vaughn Iverson

**DSSG Fellows**
* Brett Bejcek
* Anamol Pundle
* Orysya Stus
* Michael Vlah
