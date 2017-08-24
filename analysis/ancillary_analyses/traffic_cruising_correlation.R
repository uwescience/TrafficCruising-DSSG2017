#how does cruising relate to traffic flow? to parking occupancy?
#Mike Vlah (vlahm13@gmail.com)
#12 Aug 2017

#this script requires data that are not public. contact me to discuss access.

#load data and subset
library(jsonlite)
trip_list = fromJSON('~/Desktop/untracked/final_beforeFilterNoncruise.json')
trip_list = trip_list[,c('label','timeofday','hour')]
cruz_sub = trip_list[which(trip_list$label=='cruising'),]
parking = read.csv('~/git/dssg/cruising/data/large_files/ParkingOccupancy.csv')

#get counts by hour
all_traffic = tapply(trip_list$label, trip_list$hour, length)
cruisers = tapply(cruz_sub$label, cruz_sub$hour, length)

#plot all traffic and cruisers
plot(all_traffic, type='l', ylab='# vehicles', xlab='hour', las=1)
lines(cruisers, col='blue')
legend('topleft', legend=c('all','cruisers'), lty=1,
    col=c('black','blue'), bty='n')

#pearson correlation coefficient
cor(all_traffic, cruisers)

#plot cruising as percentage of traffic
plot(cruisers/all_traffic, type='l', ylab='% traffic', xlab='hour', las=1)

#both
png(width=6.5, height=5, units='in',
    filename='~/git/dssg/cruising/images/cruising_traffic_parking.png',
    type='cairo', res=300)

xmin=8; xmax=20; LWD=2
par(mfrow=c(2,1), mar=c(0,4,.5,3), oma=c(4,0,0,1))
plot(all_traffic, type='l', ylab='', xlab='hour', las=1,
    xaxt='n', font.lab=2, yaxt='n', xlim=c(xmin,xmax), col='darkgreen',
    bty='l', ylim=c(0,5700), xaxs='i', yaxs='i', lwd=LWD)
mtext('# Vehicles', 2, line=2.5, font=2)
lines(cruisers, col='steelblue4', lwd=LWD)
axis(2, las=1, at=seq(1000,6000,2000),
    labels=c('1k','3k','5k'))
legend(x=9, y=6000, legend=c('All','Cruising'), lty=1,
    col=c('darkgreen','steelblue4'), bty='n', cex=.8, lwd=LWD)
plot(cruisers/all_traffic, type='l', ylab='',
    xlab='hour', las=1, col='steelblue4', xaxt='n', font.lab=2,
    yaxt='n', xlim=c(8,20), ylim=c(.33,.50), bty='u', xaxs='i',
    yaxs='i', lwd=LWD)
mtext('% Total Traffic', 2, line=2.5, font=2, col='steelblue4')
mtext('% Total Occ.', 4, line=2.5, font=2, las=3, col='purple')
axis(2, las=1, at=seq(.34,.46,.04), labels=seq(34,46,4),
    col.axis='steelblue4')
axis(1, at=seq(8,20,2),
    labels=c('8am','10am','12pm','2pm','4pm','6pm','8pm'))
mtext('Hour', 1, line=2.5, font=2)
legend(x=15.5, y=.50, legend=c('Cruising','Parking'), lty=1,
    col=c('steelblue4','purple'), bty='n', cex=.8, lwd=LWD)
par(new=TRUE)
plot(parking$Parking.Occupancy.Ratio[parking$Time %in%
        seq(xmin,xmax,1)] * 100, type='l', xaxs='i', yaxs='i', axes=FALSE,
    ann=FALSE, col='purple', ylim=c(45, 115), lwd=LWD)
axis(4, las=1, at=seq(50,96,15), labels=seq(50,95,15),
    col.axis='purple')

dev.off()

#centered and scaled
plot(scale(all_traffic), type='l', ylab='# vehicles', xlab='hour', las=1)
lines(scale(cruisers), col='blue')
legend('topleft', legend=c('all','cruisers'), lty=1,
    col=c('black','blue'), bty='n')
plot(cruisers/all_traffic, type='l', ylab='% traffic', xlab='hour', las=1)
