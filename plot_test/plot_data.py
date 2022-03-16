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
import matplotlib.ticker as mticker


colorMap = {
    'prysm': '#FF6666', # red
    'lighthouse': '#489dec', # blue
    'teku': '#FFA500', # orange
    'nimbus': '#B6D7A8', # green
    'lodestar': '#9379d6', # purple
    'grandine': '#b3b300', # yellow / gold
    'NE_Prysm': '#7f3333',
    'NE_Lighthouse': '#244e76',
    'NE_Teku': '#7f5200',
    'NE_Nimbus': '#5b6b54',
    'NE_Lodestar': '#493c6b',
    'NE_Grandine': '#474700'
}

secondColorMap = {
    'prysm': '#7f3333',
    'lighthouse': '#244e76',
    'teku': '#7f5200',
    'nimbus': '#5b6b54',
    'lodestar': '#493c6b',
    'grandine': '#474700',
    'NE_Prysm': '#FF6666',
    'NE_Lighthouse': '#489dec',
    'NE_Teku': 'FFA500',
    'NE_Nimbus': '9379d6',
    'NE_Lodestar': '#9379d6',
    'NE_Grandine': '#b3b300'
}

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
        self.data[self.diskUsage].append(float("{:.2f}".format(float(i_row[3]) / 1000)))
        self.data[self.cpuUsage].append(float("{:.2f}".format(float(i_row[4]))))
        memUsage_MB = float(i_row[5]) * 1000000 / (1024 * 1024) # from bytes to MB
        self.data[self.memUsage].append(float("{:.2f}".format(memUsage_MB)))
        self.data[self.netSent].append(float(i_row[6]) / 1000)
        self.data[self.netReceived].append(float("{:.2f}".format(float(i_row[7]) / 1000)))
        self.data[self.currentSlot].append(int(i_row[8]))
        self.data[self.currentPeers].append(int(i_row[9]))
        
    
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

PlotMetadata = {
    'disk': {'graphTitle': "Disk_Usage", 'yLabel': "Disk Usage in GB", 'data_index': ClientData.diskUsage},
    'cpu': {'graphTitle': "CPU_Usage", 'yLabel': "CPU %", 'data_index': ClientData.cpuUsage},
    'mem': {'graphTitle': "MEM_Usage", 'yLabel': "Memory [MB]", 'data_index': ClientData.memUsage},
    'netSent': {'graphTitle': "Network Sent", 'yLabel': "Net Sent [GB]", 'data_index': ClientData.netSent},
    'netReceived': {'graphTitle': "Network Received", 'yLabel': "Net Received [GB]", 'data_index': ClientData.netReceived},
    'slot': {'graphTitle': "Slot", 'yLabel': "Slot Number", 'data_index': ClientData.currentSlot},
    'peers': {'graphTitle': "Peers", 'yLabel': "Peer number", 'data_index': ClientData.currentPeers},
}

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


def item_in_array(lookup_value, array):
    for item in array:
        if item == lookup_value:
            return True
    return False



