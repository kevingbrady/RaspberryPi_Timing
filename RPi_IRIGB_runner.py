#!usr/bin/env python
import RPi_IRIGB_offset as IRIGB
import datetime
import sys

filename = open('(3-01-17)to(3-02-17).txt', 'w')
sys.stdout = filename

pin = 12
time_end = datetime.datetime.now() + datetime.timedelta(hours=12)   #How long you want it to run
time_end += datetime.timedelta(seconds=4)			     #it takes 3 seconds to start so add 4 seconds to get an even dataset
p = IRIGB.Offset_Decoder()
count = 0
pi = ''
irig = ''

while(datetime.datetime.now() <= time_end):
	
	pi = p.pi							# collect pi timestamp value
	irig = p.get_decoded_data(pin)					# collect decoded IRIG-B timestamp

	if pi == '':							# if there is no value for pi pass (the first value always 
		pass							# reads in wrong since it starts in the middle of a pulse most of the time 
	else:								# so this avoids printing output until a full pulse has occured)
		if p.clock == '':

			print str(irig) + '   |   ' + str(pi)

		else:

			p.clock = ''
			if count > 2:
				print str(irig) + '   |   ' +  str(pi)	

	count += 1

filename.close()
