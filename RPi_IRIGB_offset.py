#! usr/bin/env python
import datetime
import RPi.GPIO as GPIO
import time
import subprocess

class Decoder():
	
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
    piFlag = 0
    pi = ''
    total = 0
    clocktime = ''
    templist = []
    numbits = []
    bits = []
    bitcount = 0
    q = []

    def __init__(self):

        self.data = []

    def setup(self,pin):

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

    def current_microseconds(self):

        microseconds = time.time() * 1000000
        return microseconds

    def pulse_microseconds(self, pin):

        starttime = self.current_microseconds()
        ptime = 0
        total_microseconds = 0

        while GPIO.input(pin) == GPIO.HIGH:

            ptime = self.current_microseconds()
            if(ptime - starttime) > 8300:

                break

            else:

                total_microseconds = int(round((ptime - starttime)/500))* 500
                
       
        return total_microseconds 

    def bin_seconds_today(self, today):

        today = datetime.datetime.strptime(today, '%Y-%m-%d')
        epoch = 0.0
        max_year = 253402232400.0

        if epoch < today.timestamp() < max_year:

            sec = today - datetime.datetime.fromtimestamp(epoch)
            return sec.total_seconds()
      
    def irig_decoder(self, pulsebits):

        third = (len(pulsebits)) - 63        
        x = 0
        self.Month = 0
        self.Day = 0
 
        self.DaysOY = (pulsebits[third] * 1) + (pulsebits[third +1] * 2) + (pulsebits[third +2] * 4) + (pulsebits[third + 3] * 8) + (pulsebits[third + 5] * 10) + (pulsebits[third + 6] * 20) + (pulsebits[third + 7] * 40) + (pulsebits[third + 8] * 80) + (pulsebits[third + 9] * 100) +(pulsebits[third + 10] * 200)
        self.Year = ((pulsebits[third + 18] * 1) + (pulsebits[third + 19] * 2) + (pulsebits[third + 20] * 4) + (pulsebits[third + 21] * 8) + (pulsebits[third + 23] * 10) + (pulsebits[third + 24] * 20) + (pulsebits[third + 25] * 40) + (pulsebits[third + 26] * 80)) + 2000
        self.SBS = float((pulsebits[third + 45] * (2**0)) + (pulsebits[third + 46] * (2**1)) + (pulsebits[third + 47] * (2**2)) + (pulsebits[third + 48] * (2**3)) + (pulsebits[third + 49] * (2**4)) + (pulsebits[third + 50] * (2**5)) + (pulsebits[third + 51] * (2**6)) + (pulsebits[third + 52] * (2**7)) + (pulsebits[third + 53] * (2**8)) + (pulsebits[third + 54] * (2**9)) + (pulsebits[third + 55] * (2**10)) + (pulsebits[third + 56] * (2**11)) + (pulsebits[third + 57] * (2**12)) + (pulsebits[third + 58] * (2**13)) + (pulsebits[third + 59] * (2**14)) + (pulsebits[third + 60] * (2**15)) + (pulsebits[third + 61] * (2**16)))
        #self.Leap_Second = '(' + str(pulsebits[third + 27]) + str(pulsebits[third + 28]) +')'
        #self.DST = '(' + str(pulsebits[third + 29]) + str(pulsebits[third + 30]) + ')'
        #self.Time_Offset = '(' + str(pulsebits[third + 31])+ str(pulsebits[third + 32]) + str(pulsebits[third + 33]) + str(pulsebits[third + 34]) + str(pulsebits[third + 35]) + str(pulsebits[third + 36]) + ')' 
        #self.Time_Quality = '(' + str(pulsebits[third + 37]) + str(pulsebits[third + 38]) + str(pulsebits[third + 39]) + str(pulsebits[third + 40])+ ')'
        #self.Parity = str(pulsebits[third + 41])
        #self.CTQ = '(' + str(pulsebits[third + 42]) + str(pulsebits[third + 43]) + str(pulsebits[third + 44]) + ')'

        if(self.Year % 4 == 0):

            if(self.Year % 100 != 0):

                self.daysInMonth[1] = 29

            elif(self.Year % 400 == 0):

                self.daysInMonth[1] = 29

            else:

                pass

        else:

            self.daysInMonth[1] = 28

        self.Day = self.DaysOY

        while(self.Month < 12):

            self.Month += 1

            if(self.Day > self.daysInMonth[x]):

                self.Day -= self.daysInMonth[x]
                x += 1
               

            else:
                
                if(self.Day == 0):

                    self.Day += 1

                break

        timestamp = self.bin_seconds_today(str(self.Year) + '-' + str(self.Month) + '-' + str(self.Day)) + self.SBS		
        Time = datetime.datetime.utcfromtimestamp(timestamp)
        
        return Time

    def reset(self):

        self.piFlag = 0
        self.total = 0
        self.clocktime = ''

    def clearlists(self):

        del self.templist[:]
        del self.bits[:]
        del self.numbits[:]
        self.bitcount = 0

    def get_decoded_data(self, pin):

        self.setup(pin)
        while True:
            
            microseconds = self.pulse_microseconds(pin)

            if microseconds < 1:
        
                pass

            elif(1000 <= microseconds <= 3000):

                if self.bitcount < 9:
                    self.templist.append(0)
                    self.bitcount += 1

                else:

                    microseconds = 8000

            elif(5000 <= microseconds <= 6000):

                if self.bitcount < 9:

                    self.templist.append(1)
                    self.bitcount += 1

                else:

                    microseconds = 8000

            elif(microseconds == 8000):

                self.templist.append(2)
                self.numbits.append(self.bitcount)
                self.bitcount = 0

            if microseconds > 1:

                self.q.append(microseconds)
                if len(self.q) > 100:

                    del self.q[0]
            
            if self.templist[-2:] == [2,2]:

                if self.piFlag != 1:

                            self.pi = datetime.datetime.utcfromtimestamp(time.time())
                            self.piFlag = 1

                if len(self.templist) > 70:
                        
                    for i in self.templist:

                        if i == 0 or i == 1:

                            self.bits.append(i)

                    self.clocktime = self.irig_decoder(self.bits)
                
                else:

                    self.clearlists()
                    self.reset()

            if self.clocktime != '':

                break

                    
  
