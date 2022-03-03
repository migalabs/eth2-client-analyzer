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

class Plot():
    def __init__(self):

        self.fig, self.ax = plt.subplots()

        self.x_array = []
        self.plot_data = []
    
    def calculate_xArray(self, i_startValue, i_maxValue, i_num_of_ticks):
        stepSize = (i_maxValue - i_startValue) / i_num_of_ticks # step Size / jump size for plotting
        self.x_array = np.arange (i_startValue, i_maxValue, stepSize)



    def add_plot_data(self, i_client_obj, i_x_index, i_y_index):

        data_indices = find_nearest_spots(self.x_array, i_client_obj.data[i_x_index])

        self.plot_data.append([])
        for item in data_indices:
            self.plot_data[-1].append(i_client_obj.data[i_y_index][item])

            
"""
Return the indexes of the timestamp_array_2 that are closer to each of the timestamp_array_1 items.
We assume these arrays are ordered

"""
def find_nearest_spots(array_1, array_2):


    array_2_index = 0
    new_delta = abs(array_1[0] - array_2[array_2_index])
    result = []
    for tmp_timestamp in array_1:
        delta = abs(tmp_timestamp - array_2[array_2_index])
        new_delta = delta

        while new_delta <= delta and array_2_index < len(array_2)-1: # iterate until we find a greater delta
            array_2_index = array_2_index + 1
            delta = new_delta
            new_delta = abs(tmp_timestamp - array_2[array_2_index])
        
        result.append(array_2_index-1)

    #print(result)
    return result
        
        

class ClientData():

    seqNumber = 0
    timestamp = 1
    diskUsage = 2
    cpuUsage = 3
    memUsage = 4
    netSent = 5
    netReceived = 6
    currentSlot = 7
    currentPeers = 8
    

    def __init__(self, i_pid, i_name):
        self.pid = i_pid
        self.name = i_name

        self.data = []

        for i in range(0,9):
            self.data.append([])

        # data, each row corresponds to an array of data
    def add_row(self, i_row):
        #self.timestamp.append(mktime(datetime.datetime.strptime(i_row[2], '%B %d %H:%M:%S:%f').timetuple()))
        
        self.data[self.seqNumber].append(int(len(self.data[self.seqNumber])))
        self.data[self.timestamp].append(datetime.datetime.strptime(i_row[2], '%d/%m/%Y-%H:%M:%S:%f').timestamp())
        #print(self.timestamp[-1])
        self.data[self.diskUsage].append(float("{:.2f}".format(float(i_row[3]) / 1000)))
        self.data[self.cpuUsage].append(float("{:.2f}".format(float(i_row[4]))))
        self.data[self.memUsage].append(float("{:.2f}".format(float(i_row[5]))))
        #self.data[self.netSent].append(float(i_row[6]))
        #self.data[self.netReceived].append(float("{:.2f}".format(float(i_row[7]))))
        #self.data[self.currentSlot].append(int(i_row[8]))
        #self.data[self.currentPeers].append(int(i_row[9]))
    
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

    start_x = int(config_obj.get("BASIC", "START_X"))
    print("Start slot: " + str(start_x))

    # 0 for DiskUsage, 1 for CPUUsage, 2 for MemUSage
    yLabel = ""
    graphTitle = ""
    data_index = 0
    if metricName == 'disk':
        graphTitle = "Disk_Usage"
        yLabel = "Disk Usage in GB"
        data_index = ClientData.diskUsage
    elif metricName == 'cpu':
        graphTitle = "CPU_Usage"
        yLabel = "CPU %"
        data_index = ClientData.cpuUsage
    elif metricName == 'mem':
        graphTitle = "MEM_Usage"
        yLabel = "Memory [MB]"
        data_index = ClientData.memUsage
    else:
        print("Unknown metric type. Default (disk) applied.")
        metricName = 'disk'
        graphTitle = "Disk_Usage"
        yLabel = "Disk Usage in GB"
        data_index = ClientData.diskUsage

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

    plot_obj = Plot()

    if xaxis_mode == 'date':

        # calculate the minimum last date
        maximumDate = min([x.data[ClientData.timestamp][-1] for x in client_object_array])

        plot_obj.calculate_xArray(initial_timestamp, maximumDate, num_of_ticks)
        x_labels = [datetime.datetime.utcfromtimestamp(x) for x in plot_obj.x_array]

        for client in client_object_array:
            plot_obj.add_plot_data(client, ClientData.timestamp, data_index)
            plot_obj.ax.plot(x_labels, plot_obj.plot_data[-1], label=client.name, color=colorMap[client.name])
        
        majorTicksFormat = mdates.DateFormatter('%d/%m/%Y-%H:%M:%S')
        plot_obj.ax.xaxis.set_major_formatter(majorTicksFormat)
        plot_obj.fig.autofmt_xdate(rotation=45)
        

    if xaxis_mode == 'seq':
        maxValue = min([x.data[ClientData.seqNumber][-1] for x in client_object_array])

        plot_obj.calculate_xArray(start_x, maxValue, num_of_ticks)
        x_labels = [secs_interval*x/3600 for x in plot_obj.x_array]

        for client in client_object_array:
            plot_obj.add_plot_data(client, ClientData.seqNumber, data_index)
            plot_obj.ax.plot(x_labels, plot_obj.plot_data[-1], label=client.name, color=colorMap[client.name])

        plt.xlabel("Hours", fontsize=12)
    
    if xaxis_mode == 'slot':

        maxValue = min([x.data[ClientData.currentSlot][-1] for x in client_object_array])
        maxValue = min([x.data[ClientData.currentSlot][-1] for x in client_object_array])

        plot_obj.calculate_xArray(start_x, maxValue, num_of_ticks)
        x_labels = plot_obj.x_array

        for client in client_object_array:
            plot_obj.add_plot_data(client, ClientData.currentSlot, data_index)
            plot_obj.ax.set_xticklabels(['{:,.0f}'.format(x) for x in x_labels])
            plot_obj.ax.plot(x_labels, plot_obj.plot_data[-1], label=client.name, color=colorMap[client.name])

        plt.xlabel("Slot", fontsize=12)

    print(graphTitle)
    plot_obj.ax.grid(axis='y')
    plot_obj.ax.grid(axis='x')
    plt.ylabel(yLabel)
    plt.title(graphTitle)
    plt.legend()
    plot_obj.ax.xaxis.set_minor_locator(AutoMinorLocator())
    
    #ax.tick_params(axis="x", which="both", rotation=45)
    plt.show()


if __name__ == "__main__":
    main()