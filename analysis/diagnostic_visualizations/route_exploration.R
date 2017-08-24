#visualization of preprocessed and routed paths for examination
#of parkers and deadheaders)
#Brett Bejcek and Mike Vlah (vlahm13@gmail.com)
#7/20/17

#basic use:
#1. in Rstudio, fold sections with Alt+o (Windows, Linux) or Cmd+Opt+o (OS X)
#2. set working directory and paths to data files below (contact us to discuss data access)
    #NOTE: requires both pre- and post-routed JSON input files. Post-routed must
    #have passed through at least the "add_features" step of the pipeline.
#3. place cursor after section B and run everything above it using Ctrl+Alt+b (Windows, Linux)
#or Cmd+Opt+b (OS X)
#4. unfold section C (click box to the right of the section header) and explore.
#5. save anything interesting you found using the commented lines in section D

#TODO:
#1. add option to plotter for labeling only sensor hits by time
#2. add option to filt by blocks_observed when total time is divided into n_blocks
#3. fix the color of the final point in cases like this: 3b44db3b498495f0402f64cbca6401bf6260200d37642f380cbb6f8cfb7b214e

#clear environment and suppress warnings
rm(list=ls()); cat('/014')
options(warn=-1)

## A - setup ####

#install packages if necessary
package_list <- c('jsonlite','ggmap','gridExtra','RColorBrewer',
                  'stringr','sourcetools')
new_packages <- package_list[!(package_list %in% installed.packages()[,"Package"])]
if(length(new_packages)) install.packages(new_packages)
#get latest version of ggmap from github (otherwise some base maps don't work)
# if(!require(ggmap)) {library(devtools); install_github("dkahle/ggmap")}

#load packages
for(i in package_list) library(i, character.only=TRUE)

#set this to your project parent directory
setwd('~/git/dssg/cruising/')

#set paths to various data files
# PATH_FOR_CORRECTED_JSON = "~/Desktop/MT_images/0_corrected.json"
# PATH_FOR_ROUTED_JSON = "~/git/dssg/cruising/data/large_files/testing/simple_zipper_fix.json"
# PATH_FOR_ROUTED_JSON = "~/Desktop/MT_images/0_routed.json"
PATH_FOR_CORRECTED_JSON = "data/large_files/testing/JSON1494284400_PF_RBF_GSEG_PF.json"
PATH_FOR_ROUTED_JSON = "data/large_files/testing/JSON1494284400_PF_RBF_GSEG_PF_RTD_ZR.json"
PATH_FOR_SENSORS = "data/large_files/correction_sequence/Acyclica_sensors.csv"
PATH_FOR_INTERSECTIONS = "data/large_files/intersection_sensor_lat_lon.csv"

#import files
# original <- fromJSON(PATH_FOR_ORIGINAL_JSON) # Data for original unfiltered, unrouted paths
corrected <- fromJSON(PATH_FOR_CORRECTED_JSON) # Data for filtered paths but not routed paths
routed <- fromJSON(PATH_FOR_ROUTED_JSON) # Data for both filtered and routed paths
sensors <- read.csv(PATH_FOR_SENSORS) # Lists sensors
intersections <- read.csv(PATH_FOR_INTERSECTIONS) # Lists all intersections

#set up ggplot map
Seattle <-get_map('Seattle', zoom=15, source="stamen",
                  maptype="terrain-lines") # Call to map only once
p <- ggmap(Seattle) # Store as ggmap object for easy plotting

#open a plot window (OS X can use quartz, which is better than x11, but whatevs)
if (is.null(dev.list()) == TRUE){
    if(.Platform$OS.type == "windows"){
        windows(record=TRUE, width=16, height=9)
    } else {
        x11(width=16, height=9)
    }
}

## B - functions ####

