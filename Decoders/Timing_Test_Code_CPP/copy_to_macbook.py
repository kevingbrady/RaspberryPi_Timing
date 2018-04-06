import os
#ip_addr = '129.6.231.175'
ip_addr = '129.6.226.230'
os.system('sudo python3 test_info.py')
os.system('scp data.txt test_info.txt kgb@' + ip_addr + ':/Users/kgb/PycharmProjects/IRIG_Decoder/Pi_Data')
