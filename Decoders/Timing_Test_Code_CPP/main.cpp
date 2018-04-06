#include <iostream>
#include <wiringPi.h>
#include <semaphore.h>
#include "Decoder/IRIGB.cpp"
#include <semaphore.h>
#include <wiringPi.h>
#include <errno.h>
#include <cstring>
#include <math.h>
#include <sys/resource.h>
#include <signal.h>

#define DAYS 0
#define HOURS 12
#define MINUTES 0
#define SECONDS 0
#define TOTAL ((86400 * DAYS) + (3600 * HOURS) + (60 * MINUTES) + SECONDS)
#define MAX_INTERRUPT 10000.0                    //SET MAXIMUM PULSE WIDTH
#define MIN_INTERRUPT 1000.0 //SET MINUMUM PULSE WIDTH
#define PIN 18   //PIN THE TEST WILL RUN ON (WIRING PI SETUP)

void interrupt_callback();
void cleanup(int);
bool isValid(double);

double thisInterrupt, lastInterrupt, totalInterrupt, lastTotalInterrupt;
int endtime = TOTAL + 5;
Decoder test_runner = Decoder(endtime);
static sem_t stopTest;
int count;

int main(int argc, char *argv[]) {

    setpriority(PRIO_PROCESS, 0, -20);
    signal(SIGINT, cleanup);

    wiringPiSetupGpio();                       //SETUP WIRINGPI ON PIN
    pinMode(PIN, INPUT);
    pullUpDnControl(PIN, PUD_DOWN);
    if( wiringPiISR(PIN, INT_EDGE_BOTH, &interrupt_callback) < 0 ){     //SETS UP ISR FUNCTION TO FIRE WHENEVER THERE IS AN INTERRUPT ON THE PIN

        fprintf(stderr, "Unable to setup ISR: %s\n", strerror(errno));

    }
    sem_init(&stopTest, 0, 0);
    sem_wait(&stopTest);
    cleanup(0);
    return 0;
}

void interrupt_callback(){

    auto interrupt = std::chrono::high_resolution_clock::now();
    thisInterrupt = std::chrono::duration_cast<std::chrono::microseconds>(interrupt.time_since_epoch()).count();
    totalInterrupt = thisInterrupt - lastInterrupt;

    if(!digitalRead(PIN)){

        if(isValid(totalInterrupt)){
	    count ++;
            if(totalInterrupt > 7000){               //Reference Bits

		if(isValid(lastTotalInterrupt) && lastTotalInterrupt > 7000){          //Two reference bits next to each other signifies the end of a pulse

                	auto pi = std::chrono::high_resolution_clock::now();
                	test_runner.pi_timestamp = std::chrono::duration_cast<std::chrono::microseconds>(pi.time_since_epoch()).count()/1e6;       //TIMESTAMP RASPBERRY PI

                	double cpu_load = test_runner.readCPULoad();
                	double cpu_temp = test_runner.readCPUTemperature();
                	test_runner.printOutput(cpu_temp, cpu_load);

			count = 0;
                	if(test_runner.endtime < 0) sem_post(&stopTest);
		}

            } else {                  //Information Bits

                if(test_runner.endtime >= test_runner.total_time){

                    if(totalInterrupt < 3000){

                        *test_runner.bitcount = 0;
			test_runner.increment();

                    } else {

                        *test_runner.bitcount = 1;
			test_runner.increment();
                    }
                }
            }
	lastTotalInterrupt = totalInterrupt;
        }
    }
    lastInterrupt = thisInterrupt;
};

bool isValid(double num){

	return(num > MIN_INTERRUPT && num < MAX_INTERRUPT);

}

void cleanup(int signalCode){

        fflush(stdout);
        sem_destroy(&stopTest);
	if(test_runner.endtime > 0){

		exit(EXIT_FAILURE);
	}
}
