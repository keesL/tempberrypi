#!/usr/bin/python
import os
import glob
import time
import datetime
import requests
from trigger import TempState

URL='http://URL-OF-PHP-SCRIPT'
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# read raw data from the device
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

# parse raw data into temperatures
def read_temp():
    lines = read_temp_raw()
    # API isn't predictable. Continue trying until it is happy
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    # grab the temperature from the output
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
    else:
        return "unknown", "unknown"


def main():
    state = TempState('tempsave.dat')
#    while True:
    c,F =  read_temp()
    now = str(datetime.datetime.now())
    decimal = now.find('.')
    
    # round at 0.5 intervals and discard fractions of seconds
    out = str(round(F * 2.0)/2.0)+" degrees F at "+now[:decimal]
    
    # add to log
    f = open('temp.log', 'a')
    f.write(out+"\n")
    f.close()
    
    # post to web site
    r = requests.get(URL, params={'temp': out});
    
    if F < 60:
        state.trigger(TempState.COLD, F)
    elif F < 75:
        state.trigger(TempState.NORMAL, F)
    elif F < 80:
        state.trigger(TempState.HIGH, F)
    else:
        state.trigger(TempState.VERYHIGH, F)
    
if __name__ == "__main__":
    main()

