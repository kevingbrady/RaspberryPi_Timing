#!usr/bin/env python
import Offset_Decoder as IRIGB
import datetime
import sys
import os
import subprocess
import time

filename = open('Pulse_Reader.txt', 'w')
sys.stdout = filename


pin = 1
time_end = datetime.datetime.now() + datetime.timedelta(hours=12)   #How long you want it to run
time_end = time_end + datetime.timedelta(seconds=3)               # It takes 3 seconds to start running so add 3 seconds to total running time to get an even dataset

p = IRIGB.Decoder()
p.setup(pin)

count = 0
irig = ''
pi = ''
count = 0
prev = ''


while datetime.datetime.now() <= time_end:

    pi = p.pi
    irig = p.get_decoded_data(pin)
    
    if count > 2:

        if prev != '':

            if irig != prev + datetime.timedelta(seconds=1):

                irig = prev + datetime.timedelta(seconds=1)
                

        if pi != '':

            if irig != '':

                print(irig, '|', pi, '|', float(p.CPUtemp[0:-1]))

    del p.cyclelist[:]
    prev = irig
    count += 1
filename.close()
