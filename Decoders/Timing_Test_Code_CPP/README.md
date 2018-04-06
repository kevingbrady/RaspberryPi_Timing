C++ Implementation of IRIGB Decoder

Download and install wiringPi library with:

git clone git://git.drogon.net/wiringPi
cd ~/wiringPi
git pull
./build

To Compile:

g++ main.cpp -o irigb_cpp -lwiringPi -std=c++11 -pthread

Run:

sudo ./irigb_cpp  

All the variables that are used to keep track of the test information are placed inside a single "Decoder" class so the memory
is released upon program exit.

Calculation for CPU Utilization is based on the /proc/stat file and measures 
the percent of the processor that is not idle every second

Previously we used the /proc/loadavg file which will give the average CPU load over the last minute,
five minutes, and fifteen minutes but can cause some misleading readings that go over 100% 