class Plot():
    def __init__(self, i_config_obj, i_section, i_second_y_axis = False):

        self.section = i_section
        self.fig, self.ax = plt.subplots()

        self.import_metrics(i_config_obj)

        if i_second_y_axis:
            self.ax2 = self.ax.twinx()

        self.x_array = [] # array of data
        self.x_labels = [] # array of data stringified
        self.plot_data = []
        self.second_plot_data = []
    
    def finish_plot(self, i_client_obj = None):
        self.ax.grid(axis='y')
        self.ax.grid(axis='x')

        yLabel_color = "#000"
        if i_client_obj is not None:
            yLabel_color = colorMap[i_client_obj.name]
        
        self.ax.set_ylabel(self.yLabel, color=yLabel_color)

        self.ax.set_title(self.graphTitle)
        self.ax.legend()
        self.ax.xaxis.set_minor_locator(AutoMinorLocator())
        self.ax.set_ylim([self.min_y_value, self.max_y_value])

        second_yLabel_color = "#000"
        if i_client_obj is not None:
            second_yLabel_color = secondColorMap[i_client_obj.name]

        if self.second_data_index != -1:
            self.ax2.set_ylabel(self.second_yLabel, color=second_yLabel_color)
            self.ax2.set_ylim([self.min_second_y_value, self.max_second_y_value])
        
        plt.tight_layout()
        #plt.show()
        plt.savefig(self.storePath)

        #ax.tick_params(axis="x", which="both", rotation=45)

    def calculate_xArray(self, i_startValue, i_maxValue):
        stepSize = (i_maxValue - i_startValue)
        stepSize = stepSize / self.num_of_ticks # step Size / jump size for plotting
        self.x_array = np.arange (i_startValue, i_maxValue, stepSize)
    
    def plot(self, i_ax, i_x_labels, i_plot_data, i_label, i_color, i_type = 'line'):
        if i_type == 'line':
            i_ax.plot(i_x_labels, i_plot_data, label=i_label, color=i_color)
        
        elif i_type == 'scatter':
            dot_sizes = [2] * len(i_plot_data)
            i_ax.scatter(i_x_labels, i_plot_data, label=i_label, color=i_color, s=dot_sizes)

    # i_x_index = the array from the client obj to use as x (usually seqNumber or timestamp or currentSlot)
    def add_plot_data(self, i_client_obj, i_x_index):
        
        data_indices = find_nearest_spots(self.x_array, i_client_obj.data[i_x_index])

        self.plot_data.append([])
        self.second_plot_data.append([])
        for item in data_indices:
            self.plot_data[-1].append(i_client_obj.data[self.data_index][item])
            # in case a second plot
            if self.second_data_index != -1:
                self.second_plot_data[-1].append(i_client_obj.data[self.second_data_index][item])
        #print(i_client_obj.name, self.plot_data[-1][-1], data_indices[-1])
        self.plot(self.ax, self.x_labels, self.plot_data[-1], i_client_obj.name, colorMap[i_client_obj.name], self.plotType)

        if self.second_data_index != -1:
            self.ax2 = self.ax.twinx()
            self.plot(self.ax2, self.x_labels, self.second_plot_data[-1], i_client_obj.name, secondColorMap[i_client_obj.name], self.secondPlotType)

        
    def import_metrics(self, config_obj):
        self.metricName = str(config_obj.get(self.section, "METRIC_NAME")) 
        self.plotType = str(config_obj.get(self.section, "PLOT_TYPE")) 

        self.second_metricName = str(config_obj.get(self.section, "SECOND_METRIC_NAME"))
        self.secondPlotType = str(config_obj.get(self.section, "SECOND_PLOT_TYPE")) 
        
        self.num_of_ticks = int(config_obj.get(self.section, "NUM_OF_POINTS")) 
        self.initial_timestamp = datetime.datetime.strptime(config_obj.get(self.section, "INITIAL_DATE"), '%d/%m/%Y %H:%M:%S').timestamp() #print("Initial timestamp: " + str(num_of_ticks))
        self.secs_interval = int(config_obj.get(self.section, "INTERVAL_SECS")) 
        
        self.xaxis_mode = str(config_obj.get(self.section, "XAXIS")) 
        self.start_x = int(config_obj.get(self.section, "START_X")) 
        
        self.min_y_value = int(config_obj.get(self.section, "MIN_Y_VALUE")) 
        self.max_y_value = int(config_obj.get(self.section, "MAX_Y_VALUE")) 
        self.min_second_y_value = int(config_obj.get(self.section, "MIN_SECOND_Y_VALUE"))
        self.max_second_y_value = int(config_obj.get(self.section, "MAX_SECOND_Y_VALUE"))
        
        self.client_allowlist = str(config_obj.get(self.section, "CLIENT_ALLOWLIST")).split(",")

        self.storePath = str(config_obj.get(self.section, "STORE_PATH"))

        # 0 for DiskUsage, 1 for CPUUsage, 2 for MemUSage

        self.yLabel = ""
        self.second_yLabel = ""
        self.graphTitle = ""
        self.data_index = -1
        self.second_data_index =-1

        if self.metricName in PlotMetadata:
            self.graphTitle = PlotMetadata[self.metricName]['graphTitle']
            self.yLabel = PlotMetadata[self.metricName]['yLabel']
            self.data_index = PlotMetadata[self.metricName]['data_index']
        else:
            print("Unknown metric type.")
            exit(0)
        
        if self.second_metricName in PlotMetadata:
            self.graphTitle = self.graphTitle + " vs " + PlotMetadata[self.metricName]['graphTitle']
            self.second_yLabel = PlotMetadata[self.metricName]['yLabel']
            self.second_data_index = PlotMetadata[self.metricName]['data_index']

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

    section_number = 1
    section_base_name = "PLOT"


    number_of_args = len(sys.argv)
    data_files = []
    for i in range(2, number_of_args, 1):
        
        data_files.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), str(sys.argv[i])))
        print("Importing " + data_files[-1] + "...")

    client_object_array = []

    for file in data_files:
        import_from_file(file, client_object_array)

    while config_obj.has_section(section_base_name+str(section_number)):
        section = section_base_name+str(section_number)
        section_number = section_number + 1
        plot_obj = Plot(config_obj, section)

        client_object_subarray = []
        print(plot_obj.client_allowlist)
        for client in client_object_array:
            
            if item_in_array(client.name, plot_obj.client_allowlist):
                client_object_subarray.append(client)
                
        
        if plot_obj.xaxis_mode == 'date':

            # calculate the minimum last date
            maximumDate = min([x.data[ClientData.timestamp][-1] for x in client_object_subarray])

            plot_obj.calculate_xArray(plot_obj.initial_timestamp, maximumDate)
            plot_obj.x_labels = [datetime.datetime.utcfromtimestamp(x) for x in plot_obj.x_array]

            for client in client_object_subarray:
                plot_obj.add_plot_data(client, ClientData.timestamp)
            
            majorTicksFormat = mdates.DateFormatter('%d/%m-%H:%M')
            plot_obj.ax.xaxis.set_major_formatter(majorTicksFormat)
            plot_obj.ax.tick_params(axis='x', labelsize=8)
            plot_obj.fig.autofmt_xdate(rotation=30)
            plot_obj.ax.set_xlabel("Date", fontsize=12)

        if plot_obj.xaxis_mode == 'seq':
            maxValue = min([x.data[ClientData.seqNumber][-1] for x in client_object_subarray])

            plot_obj.calculate_xArray(plot_obj.start_x, maxValue)
            plot_obj.x_labels = [plot_obj.secs_interval*x/3600 for x in plot_obj.x_array]

            for client in client_object_subarray:
                plot_obj.add_plot_data(client, ClientData.seqNumber)

            plot_obj.ax.set_xlabel("Hours", fontsize=12)
        
        if plot_obj.xaxis_mode == 'slot':

            maxValue = min([x.data[ClientData.currentSlot][-1] for x in client_object_subarray])
            
            plot_obj.calculate_xArray(plot_obj.start_x, maxValue)
            
            plot_obj.x_labels = plot_obj.x_array

            for client in client_object_subarray:
                plot_obj.add_plot_data(client, ClientData.currentSlot)

                plot_obj.ax.ticklabel_format(axis='x', style='plain', scilimits=(-3, 3), useMathText=True)

            plot_obj.ax.set_xlabel("Slot", fontsize=12)

        if len(client_object_subarray) == 1 and plot_obj.second_data_index != -1:
            plot_obj.finish_plot(client_object_subarray[0])
        else:
            plot_obj.finish_plot()


if __name__ == "__main__":
    main()