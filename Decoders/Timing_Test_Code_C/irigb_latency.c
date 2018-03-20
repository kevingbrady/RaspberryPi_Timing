#include <stdio.h>
#include <wiringPi.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>
#include <sys/time.h>
#include <pthread.h>
#include <limits.h>
#include <sys/resource.h>
#include <pthread.h>

#define PIN 18
#define DAYS 0
#define HOURS 12
#define MINUTES 0
#define SECONDS 0
#define TOTAL (86400 * DAYS) + (3600 * HOURS) + (60 * MINUTES) + SECONDS

void *readcputemp(void *);
void *decode_irigb(void *);
//void *printOutput(void *);
//void readcputemp(void);
//void decode_irigb(void);
void printOutput(void);
void printArray(void);
void interrupt_callback(void);

char next_pi_timestamp[26], current_pi_timestamp[26], irig[20] = "";
double last_time, Seconds_of_Day, cpu_temperature, check;
static struct timespec end, start, tp, timestamp;
int bitArray[89], pulseArray[100], value, endFlag, DaysOY, Year, endtime;

int* bitcount = bitArray;
int* pulsecount = pulseArray;

long microsecs;

int main(){

	setpriority(PRIO_PROCESS, 0, -20);
//	piHiPri(99);

	endtime = time(NULL) + TOTAL + 2;
	wiringPiSetupGpio();
	pinMode(PIN, INPUT);
	wiringPiISR(PIN, INT_EDGE_BOTH, interrupt_callback);
	//pullUpDnControl(PIN, PUD_UP);
	while(time(NULL) < endtime){

		delay(10);

	}

	return 0;
}

void interrupt_callback(void){

	if(!digitalRead(PIN) && end.tv_sec == 0){				//FALLING EDGE

			clock_gettime(CLOCK_REALTIME, &end);
			value = (end.tv_nsec - start.tv_nsec)/1000;
			value = (value < 0) ? 1000000 + value: value;

			*pulsecount = value;
			((pulsecount - pulseArray) == 100) ? pulsecount = pulseArray: pulsecount ++;
			//printf("%u\n", value);
			switch(value){

				case 1000 ... 3000:

					endFlag = 0;
					*bitcount = 0;
					((bitcount - bitArray) == 89) ? bitcount = bitArray: bitcount ++;
					break;

				case 7000 ... 9000:

					if(endFlag == 1){

						clock_gettime(CLOCK_REALTIME, &tp);
						if((bitcount - bitArray) == 89){

							
							pthread_t decode, out, cputemp;
							pthread_create(&cputemp, NULL, readcputemp, NULL);
							pthread_create(&decode, NULL, decode_irigb, NULL);

							pthread_join(decode, NULL);
							pthread_join(cputemp, NULL);
							


							//pthread_create(&out, NULL, printOutput, NULL);
							//pthread_join(out, NULL);
							//readcputemp();
							//decode_irigb();
							printOutput();
						}
						bitcount = bitArray;
					}
					endFlag = 1;
					break;
			default:

				endFlag = 0;
                                *bitcount = 1;
                                ((bitcount - bitArray) == 89) ? bitcount = bitArray: bitcount ++;
                                break;

		}

	start.tv_sec = start.tv_nsec = 0;
	}
	else if(digitalRead(PIN)){

		//delay(0.2);
		(digitalRead(PIN) && start.tv_sec == 0) ? clock_gettime(CLOCK_REALTIME, &start): 0;
		end.tv_sec = end.tv_nsec = 0;

	}
}

void *decode_irigb(void *arguments)
//void decode_irigb(void)
{

	DaysOY = (*(bitcount - 63) * 1) + (*(bitcount - 62) * 2) +  (*(bitcount - 61) * 4) + (*(bitcount - 60) * 8) + (*(bitcount - 58) * 10) + (*(bitcount - 57) * 20) + (*(bitcount - 56) *  40) + (*(bitcount - 55) * 80) + (*(bitcount - 54) * 100) + (*(bitcount - 53) * 200);
	Year = (*(bitcount - 45) * 1) + (*(bitcount - 44) * 2) + (*(bitcount - 43) * 4) + (*(bitcount - 42) * 8) + (*(bitcount - 40) * 10) + (*(bitcount - 39) * 20) + (*(bitcount - 38) * 40) + (*(bitcount - 37) * 80) + 2000; 
	Seconds_of_Day = (*(bitcount - 18) * pow(2, 0)) + (*(bitcount - 17) * pow(2, 1)) + (*(bitcount - 16) * pow(2, 2)) + (*(bitcount - 15) * pow(2, 3)) + (*(bitcount - 14) * pow(2, 4)) + (*(bitcount - 13) * pow(2, 5)) + (*(bitcount - 12) * pow(2, 6)) + (*(bitcount - 11) * pow(2, 7)) + (*(bitcount - 10) * pow(2, 8)) + (*(bitcount - 9) * pow(2, 9)) + (*(bitcount - 8) * pow(2, 10)) + (*(bitcount - 7) * pow(2, 11)) + (*(bitcount - 6) * pow(2, 12)) + (*(bitcount - 5) * pow(2, 13)) + (*(bitcount - 4) * pow(2, 14)) + (*(bitcount - 3) * pow(2, 15)) + (*(bitcount - 2) * pow(2, 16));    

	if(Year % 4 == 0) {
		;
	}
	else{

		DaysOY -= 1;
	}

	DaysOY = DaysOY *  86400;
	Year = (365.25 * 86400) * (Year - 1970);
	timestamp.tv_sec = (DaysOY + Year + Seconds_of_Day);
}

void *readcputemp(void *vargp)
//void readcputemp(void)
{

FILE *temperatureFile;
double T;
temperatureFile = fopen ("/sys/class/thermal/thermal_zone0/temp", "r");
fscanf (temperatureFile, "%lf", &T);
T /= 1000;
fclose (temperatureFile);
cpu_temperature = T;
}

//void *printOutput(void *vargp){
void printOutput(void){

	strftime(next_pi_timestamp, sizeof(next_pi_timestamp), "%Y-%m-%d %H:%M:%S", gmtime(&tp.tv_sec));
	strftime(irig, sizeof(irig), "%Y-%m-%d %H:%M:%S", gmtime(&timestamp.tv_sec));

	if(current_pi_timestamp[0] != '\0'){

		printf("%s | %s.%06u | %6.3f \n", irig, current_pi_timestamp, (tp.tv_nsec/1000), cpu_temperature);

	}
	strcpy(current_pi_timestamp, next_pi_timestamp);;
	pulsecount = pulseArray;
}



void printArray(void){

	int i;
	for(i=0; i < (sizeof(pulseArray)/sizeof(int)); i++){

		printf("%u\n", pulseArray[i]);
	}
	printf("\n%d\n\n", (sizeof(pulseArray)/sizeof(int)));

}
