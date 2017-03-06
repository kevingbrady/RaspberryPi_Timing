#! usr/bin/env python
import datetime
import RPi.GPIO as GPIO
import time

class Offset_Decoder():

    daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]         
    Seconds = 0.0
    Minutes = 0
    Hours = 0
    Year = 0
    DaysOY = 0
    Month = 0
    Day = 0
    Leap_Second = ''
    DST = ''
    Time_Offset = ''
    Time_Quality = ''
    Parity = ''
    CTQ = ''
    SBS = 0.0
    pi = ''
    piFlag = 1
    clock = ''

    def __init__(self):
        self.data = []

    def setup(self, pin):                           # sets up GPIO pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def current_microseconds(self):                 # calculates current timestamp in microseconds
        current_microseconds = int(round(time.time() * 1000000))
        return current_microseconds

    def pulse_microseconds(self, pin):              # reads in pulse and calculates the number of microseconds bewteen high and low input values
        ptime = 0
        starttime = self.current_microseconds()
        while (GPIO.input(pin)):
            if (GPIO.input(pin) == False):
                break
            else:
                ptime = self.current_microseconds()

        total_microseconds = (ptime - starttime)
        return total_microseconds

    def bin_seconds_today(self, today):                 # calculates binary seconds of current day based on date enetred in Y-m-d format

        today = datetime.datetime.strptime(today, '%Y-%m-%d')
        epoch = datetime.datetime.strptime('1970-1-1', '%Y-%m-%d')
        if today > epoch:

            sec = time.mktime(today.timetuple())
            return sec

    def fix_bits(self, templist):                           # checks if the pointer bits are at the correct indexes, if not then
        try:                                                # append or delete values if there are an incorrect number of bits
            z = 0                                           # between each pointer bit
            i = 8                                           # sets check equal to 1 if input is normal
            c = 0
            while z < len(templist) - 1:

                if templist[z] == 2:
                    if z == i:
                        c += 1
                    else:
                        if z < i:
                            while z != i:
                                templist.insert(z, 0)
                                z += 1
                        elif z > i:
                            while z != i:
                                del templist[z - 1]
                                z -= 1
                    i += 10
                z += 1
                if c == 10:
                    check = 1
                    return check
        except IndexError:
            pass

    def irig_decoder(self, pulsebits):              # decodes IRIG-B timestamp based on the indexes of the bits in pulsebits
        x = 0
        self.Month = 0
        self.Day = 0

        self.Seconds = float((pulsebits[0] * 1) + (pulsebits[1] * 2) + (pulsebits[2] * 4) + (pulsebits[3] * 8) + (pulsebits[5] * 10) + (pulsebits[6] * 20) + (pulsebits[7] * 40))
        self.Minutes = (pulsebits[8] * 1) + (pulsebits[9] * 2) + (pulsebits[10] * 4) + (pulsebits[11] * 8) + (pulsebits[13] * 10) + (pulsebits[14] * 20) + (pulsebits[15] * 40)
        self.Hours =  (pulsebits[17] * 1) + (pulsebits[18] * 2) + (pulsebits[19] * 4) + (pulsebits[20] * 8) + (pulsebits[22] * 10) + (pulsebits[23] * 20)
        self.DaysOY = (pulsebits[26] * 1) + (pulsebits[27] * 2) + (pulsebits[28] * 4) + (pulsebits[29] * 8) + (
        pulsebits[31] * 10) + (pulsebits[32] * 20) + (pulsebits[33] * 40) + (pulsebits[34] * 80) + (
                      pulsebits[35] * 100) + (pulsebits[36] * 200)
        self.Year = ((pulsebits[44] * 1) + (pulsebits[45] * 2) + (pulsebits[46] * 4) + (pulsebits[47] * 8) + (
        pulsebits[49] * 10) + (pulsebits[50] * 20) + (pulsebits[51] * 40) + (pulsebits[52] * 80)) + 2000
        self.SBS = float((pulsebits[71] * (2 ** 0)) + (pulsebits[72] * (2 ** 1)) + (pulsebits[73] * (2 ** 2)) + (
        pulsebits[74] * (2 ** 3)) + (pulsebits[75] * (2 ** 4)) + (pulsebits[76] * (2 ** 5)) + (
                         pulsebits[77] * (2 ** 6)) + (pulsebits[78] * (2 ** 7)) + (pulsebits[79] * (2 ** 8)) + (
                         pulsebits[80] * (2 ** 9)) + (pulsebits[81] * (2 ** 10)) + (pulsebits[82] * (2 ** 11)) + (
                         pulsebits[83] * (2 ** 12)) + (pulsebits[84] * (2 ** 13)) + (pulsebits[85] * (2 ** 14)) + (
                         pulsebits[86] * (2 ** 15)) + (pulsebits[87] * (2 ** 16)))
        self.Leap_Second = '(' + str(pulsebits[53]) + str(pulsebits[54]) + ')'
        self.DST = '(' + str(pulsebits[55]) + str(pulsebits[56]) + ')'
        self.Time_Offset = '(' + str(pulsebits[57]) + str(pulsebits[58]) + str(pulsebits[59]) + str(
            pulsebits[60]) + str(pulsebits[61]) + str(pulsebits[62]) + ')'
        self.Time_Quality = '(' + str(pulsebits[63]) + str(pulsebits[64]) + str(pulsebits[65]) + str(
            pulsebits[66]) + ')'
        self.Parity = str(pulsebits[67])
        self.CTQ = '(' + str(pulsebits[68]) + str(pulsebits[69]) + str(pulsebits[70]) + ')'

        if (self.Year % 4 == 0):                        #check for leap year and change daysInMonth if it is
            if (self.Year % 100 != 0):
                self.daysInMonth[1] = 29
            elif (self.Year % 400 == 0):
                self.daysInMonth[1] = 29
        else:
            pass

        self.Day = self.DaysOY

        while (self.Month < 12):                        # calculate the month and the day from Days of the Year
            self.Month += 1
            if (self.Day > self.daysInMonth[x]):
                self.Day -= self.daysInMonth[x]
                x += 1
            else:
                if (self.Day == 0):
                    self.Day += 1
                break
                                                        
                                                        # calculates the binary seconds for the current day at 24:00 and adds this to the SBS
                                                        # decoded from pulsebits to get the correct decoded value as a number
        timestamp = self.bin_seconds_today(str(self.Year) + '-' + str(self.Month) + '-' + str(self.Day)) + self.SBS
        Time = str(datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))   # puts numerical timestamp in datetime format
        
        return Time

    def get_decoded_data(self, pin):
        self.setup(pin)                 #sets up pin for input
        field = []
        total = []
        templist = []
        pointer = 1
        clocktime = ''

        while True:
            microseconds = 0                                        # resets microseconds (keeps from a value carrying over in the loop)
            microseconds = self.pulse_microseconds(pin)             # reads in the width of the pulse (100 per second for IRIG-B)
            if microseconds > 200:

                if (microseconds <= 3200):                          # appends a 0, 1, or 2 based on the width of the pulse
                    templist.append(0)
                elif (microseconds <= 7200):
                    templist.append(1)
                elif (microseconds <= 9200):
                    templist.append(2)
                else:
                    pass

                if templist[-1] == 2:                               # TIMESTAMP RASPBERRY PI
                    if pointer != 10:                               # keeps track of number of pointer bits that have come in and timestamps when it recognizes the P0 bit (on-time reference bit)
                        if pointer == 0:                            # Sets piFlag = 1 to ensure that the Raspberry Pi only timestamps once
                            if self.piFlag == 0:
                                self.pi = datetime.datetime.utcfromtimestamp(time.time())
                                self.piFlag = 1
                            pointer = 1
                        else:            
                            pointer += 1
                    else:
                        pointer = 0
                        self.piFlag = 0

                    if templist[-2:] == [2, 2]:                     # DECODE IRIGB
                                                                    # If the length of templist is 100 then run the checker to ensure that there are not any input errors
                        if len(templist) == 100:            
                            checkFlag = self.fix_bits(templist)
                        else:                                       # If length is not 100 there are input errors so run checker to fix them
                            self.clock = datetime.datetime.utcfromtimestamp(time.time())
                            self.fix_bits(templist)
                            checkFlag = self.fix_bits(templist)

                        for a, b, c in zip(templist, templist[1:], templist[2:]):

                            if (a == 0 or a == 1):                  # Run through templist and append the bits to a new list that excludes the pointer bits
                                field.append(a)
                                if (b == 2):
                                    total += field
                                    del field[:]
                                    if (c == 2):
                                        if (len(total) == 89 and checkFlag == 1):       # If total is the correct length and
                                            clocktime = str(self.irig_decoder(total))   # there are not input errors run the decoder on total
                                        del total[:]
                                        del templist[:]                                 # delete values in both lists to avoid them carrying over 
                        if clocktime == '':
                            pass
                        else:
                            return clocktime                                            # do not return a value unless there is one to return 
                       
