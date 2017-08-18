#load data and subset
library(jsonlite)
x = fromJSON('~/Desktop/untracked/final_beforeFilterNoncruise.json')
x = x[,c('label','timeofday','hour')]
cruz_sub = x[which(x$label=='cruising'),]

#get counts by hour
all_traffic = tapply(x$label, x$hour, length)
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
par(mfrow=c(2,1), mar=c(0,4,0,0), oma=c(4,0,1,1))
plot(all_traffic, type='l', ylab='# Vehicles', xlab='hour', las=1,
     xaxt='n', font.lab=2, yaxt='n', xlim=c(8,20))
lines(cruisers, col='blue')
axis(2, las=1, at=seq(1000,5000,1000), labels=c('1k','2k','3k','4k','5k'))
legend('topleft', legend=c('all','cruisers'), lty=1,
       col=c('black','blue'), bty='n')
plot(cruisers/all_traffic, type='l', ylab='% Overall Traffic', xlab='hour', las=1,
     col='blue', xaxt='n', font.lab=2, yaxt='n', xlim=c(8,20), ylim=c(.33,.50))
axis(2, las=1, at=seq(.35,.50,.05), labels=seq(35,50,5))
axis(1, at=seq(8,20,2), labels=c('8am','10am','12pm','2pm','4pm','6pm','8pm'))
mtext('Hour', 1, line=2.5, font=2)
#showing only 8am to 8pm


#centered and scaled
plot(scale(all_traffic), type='l', ylab='# vehicles', xlab='hour', las=1)
lines(scale(cruisers), col='blue')
legend('topleft', legend=c('all','cruisers'), lty=1,
       col=c('black','blue'), bty='n')
plot(cruisers/all_traffic, type='l', ylab='% traffic', xlab='hour', las=1)