#identify various types of travelers and read saved lists
#(details in section C)
filt = function(gap=0, ngaps=0, stop=0,
                          n_sensors=0, disp_ratio=-999){

    out = character()

    #identify special cases (see following comments)
    for(i in 1:nrow(corrected)){

        #travelers who disappear for >= gap minutes and then return
        readtimes = as.numeric(corrected$reduction[[i]]$time)
        gap_durations = diff(readtimes)

        #travelers who disappear and return >= ngaps times for >= gap minutes
        gap_count = length(which(gap_durations >= gap*60))

        #travelers who stay in one place for >= stop minutes
        hits_per_sensor = rle(corrected$reduction[[i]]$sensor)$lengths #vector of # repeats for each sensor
        repeat_sensors = which(hits_per_sensor != 1) #indices where # repeats > 1
        cs = cumsum(hits_per_sensor)
        rep_ends = cs[repeat_sensors] #indices of final times for sensors with repeats
        rep_starts = cs[repeat_sensors] - hits_per_sensor[repeat_sensors] + 1 #start times
        diffs = as.numeric(corrected$reduction[[i]]$time[rep_ends]) -
            as.numeric(corrected$reduction[[i]]$time[rep_starts])
        if(length(diffs) == 0){diffs = 0} #if there are no stops, assign diffs=0

        #possible bus drivers (total_reads/nsensors = disp_ratio)
        nsensors = length(unique(corrected$reduction[[i]]$sensor))
        total_reads = nrow(corrected$reduction[[i]])

        #filter by each of these criteria
        if(any(gap_durations >= gap*60) &&
           gap_count >= ngaps &&
           any(diffs >= stop*60) &&
           total_reads / nsensors > disp_ratio &&
           nsensors > n_sensors &&
           gap_count >= ngaps) {
            out = append(out, corrected$group[i])
        }
    }

    #load stored lists
    stored_list_names = dir('data/tricky_hashes/', pattern='.json')
    stored_lists = list()
    for(i in 1:length(stored_list_names)){
        stored_lists[[i]] = fromJSON(read(paste0('data/tricky_hashes/',
                stored_list_names[i])))
        names(stored_lists)[[i]] = str_match(stored_list_names[i],
                                             '(.*)\\.json')[2]
    }

    return(list('filtered'=out, 'stored_lists'=stored_lists))
}

#identify where travelers stop for multiple reads (chill-seshes).
#this function is used within the plotting function and
#not called directly
label_chillsesh = function(data_mat, rm_repeats=TRUE){

    #color the points at the end of each chill sesh (when a traveler is sitting still)
    data_mat$pt_col = rep('white', nrow(data_mat)) #first assign white to all points
    hits_per_sensor = rle(data_mat$sensor)$lengths #vector of # repeats for each sensor
    repeat_sensors = which(hits_per_sensor != 1) #indices where # repeats > 1
    cs = cumsum(hits_per_sensor)
    rep_ends = cs[repeat_sensors] #indices of final times for sensors with repeats
    rep_starts = cs[repeat_sensors] - hits_per_sensor[repeat_sensors] + 1 #start times
    diffs = as.numeric(data_mat$time[rep_ends]) - as.numeric(data_mat$time[rep_starts])
    data_mat$pt_col[rep_ends] = as.vector(cut(diffs,
        breaks=c(0, 60, 5*60, 15*60, 99999),
        labels=brewer.pal(9, 'YlGnBu')[c(3,5,7,9)],
        right=FALSE)) #color by chill time
    data_mat$pt_col[which(is.na(data_mat$strength))] = NA #make interpolated points invisible

    #remove all but the last point of a chill sesh if desired
    if(rm_repeats){
        chill_seshes = mapply(seq, rep_starts, rep_ends, SIMPLIFY=FALSE)#get indices of chill seshes
        maxes = sapply(chill_seshes, max) #get ends of chill seshes
        chill_tails = setdiff(unlist(chill_seshes), maxes) #get everything but the ends
        if(length(chill_tails)){ #if there are any chill seshes
            data_mat = data_mat[-chill_tails,] #remove everything but the ends
        }
    }
    data_mat$order = 1:nrow(data_mat)

    return(data_mat)
}

