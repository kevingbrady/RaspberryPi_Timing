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
#include <semaphore.h>
#include <errno.h>
#include <stdlib.h>

//PIN THE TEST WILL RUN ON (WIRING PI SETUP)
#define PIN 18

//SET TIME FOR THE TEST TO RUN
#define DAYS 0
#define HOURS 12
#define MINUTES 0
#define SECONDS 0
#define TOTAL (86400 * DAYS) + (3600 * HOURS) + (60 * MINUTES) + SECONDS

//NODE STRUCT AND POINTERS FOR LINKED LIST
struct Node {

        double val;
        int count;
        struct Node* next;

};
struct Node *head, *tail, *head2, *tail2;

// Methods to run in separate threads while the latency is recorded
void *readcputemp(void *);    //reads CPU Board Temperature from /sys/class/thermal/thermal_zone0/temp
void *getCPULoad(void*);      //reads average processor load from last minute from /proc/loadavg    

//Methods involved in decoding irigb signal and recording latency
double decode_irigb(void);
void printOutput(void);
void printList(struct Node**);
void interrupt_callback(void);
void emptyList(struct Node**, struct Node**);
void push(struct Node**, struct Node**, double);
void removeFirst(struct Node**);
double find(struct Node*, int);

char next_pi_timestamp[26], current_pi_timestamp[26], irig[20] = "";    //Strings to hold datetime values of irigb and raspberry pi
double cpu_temperature, thisInterrupt, lastInterrupt, totalInterrupt, MAX_INTERRUPT, MIN_INTERRUPT;
static struct timespec tp, timestamp, interrupt_time;
int endFlag, endtime, cpu_load;
long microsecs;
time_t last_pi_timestamp, last_irigb_timestamp;
static FILE* output;
static sem_t stopTest;

int main(){

	MAX_INTERRUPT = 9000.0;                    //SET MAXIMUM PULSE WIDTH
	MIN_INTERRUPT = 1000.0;                    //SET MINUMUM PULSE WIDTH
	sem_init(&stopTest, 0, 0);                 //CREATE SEMAPHORE TO BLOCK MAIN FOR THE DURATION OF THE TEST

	setpriority(PRIO_PROCESS, 0, -20);         //SET HIGHEST PRIORITY POSSIBLE

        output = fopen("data.txt", "w+");        //CREATE OUTPUT FILE
	endtime = TOTAL + 2;
	wiringPiSetupGpio();                       //SETUP WIRINGPI ON PIN
	pinMode(PIN, INPUT);
	pullUpDnControl(PIN, PUD_DOWN);
	if( wiringPiISR(PIN, INT_EDGE_BOTH, interrupt_callback) < 0 ){     //SETS UP ISR FUNCTION TO FIRE WHENEVER THERE IS AN INTERRUPT ON THE PIN

		fprintf(stderr, "Unable to setup ISR: %s\n", strerror(errno));
		return 1;

	}
	sem_wait(&stopTest);                      //USE SEMAPHORE TO BLOCK MAIN UNTIL TEST DURATION HAS EXPIRED

	fclose(output);                          //CLOSE OUTPUT FILE 
	return 0;
}

