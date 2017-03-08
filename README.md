# RaspberryPi_Timing

Timing Measurements for Raspberry Pi

There is a basic IRIGB Decoder for Raspberry Pi that adds a second to keep up with the clock since it takes a full second for the pulse to come in to be able to be decoded.

The RPi_IRIGB_Offset code does not add a second but instead timestamps when the Raspberry Pi recognizes the on-time reference bit from the IRIGB pulse and then decodes the value after it comes in. The value that you are decoding for from the pulse is for this on time reference bit, so the offset is the difference between the IRIGB value and when the Pi recognizes the bit.

