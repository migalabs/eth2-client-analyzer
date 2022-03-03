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

python3 plot_data.py disk 30 1000 "01/02/2022 00:00" file1.csv file2.csv...

"""


import configparser
import matplotlib.pyplot as plt
import csv
import datetime
import sys

import numpy as np
import pandas as pd
import os
import matplotlib.dates as mdates
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)


colorMap = {
    'prysm': '#FF6666',
    'lighthouse': '#489dec',
    'teku': 'orange',
    'nimbus': 'green',
    'lodestar': '#9379d6',
    'grandine': 'yellow'
}


initial_timestamp = ""

def replace_month_name(input_str):
    result = input_str.replace("January", "Jan")
    result = result.replace("February", "Feb")
    result = result.replace("March", "Mar")
    result = result.replace("April", "Apr")
    result = result.replace("May", "May")
    result = result.replace("June", "Jun")
    result = result.replace("July", "Jul")
    result = result.replace("August", "Aug")
    result = result.replace("September", "Sep")
    result = result.replace("October", "Oct")
    result = result.replace("November", "Nov")
    result = result.replace("December", "Dec")
    
    return result

class ClientData():

    def __init__(self, i_pid, i_name):
        self.pid = i_pid
        self.name = i_name

        self.timestamp = []
        self.diskUsage = []
        self.cpuUsage = []
        self.memUsage = []
        self.netSent = []
        self.netReceived = []
        self.currentSlot = []
        self.currentPeers = []
    
    def add_row(self, i_row):
        #self.timestamp.append(mktime(datetime.datetime.strptime(i_row[2], '%B %d %H:%M:%S:%f').timetuple()))
        
        self.timestamp.append(datetime.datetime.strptime(i_row[2], '%d/%m/%Y-%H:%M:%S:%f').timestamp())
        #print(self.timestamp[-1])
        self.diskUsage.append(float("{:.2f}".format(float(i_row[3]) / 1000)))
        self.cpuUsage.append(float("{:.2f}".format(float(i_row[4]))))
        self.memUsage.append(float("{:.2f}".format(float(i_row[5]))))
        #self.netSent.append(float("{:.2f}".format(float(i_row[6]))))
        self.netSent.append(float(i_row[6]))
        self.netReceived.append(float("{:.2f}".format(float(i_row[7]))))
        self.currentSlot.append(int(i_row[8]))
        self.currentPeers.append(int(i_row[9]))
    
# checks if the specified name exists in an array of ClientData objects
# returns the index of the specified client name in case of found.
# Otherwise, return -1
    
def check_clientName_exists(input_str, input_client_array):

        for idx, client in enumerate(input_client_array):
            if client.name == input_str:
                return idx
        
        return -1


def import_from_file(i_file, client_object_array):
    # open the file containing the data
    with open(i_file,'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        row_counter = 0
        
        for row in csv_reader:

            row_counter = row_counter + 1
            if row_counter == 1:
                # this is the title row
                continue
                
            client_pid = row[0]
            client_name = row[1]
            
            # get the position in our array to identify the client
            client_index = check_clientName_exists(client_name, client_object_array)
            
            if client_index == -1:
                # this means we need to add the client object to the array
                # this client did not exist in our array
                client_object_array.append(ClientData(client_pid, client_name))
            
            # there is already an object for the specified client where to add the data

            client_object_array[client_index].add_row(row)


"""
Return the indexes of the timestamp_array_2 that are closer to each of the timestamp_array_1 items.
We assume these arrays are ordered

