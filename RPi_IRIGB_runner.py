#!usr/bin/env python
import test_decoder2 as IRIGB
import datetime
import sys
import os
import subprocess

filename = open('Pulse_Reader.txt', 'w')
sys.stdout = filename


pin = 12
time_end = datetime.datetime.now() + datetime.timedelta(hours=12)   #How long you want it to run
time_end = time_end + datetime.timedelta(seconds=3)               # It takes 3 seconds to start running so add 3 seconds to total running time to get an even dataset

p = IRIGB.Decoder()
count = 0
prev = ''
pi = ''
os.nice(-20)
os.setpriority(os.PRIO_PROCESS, 0, -20)

while(datetime.datetime.now() <= time_end):

    try:

        pi = p.pi
        p.get_decoded_data(pin)

    except OverflowError:

        pass

    if count > 2:

        if prev != '':
                     
            if p.clocktime != prev + datetime.timedelta(seconds=1):
 
                p.clocktime = prev + datetime.timedelta(seconds=1)
       
        if pi != '':

            CPUtemp = subprocess.check_output(['cat', '/sys/class/thermal/thermal_zone0/temp'])
            GPUtemp = subprocess.check_output(['vcgencmd', 'measure_temp'])
            GPUtemp = float(GPUtemp[5:9])
            CPUtemp = float(CPUtemp)/ 1000
            print(p.clocktime, '|' ,pi,'|', CPUtemp, '|', GPUtemp)

    prev = p.clocktime
    p.clearlists()
    p.reset()
    count += 1
filename.close()
