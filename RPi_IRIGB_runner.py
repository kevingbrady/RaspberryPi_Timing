#!usr/bin/env python
import RPi_IRIGB_offset as IRIGB
import datetime
import sys

filename = open('(3-01-17)to(3-02-17).txt', 'w')
sys.stdout = filename

pin = 12
time_end = datetime.datetime.now() + datetime.timedelta(hours=12)   #How long you want it to run
time_end += datetime.timedelta(seconds=3)			     #It takes 3 seconds to adjust to the pulse and then starts
p = IRIGB.Offset_Decoder()
count = 0
pi = ''
irig = ''

while(datetime.datetime.now() <= time_end):
	
	pi = p.pi
	irig = p.get_decoded_data(pin)

	if pi == '':
		pass
	else:		
		if p.clock == '':

			print str(irig) + '   |   ' + str(pi)

		else:

			p.clock = ''
			if count > 2:
				print str(irig) + '   |   ' +  str(pi)

	count += 1

filename.close()