void interrupt_callback(void){

	clock_gettime(CLOCK_MONOTONIC_RAW, &interrupt_time);    //Timestamp every interrupt on pin using raw monotonic clock option
	thisInterrupt = (interrupt_time.tv_sec + (interrupt_time.tv_nsec/ 1000000000.0));
	totalInterrupt = (thisInterrupt - lastInterrupt) * 1e6;                                 //get pulse width by subtracting numerical timestamps and converting to microseconds

        if(digitalRead(PIN) == 0){                                  //FALLING EDGE if pin is low, take last 2 interrupt timestamps to find the pusle width

		//push(&head2, &tail2, totalInterrupt);              //Secondary linked list to hold pulse widths of last 2 irigb signals to help debug errors if needed
                //if(tail2->count > 198) removeFirst(&head2);

		if(totalInterrupt > MIN_INTERRUPT && totalInterrupt < MAX_INTERRUPT){          //Only run code if the measured interrupt is between 1 ms and 9 ms

			if(totalInterrupt > 7000){               //Reference Bits

				endFlag ++;

			} else {                  //Information Bits

				if(timestamp.tv_sec <= 0){       //If it has the valid reference timestamp then ignore, otherwise collect information bits in queue to decode

			 		if(totalInterrupt < 3000){

						push(&head, &tail, 0);
						(tail->count > 88)? removeFirst(&head): 0;

			 		} else {

						push(&head, &tail, 1);
						(tail->count > 88)? removeFirst(&head): 0;
					}
				}
				endFlag = 0;              //Reset number of reference bits to be able to see when the end of a full signal happens
			}

			if(endFlag == 2){          //Two reference bits next to each other signifies the end of a pulse

        	        	clock_gettime(CLOCK_REALTIME, &tp);         //TIMESTAMP RASPBERRY PI
	                        pthread_t cputemp, cpuload;
	                        pthread_create(&cputemp, NULL, readcputemp, NULL);           //Measure CPU TEMPERATURE and CPU PROCESSOR LOAD in separate threads
                                pthread_create(&cpuload, NULL, getCPULoad, NULL);            //They can be measured concurrently
	                        if(timestamp.tv_sec <= 0){ 

        	                       	timestamp.tv_sec = decode_irigb();

        	                }
        	                pthread_join(cputemp, NULL);
                                pthread_join(cpuload, NULL);
        	                printOutput();
        	                (endtime > 0) ? endtime --: sem_post(&stopTest);            //decrease test counter until it hits 0, when it does release the semaphore in main
        	       }
		}
    }
    lastInterrupt = thisInterrupt;                //move value for current interrupt timestamp so it can be compared upon the next interrupt firing
}

double decode_irigb(void){            //Decode bits recorded in linked list (implemented as a queue) into irigb timestamp

	double DaysOY, timestamp;
	int Year, Seconds_of_Day, bitcount;

	bitcount = (tail->count + 1);
	DaysOY = (find(head, (bitcount - 63)) * 1) + (find(head, (bitcount - 62)) * 2) +  (find(head, (bitcount - 61)) * 4) + (find(head, (bitcount - 60)) * 8) + (find(head, (bitcount - 58)) * 10) + (find(head, (bitcount - 57)) * 20) + (find(head, (bitcount - 56)) *  40) + (find(head, (bitcount - 55)) * 80) + (find(head, (bitcount - 54)) * 100) + (find(head, (bitcount - 53)) * 200);
	Year = (find(head, (bitcount - 45)) * 1) + (find(head, (bitcount - 44)) * 2) + (find(head, (bitcount - 43)) * 4) + (find(head, (bitcount - 42)) * 8) + (find(head, (bitcount - 40)) * 10) + (find(head, (bitcount - 39)) * 20) + (find(head, (bitcount - 38)) * 40) + (find(head, (bitcount - 37)) * 80) + 2000; 
	Seconds_of_Day = (find(head, (bitcount - 18)) * pow(2, 0)) + (find(head, (bitcount - 17)) * pow(2, 1)) + (find(head, (bitcount - 16)) * pow(2, 2)) + (find(head, (bitcount - 15)) * pow(2, 3)) + (find(head, (bitcount - 14)) * pow(2, 4)) + (find(head, (bitcount - 13)) * pow(2, 5)) + (find(head, (bitcount - 12)) * pow(2, 6)) + (find(head, (bitcount - 11)) * pow(2, 7)) + (find(head, (bitcount - 10)) * pow(2, 8)) + (find(head, (bitcount - 9)) * pow(2, 9)) + (find(head, (bitcount - 8)) * pow(2, 10)) + (find(head, (bitcount - 7)) * pow(2, 11)) + (find(head, (bitcount - 6)) * pow(2, 12)) + (find(head, (bitcount - 5)) * pow(2, 13)) + (find(head, (bitcount - 4)) * pow(2, 14)) + (find(head, (bitcount - 3)) * pow(2, 15)) + (find(head, (bitcount - 2)) * pow(2, 16));    

	if(Year % 4 == 0) {
		;
	}
	else{

		DaysOY -= 1;
	}

	DaysOY = DaysOY *  86400;
	Year = (365.25 * 86400) * (Year - 1970);
	timestamp = (DaysOY + Year + Seconds_of_Day);
	return timestamp;
}

void *readcputemp(void *argv){

	FILE *temperatureFile;
	double T;
	temperatureFile = fopen ("/sys/class/thermal/thermal_zone0/temp", "r");
	fscanf (temperatureFile, "%lf", &T);
	T /= 1000;
	fclose (temperatureFile);
	cpu_temperature = T;
}

