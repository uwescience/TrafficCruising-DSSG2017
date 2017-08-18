#reference map for sensor points (and all nodes included in our routing scheme)
#mike vlah (vlahm13@gmail.com)
#7/7/17

rm(list=ls()); cat('/014')

#install (if necessary) and load packages
if(!require(ggmap)) install.packages('ggmap')
if(!require(jsonlite)) install.packages('jsonlite')
library(ggmap)
library(jsonlite)

#load data
setwd('~/git/dssg/cruising/data/')
sens = read.csv('large_files/Acyclica_sensors_CBD.csv')
nodez = fromJSON('nodes.json')
# ints = read.csv('../scripts/Shortest_Distance/intersection_sensor_lat_lon.csv')

#get seattle street map from gmaps
Seattle = get_map('Seattle', zoom=15, source="stamen", maptype="terrain-lines")

#plot labeled image just for reference purposes
# pdf(width=10, height=10, file='../images/ints_labeled.pdf', compress=FALSE)
p = ggmap(Seattle)
# p + geom_point(data=ints,
p + geom_point(data=nodez$elements,
               aes(x=lon, y=lat, color=I('red')),
               # aes(x=intersection_lon, y=intersection_lat, color=I('red')),
               size=1) +
    geom_text(data=nodez$elements,
              aes(x=lon, y=lat, color=I('black'),
                             label=id, hjust=0),
              nudge_y=0.000, nudge_x=0.0002, size=2.5) +
    geom_point(data=sens,
               aes(x=longitude, y=latitude, color=I('blue')),
               size=1.9)
    # geom_text(data=sens, aes(x=longitude, y=latitude, color=I('gray30'),
    #                          label=short_name, hjust=0),
    #           nudge_y=0.00024, nudge_x=0.0001, size=2.8) +
    # geom_text(data=sens, aes(x=longitude, y=latitude, color=I('blue'),
    #                          label=serial, hjust=0),
    #           nudge_y=-0.00018, nudge_x=0.0001, size=2.4)
# dev.off()

#plot UNlabeled image for presentation
# pdf(width=5, height=5, file='../images/sensors_unlabeled.pdf', compress=FALSE)
png(width=5, height=5, units='in', filename='../images/sensors_unlabeled.png',
     type='cairo', res=300)
p = ggmap(Seattle, legend='topright')
p + geom_point(data=nodez$elements,
               aes(x=lon, y=lat, color=I('mediumblue')),
               size=1) +
    geom_point(data=sens,
               aes(x=longitude, y=latitude, color=I('mediumblue')),
               size=2.4) +
    geom_point(data=sens,
               aes(x=longitude, y=latitude, color=I('cyan3')),
               size=1.9) #ggplot legends are impossible...
    # scale_shape_manual(name="Intersections in\nDirected Graph",
    #                      values=c('mediumblue','cyan3'),
    #                      breaks=c("Female", "Male"),
    #                      labels=c("Woman", "Man"))
    # theme(legend.text=c('Intersection', 'Intersection with Sensor'))
dev.off()

