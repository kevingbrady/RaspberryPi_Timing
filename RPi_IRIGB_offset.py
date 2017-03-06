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

    def setup(self, pin):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def current_microseconds(self):
        current_microseconds = int(round(time.time() * 1000000))
        return current_microseconds

    def pulse_microseconds(self, pin):
        ptime = 0
        starttime = self.current_microseconds()
        while (GPIO.input(pin)):
            if (GPIO.input(pin) == False):
                break
            else:
                ptime = self.current_microseconds()

        total_microseconds = (ptime - starttime)
        return total_microseconds

    def bin_seconds_today(self, today):

        today = datetime.datetime.strptime(today, '%Y-%m-%d')
        epoch = datetime.datetime.strptime('1970-1-1', '%Y-%m-%d')
        if today > epoch:

            sec = time.mktime(today.timetuple())
            return sec

    def fix_bits(self, templist):
        try:
            z = 0
            i = 8
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

    def irig_decoder(self, pulsebits):
        x = 0
        self.Month = 0
        self.Day = 0

        # self.Seconds = float((pulsebits[0] * 1) + (pulsebits[1] * 2) + (pulsebits[2] * 4) + (pulsebits[3] * 8) + (pulsebits[5] * 10) + (pulsebits[6] * 20) + (pulsebits[7] * 40))
        # self.Minutes = (pulsebits[8] * 1) + (pulsebits[9] * 2) + (pulsebits[10] * 4) + (pulsebits[11] * 8) + (pulsebits[13] * 10) + (pulsebits[14] * 20) + (pulsebits[15] * 40)
        # self.Hours =  (pulsebits[17] * 1) + (pulsebits[18] * 2) + (pulsebits[19] * 4) + (pulsebits[20] * 8) + (pulsebits[22] * 10) + (pulsebits[23] * 20)
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

        if (self.Year % 4 == 0):
            if (self.Year % 100 != 0):
                self.daysInMonth[1] = 29
            elif (self.Year % 400 == 0):
                self.daysInMonth[1] = 29
        else:
            pass

        self.Day = self.DaysOY

        while (self.Month < 12):
            self.Month += 1
            if (self.Day > self.daysInMonth[x]):
                self.Day -= self.daysInMonth[x]
                x += 1
            else:
                if (self.Day == 0):
                    self.Day += 1
                break

        timestamp = self.bin_seconds_today(str(self.Year) + '-' + str(self.Month) + '-' + str(self.Day)) + self.SBS

        Time = str(datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'))
        # Time = str(self.Year) + '-' + str(self.Month) + '-' + str(self.Day) + '  ' +  str(self.Hours) + ':' + str(self.Minutes) + ':' +  str(float(self.Seconds))
        # Time = datetime.datetime.strptime(Time, '%Y-%m-%d %H:%M:%S.%f')

        return Time

    def get_decoded_data(self, pin):
        self.setup(pin)
        field = []
        total = []
        templist = []
        pointer = 1
        clocktime = ''

        while True:
            microseconds = 0
            microseconds = self.pulse_microseconds(pin)
            if microseconds > 200:

                if (microseconds <= 3200):
                    templist.append(0)
                elif (microseconds <= 7200):
                    templist.append(1)
                elif (microseconds <= 9200):
                    templist.append(2)
                else:
                    print microseconds
                    print templist
                    pass

                if templist[-1] == 2:
                    if pointer != 10:
                        if pointer == 0:
                            if self.piFlag == 0:
                                self.pi = datetime.datetime.utcfromtimestamp(time.time())
                                self.piFlag = 1
                            # pointer = str('On Time Reference Bit')
                            # print pointer + ': ' + str(datetime.datetime.utcfromtimestamp(time.time()))
                            pointer = 1
                        else:
                            # print 'Pointer ' + str(pointer) + ' is: ' + str(datetime.datetime.utcfromtimestamp(time.time()))
                            pointer += 1
                    else:
                        pointer = 0
                        self.piFlag = 0
                    # print 'Pointer ' + str(pointer) + ' is: ' + str(datetime.datetime.utcfromtimestamp(time.time()))

                    if templist[-2:] == [2, 2]:

                        if len(templist) == 100:
                            checkFlag = self.fix_bits(templist)
                        else:
                            self.clock = datetime.datetime.utcfromtimestamp(time.time())
                            self.fix_bits(templist)

                        # templist = templist[(len(templist) - 72):]
                        # while len(templist) != 100:
                        # templist.insert(0, 0)

                        # templist[8] = 2
                        # templist[18] = 2
                        # templist[28] = 2

                            checkFlag = self.fix_bits(templist)

                        for a, b, c in zip(templist, templist[1:], templist[2:]):

                            if (a == 0 or a == 1):
                                field.append(a)
                                if (b == 2):
                                    total += field
                                    del field[:]
                                    if (c == 2):

                                        if (len(total) == 89 and checkFlag == 1):
                                            clocktime = str(self.irig_decoder(total))

                                        del total[:]
                                        del templist[:]
                        if clocktime == '':
                            pass
                        else:
                            return clocktime
                        # return 'end pulse: ' + str(datetime.datetime.utcfromtimestamp(time.time()))