"""
def find_nearest_spots(timestamp_array_1, timestamp_array_2):


    array_2_index = 0
    new_delta = abs(timestamp_array_1[0] - timestamp_array_2[array_2_index])
    result = []
    for tmp_timestamp in timestamp_array_1:
        delta = abs(tmp_timestamp - timestamp_array_2[array_2_index])
        new_delta = delta

        while new_delta <= delta and array_2_index < len(timestamp_array_2)-1: # iterate until we find a greater delta
            array_2_index = array_2_index + 1
            delta = new_delta
            new_delta = abs(tmp_timestamp - timestamp_array_2[array_2_index])
        
        result.append(array_2_index-1)

    #print(result)
    return result


def main():

    # prepare to parse config file
    config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), str(sys.argv[1]))
    config_obj = configparser.ConfigParser()
    

    # check if file exists and read
    if os.path.isfile(config_file):

        config_obj.read(config_file)

    else:
        print("Config file not found")
        exit()
    
    metricName = str(config_obj.get("BASIC", "METRIC_NAME"))
    print("Metric name: " + str(metricName))

    num_of_ticks = int(config_obj.get("BASIC", "NUM_OF_POINTS"))
    print("Number of points: " + str(num_of_ticks))

    initial_timestamp = datetime.datetime.strptime(config_obj.get("BASIC", "INITIAL_DATE"), '%d/%m/%Y %H:%M:%S').timestamp()
    print("Initial timestamp: " + str(num_of_ticks))

    xaxis_mode = str(config_obj.get("BASIC", "XAXIS"))
    print("xaxis mode is: " + str(xaxis_mode))

    secs_interval = int(config_obj.get("BASIC", "INTERVAL_SECS"))
    print("Interval secs: " + str(secs_interval))

    start_slot = int(config_obj.get("BASIC", "START_SLOT"))
    print("Start slot: " + str(start_slot))

    # 0 for DiskUsage, 1 for CPUUsage, 2 for MemUSage
    yLabel = ""
    graphTitle = ""
    print(metricName)
    if metricName == 'disk':
        
        graphTitle = "Disk_Usage"
        yLabel = "Disk Usage in GB"
    elif metricName == 'cpu':
        graphTitle = "CPU_Usage"
        yLabel = "CPU %"
    elif metricName == 'mem':
        graphTitle = "MEM_Usage"
        yLabel = "Memory [MB]"
    else:
        print("Unknown metric type. Default (disk) applied.")
        metricName = 'disk'

    number_of_args = len(sys.argv)
    data_files = []
    for i in range(2, number_of_args, 1):
        
        data_files.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), str(sys.argv[i])))
        print("Importing " + data_files[-1] + "...")

    client_object_array = []

    for file in data_files:
        import_from_file(file, client_object_array)

    
    print("You chose metric: ", metricName)

    x_array = []
    x_labels = []

    fig, ax = plt.subplots()
    plot_data = []

    if xaxis_mode == 'date':
        # calculate the maximum first date
        minimumDate = initial_timestamp

        # calculate the minimum last date
        maximumDate = min([x.timestamp[-1] for x in client_object_array])

        timedelta = maximumDate - minimumDate
        stepSize = timedelta / num_of_ticks # step Size / jump size for plotting

        tmp_timestamp = minimumDate

        while tmp_timestamp < maximumDate:
            x_array.append(tmp_timestamp)
            tmp_timestamp = tmp_timestamp + stepSize
            #x_labels.append(x_array[-1])
            x_labels.append(datetime.datetime.utcfromtimestamp(tmp_timestamp))
        
        for client in client_object_array:
            data_indices = find_nearest_spots(x_array, client.timestamp)
            plot_data.append([])
            for item in data_indices:
                if metricName == 'disk':
                    plot_data[-1].append(client.diskUsage[item])
                if metricName == 'cpu':
                    plot_data[-1].append(client.cpuUsage[item])
                if metricName == 'mem':
                    plot_data[-1].append(client.memUsage[item])
        
            ax.plot(x_labels, plot_data[-1], label=client.name, color=colorMap[client.name])
        
        majorTicksFormat = mdates.DateFormatter('%d/%m/%Y-%H:%M:%S')
        ax.xaxis.set_major_formatter(majorTicksFormat)
        fig.autofmt_xdate(rotation=45)
        

    if xaxis_mode == 'seq':
        # calculate the maximum first date
        #minimumDate = max([x.timestamp[0] for x in client_object_array])
        maxLength = min([len(x.timestamp) for x in client_object_array])

        stepSize = int(maxLength / num_of_ticks) # step Size / jump size for plotting

        data_indices = range(0, maxLength, stepSize)
        x_labels = [secs_interval*x/3600 for x in data_indices]
        
        for client in client_object_array:
            
            plot_data.append([])
            for item in data_indices:
                if metricName == 'disk':
                    plot_data[-1].append(client.diskUsage[item])
                if metricName == 'cpu':
                    plot_data[-1].append(client.cpuUsage[item])
                if metricName == 'mem':
                    plot_data[-1].append(client.memUsage[item])
        
            ax.plot(x_labels, plot_data[-1], label=client.name, color=colorMap[client.name])
        
        plt.xlabel("Hours", fontsize=12)
    
    if xaxis_mode == 'slot':

        # calculate the minimum last date
        maximumSlot = min([x.currentSlot[-1] for x in client_object_array])

        stepSize = int((maximumSlot-start_slot) / num_of_ticks) # step Size / jump size for plotting
        x_labels = range(start_slot, maximumSlot, stepSize)
        
        for client in client_object_array:
            data_indices = find_nearest_spots(x_labels, client.currentSlot)
            print(data_indices)
            plot_data.append([]) 
            for item in data_indices:
                if metricName == 'disk':
                    plot_data[-1].append(client.diskUsage[item])
                if metricName == 'cpu':
                    plot_data[-1].append(client.cpuUsage[item])
                if metricName == 'mem':
                    plot_data[-1].append(client.memUsage[item])
        
            
            ax.set_xticklabels(['{:,.0f}'.format(x) for x in x_labels])
            ax.plot(x_labels, plot_data[-1], label=client.name, color=colorMap[client.name])

        
        plt.xlabel("Slot", fontsize=12)

    print(graphTitle)
    ax.grid(axis='y')
    ax.grid(axis='x')
    plt.ylabel(yLabel)
    plt.title(graphTitle)
    plt.legend()
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    
    #ax.tick_params(axis="x", which="both", rotation=45)
    plt.show()


if __name__ == "__main__":
    main()