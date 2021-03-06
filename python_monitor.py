"""


BSD 3-Clause License

Copyright (c) 2021, by Barcelona SuperComputing Center
                Contributors: Tarun Mohandas
                              Leonardo Bautista
                E-mail: tarun.mohandas@bsc.es
                URL: https://github.com/migalabs/eth2-client-analyzer
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""



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

import csv
import os.path
import logging

import configparser
import threading

from flask import Flask
from flask import jsonify 

import requests

process_array = []

folderPercentage = "/"
if len(sys.argv) > 3:
    folderPercentage = str(sys.argv[3])


app = Flask(__name__)

@app.route("/metrics")
def main():
    result = []
    copy_array = process_array.copy()
    for single_process in copy_array:
        process_json = {}
        process_json['name'] = single_process.processName
        process_json['cpuUsage'] = single_process.cpuUsage
        process_json['diskUsage'] = single_process.diskUsageMB
        process_json['memUsage'] = single_process.memUsage

        process_json['sent_mb'] = single_process.sent_mb
        process_json['received_mb'] = single_process.received_mb
        process_json['currentSlot'] = single_process.currentSlot
        process_json['currentPeers'] = single_process.currentPeers
        process_json['diskUsage_percent'] = psutil.disk_usage(folderPercentage)[3]
        result.append(process_json)
        print(process_json)
    
    return jsonify(result)


folderStorage = []
# this array will store the tuples to write to disk
data_to_write = []
output_file = ""
number_of_pids = 0


BASIC_CONFIG = "BASIC"
NAMES_CONFIG = "NAMES"
OUTPUT_FILE_CONFIG = "OUTPUT_FILE"
PIDS_CONFIG = "PIDS"
FOLDERS_CONFIG = "FOLDERS"
NETWORK_CONFIG = "NETWORK_INTERFACE"
PORT_METRIC_CONFIG = "METRIC_PORT"
SYNC_METRIC_CONFIG = "SYNC_METRIC_PATH"
PEERS_METRIC_CONFIG = "PEERS_METRIC_PATH"
SERVER_PORT_CONFIG = "SERVER_PORT"
FOLDER_PERCENTAGE_CONFIG = "FOLDER_PERCENTAGE"
SLEEP_INT_CONFIG = 'SLEEP_INTERVAL'


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


def get_sync_process(i_port, i_path):
    try:
        response = requests.get("http://localhost:" + i_port + i_path)
        json_data = response.json()
        return int(json_data["data"]["head_slot"])
    except:
        try: # grandine API
            response = requests.get("http://localhost:" + i_port + i_path)
            json_data = response.json()
            return int(json_data["slot"])
        except:
            return int(0)

def get_peer_count(i_port, i_path):
    try:
        response = requests.get("http://localhost:" + i_port + i_path)
        json_data = response.json()
        return int(json_data["data"]["connected"])
    except:
        return int(0)


class ProcessInfo():

    nameMap = {}

    def __init__(self, input_pid, input_folder, input_net_iface, i_metricPort, i_syncPath, i_peerPath):
        
        self.pid = int(input_pid)
        try:
            self.process = psutil.Process(int(input_pid))

            # defines if the process exists or not
            self.exists = True

            # the folder where the user has told us this process stores information
            self.folder = input_folder

            self.processName = self.process.name()

            # this represents the interface to monitor
            # it has nothing to do with the process, but this is the only way we have found to measure the network consumption
            # it will be the same value for all processes, as it measures the machine traffic, not the process specific traffic
            self.network_interface = input_net_iface

            networkUsage = psutil.net_io_counters(pernic=True, nowrap=True)
            self.initial_sent_mb = networkUsage[self.network_interface][0] / 1000000
            self.initial_received_mb = networkUsage[self.network_interface][1] / 1000000

            self.metricPort = i_metricPort
            self.syncPath = i_syncPath
            self.peerPath = i_peerPath

            self.currentSlot = 0
            self.currentPeers = 0
            
            self.refresh_hardware_info()
        
        except psutil.NoSuchProcess as e:
            # logging.info("Process with PID: ", input_pid, " does not exist")
            print ("No process: ", input_pid)
            self.exists = False
            return
            
        
    
    def get_eqvlnt_process_name(self):
        if self.processName in ProcessInfo.nameMap:
            return ProcessInfo.nameMap.get(self.processName)
        
        return self.processName

        
    # refresh values about hardware
    def refresh_hardware_info(self):
        try:

            self.timestamp = datetime.datetime.now()
            self.currentTime = self.timestamp.strftime("%d/%m/%Y-%H:%M:%S:%f")
            self.cpuUsage = self.process.cpu_percent() / psutil.cpu_count()
            self.diskUsageMB = int(get_size(self.folder)) /int(1000000)
            self.memUsage = float(self.process.memory_info().rss / 1000000)

            networkUsage = psutil.net_io_counters(pernic=True, nowrap=True)
            
            self.sent_mb = (networkUsage[self.network_interface][0] / 1000000) - self.initial_sent_mb
            self.received_mb = (networkUsage[self.network_interface][1] / 1000000) - self.initial_received_mb
            
            self.currentSlot = get_sync_process(self.metricPort, self.syncPath)
            self.currentPeers = get_peer_count(self.metricPort, self.peerPath)

        except psutil.NoSuchProcess as e:
            logging.error(e)
            self.cpuUsage = 0
            self.diskUsageMB = 0
            self.memUsage = float(0)
            

            self.timestamp = datetime.datetime.now()
            self.currentTime = self.timestamp.strftime("%B %d %H:%M:%S:%f")
            return
        
        except Exception  as err:
            logging.error(err)
            return
            


    def __str__(self):

        result = str(self.pid) + ",     " + self.get_eqvlnt_process_name() + "," + "       " + "," + self.currentTime + "," + \
            "    " + "," + str(self.diskUsageMB) + "MB           " + \
            "," + str(self.cpuUsage), "      " + "," + str(self.memUsage) + ",     " + str(self.sent_mb)+ "MB  " + "," + str(self.received_mb) + "MB  " + str(self.currentSlot) + "     "  + str(self.currentPeers)

        return ''.join(result)

        

    def export_to_csv(self):
        return self.pid, self.get_eqvlnt_process_name(), self.currentTime, str(self.diskUsageMB), str(self.cpuUsage), str(self.memUsage), str(self.sent_mb), str(self.received_mb), str(self.currentSlot), str(self.currentPeers)



"""

    This function receives information to be writen to disk about a process
    It will load the information in a buffer and then flush to the CSV file once the buffer is full