void *getCPULoad(void *argv) {

        FILE *FileHandler;
        float load_1, load_5, load_15;     //can read average processor load of last minute, five minutes, or 15 minutes from /prov/loadavg

        FileHandler = fopen("/proc/loadavg", "r");
        fscanf(FileHandler, "%f %f %f", &load_1, &load_5, &load_15);
        fclose(FileHandler);
        cpu_load = (int)(load_1 * 100);
}

void printOutput(void){          //Convert String Arrays to Datetimes and Print output values

	strftime(next_pi_timestamp, sizeof(next_pi_timestamp), "%Y-%m-%d %H:%M:%S", gmtime(&tp.tv_sec));
        strftime(irig, sizeof(irig), "%Y-%m-%d %H:%M:%S", gmtime(&timestamp.tv_sec));
	if(endtime < TOTAL){   //Gives two seconds for the test to start before it records values (Ensures that a full irigb signal has been recorded before attempting to write output)

		//printf("%s | %s.%06u | %6.3f | %d%\n", irig, current_pi_timestamp, (tp.tv_nsec/1000), cpu_temperature, cpu_load);
		//Commenting out the line above will make the code print to the screen if you want to see it live. Below will write to the output file
		
                fprintf(output, "%s | %s.%06u | %6.3f | %d%\n", irig, current_pi_timestamp, (tp.tv_nsec/1000), cpu_temperature, cpu_load);
                /*if(tp.tv_sec - last_pi_timestamp != 1.0){      //print list of pulse width values if the difference between the last two recorded raspberry pi timestamp values is more than 1 second
                                                               //This means it missed the end of an irigb signal

			printList(&head2);

		}*/
	}
	(timestamp.tv_sec > 0) ? timestamp.tv_sec += (tp.tv_sec - last_pi_timestamp): 0;     //Increase reference (irigb) timestamp value by the difference between the last 2 recorded raspberry pi timestamp values
	last_pi_timestamp = tp.tv_sec;
	strcpy(current_pi_timestamp, next_pi_timestamp);            //Copy the newly recorded raspberry pi timestamp to an array to match it to is corresponding refernce value
}

void push(struct Node** startNode, struct Node** endNode, double val){   //push element to end of linked list

	
	if((*startNode) == NULL){

		*startNode = malloc(sizeof(struct Node));
		(*startNode)->next= NULL;
		(*startNode)->val = val;
		(*startNode)->count = 0;
		*endNode = *startNode;

	} else {
		struct Node* newNode = malloc(sizeof(struct Node));
		(*endNode)->next = newNode;
		newNode->val = val;
		newNode->count = (*endNode)->count + 1;
		newNode->next = NULL;
		*endNode = newNode;

	}
}

void removeFirst(struct Node** first){   //remove first element from linked list

	struct Node* temp = *first;
	temp = temp->next;
	free(*first);
	*first = temp;
	while(temp != NULL){

		temp->count -= 1;
		temp = temp->next;
	}
}

void emptyList(struct Node** first, struct Node** last){    //empty linked list (only really used for secondary linked list)

	struct Node* current = *first;
	struct Node* next;

	while(current != NULL){

		next = current->next;
		free(current);
		current = next;
	}
	*first = *last = NULL;
	timestamp.tv_sec = 0;
}

double find(struct Node *current, int x){             //recursive function to find value at index x

	if(current == NULL){

		return -1;

	}
	if(current->count == x){

		return current->val;
	}
	return find(current->next, x);
}

void printList(struct Node** first){                 //Method to print out secondary linked list of pulse width values if needed

	struct Node* current = *first;
	double value;
	while(current != NULL){


		//fprintf(output, "%d \n", current->val);
		printf("%f \n", current->val);
		if((current->val > 2200 && current->val < 4600) || (current->val > 5200 && current->val < 7200) || (current->val > 8200)) printf("--------IRREGULAR VALUE--------\n"); 
		if(current->val > 7000 && value > 7000 && current->next != NULL) printf("\n\n");

		value = current->val;
		if(current->next == NULL){

			//fprintf(output, "\n\n%d\n\n", (current->count + 1));
			printf("\n\n%d\n\n", (current->count));

		}

		current = current->next;

	}
}