#thanks for making legends easy, ggplot
#(this is used in the plot; no need to call)
make_legends = function(label){

    #make line legend
    # if(label=='speed'){
    labs = factor(c('[0-5)','[5-15)','[15-25)','[25-40)','>= 40'),
                  levels=c('[0-5)','[5-15)','[15-25)','[25-40)','>= 40'))
    df = data.frame(lab = labs,
                    val = rep(0, 5),
                    col = brewer.pal(9, 'YlOrRd')[c(1,3,5,7,9)])
    pal = brewer.pal(9, 'YlOrRd')
    x = ggplot(df, aes(x=val, y=val, color=lab)) + geom_line(size=1) +
        scale_color_manual(name='MPH',
                           values=c('[0-5)'=pal[1], '[5-15)'=pal[3],
                                    '[15-25)'=pal[5], '[25-40)'=pal[7],
                                    '>= 40'=pal[9])) +
        theme(panel.background=element_rect(fill='white', color='white'),
              legend.position=c(.5, .5),
              # legend.key.height=unit(.16, units='npc'),
              # legend.key.width=unit(c(.8), units='npc'),
              # legend.text=element_text(size=32),
              # legend.title=element_text(size=48, face='bold'),
              # legend.title.align=0.5,
              axis.line=element_blank(),axis.text.x=element_blank(),
              axis.text.y=element_blank(),axis.ticks=element_blank(),
              axis.title.x=element_blank(),
              axis.title.y=element_blank())
    # } else {
    #     if(label=='mode'){
    labs3 = factor(c('walking', 'driving', 'bogus'),
                  levels=c('walking', 'driving', 'bogus'))
    df3 = data.frame(lab = labs3,
                    val = rep(0, 3),
                    col = c('aquamarine2','coral2', 'black'))
    z = ggplot(df3, aes(x=val, y=val, color=lab)) + geom_line(size=1) +
        scale_color_manual(name='Mode',
                           values=c('walking'='aquamarine2',
                                    'driving'='coral2',
                                    'bogus'='black')) +
        theme(panel.background=element_rect(fill='white', color='white'),
              legend.position=c(.5, .5),
              # legend.key.height=unit(.16, units='npc'),
              # legend.key.width=unit(c(.8), units='npc'),
              # legend.text=element_text(size=32),
              # legend.title=element_text(size=48, face='bold'),
              # legend.title.align=0.5,
              axis.line=element_blank(),axis.text.x=element_blank(),
              axis.text.y=element_blank(),axis.ticks=element_blank(),
              axis.title.x=element_blank(),
              axis.title.y=element_blank())

    #     }
    # }

    #make point legend
    labs2 = factor(c('0','(0-1)','[1-5)','[5-15)','>= 15'),
                   levels=c('0','(0-1)','[1-5)','[5-15)','>= 15'))
    df2 = data.frame(lab = labs2,
                     val = rep(0, 5),
                     col = c('white', brewer.pal(9, 'YlGnBu')[c(3,5,7,9)]))
    pal2 = brewer.pal(9, 'YlGnBu')
    y = ggplot(df2, aes(x=val, y=val, color=lab)) + geom_point(size=2) +
        scale_color_manual(name='Minutes',
                           values=c('0'='white', '(0-1)'=pal2[3],
                                    '[1-5)'=pal2[5], '[5-15)'=pal2[7],
                                    '>= 15'=pal2[9])) +
        theme(panel.background=element_rect(fill='white', color='white'),
              legend.position=c(.5, .5),
              axis.line=element_blank(),axis.text.x=element_blank(),
              axis.text.y=element_blank(),axis.ticks=element_blank(),
              axis.title.x=element_blank(),
              axis.title.y=element_blank())

    return(list(line=x, point=y, line2=z))
}

