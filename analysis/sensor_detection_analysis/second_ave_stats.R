#does sensor accuracy vary throughout the day?
#Mike Vlah (vlahm13@gmail.com)
#10 July 2017

#install packages if necessary and load them
if(!require(lubridate)) install.packages('lubridate')
if(!require(anytime)) install.packages('anytime')
library(lubridate)
library(anytime)

#import 2nd ave trip data
setwd('/home/mike/git/dssg/cruising/data/large_files')
trips = read.csv('second_ave_sensors_path.csv')
colnames(trips)[colnames(trips)=='hour'] = 'timestamp'

#convert timestamp to datetime and isolate hour
trips$hour = factor(hour(anytime(as.numeric(substr(trips$timestamp, 12, 21)))))
# weekdays = unique(wday(anytime(as.numeric(substr(trips$timestamp, 12, 21))), label=TRUE, abbr=TRUE))
# dates = unique(anydate(as.numeric(substr(trips$timestamp, 12, 21))))

# logistic regression (same thing done below in a different way)
# bindat = as.matrix(trips[,c(3,4,6:11,13,14)])
# binmod = glm( ~ trips$hour, family=binomial(link='logit'))
# summary(binmod)

#aggregate (sum) sensor readings by hour
sums = as.data.frame(apply(trips[,grepl('X\\d{6}', colnames(trips))],
                           MARGIN=2,
                           FUN=function(x) tapply(x, trips$hour, sum)))

#two of these columns are endpoints of 2nd ave and represent the total # obs
sums = cbind(sums[,c(1,2,4:9,11,12)], sums[,3])
colnames(sums)[11] = 'nobs'

#convert to proportions
props = sums
props[,-11] = sums[,-11] / sums$nobs

#flatten
flat = cbind(as.numeric(rep(rownames(props), each=ncol(props)-1)),
             c(t(as.matrix(props[,-11]))))

#visualize (single sensor)
# barplot(props$X265180, names.arg=rownames(props),
#         las=2, xlab='hour', ylab='read rate')

#visualize (dist by hour)
boxplot(flat[,2] ~ flat[,1], #something's wanky about this
        las=2, xlab='hour', ylab='read rate')
axis(3, 1:15, props[,11], las=2)
mtext('# observations', 3, line=2.5)

#visualize (all sensors)
defpar = par(mfrow=c(5,2), mar=c(0,0,0,0))
for(i in 1:10){ #but this is chill
    barplot(props[,i], names.arg=rownames(props),
            las=2, xlab='hour', ylab='read rate')
}
par(defpar)

#does proportion of successful readings vary by hour
time = factor(7:21)
mod = glm(props$X265180 ~ time, weights=props$nobs,
          family=binomial(link='logit'))
summary(mod)
