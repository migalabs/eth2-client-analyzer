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


from os import spawnl, sysconf
import matplotlib.pyplot as plt
import csv
import datetime
import sys

import numpy as np
import pandas as pd
import os
import matplotlib.dates as mdates


initial_timestamp = datetime.datetime.strptime(sys.argv[4], '%d/%m/%Y %H:%M')

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
        self.timestamp.append(datetime.datetime.strptime(i_row[2], '%d/%m/%Y-%H:%M:%S:%f'))
        self.diskUsage.append(float("{:.2f}".format(float(i_row[3]) / 1000)))
        self.cpuUsage.append(float("{:.2f}".format(float(i_row[4]))))
        self.memUsage.append(float("{:.2f}".format(float(i_row[5]))))
        self.netSent.append(float("{:.2f}".format(float(i_row[6]))))
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
            
            #print(row)
            #if datetime.datetime.strptime(row[2], '%d/%m/%Y %H:%M:%S:%f') < initial_timestamp:
            #    continue
                
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
    new_delta = abs((timestamp_array_1[0] - timestamp_array_2[array_2_index]).total_seconds())
    result = []
    for tmp_timestamp in timestamp_array_1:
        delta = abs((tmp_timestamp - timestamp_array_2[array_2_index]).total_seconds())
        new_delta = delta

        while new_delta <= delta and array_2_index < len(timestamp_array_2)-1: # iterate until we find a greater delta
            array_2_index = array_2_index + 1
            delta = new_delta
            new_delta = abs((tmp_timestamp - timestamp_array_2[array_2_index]).total_seconds())
            #print("New delta is: " + str(new_delta))
            #print("Old delta is: " + str(delta))
            
                
        #print("Index in: " + str(array_2_index))
        result.append(array_2_index-1)
    #print(result)

    return result


def main():
    x = []
    y = []

    metricName =  str(sys.argv[1]) 
    metricType = 1 # default

    # 0 for DiskUsage, 1 for CPUUsage, 2 for MemUSage
    yLabel = ""
    graphTitle = ""

    if metricName == 'disk':
        metricType = 1
        graphTitle = "Disk_Usage"
        yLabel = "Disk Usage in GB"
    elif metricName == 'cpu':
        metricType = 2
        graphTitle = "CPU_Usage"
        yLabel = "CPU %"
    elif metricName == 'mem':
        metricType = 3
        graphTitle = "MEM_Usage"
        yLabel = "Memory [MB]"
    else:
        print("Unknown metric type. Default (disk) applied.")
        metricType = 1
    
    num_of_ticks = int(sys.argv[2]) # number of ticks in the plot
    number_of_lines = int(sys.argv[3]) # amount of data to plot
    number_of_files = len(sys.argv) - 4 # first is the metric type and second is the interval, third is the amount of lines to process and fourth is the initial timestamp
    data_files = []
    for i in range(1, number_of_files, 1):
        
        data_files.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), str(sys.argv[i+4])))
        print("Importing " + data_files[-1] + "...")

    client_object_array = []

    for file in data_files:
        import_from_file(file, client_object_array)

    yLabel = ""
    graphTitle = ""

    plt.xlabel("Measure time (HH:MM:SS) since: " + str(initial_timestamp), fontsize=12)
    print("You chose metric: ", metricType)

    # calculate the maximum first date
    minimumDate = max([x.timestamp[0] for x in client_object_array])

    # calculate the minimum last date
    maximumDate = min([x.timestamp[-1] for x in client_object_array])
    time_array = []

    timedelta = maximumDate - minimumDate
    stepSize = timedelta / num_of_ticks # step Size / jump size for plotting

    tmp_timestamp = minimumDate

    while tmp_timestamp < maximumDate:
        time_array.append(tmp_timestamp)
        tmp_timestamp = tmp_timestamp + stepSize


    plot_data = []
    for client in client_object_array:
        data_indices = find_nearest_spots(time_array, client.timestamp)
        plot_data.append([])
        for item in data_indices:
            #print(item)
            if metricType == 1:
                plot_data[-1].append(client.diskUsage[item])
            if metricType == 2:
                plot_data[-1].append(client.cpuUsage[item])
            if metricType == 3:
                plot_data[-1].append(client.memUsage[item])
    
        plt.plot(time_array, plot_data[-1], label=client.name)
        #print(plot_data[-1])
        #print(time_array)
    #plt.xticks(range(len(time_array)), time_array, rotation=45, ha="right")
    plt.ylabel(yLabel)
    plt.title(graphTitle)
    plt.legend()
    plt.show()



"""
    i = 1
    # atempting to get 40 indexes in x axis
    data_jump = int(min_x_data / 40)



    x_array_time.append(str(initial_timestamp))
    #for i in range(1,number_of_lines):
    #    last_time = x_array_time[i-1]
    #    #print(last_time)
    #    x_array_time.append(str((datetime.datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=metricInterval))))

    fig, axs = plt.subplots(1, 1, figsize=(6.4, 7), constrained_layout=True)
    # plot for each client
    for client in client_object_array:

        if metricType == 1:
            axs.plot(client.timestamp[0:min_x_data:data_jump], client.diskUsage[0:min_x_data:data_jump], label=client.name)
            graphTitle = "Disk_Usage"
            yLabel = "Disk Usage in GB"
        
        elif metricType == 2:
            
            axs.plot(client.timestamp[0:min_x_data:data_jump], client.cpuUsage[0:min_x_data:data_jump], label=client.name)
            graphTitle = "CPU_Usage"
            yLabel = "CPU %"
        
        elif metricType == 3:

            axs.plot(client.timestamp[0:min_x_data:data_jump], client.memUsage[0:min_x_data:data_jump], label=client.name)
            graphTitle = "MEM_Usage"
            yLabel = "Memory [MB]"


    axs.xaxis_date()
    axs.grid(True)
    axs.set_ylabel(yLabel)
    plt.xticks(range(len(client.timestamp[0:min_x_data:data_jump])), client.timestamp[0:min_x_data:data_jump], rotation=45, ha="right")

    #plt.ylabel(yLabel)
    plt.title(graphTitle)
    plt.legend()
    plt.show()
"""
if __name__ == "__main__":
    main()