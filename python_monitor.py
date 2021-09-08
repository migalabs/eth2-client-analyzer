"""

This script outputs information about hardware consumption within a single process and single folder
It receives two areguments:
- PID: process to be monitored
- folder: folder whose size to monitor

This script not only outputs through terminal the results but also writes to disk in CSV format


"""



#! /bin/python

import os
import sys
import time
import psutil
import datetime
from datetime import datetime as dt

import signal

import csv
import os.path
import logging



folderStorage = []
# this array will store the tuples to write to disk
data_to_write = []
output_file = ""


#GET SIZE OF ARGUMENT FOLDER
def get_size(input_folder):
    #print("Size of: ", input_folder)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(input_folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


class ProcessInfo():

    def __init__(self, input_pid, input_folder):
        
        self.pid = input_pid
        try:
            self.process = psutil.Process(int(input_pid))

            # defines if the process exists or not
            self.exists = True

            # the folder where the user has told us this process stores information
            self.folder = input_folder

            self.processName = self.process.name()
            
            self.refresh_hardware_info()
        
        except psutil.NoSuchProcess as e:
            # logging.info("Process with PID: ", input_pid, " does not exist")
            print ("No process: ", input_pid)
            self.exists = False

            return
            
        


        
    # refresh values about hardware
    def refresh_hardware_info(self):
        try:
            self.cpuUsage = self.process.cpu_percent(interval=1)
            self.diskUsageMB = int(get_size(self.folder)) /int(1000000)
            self.memUsage = float(self.process.memory_info().rss / 1000000)

            self.timestamp = datetime.datetime.now()
            self.currentTime = self.timestamp.strftime("%B %d %H:%M:%S:%f")

        except Exception as e:
            logging.error(e)
            return
            


    def __str__(self):

        result = self.pid + ",     " + self.processName + "," + "       " + "," + self.currentTime + "," + \
            "    " + "," + str(self.diskUsageMB) + "MB           " + \
            "," + str(self.cpuUsage), "      " + "," + str(self.memUsage)

        return ''.join(result)

        

    def export_to_csv(self):
        return self.pid, self.processName, self.currentTime, str(self.diskUsageMB), str(self.cpuUsage), str(self.memUsage)













"""

    This function receives information to be writen to disk about a process
    It will load the information in a buffer and then flush to the CSV file once the buffer is full

"""
def add_info_row(input_tuple):
    global data_to_write

    data_to_write.append(input_tuple)
    # print(data_to_write)

    if len(data_to_write) > 4:
        #print("About to CSV" , output_file)
        # Write CSV file
        with open(output_file, "at") as out:
            writer = csv.writer(out)
            # writer.writerow(["your", "header", "foo"])  # write header
            writer.writerows(data_to_write)

        data_to_write = []



def main():
    print("Hello World!")
    # main

    global folderStorage
    global output_file
    global data_to_write


    pids = sys.argv[1].split(',')
    print("Pid: "+str(pids))
    folderStorage = sys.argv[2].split(',')
    print("Monitoring storage of: " + str(folderStorage))

    output_file = str(sys.argv[3])
    print("Output file is: ", output_file)
    if os.path.isfile(output_file) is True:
        print("Output file exists.")

    else:
        print("File does not exist, creating...")
        file = open(output_file, "w")
        file.write("PID,PID_NAME,TIME [month dd hh:mm:ss:ms],DISKUSAGE [MB],CPU[%],MEM[MB]") 
        file.close() 



    # declare our array of pids to monitor
    process_array = []

    for single_pid, single_folder in zip(pids, folderStorage):
        process_array.append(ProcessInfo(single_pid, single_folder))



    print("PID |    PID_NAME    |   TIME [month dd hh:mm:ss:ms]  |    DISKUSAGE [MB]    |     CPU[%],    MEM[MB]")
    counter = 0
    while counter < 5:
        counter = counter + 1
        try:
           
            for single_process_object in process_array:
                if single_process_object.exists:
                    single_process_object.refresh_hardware_info()
                    print(str(single_process_object))
                    add_info_row(single_process_object.export_to_csv())
                else:
                    process_array.remove(single_process_object)


        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()