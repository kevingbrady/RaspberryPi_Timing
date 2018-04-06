//
// Created by kgb on 4/3/18.
//

#ifndef IRIGB_H
#define IRIGB_H

#include <fstream>
#include <cmath>
#include <chrono>
#include <ctime>

class Decoder {
    public:

        Decoder(int total_time);
        virtual ~Decoder();
        void decode_irigb();
        double readCPUTemperature();
        double readCPULoad();
        void printOutput(double cpu_temp, double cpu_load);
	void increment();
	void setupNext();

        int endtime, total_time, endFlag;
        int bitArray[89];
        int *bitcount;

        double pi_timestamp, irigb_timestamp, last_pi_timestamp, previous_total_load_time, previous_idle_load_time;
};


#endif //IRIGB_H
