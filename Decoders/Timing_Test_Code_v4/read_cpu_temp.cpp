#include <iostream>
#include <fstream>
#include <string>
#include <stdlib.h>
#include <boost/python.hpp>
#include <cmath>

using namespace std;

double decode_irigb(const boost::python::list pulsebits){

    double DaysOY, SBS, timestamp;
    int Year, third;
    third = boost::python::len(pulsebits) - 63;
    DaysOY = ((boost::python::extract<double>(pulsebits[third])) + (boost::python::extract<double>(pulsebits[third + 1]) * 2) + (boost::python::extract<double>(pulsebits[third + 2])* 4) + (boost::python::extract<double>(pulsebits[third + 3]) * 8) + (boost::python::extract<double>(pulsebits[third + 5]) * 10) + (boost::python::extract<double>(pulsebits[third + 6]) * 20) + (boost::python::extract<double>(pulsebits[third + 7]) * 40) + (boost::python::extract<double>(pulsebits[third + 8]) * 80) + (boost::python::extract<double>(pulsebits[third + 9]) * 100) + (boost::python::extract<double>(pulsebits[third + 10])* 200.0));
    Year = ((boost::python::extract<double>(pulsebits[third + 18])) + (boost::python::extract<double>(pulsebits[third + 19]) * 2) + (boost::python::extract<double>(pulsebits[third + 20]) * 4) + (boost::python::extract<double>(pulsebits[third + 21]) * 8) + (boost::python::extract<double>(pulsebits[third + 23]) * 10) + (boost::python::extract<double>(pulsebits[third + 24])* 20) + (boost::python::extract<double>(pulsebits[third+ 25])* 40) + (boost::python::extract<double>(pulsebits[third + 26]) * 80) + 2000);
    SBS = (boost::python::extract<double>(pulsebits[third + 45]) * pow(2.0, 0.0)) + (boost::python::extract<double>(pulsebits[third + 46]) * pow(2.0, 1.0)) + (boost::python::extract<double>(pulsebits[third + 47]) * pow(2.0, 2.0)) + (boost::python::extract<double>(pulsebits[third + 48]) * pow(2.0, 3.0)) + (boost::python::extract<double>(pulsebits[third + 49]) * pow(2.0, 4.0)) + (boost::python::extract<double>(pulsebits[third + 50]) * pow(2.0, 5.0)) + (boost::python::extract<double>(pulsebits[third + 51]) * pow(2.0, 6.0)) + (boost::python::extract<double>(pulsebits[third + 52]) * pow(2.0, 7.0)) + (boost::python::extract<double>(pulsebits[third + 53]) * pow(2.0, 8.0)) + (boost::python::extract<double>(pulsebits[third + 54] * pow(2.0, 9.0)) + (boost::python::extract<double>(pulsebits[third + 55]) * pow(2.0, 10.0)) + (boost::python::extract<double>(pulsebits[third + 56]) * pow(2.0, 11.0)) + (boost::python::extract<double>(pulsebits[third + 57]) * pow(2.0, 12.0)) + (boost::python::extract<double>(pulsebits[third + 58]) * pow(2.0, 13.0)) + (boost::python::extract<double>(pulsebits[third + 59]) * pow(2.0, 14.0)) + (boost::python::extract<double>(pulsebits[third + 60]) * pow(2.0, 15.0)) + (boost::python::extract<double>(pulsebits[third + 61]) * pow(2.0, 16.0)));

    if ( Year % 4 == 0 )
    {
        if ( Year % 100 != 1 || Year % 400 == 0 )
            ;
    }
    else {

        DaysOY --;
    }

    timestamp = ((DaysOY * 86400.0) + ((365.25 * 86400.0) * double(Year - 1970)) + SBS + (6.0 * 3600.0));
    return(timestamp);

}

double readcputemp(void)
{

FILE *temperatureFile;
double T;
temperatureFile = fopen ("/sys/class/thermal/thermal_zone0/temp", "r");
if (temperatureFile == NULL)
  ; //print some message
fscanf (temperatureFile, "%lf", &T);
T /= 1000;
//printf ("%6.3f\n",T);
fclose (temperatureFile);
return(T);

}

BOOST_PYTHON_MODULE(CPUInfo){

    using namespace boost::python;
    def("readcputemperature", readcputemp); 
    def("decode_irigb", decode_irigb);
}