#plot function. details in section C
plotter = function(hash_vec, label_all=FALSE, color_interps=TRUE,
                   starting_point=1, rm_repeats=TRUE, label='speed'){

    #remove hashes prior to the selected starting point
    hash_vec = hash_vec[starting_point:length(hash_vec)]

    #vector to append interesting hashes to
    saved_hashes = character()

    # Iterate through all hashes in the hash vector
    for(i in 1:length(hash_vec))
    {
        current_hash = hash_vec[i] # Current hash we are working on
        print(current_hash) # Let's user know which hash they are working on

        # original_id = which(original[['group']]==current_hash)# Location of path in original JSON file
        corrected_id = which(corrected[['group']]==current_hash) # Location of path in corrected JSON file
        routed_id = which(routed[['group']]==current_hash) # Location of path in routed JSON file

        ## WORKING WITH CORRECTED DATA NOW
        num_sensors = length(corrected[['reduction']][[corrected_id]][['IntersectionID']]) # num_sensors in corrected data set
        corrected_data <- matrix(nrow = num_sensors, ncol = 6) # creates empty matrix
        colnames(corrected_data) <- c("sensor","lat", "lon", "time", "strength", "adj_lon") # columns for matrix

        for(j in 1:num_sensors) # iterates through sensors in path for given hash
        {
            corrected_data[j,"sensor"] = corrected[['reduction']][[corrected_id]][['sensor']][j] # records current sensor
            corrected_data[j,"lat"] = sensors[sensors$serial == corrected[['reduction']][[corrected_id]][['sensor']][j],'latitude']
            corrected_data[j,"lon"] = sensors[sensors$serial == corrected[['reduction']][[corrected_id]][['sensor']][j],'longitude']
            corrected_data[j,"time"] = corrected[['reduction']][[corrected_id]][['time']][j]
            corrected_data[j,"strength"] = timestamp = corrected[['reduction']][[corrected_id]][['strength']][j]
            corrected_data[j,"adj_lon"] = sensors[sensors$serial == corrected[['reduction']][[corrected_id]][['sensor']][j],'longitude'] # for purposes of plotting label
        }

        corrected_data <- as.data.frame(corrected_data,stringsAsFactors=FALSE) # convert to dataframe
        corrected_data <- corrected_data[order(corrected_data$time),] # order by time
        corrected_data$order <- 1:nrow(corrected_data) # assign order variable
        rownames(corrected_data) <- 1:nrow(corrected_data) # reorder rownames to correct order
        corrected_data$htime = format(as.POSIXct(as.numeric(corrected_data$time), origin="1970-01-01"),"%I:%M:%S %p") # adjust time to readable format

        #color intersections by time spent at them
        corrected_data = label_chillsesh(corrected_data,
                                         rm_repeats=rm_repeats)

        # for purposes of plotting labels
        for(j in 2:nrow(corrected_data))
        {
            sensor = corrected_data$sensor[j]
            if(sensor %in% corrected_data$sensor[1:j-1])
            {
                base = max(which(corrected_data$sensor[1:j-1]==sensor))
                corrected_data$adj_lon[j] = (as.numeric(corrected_data$adj_lon[base]) + 0.0009)
            }
        }

        ## WORKING WITH ROUTED DATA NOW
        num_sensors = length(routed[['reduction']][[routed_id]][['IntersectionID']]) # num_sensors in original JSON file for hash with original_id
        routed_data <- matrix(nrow = num_sensors, ncol = 13) # Create an empty matrix with num_sensors rows and 7 columns
        colnames(routed_data) <- c("intersection","lat","lon","order","adj_lon","adj_lon2",
                                   "adj_lat","sensor","time","distance","velocity",
                                   "strength","mode") # columns of matrix

        vel = c(routed$reduction[[routed_id]]$velocity[-1], 0) #shift velocity vector forward for accurate plotting
        md = c(routed$reduction[[routed_id]]$mode[-1], NA) #shift velocity vector forward for accurate plotting

        for(j in 1:num_sensors) # iterating through path for hash_vec[original_id] in original JSON file
        {
            routed_data[j,"intersection"] = routed[['reduction']][[routed_id]][['IntersectionID']][j] # get the intersectionID
            routed_data[j,"lat"] = intersections[intersections$intersection == routed[['reduction']][[routed_id]][['IntersectionID']][j],'intersection_lat']
            routed_data[j,"lon"] = intersections[intersections$intersection == routed[['reduction']][[routed_id]][['IntersectionID']][j],'intersection_lon']
            routed_data[j,"order"] = as.numeric(routed[['reduction']][[routed_id]][['time']][j]) + 1
            routed_data[j,"adj_lat"] = intersections[intersections$intersection == routed[['reduction']][[routed_id]][['IntersectionID']][j],'intersection_lat'] # adj_lat to avoid plotting points over each other
            routed_data[j,"adj_lon"] = intersections[intersections$intersection == routed[['reduction']][[routed_id]][['IntersectionID']][j],'intersection_lon'] # adj_lon for printing label on map purposes
            routed_data[j,"adj_lon2"] = intersections[intersections$intersection == routed[['reduction']][[routed_id]][['IntersectionID']][j],'intersection_lon'] # adj_lon for printing label on map purposes
            routed_data[j,"sensor"] = routed$reduction[[routed_id]]$sensor[j]
            routed_data[j,"time"] = routed$reduction[[routed_id]]$time[j] #unix time
            # routed_data[j,"distance"] = routed$reduction[[routed_id]]$distance[j]
            routed_data[j,"velocity"] = vel[j]
            routed_data[j,"strength"] = routed$reduction[[routed_id]]$strength[j]
            routed_data[j,"mode"] = md[j]
        }

        routed_data <- as.data.frame(routed_data,stringsAsFactors=FALSE) # convert matrix to dataframe
        routed_data <- routed_data[order(as.numeric(routed_data$order)),] # order data frame by time
        rownames(routed_data) <- 1:nrow(routed_data) # reorder rownames to correct order
        routed_data$order = as.integer(routed_data$order)
        routed_data$distance = as.numeric(routed_data$distance)
        routed_data$velocity = as.numeric(routed_data$velocity)
        routed_data$htime = format(as.POSIXct(as.numeric(routed_data$time), origin="1970-01-01"),"%H:%M:%S")

        #color intersections by time spent at them
        routed_data = label_chillsesh(routed_data, rm_repeats=rm_repeats)

        # if(label=='speed'){
            #color segments by velocity
        routed_data$velocity = routed_data$velocity * 2.23694 #convert m/s to mph
        routed_data$line_col = as.vector(cut(routed_data$velocity, #color
               breaks=c(-99999,0,5,15,25,40,99999),
               labels=c('cyan', brewer.pal(9, 'YlOrRd')[c(1,3,5,7,9)]), #speed shown in shades of red. other colors for errors
               # labels=c('cyan', 'yellow', 'orange', 'red', 'purple', 'green'),
               right=FALSE))
        if(!color_interps){
            routed_data$line_col[is.na(routed_data$pt_col)] = 'black'
        }
        # } else {
            # if(label=='mode'){
                #color segments by mode of transportation
                # mode_shifted = c(routed_data$mode[nrow(routed_data)],
                #                  routed_data$mode[1:(nrow(routed_data)-1)])
        mode_shifted = routed_data$mode
        routed_data$line_col2 = as.vector(factor(mode_shifted,
          levels=c('bogus','chilling','driving','walking'),
          labels=c('black','white','coral2','aquamarine2')))
        routed_data$line_col2[nrow(routed_data)] = 'transparent'
                # routed_data$line_col = modecol[which(!is.na(modecol))]

        #     }
        # }

        #make interpolated lines dashed
        # routed_data$line_wd = rep(2, nrow(routed_data)) #make all lines thick
        # routed_data$line_wd[is.na(routed_data$pt_col)] = 1 #thin the interp ones
        # routed_data$line_type = rep(1, nrow(routed_data)) #make all lines solid
        # routed_data$line_type[is.na(routed_data$pt_col)] = 2 #dash the interp ones
        # routed_data$opacity = rep(0.6, nrow(routed_data)) #make all lines transparent
        # routed_data$opacity[is.na(routed_data$pt_col)] = 1 #fill in the interp ones

        for(j in 2:nrow(routed_data)){ #shift intersections that have been hit already
            intersection = routed_data$intersection[j] # gets current sensor in loop
            if(intersection %in% routed_data$intersection[1:j-1]){ # checks to see if sensor exists above it
                base = max(which(routed_data$intersection[1:j-1]==intersection)) # gets the location of last time sensor listed
                routed_data$adj_lat[j] = (as.numeric(routed_data$adj_lat[base]) + 0.0002) # offsets the location of printing
                routed_data$adj_lon[j] = (as.numeric(routed_data$adj_lon[base]) + 0.0009) # offsets the location of printing
            }
        }

        #generate appropriate legends
        legends = make_legends(label=label)
        line_legend = legends$line
        point_legend = legends$point
        mode_legend = legends$line2

        # Prefiltered plot
        plot2 = p + geom_path(data=corrected_data,
                               aes(x=as.numeric(lon), y=as.numeric(lat)),
                               size = 3, color = 'red',
                              alpha = 0.3) +
            theme(legend.position="none",
                  plot.title=element_text(color="#666666", face="bold",
                                          size=24, hjust=0.5)) +
            geom_point(data=corrected_data,
                       aes(x=as.numeric(lon), y=as.numeric(lat)),
                       size = 5, color=corrected_data$pt_col, alpha = 0.6) +
            geom_text(data = corrected_data,
                      aes(x=as.numeric(adj_lon), y=as.numeric(lat), label = order),
                      size = 4) +
            ggtitle('Prefiltered') + xlab('Longitude') + ylab('Latitude')

        # Rerouted plot
        if(!label_all){ #only plot first and last label (time)
            routed_data$htime[2:(nrow(routed_data)-1)] = '' #remove all but first and last htimes
            routed_data$order = routed_data$htime #replace order column with htime, since that's what gets plotted
            routed_data$adj_lon2 = as.numeric(routed_data$lon) + 0.0018
        } else { #plot every other label (order)
            routed_data$adj_lon2 = as.numeric(routed_data$adj_lon) + 0.0006
            routed_data$order[seq(2, nrow(routed_data), 2)] = ''
        }

        plot3 <- p + geom_path(data=routed_data,
                               aes(x=as.numeric(lon), y=as.numeric(adj_lat)),
                               size = 1, linetype=1,
                               color=routed_data$line_col) +
            theme(legend.position="none",
                  plot.title=element_text(color="#666666", face="bold",
                                          size=24, hjust=0.5)) +
            geom_point(data=routed_data,
                       aes(x=as.numeric(lon), y=as.numeric(adj_lat)),
                       size=2, color=routed_data$pt_col, alpha=1) +
            geom_text(data=routed_data,
                      aes(x=adj_lon2, y=as.numeric(lat), label=order),
                      size=4) +
            ggtitle('Routed') + xlab('Longitude') + ylab('Latitude')

        #this is for visualizing mode
        plot4 <- p + geom_path(data=routed_data,
                               aes(x=as.numeric(lon), y=as.numeric(adj_lat)),
                               size = 1, linetype=1,
                               color=routed_data$line_col2) +
            theme(legend.position="none",
                  plot.title=element_text(color="#666666", face="bold",
                                          size=24, hjust=0.5)) +
            geom_point(data=routed_data,
                       aes(x=as.numeric(lon), y=as.numeric(adj_lat)),
                       size=1.5, color=routed_data$pt_col, alpha=1) +
            geom_text(data=routed_data,
                      aes(x=adj_lon2, y=as.numeric(lat), label=order),
                      size=4) +
            ggtitle('Mode') + xlab('Longitude') + ylab('Latitude')


        if(label=='speed'){
            grid.arrange(plot2, plot3, line_legend, point_legend,
                         layout_matrix=matrix(c(1,1,1,1,2,2,2,2,3,
                                                1,1,1,1,2,2,2,2,3,
                                                1,1,1,1,2,2,2,2,4,
                                                1,1,1,1,2,2,2,2,4), nrow=4, byrow=TRUE))
        } else {
            if(label=='mode'){
                grid.arrange(plot3, plot4, line_legend, mode_legend, point_legend,
                             layout_matrix=matrix(c(1,1,1,1,1,2,2,2,2,2,3,
                                                    1,1,1,1,1,2,2,2,2,2,3,
                                                    1,1,1,1,1,2,2,2,2,2,4,
                                                    1,1,1,1,1,2,2,2,2,2,5,
                                                    1,1,1,1,1,2,2,2,2,2,5), nrow=5, byrow=TRUE))
            }
        }

        rownames(corrected_data) = 1:nrow(corrected_data)
        rownames(routed_data) = 1:nrow(routed_data)
        print("Pre-filtered:")
        print(corrected_data[,c('sensor','time','strength')])

        print("Routed:")
        print(routed_data[,c('intersection', 'order', 'mode')])

        selection = readline(prompt="s=save current hash; q=quit; other=continue ")
        if(selection == 'q'){
            break
        } else {
            if(selection == 's'){
                saved_hashes = append(saved_hashes, current_hash)
            } else next
        }
    }
    message('exiting plot mode')
    return(saved_hashes)
}

