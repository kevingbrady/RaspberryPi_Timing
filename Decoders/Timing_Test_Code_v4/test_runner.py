#!usr/bin/env python
import test_decoder as IRIGB
from datetime import datetime
from CPUInfo import readcputemperature        # C++ module for reading cpu temperature  
from os import setpriority, PRIO_PROCESS
import sys

setpriority(PRIO_PROCESS, 0, -20)           # set highest priority of process at start
filename = open('Pulse_Reader.txt', 'w')      # open text file to hold data, pipe the output into this text file
sys.stdout = filename
pin, hours = 12, 12                        # set how long the test should be run for and on what pin

time_end = (3600 * hours) + 5              # multiply hours by 3600 to get total sumber of seconds the code should run for ( add 5 seconds because it takes 5 seconds to start)
start = time_end - 4                      

p = IRIGB.Decoder()                        # initialize decoder object

irig, last_irig, last_pi, pi = 0, 0, 0, 0

check_irig = lambda irig, last_irig, pi: round(pi) if (irig != last_irig + 1 and  last_irig != 0) else irig        # checks if value returned from get_decoded_data is valid

while time_end != 0:

    pi, irig = p.pi, p.get_decoded_data(pin)          
    if  time_end <= start:

        irig = check_irig(irig, last_irig, pi)
        print("%s | %s | %.3f" % (datetime.utcfromtimestamp(irig), datetime.utcfromtimestamp(pi), readcputemperature()))      # convert numerical timestamps to datetime objects, print value as string

    last_irig, time_end = irig, (time_end-1)         # keep track of previous decoded irigb value for comparison

filename.close()
