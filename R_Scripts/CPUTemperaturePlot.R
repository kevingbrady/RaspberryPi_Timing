# Will plot the CPU Temperature or GPU Temperature over time
# Need to Change value for temp to GPU along with the name of the .png file and the graph title to GPU as well

library(lubridate)
dat <- read.table('Data.txt', sep = '|', strip.white = TRUE)
pi_data <- dat
colnames(pi_data)[colnames(pi_data)=="V1"] <- "IRIGB"
colnames(pi_data)[colnames(pi_data)=="V2"] <- "RaspberryPi"
colnames(pi_data)[colnames(pi_data)=="V3"] <- "CPU_Temperature"
colnames(pi_data)[colnames(pi_data)=="V4"] <- "GPU_Temperature"

pi_data$CPU_Temperature <-  (as.numeric(gsub("[^\\d]+", "", pi_data$CPU_Temperature, perl=TRUE))/1000)
pi_data$GPU_Temperature <-  as.numeric(gsub("[^\\d]+", "", pi_data$GPU_Temperature, perl=TRUE))
pi_data$CPU_Temperature[which(pi_data$CPU_Temperature < 10.0)] <- pi_data$CPU_Temperature[which(pi_data$CPU_Temperature < 10.0)] * 10
pi_data$GPU_Temperature <- (pi_data$GPU_Temperature/ 10)

temp <- pi_data$CPU_Temperature

pi_data$IRIGB <- ymd_hms(pi_data$IRIGB)
pi_data$RaspberryPi <- ymd_hms(pi_data$RaspberryPi)
pi_data$IRIGB <- as.POSIXct(pi_data$IRIGB, format="%Y-%m-%d %H:%M:%0S6")
pi_data$RaspberryPi <- as.POSIXct(pi_data$RaspberryPi, format="%Y-%m-%d %H:%M:%0S6")
pi_data$offset <- as.numeric(pi_data$RaspberryPi - pi_data$IRIGB)
pi_data$offset[which(pi_data$offset > 1.0)] <- NA

pi_data$IRIGB[which(pi_data$IRIGB < pi_data$IRIGB[1])] <- NA
pi_data$RaspberryPi[which(pi_data$RaspberryPi < pi_data$RaspberryPi[1])] <- NA

total_time <- round(pi_data$IRIGB[length(pi_data$IRIGB)] - min(pi_data$IRIGB, na.rm = TRUE))
pi_data$IRIGB[which(pi_data$IRIGB > (min(pi_data$IRIGB, na.rm = TRUE) + total_time))] <- NA
pi_data$RaspberryPi[which(pi_data$RaspberryPi > (min(pi_data$RaspberryPi, na.rm = TRUE) + total_time))] <- NA
print(total_time)

reads <- 1                                                   # Once A Second : 1, Once A Minute : 60, Once 5 Minute: 300
                                                              # Once 15 Minute: 900, Once (1/2) hour: 1800
omin <- pi_data$IRIGB[seq(1,length(pi_data$IRIGB), reads)]
zlat <- temp[seq(1,length(temp), reads)]      
#ilat <- functionvector(mean,reads,pi_data$offset)              # reads needs to be > 1 to be able to use this
omin <- as.numeric(omin)
n <- matrix(c(omin, zlat), nrow=length(omin), ncol = 2)
png("CPUTemperatureOverTime(no sync).png", width = 800, height = 500)           # Need to change name of .png file here for GPU

xmin <- as.POSIXct(min(n[,1], na.rm = TRUE), origin= '1970-1-1')
xmax <- as.POSIXct(max(n[,1], na.rm = TRUE), origin= '1970-1-1')
#ymin <- min(n[,2], na.rm = TRUE)
#ymax <- max(n[,2], na.rm = TRUE)                                               # can use max and min values of x and y as bounds

#xmin <- as.POSIXct(('2017-01-13 00:00:01'), origin= '1970-1-1')                # can use your own specific values of x and y as bounds
#xmax <- as.POSIXct(('2017-03-08 20:028:01'), origin= '1970-1-1')
ymin <- 30.0
ymax <- 60.0

xseq <- seq.POSIXt(xmin, xmax, by = (total_time/4))                             # creates sequence, number total_time is divided by is the number of ticks you will have on the x-axis (4 here)

# Need to change title of plot here for GPU

plot(n[,2]~n[,1], data = n, type = 'l', main = 'CPU Temperature Over Time', ylab = 'Temperature (C)', xlab = 'Time (UTC)', col = 'blue', xaxt = 'n',  ylim = c(ymin,ymax), xlim = c(xmin,xmax), lwd = 1)
axis.POSIXct(side = 1, at= xseq, labels= TRUE, format= '%m-%d %H:%M:%S', cex.lab = 3 , cex.axis = 0.8)

dev.off()