## C - explore ####

#first, choose how you'd like to filter travelers using the
#filt function. (this function also reads any saved lists
#in data/tricky_hashes automatically)
# filt(gap=0, #gap duration (minutes between sensor hits)
#      ngaps=0, #number of gaps of the above duration
#      stop=0, #duration of longest stop (mins)
#      n_sensors=0, #unique sensor hits
#      disp_ratio=-999) #total reads / unique sensor hits

#select only travelers who disappear for at least 15 minutes
filtered_hashes = filt(gap=15)

#select only travelers who disappear at least twice for
#at least 10 minutes each
filtered_hashes = filt(gap=10, ngaps=2)

#select only travelers who stay in one place for at least
#18 minutes and hit at least 6 sensors
filtered_hashes = filt(stop=18, n_sensors=6)

#select only potential bus drivers
filtered_hashes = filt(gap=15, ngaps=2, disp_ratio=2, n_sensors=4)

#find routing weirdness
filtered_hashes = filt(disp_ratio=7, n_sensors=4)

#then plot like so. you can store interesting hashes as you go by
#following the prompt
# plotter(hashes, #list of hashes
#         label_all=FALSE, #label all points or just endpoints
#         color_interps=TRUE, #color routed segments by speed
#         starting_point=1, #hash in the list to start from
#         rm_repeats=TRUE #omit all but the last time point during a stop
#         label = either 'speed' or 'mode' (choose the latter to see walk/drive portions

