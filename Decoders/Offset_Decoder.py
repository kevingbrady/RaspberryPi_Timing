#! usr/bin/env python
import datetime
import time
import subprocess
import wiringpi as GPIO

class Decoder():
	
    Year = 0
    SBS = 0.0
    pi = ''
    cyclelist = []
    templist = []
    CPUtemp = ''

    def __init__(self):

        self.data = []

    def setup(self,pin):
        
        GPIO.wiringPiSetup()
        GPIO.pinMode(1,0)


    def cycles(self, pin):

        high = 0
        max = 23

        while GPIO.digitalRead(pin) == 1:

            if high < max:

                time.sleep(0.0002)
                high += 1

        return(high)

    def irig_decoder(self, pulsebits):
       
        Time = ''
        third = len(pulsebits) - 63
        x = 0
      
        DaysOY = (pulsebits[third] * 1) + (pulsebits[third +1] * 2) + (pulsebits[third +2] * 4) + (pulsebits[third + 3] * 8) + (pulsebits[third + 5] * 10) + (pulsebits[third + 6] * 20) + (pulsebits[third + 7] * 40) + (pulsebits[third + 8] * 80) + (pulsebits[third + 9] * 100) +(pulsebits[third + 10] * 200)
        self.Year = ((pulsebits[third + 18] * 1) + (pulsebits[third + 19] * 2) + (pulsebits[third + 20] * 4) + (pulsebits[third + 21] * 8) + (pulsebits[third + 23] * 10) + (pulsebits[third + 24] * 20) + (pulsebits[third + 25] * 40) + (pulsebits[third + 26] * 80)) + 2000
        self.SBS = float((pulsebits[third + 45] * (2**0)) + (pulsebits[third + 46] * (2**1)) + (pulsebits[third + 47] * (2**2)) + (pulsebits[third + 48] * (2**3)) + (pulsebits[third + 49] * (2**4)) + (pulsebits[third + 50] * (2**5)) + (pulsebits[third + 51] * (2**6)) + (pulsebits[third + 52] * (2**7)) + (pulsebits[third + 53] * (2**8)) + (pulsebits[third + 54] * (2**9)) + (pulsebits[third + 55] * (2**10)) + (pulsebits[third + 56] * (2**11)) + (pulsebits[third + 57] * (2**12)) + (pulsebits[third + 58] * (2**13)) + (pulsebits[third + 59] * (2**14)) + (pulsebits[third + 60] * (2**15)) + (pulsebits[third + 61] * (2**16)))

        if(self.Year % 4 == 0):

            if(self.Year % 100 != 0):

                pass

            elif(self.Year % 400 == 0):

                pass

           
        else:

            DaysOY -= 1

        DOY = DaysOY * 86400
        year = (365.25 * 86400) * (self.Year - 1970)
        timestamp = DOY + year + self.SBS + (6 * 3600)
		
        if 0 < timestamp < 2147483641:
 
            Time = datetime.datetime.utcfromtimestamp(timestamp)

        return Time

    def get_decoded_data(self, pin):

        clocktime = ''
        templist = []
        piFlag = 0
        bitcount = 0
        numbits = []
        bits = []        
        high = 0
        self.CPUtemp = subprocess.check_output('./ReadCPUTemp')

        while True:

            time.sleep(0.001)

            high = self.cycles(pin)

            if high > 0:

                self.cyclelist.append(high)

            
            if high < 23: 

                    if high < 2:

                        pass
                
                    elif high < 10:
                  
                        bits.append(0)
                        bitcount += 1

                    else: 
                        
                        bits.append(1)
                        bitcount += 1
        
            else:

                if len(numbits) == 10:

                    numbits.append(0)

                else:

                    numbits.append(bitcount)
                    bitcount = 0
           
            if numbits[-1:] == [0]:

                if piFlag != 1:

                    self.pi = datetime.datetime.utcfromtimestamp(time.time())
                    piFlag = 1


                if len(bits) > 63:

                    clocktime = self.irig_decoder(bits)

                else:

                    del bits[:]
    
                del numbits[:]
                return(clocktime)
