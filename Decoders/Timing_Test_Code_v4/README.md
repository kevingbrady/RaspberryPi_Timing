Compile CPUInfo module on raspberry pi

g++ -fPIC -shared -o CPUInfo.so -I/usr/include/python3.4m -I/usr/include/boost read_cpu_temp.cpp -lboost_python3 -lpython3.4m

may need to link boost's python3 shared library to specify that boost should use python3 to compile the module (it uses python2 by default). Here I named it "lboost_python3" 