#plot a filtered list from above and store anything interesting in save_list
save_list = plotter(filtered_hashes$filtered)

#explore stored lists (must have corresponding json files loaded
plotter(filtered_hashes$stored_lists$parking_and_not_parking_1494259200)
plotter(filtered_hashes$stored_lists$parking_etc_1494284400)
plotter(filtered_hashes$stored_lists$potential_returners_1494259200)
plotter(filtered_hashes$stored_lists$for_steve)
plotter(filtered_hashes$stored_lists$weirdness_1494284400)

#workspace:
deets = read.csv('~/Desktop/untracked/more_images/deets.csv')
image_list = deets$hash
# filtered_hashes = filt()
save_list = plotter(image_list, label='speed', starting_point=19)
plotter('ebe14e562cb8dbff11deb72e448a6e7de4c8e4718509b48f45196b401022d0e9')
plotter('4c8f38c9dcdd93426bba77d7ea18e6ead29e8fd9407433b7df45f33a014ab1a9_G1')
plotter('e3a1bdae31513739f2bba133b40acc07c223d7081ed54d78c22d562a5613e2e4')

current_hash=filtered_hashes$filtered[1]; label_all=FALSE; color_interps=TRUE;
starting_point=1; rm_repeats=TRUE; label='speed'

## D - store interesting hashes ####

#comment the following lines after running them to avoid
#accidental overwriting of saved lists!

# write(toJSON(save_list),
#       file='data/tricky_hashes/for_steve.json')
