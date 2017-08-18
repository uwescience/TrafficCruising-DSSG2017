##################################################
## THIS IS FOR VAUGHN'S TASK --- MWAHAHAHAHAH   ##
##           07-06-17 | Brett Bejcek            ##
##################################################

# File List for Analysis of 2nd Street

files <- c("Sensor_Raw_1494252000.csv", "Sensor_Raw_1494255600.csv", "Sensor_Raw_1494259200.csv",
           "Sensor_Raw_1494262800.csv", "Sensor_Raw_1494266400.csv", "Sensor_Raw_1494270000.csv", 
           "Sensor_Raw_1494273600.csv", "Sensor_Raw_1494277200.csv", "Sensor_Raw_1494280800.csv",
           "Sensor_Raw_1494284400.csv", "Sensor_Raw_1494288000.csv", "Sensor_Raw_1494291600.csv",
           "Sensor_Raw_1494295200.csv", "Sensor_Raw_1494298800.csv", "Sensor_Raw_1494302400.csv",
           "Sensor_Raw_1494338400.csv", "Sensor_Raw_1494342000.csv", "Sensor_Raw_1494345600.csv",
           "Sensor_Raw_1494349200.csv", "Sensor_Raw_1494352800.csv", "Sensor_Raw_1494356400.csv",
           "Sensor_Raw_1494360000.csv", "Sensor_Raw_1494363600.csv", "Sensor_Raw_1494367200.csv",
           "Sensor_Raw_1494370800.csv", "Sensor_Raw_1494374400.csv", "Sensor_Raw_1494378000.csv",
           "Sensor_Raw_1494381600.csv", "Sensor_Raw_1494385200.csv", "Sensor_Raw_1494388800.csv",
           "Sensor_Raw_1494424800.csv", "Sensor_Raw_1494428400.csv", "Sensor_Raw_1494432000.csv",
           "Sensor_Raw_1494435600.csv", "Sensor_Raw_1494439200.csv", "Sensor_Raw_1494442800.csv",
           "Sensor_Raw_1494446400.csv", "Sensor_Raw_1494450000.csv", "Sensor_Raw_1494453600.csv",
           "Sensor_Raw_1494457200.csv", "Sensor_Raw_1494460800.csv", "Sensor_Raw_1494464400.csv",
           "Sensor_Raw_1494468000.csv", "Sensor_Raw_1494471600.csv", "Sensor_Raw_1494475200.csv",
           "Sensor_Raw_1494511200.csv", "Sensor_Raw_1494514800.csv", "Sensor_Raw_1494518400.csv",
           "Sensor_Raw_1494522000.csv", "Sensor_Raw_1494525600.csv", "Sensor_Raw_1494529200.csv",
           "Sensor_Raw_1494532800.csv", "Sensor_Raw_1494536400.csv", "Sensor_Raw_1494540000.csv",
           "Sensor_Raw_1494543600.csv", "Sensor_Raw_1494547200.csv", "Sensor_Raw_1494550800.csv",
           "Sensor_Raw_1494554400.csv", "Sensor_Raw_1494558000.csv", "Sensor_Raw_1494561600.csv",
           "Sensor_Raw_1494597600.csv", "Sensor_Raw_1494601200.csv", "Sensor_Raw_1494604800.csv",
           "Sensor_Raw_1494608400.csv", "Sensor_Raw_1494612000.csv", "Sensor_Raw_1494615600.csv",
           "Sensor_Raw_1494619200.csv", "Sensor_Raw_1494622800.csv", "Sensor_Raw_1494626400.csv",
           "Sensor_Raw_1494630000.csv", "Sensor_Raw_1494633600.csv", "Sensor_Raw_1494637200.csv",
           "Sensor_Raw_1494640800.csv", "Sensor_Raw_1494644400.csv", "Sensor_Raw_1494648000.csv")
# file paths to different sensor information

for(x in 1:length(files)){
# Read in Raw Data
Sensor_Raw_1494252000 <- read.csv(files[x])
sensors <- read.csv("Acyclica_Sensors.csv") # file path to sensor information
colnames(sensors)[6] <- "sensor"
sensors_2nd <- sensors[grepl('2nd*', sensors$short_name, perl=T),]
sensors_all_other <- sensors[!(sensors$sensor %in% sensors_2nd$sensor),]
data <- Sensor_Raw_1494252000
data <- unique(data[,1:6])

# Starting and End Point 
start <- 265104 #2nd and stewart beginning
end <- 265118 # 2nd and james end

# Filter out any hashes that don't touch start and end
hash_start <- unique(as.vector(data$hash[data$sensor == start]))
hash_end <- unique(as.vector(data$hash[data$sensor == end]))
hash_combined <- hash_start[hash_start %in% hash_end]
data <- data[data$hash %in% hash_combined,]

# Filter out before start and after end
data_appended <- data[0,]

for(i in as.vector(unique(data$hash)))
{
  subset <- data[data$hash == i,]
  timeStart <- subset$time[subset$sensor==start]
  timeEnd <- subset$time[subset$sensor==end]
  subset <- subset[subset$time>=timeStart[1],]
  subset <- subset[subset$time<=timeEnd[1],]
  data_appended <- rbind(data_appended,subset)
}
data <- data_appended

# Filter out if it touched any other point
hash.visitedAnyOtherPoint <- unique(as.vector(data[data$sensor %in% sensors_all_other$sensor,2]))
data <- data[!(data$hash %in% hash.visitedAnyOtherPoint),]

# Add Time Converted Column
# data$timeConverted <- as.POSIXct(data$time, origin = "1970-01-01")

# Plot for sanity check
# library(ggmap)
# Seattle <-get_map('Seattle', zoom = 15, source = "stamen", maptype = "terrain-lines")
# p <- ggmap(Seattle)
# p + geom_path(data=data, aes(x=longitude, y=latitude, color = hash), size=1) + theme(legend.position="none")

error_matrix <- matrix(data = 0, nrow = length(unique(data$hash)), ncol = nrow(sensors_2nd))
colnames(error_matrix) <- sensors_2nd$sensor
rownames(error_matrix) <- unique(data$hash)


if(length(unique(data$hash))!=0){
for(i in 1:length(unique(data$hash)))
{
  hash_data <- data[data$hash==unique(data$hash)[i],]
  error_matrix[i,sensors_2nd$sensor%in%hash_data$sensor] <- 1
}

error_matrix <- as.data.frame(error_matrix)
error_matrix$hash <- rownames(error_matrix)

#Time check

max <- aggregate(data$time,by=list(data$hash),max)
min <- aggregate(data$time,by=list(data$hash),min)
combined <- merge(max,min, by = "Group.1", all.x = TRUE)
combined$duration = combined$x.x - combined$x.y
combined <- combined[,c(1,4)]
colnames(combined)[1] <- "hash"

final <- merge(error_matrix,combined, by= "hash")
final$hour <- files[x]
if(x == 1)
{
  to_print <- final
} else {
  to_print <- rbind(to_print, final)
}
}
}

