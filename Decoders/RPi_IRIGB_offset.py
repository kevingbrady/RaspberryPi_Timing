#! usr/bin/env python
import datetime
import RPi.GPIO as GPIO
import time

class Decoder():
	
    daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]        #List of the days in each month, used to calculate month and day from days of year
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
    clocktime = ''
    templist = []                                   # list of bits including pointer bits
    numbits = []                                    # list to keep tracj of the number of bits read in between each pointer bit
    bits = []                                       # list of bits excluding pointer bits
    bitcount = 0
    q = []                                          #queue to hold raw input values

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
            if(ptime - starttime) > 8300:               # if the difference is greater than 8300 it is an error so break out of the loop

                break

            else:

                total_microseconds = int(round((ptime - starttime)/500))* 500
                
       
        return total_microseconds 

    def bin_seconds_today(self, today):

        today = datetime.datetime.strptime(today, '%Y-%m-%d')
        epoch = 0.0                                                   # maximum and minimum values that "today" can be to avoid Overflow Errors
        max_year = 253402232400.0

        if epoch < today.timestamp() < max_year:

            sec = today - datetime.datetime.fromtimestamp(epoch)         # calculate binary seconds of the current day based on the values read in from the decoder
            return sec.total_seconds()
      
    def irig_decoder(self, pulsebits):

        third = (len(pulsebits)) - 63                                    # find where the third pointer bit is in the pulse and decode the rest of the values based on  
        x = 0                                                            # where this bit is. This way the pulse can be missing up to 28 bits at the beginning and still decode properly
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

        if(self.Year % 4 == 0):                       # check if it is a leap year and change daysInMonth accordingly

            if(self.Year % 100 != 0):

                self.daysInMonth[1] = 29

            elif(self.Year % 400 == 0):

                self.daysInMonth[1] = 29

            else:

                pass

        else:

            self.daysInMonth[1] = 28                   # since daysInMonth is a class variable you have to make sure that this gets reset

        self.Day = self.DaysOY

        while(self.Month < 12):                      # calculate month and day based on the number of days of the year

            self.Month += 1

            if(self.Day > self.daysInMonth[x]):

                self.Day -= self.daysInMonth[x]
                x += 1
               

            else:
                
                if(self.Day == 0):

                    self.Day += 1

                break

	# get the total binary seconds of the current day and add it to the SBS decoded from the pulse to get a numerical timestamp.
	# Convert this numerical timestamp to UTC format
	
        timestamp = self.bin_seconds_today(str(self.Year) + '-' + str(self.Month) + '-' + str(self.Day)) + self.SBS   		
        Time = datetime.datetime.utcfromtimestamp(timestamp)
        
        return Time

    def reset(self):                     # reset timestamp and decoded pulse placeholder varibles

        self.piFlag = 0                
        self.total = 0
        self.clocktime = ''

    def clearlists(self):                # reset class list variables (and counter for number of bits)

        del self.templist[:]
        del self.bits[:]
        del self.numbits[:]
        self.bitcount = 0

    def get_decoded_data(self, pin):

        self.setup(pin)                  # set up pin for input
        while True:
            
            microseconds = self.pulse_microseconds(pin)

            if microseconds < 1:
        
                pass

            elif(1000 <= microseconds <= 3000):                          # assign value to bit based on the width of the pulse
                                                                         # if bitcount is equal to 9 then it is supposed to be a pointer bit
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

            elif(microseconds == 8000):                                # append 2 to templist for a pointer bit, reset bitcount and append the number of bits between each pointer bit to numbits

                self.templist.append(2)
                self.numbits.append(self.bitcount)
                self.bitcount = 0

            if microseconds > 1:

                self.q.append(microseconds)                         # add raw value to queue, delete first element if the length of the queue is greater than 100
                if len(self.q) > 100:

                    del self.q[0]
            
            if self.templist[-2:] == [2,2]:                      # if there are two pointer bits at the end of the list then it is the on-time reference bit

                if self.piFlag != 1:

                            self.pi = datetime.datetime.utcfromtimestamp(time.time())     # TIMESTAMP RASPBERRY PI      
                            self.piFlag = 1                                               # PiFlag ensures that it only timestamps once if there are multiple iterations through this part of the loop

                if len(self.templist) > 70:                              # DECODE IRIGB
                                                                         # if the length of templist is greater than the minimum needed to decode a pulse then extract the bits that are not pointer bits and run the decoder method on the list
                    for i in self.templist:

                        if i == 0 or i == 1:

                            self.bits.append(i)

                    self.clocktime = self.irig_decoder(self.bits)
                
                else:                                                   # if the length of templist is smaller than the minimum than reset everything and start over

                    self.clearlists()
                    self.reset()

            if self.clocktime != '':                                    # if the decoder method decodes a value then break out of the loop

                break        

                    
  
