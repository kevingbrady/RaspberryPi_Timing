library(lubridate)
dat <- read.table('Pi_Data/(3-01-17)to(3-02-17).txt', sep = '|', strip.white = TRUE)
pi_data <- dat
colnames(pi_data)[colnames(pi_data)=="V1"] <- "IRIGB"
colnames(pi_data)[colnames(pi_data)=="V2"] <- "RaspberryPi"

pi_data$IRIGB[which(pi_data$IRIGB == "None")] <-NA
pi_data$IRIGB <- ymd_hms(pi_data$IRIGB)                                   # convert to POSIXct type from string using lubridate 
pi_data$RaspberryPi <- ymd_hms(pi_data$RaspberryPi)
pi_data$IRIGB <- as.POSIXct(pi_data$IRIGB, format="%Y-%m-%d %H:%M:%0S6")
pi_data$RaspberryPi <- as.POSIXct(pi_data$RaspberryPi, format="%Y-%m-%d %H:%M:%0S6")
pi_data$offset <- as.numeric(pi_data$RaspberryPi - pi_data$IRIGB)

pi_data$IRIGB[which(pi_data$IRIGB < pi_data$IRIGB[1])] <- NA
pi_data$RaspberryPi[which(pi_data$RaspberryPi < pi_data$RaspberryPi[1])] <- NA
total_time <- round(pi_data$IRIGB[length(pi_data$IRIGB)] - min(pi_data$IRIGB, na.rm = TRUE))
print(total_time)

reads <- 1                                                   # Once A Second : 1, Once A Minute : 60, Once 5 Minute: 300
                                                              # Once 15 Minute: 900, Once (1/2) hour: 1800
imin <- pi_data$IRIGB[seq(1,length(pi_data$IRIGB), reads)]
ilat <- pi_data$offset[seq(1,length(pi_data$offset), reads)]      
#ilat <- functionvector(mean,reads,pi_data$latency)              # reads needs to be > 1 to be able to use this
imin <- as.numeric(imin)
#resize_dataset(ilat, nrow(pi_data$IRIGB))
n <- matrix(c(imin, ilat), nrow=length(imin), ncol = 2)
png("OffsetOverTime.png", width = 800, height = 500)

xmin <- as.POSIXct(min(n[,1], na.rm = TRUE), origin= '1970-1-1')
xmax <- as.POSIXct(max(n[,1], na.rm = TRUE), origin= '1970-1-1')
#ymin <- min(n[,2], na.rm = TRUE)                                   #set min and max values for the axes to min and max values of the dataset
#ymax <- max(n[,2], na.rm = TRUE)
#xmin <- as.POSIXct(('2017-01-13 00:00:01'), origin= '1970-1-1')
#xmax <- as.POSIXct(('2017-01-13 00:020:01'), origin= '1970-1-1')   # set min an dmax values for the axes to fixed values
ymin <- 0.0
ymax <- 0.012
xseq <- seq.POSIXt(xmin, xmax, by = (total_time/4))                 # how many ticks you want for the 'Time' axis

#Plots whatever you put into imin and ilat above

plot(n[,2]~n[,1], data = n, type = 'l', main = 'Offset Over Time', ylab = 'Offset (s)', xlab = 'Time (UTC)', col = 'blue', xaxt = 'n',  ylim = c(ymin,ymax), xlim = c(xmin,xmax), lwd = 1)
axis.POSIXct(side = 1, at= xseq, labels= TRUE, format= '%m-%d %H:%M:%S', cex.lab = 3 , cex.axis = 0.8)

dev.off()