"""
def add_info_row(input_tuple):
    global data_to_write

    data_to_write.append(input_tuple)
    # print(data_to_write)

    if len(data_to_write) >= number_of_pids:
        #print("About to CSV" , output_file)
        # Write CSV file
        with open(output_file, "at") as out:
            writer = csv.writer(out)
            # writer.writerow(["your", "header", "foo"])  # write header
            writer.writerows(data_to_write)

        data_to_write = []




def main():
    
    # main

    global folderStorage
    global output_file
    global data_to_write


    # prepare to parse config file
    config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), str(sys.argv[1]))
    config_obj = configparser.ConfigParser()
    

    # check if file exists and read
    if os.path.isfile(config_file):

        config_obj.read(config_file)

    else:
        print("Config file not found")
        exit()
    

    
    # read the names the user has configured in the configuration file
    for x in config_obj.options(NAMES_CONFIG):
        ProcessInfo.nameMap[x] = config_obj.get(NAMES_CONFIG, x)


    # start getting configuration values
    
    pids = [int(x) for x in config_obj.get(BASIC_CONFIG, PIDS_CONFIG).split(",")]
    print("PIDs: " + str(pids))


    folderStorage = config_obj.get(BASIC_CONFIG, FOLDERS_CONFIG).split(",")
    print("Monitoring storage of: " + str(folderStorage))


    output_file = config_obj.get(BASIC_CONFIG, OUTPUT_FILE_CONFIG)
    print("Output file is: ", output_file)

    network_interface = config_obj.get(BASIC_CONFIG, NETWORK_CONFIG)
    print("Network interface is: ", network_interface)

    metricPort = config_obj.get(BASIC_CONFIG, PORT_METRIC_CONFIG)
    print("Metrics port is: ", metricPort)

    syncPath = config_obj.get(BASIC_CONFIG, SYNC_METRIC_CONFIG)
    print("Metrics sync path is: ", syncPath)

    peersPath = config_obj.get(BASIC_CONFIG, PEERS_METRIC_CONFIG)
    print("Metrics peer path is: ", peersPath)


    # check if output file exists
    if os.path.isfile(output_file) is True:

        print("Output file exists.")

    # if not exists, create the csv file with the header
    else:
        print("File does not exist, creating...")
        file = open(output_file, "w")
        file.write("PID,PID_NAME,TIME [month dd hh:mm:ss:ms],DISKUSAGE [MB],CPU[%],MEM[MB],NET_SENT[MB],NET_RECEIVED[MB],CURRENT_SLOT,CURRENT_PEERS\n") 
        file.close() 


    # check if amount of pids and folders to monitor are the same
    if len(pids) != len(folderStorage):
        print("Not the same amount of PIDs and folders.")
        print("Please input the same amount of both.")
        print("Exiting...")
        exit()


    # sleepInterval between each time the script reads the information
    sleepInterval = int(config_obj.get(BASIC_CONFIG, SLEEP_INT_CONFIG))
    if sleepInterval < 1:
        print("Sleep Interval is too low.")
        print("Please input a number equla or higher than 1")
        exit()

    print("Sleep interval: ", sleepInterval)



    # declare our array of pid processes to monitor
    

    # loop over both arrays at the same time
    for single_pid, single_folder in zip(pids, folderStorage):
        new_process = ProcessInfo(single_pid, single_folder, network_interface, metricPort, syncPath, peersPath)

        # only add if new process exists, meaning it was properly created
        if new_process.exists is True:
            process_array.append(new_process)

    print("PID |    PID_NAME    |   TIME [month dd hh:mm:ss:ms]  |    DISKUSAGE [MB]        |     CPU[%]   |    MEM[MB]   |    NET_SENT[MB]  |    NET_RECEIVED[MB]   |    CURRENT_SLOT    |   CURRENT_PEERS")

    # infinite loop
    while True: #counter < 5:
        
        try:
            # read the metrics for all clients in the array
            for single_process_object in process_array:

                single_process_object.refresh_hardware_info()

                if single_process_object.exists:
                    
                    print(str(single_process_object))

                    # add information to the CSV file
                    add_info_row(single_process_object.export_to_csv())
                else:
                    # if the process does not exist, remove it from the list
                    process_array.remove(single_process_object)

           
            time.sleep(sleepInterval)
  

        except Exception as e:
            print(e)


if __name__ == "__main__":

    serverPort = 5000
    if len(sys.argv) > 2:
        serverPort = int(sys.argv[2])


    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=serverPort, debug = False, threaded=True, use_reloader=False), daemon=True).start()
    main()