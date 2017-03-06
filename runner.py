#!usr/bin/env python
import irigb_decoder as IRIGB
import datetime
import sys

filename = open('(2-8-17)to(2-9-17).txt', 'w')
sys.stdout = filename

pin = 12
time_end = datetime.datetime.now() + datetime.timedelta(days=1)  # How long you want it to run
time_end += datetime.timedelta(seconds=3)  # it takes 3 seconds to adjust to the pulse and then starts
p = IRIGB.IRIGB_Decoder()
count = 0
pi = ''

while (datetime.datetime.now() <= time_end):

    irig = p.get_decoded_data(pin)
    if count > 2:  # start printing after 3 seconds to avoid 'None' irig reads
        print irig
    count += 1

    # Year = str(p.Year)
    # Month = str(p.Month)
    # Day = str(p.Day)
    # Hours = str(p.Hours)
    # Minutes = str(p.Minutes)
    # Seconds = str(p.Seconds)
    # SBS = str(p.SBS)
    # LS = str(p.Leap_Second)
    # DST = str(p.DST)
    # TQ = str(p.Time_Quality)
    # P = str(p.Parity)
    # TO = str(p.Time_Offset)
    # CTQ = str(p.CTQ)
    # print Year + '-' + Month + '-' + Day + ' '  + Hours + ':' + Minutes + ':' + Seconds + ' ' + LS + ';' + DST + ';' + TQ + ';' + P + ';' + TO + ';' + CTQ + ';' + SBS
