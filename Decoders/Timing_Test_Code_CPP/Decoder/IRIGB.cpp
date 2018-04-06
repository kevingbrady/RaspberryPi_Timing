//
// Created by kgb on 4/3/18.
//

#include <iostream>
#include <iomanip>
#include "IRIGB.h"

//std::ofstream outputFile("data.txt");

Decoder::Decoder(int total_time): endtime(total_time), total_time((total_time-5)){

	this->bitcount = this->bitArray;
	this->irigb_timestamp = this->pi_timestamp = this->last_pi_timestamp = 0;
}

Decoder::~Decoder(){

}
void Decoder::printOutput(double cpu_temp, double cpu_load){

	double difference = (int)this->pi_timestamp - (int)this->last_pi_timestamp;
	this->irigb_timestamp += difference;

	char current_pi_timestamp[26], irig[26];
	time_t pi, irigb;
	pi = (int) this->last_pi_timestamp;
	irigb = (int) this->irigb_timestamp;

	std::string latency = std::to_string(this->last_pi_timestamp - (int) this->last_pi_timestamp).erase(0,1);
	strftime(current_pi_timestamp, sizeof(current_pi_timestamp), "%Y-%m-%d %H:%M:%S", gmtime(&pi));
	strftime(irig, sizeof(irig), "%Y-%m-%d %H:%M:%S", gmtime(&irigb));

	if((this->endtime < this->total_time)){

		std::cout << irig << " | " << current_pi_timestamp << latency << " | " << std::fixed << std::setprecision(2) << cpu_temp << " | " << cpu_load << "%" << std::endl;
		//outputFile << irig << " | " << current_pi_timestamp << latency << " | " << std::fixed << std::setprecision(2) << cpu_temp << " | " << cpu_load << "%" << std::endl;
        } else {

		this->decode_irigb();
	}

	this->setupNext();
}

void Decoder::decode_irigb(){

    if(this->bitcount - this->bitArray < 63) return;

    double DaysOY, Year, Seconds_of_Day;
    DaysOY = (*(this->bitcount - 63) * 1) + (*(this->bitcount - 62) * 2) +  (*(this->bitcount - 61) * 4) + (*(this->bitcount - 60) * 8) + (*(this->bitcount - 58) * 10) + (*(this->bitcount - 57) * 20) + (*(this->bitcount - 56) *  40) + (*(this->bitcount - 55) * 80) + (*(this->bitcount - 54) * 100) + (*(this->bitcount - 53) * 200);
    Year = (*(this->bitcount - 45) * 1) + (*(this->bitcount - 44) * 2) + (*(this->bitcount - 43) * 4) + (*(this->bitcount - 42) * 8) + (*(this->bitcount - 40) * 10) + (*(this->bitcount - 39) * 20) + (*(this->bitcount - 38) * 40) + (*(this->bitcount - 37) * 80) + 2000;
    Seconds_of_Day = (*(this->bitcount - 18) * pow(2, 0)) + (*(this->bitcount - 17) * pow(2, 1)) + (*(this->bitcount - 16) * pow(2, 2)) + (*(this->bitcount - 15) * pow(2, 3)) + (*(this->bitcount - 14) * pow(2, 4)) + (*(this->bitcount - 13) * pow(2, 5)) + (*(this->bitcount - 12) * pow(2, 6)) + (*(this->bitcount - 11) * pow(2, 7)) + (*(this->bitcount - 10) * pow(2, 8)) + (*(this->bitcount - 9) * pow(2, 9)) + (*(this->bitcount - 8) * pow(2, 10)) + (*(this->bitcount - 7) * pow(2, 11)) + (*(this->bitcount - 6) * pow(2, 12)) + (*(this->bitcount - 5) * pow(2, 13)) + (*(this->bitcount - 4) * pow(2, 14)) + (*(this->bitcount - 3) * pow(2, 15)) + (*(this->bitcount - 2) * pow(2, 16));

    if((int)Year % 4 == 0) {
        ;
    }
    else{

        DaysOY -= 1;
    }

    DaysOY = DaysOY *  86400;
    Year = (365.25 * 86400) * (Year - 1970);
    this->irigb_timestamp = (DaysOY + Year + Seconds_of_Day);


}

double Decoder::readCPUTemperature(){

    std::ifstream fin("/sys/class/thermal/thermal_zone0/temp");
    double cpu_temp;
    fin >> cpu_temp;
    fin.close();

    cpu_temp /= 1000;
    return cpu_temp;
}

double Decoder::readCPULoad(){

    std::ifstream cpufile("/proc/stat");
    std::string cpu;
    double cpu_load_percentage, total_load_time, idle_load_time, input1, input2, input3, input4, input5, input6, input7, input8, input9;

    cpufile >> cpu >> input1 >> input2 >> input3 >> idle_load_time >> input4 >> input5 >> input6 >> input7 >> input8 >> input9;
    cpufile.close();

    total_load_time = input1 + input2 + input3 + input4 + input5 + input6 + input7 + input8 + input9 + idle_load_time;
    cpu_load_percentage = 1.0 - (idle_load_time - this->previous_idle_load_time)/(total_load_time - this->previous_total_load_time);

    this->previous_idle_load_time = idle_load_time;
    this->previous_total_load_time = total_load_time;

    return cpu_load_percentage * 100;

}
void Decoder::increment(){

	if(this->bitcount - this->bitArray > (sizeof(bitArray)/sizeof(int))){

		this->bitcount = this->bitArray;

	} else {

		this->bitcount ++;

	}

}
void Decoder::setupNext(){


        this->last_pi_timestamp = this->pi_timestamp;
        this->bitcount = this->bitArray;
        this->endtime --;
	//if(this->endtime < 0) outputFile.close();
}
