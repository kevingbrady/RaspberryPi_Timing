#! usr/bin/env python
import RPi.GPIO as GPIO
from time import time
from timeit import default_timer         # import default timer to get more efficient timestamp than time.time()

class Decoder():

    pi = 0                    # variable to hold pi timsetamp
    templist = []             #list to hold irigb values
    interpret = lambda self, high: 2 if 7000 < high <= 9000 else 0 if high <= 3000 else 1    # reads number of microseconds of the pulse and decides whenther it should be a 0, 1, or reference bit based on this input value
    check = lambda self, templist: (([0] * (89 - len(templist))) + templist) if len(templist) < 89 else templist[(len(templist) - 89):] if len(templist) > 89 else templist     # ensures that the length of templist is 89 values by either padding the front of the list with zeros or removing elements from the front of the list

    def setup(self,pin):

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)       # sets up pin for input with the pull up down resistor defaulted to low

    def read(self, pin):

        GPIO.wait_for_edge(pin, GPIO.RISING)            # block execution of code until rising edge is detected on pin
        start = default_timer()
        GPIO.wait_for_edge(pin, GPIO.BOTH)              # block execution again until falling edge detected on pin
        end = default_timer()

        return(self.interpret(round((end-start) * 1000000)))        # calculate number of microseconds based on the difference between the ending and starting timestamps, then send this value to the interpret function to get value of pulse

    def irig_decoder(self):

        pulsebits = self.check(self.templist)           
        third = 26                    # index value of third refence bit ( where Days of Year information starts)
        DaysOY = (pulsebits[third] * 1) + (pulsebits[third +1] * 2) + (pulsebits[third + 2] * 4) + (pulsebits[third + 3] * 8) + (pulsebits[third + 5] * 10) + (pulsebits[third + 6] * 20) + (pulsebits[third + 7] * 40) + (pulsebits[third + 8] * 80) + (pulsebits[third + 9] * 100) +(pulsebits[third + 10] * 200)
        Year = ((pulsebits[third + 18] * 1) + (pulsebits[third + 19] * 2) + (pulsebits[third + 20] * 4) + (pulsebits[third + 21] * 8) + (pulsebits[third + 23] * 10) + (pulsebits[third + 24] * 20) + (pulsebits[third + 25] * 40) + (pulsebits[third + 26] * 80)) + 2000
        SBS = (pulsebits[third + 45] * (2**0)) + (pulsebits[third + 46] * (2**1)) + (pulsebits[third + 47] * (2**2)) + (pulsebits[third + 48] * (2**3)) + (pulsebits[third + 49] * (2**4)) + (pulsebits[third + 50] * (2**5)) + (pulsebits[third + 51] * (2**6)) + (pulsebits[third + 52] * (2**7)) + (pulsebits[third + 53] * (2**8)) + (pulsebits[third + 54] * (2**9)) + (pulsebits[third + 55] * (2**10)) + (pulsebits[third + 56] * (2**11)) + (pulsebits[third + 57] * (2**12)) + (pulsebits[third + 58] * (2**13)) + (pulsebits[third + 59] * (2**14)) + (pulsebits[third + 60] * (2**15)) + (pulsebits[third + 61] * (2**16))
        
        if(Year % 4 is 0):                     # check if it is a leap year and adjust Days of Year accordingly
 
            if(Year % 100 is not 0 or Year % 400 is 0):

                pass

        else:

            DaysOY -= 1

        return((DaysOY * 86400) + ((365.25 * 86400) * (Year - 1970)) + SBS + (6 * 3600))    # calculate numerical timestamp from Days of Year, Year, and SBS information (add 6 hours to get utc timestamp)
        

    def get_decoded_data(self, pin):

        high = 0
        last_high = 0
        
        while 1:                          # read values into list until 2 reference bits are detected next to eachother.
                                          # Only append the 0s and 1s to templist and keep track of current value and previous value read from the pin to know when the end of the pulse comes up

            self.setup(pin)           
            high = self.read(pin)
            if high is 2: 
                
                if last_high is 2:

                    break

            else: 

                if len(self.templist) is 89:         # break out of the loop if list is 89 values (if the read() method misses a falling edge at the end of the pulse)

                    break

                self.templist.append(high)

            last_high = high

        self.pi = time()        # timestamp pi
        del self.templist[:]
        return((0, self.irig_decoder())[0 < self.irig_decoder() < 2147483641])  # return either a 0 or the timestamp calculated from the irig_decoder() method if the value returned from irig_decoder can be interpreted by the datetime module (prevents Overflow Error that will stop the code from running)
