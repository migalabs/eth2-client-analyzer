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
from pydoc import cli
import matplotlib.pyplot as plt
import matplotlib
import csv
import datetime
import sys
import numpy as np
import pandas as pd
import os
import matplotlib.dates as mdates
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

colors = {
    'prysm':        ['#ce1e16', '#e68e8a', '#7b120d', '#9fc0b6', '#538e7b', '#204136'], # red
    'lighthouse':   ['#3232ff', '#b2b2ff', '#00007f', '#ffbc8f', '#ff791f', '#994812'], # blue
    'teku':         ['#ffa500', '#ffd27f', '#7f5200', '#bacce4', '#7e99bd', '#465569'], # orange
    'nimbus':       ['#008000', '#99cc99', '#004000', '#d9c5b2', '#a08a74', '#50453a'], # green
    'lodestar':     ['#8c198c', '#cc99cc', '#4c004c', '#9adf7b', '58a835', '#2c541a'], # purple
    'grandine':     ['#999900', '#cccc7f', '#4c4c00', '#e69da5', '#c82236', '#610510'], # yellow / gold
}

class ColorQueue():

    def __init__(self, i_first_index: int):
        self.colorIndex = {
            "prysm": i_first_index,
            "lighthouse": i_first_index,
            "teku": i_first_index,
            "nimbus": i_first_index,
            "lodestar": i_first_index,
            "grandine": i_first_index,
        }

    def obtain_next_color(self, i_client_name: str):
        for key, value in self.colorIndex.items():
            if key.lower() in i_client_name.lower():
                # we found the client
                self.colorIndex[key] = int(value + 1)
                return colors[key][value % len(self.colorIndex)]
                


colorMap = {
    'prysm':                    colors['prysm'][1], # red
    'lighthouse':               colors['lighthouse'][1], # blue
    'teku':                     colors['teku'][1], # orange
    'nimbus':                   colors['nimbus'][1], # green
    'lodestar':                 colors['lodestar'][1], # purple
    'grandine':                 colors['grandine'][1], # yellow / gold
    'NE_Prysm':                 colors['prysm'][0],
    'NE_Lighthouse':            colors['lighthouse'][0],
    'NE_Teku':                  colors['teku'][0],
    'NE_Nimbus':                colors['nimbus'][0],
    'NE_Lodestar':              colors['lodestar'][0],
    'NE_Grandine':              colors['grandine'][0],
    'all-topics-prysm':         colors['prysm'][1], # red
    'all-topics-lighthouse':    colors['lighthouse'][1], # blue
    'all-topics-teku':          colors['teku'][1], # orange
    'all-topics-nimbus':        colors['nimbus'][1], # green
    'all-topics-lodestar':      colors['lodestar'][1], # purple
    'all-topics-grandine':      colors['grandine'][1], # yellow / gold

}

secondColorMap = {
    'prysm':                    colors['prysm'][3], # red
    'lighthouse':               colors['lighthouse'][3], # blue
    'teku':                     colors['teku'][3], # orange
    'nimbus':                   colors['nimbus'][3], # green
    'lodestar':                 colors['lodestar'][3], # purple
    'grandine':                 colors['grandine'][3], # yellow / gold
    'NE_Prysm':                 colors['prysm'][3],
    'NE_Lighthouse':            colors['lighthouse'][3],
    'NE_Teku':                  colors['teku'][3],
    'NE_Nimbus':                colors['nimbus'][3],
    'NE_Lodestar':              colors['lodestar'][3],
    'NE_Grandine':              colors['grandine'][3],
    'all-topics-prysm':         colors['prysm'][3], # red
    'all-topics-lighthouse':    colors['lighthouse'][3], # blue
    'all-topics-teku':          colors['teku'][3], # orange
    'all-topics-nimbus':        colors['nimbus'][3], # green
    'all-topics-lodestar':      colors['lodestar'][3], # purple
    'all-topics-grandine':      colors['grandine'][3], # yellow / gold

}

MAX_MAJOR_TICKS = 5

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
    netInRatio = 9
    netOutRatio = 10
    rewards = 11
    

    def __init__(self, i_pid, i_name):
        self.pid = i_pid
        self.name = i_name

        self.data = []

        for _ in range(0,11):
            self.data.append([])


        # data, each row corresponds to an array of data
    def add_row(self, i_row):
        #self.timestamp.append(mktime(datetime.datetime.strptime(i_row[2], '%B %d %H:%M:%S:%f').timetuple()))
        
        self.data[self.seqNumber].append(int(len(self.data[self.seqNumber])))
        self.data[self.timestamp].append(datetime.datetime.strptime(i_row[2], '%d/%m/%Y-%H:%M:%S:%f').timestamp())
        
        diskUsage_GB = float(i_row[3]) * 1000000 / (1024 * 1024 * 1024) # from bytes to GB
        if "NE_" in self.name:
            diskUsage_GB = float(i_row[3]) / 1024
        self.data[self.diskUsage].append(float("{:.2f}".format(diskUsage_GB)))
        
        self.data[self.cpuUsage].append(float("{:.2f}".format(float(i_row[4]))))
        
        memUsage_MB = float(i_row[5]) * 1000000 / (1024 * 1024) # from bytes to MB
        if "NE_" in self.name:
            memUsage_MB = float(i_row[5])
        self.data[self.memUsage].append(float("{:.2f}".format(memUsage_MB)))


        netSent_GB = float(i_row[6]) * 1000000 / (1024 * 1024 * 1024) # from bytes to GB
        if "NE_" in self.name:
            netSent_GB = float(i_row[6]) / 1024
        self.data[self.netSent].append(netSent_GB)
        
        netRecived_GB = float(i_row[7]) * 1000000 / (1024 * 1024 * 1024) # from bytes to GB
        if "NE_" in self.name:
            netRecived_GB = float(i_row[7]) / 1024

        self.data[self.netReceived].append(float("{:.2f}".format(netRecived_GB)))
        self.data[self.currentSlot].append(int(i_row[8]))
        self.data[self.currentPeers].append(int(i_row[9]))

        #netOutRatio_MB = float(i_row[6]) * 1000000 / (1024 * 1024) # from bytes to GB
        #self.data[self.netInRatio].append(netOutRatio_MB)
#
        #netInRatio_MB = float(i_row[11]) * 1000000 / (1024 * 1024) # from bytes to GB
        #self.data[self.netOutRatio].append(netInRatio_MB)
        
    
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
    'disk': {'legend': "disk", 'graphTitle': "Disk_Usage", 'yLabel': "Disk Usage in GB", 'data_index': ClientData.diskUsage},
    'cpu': {'legend': "cpu", 'graphTitle': "CPU_Usage", 'yLabel': "CPU %", 'data_index': ClientData.cpuUsage},
    'mem': {'legend': "mem", 'graphTitle': "MEM_Usage", 'yLabel': "Memory [MB]", 'data_index': ClientData.memUsage},
    'netSent': {'legend': "Net Sent", 'graphTitle': "Network Sent", 'yLabel': "Net Sent [GB]", 'data_index': ClientData.netSent},
    'netReceived': {'legend': "Net Received", 'graphTitle': "Network Received", 'yLabel': "Net Received [GB]", 'data_index': ClientData.netReceived},
    'slot': {'legend': "slot", 'graphTitle': "Slot", 'yLabel': "Slot Number", 'data_index': ClientData.currentSlot},
    'peers': {'legend': "peers", 'graphTitle': "Peers", 'yLabel': "Peer number", 'data_index': ClientData.currentPeers},
    'netInRatio': {'legend': "Net Received Ratio", 'graphTitle': "Network In Ratio", 'yLabel': "Peer number", 'data_index': ClientData.netInRatio},
    'netOutRatio': {'legend': "Net Sent Ratio", 'graphTitle': "Network Out Ratio", 'yLabel': "Peer number", 'data_index': ClientData.netOutRatio},
    'netOutRatio': {'legend': "Rewards", 'graphTitle': "Rewards per Epoch", 'yLabel': "Gwei", 'data_index': ClientData.rewards},
}

"""
Return the indexes of the timestamp_array_2 that are closer to each of the timestamp_array_1 items.
We assume these arrays are ordered

"""
def find_nearest_spots(array_1, array_2):


    array_2_index = 0
    new_delta = abs(array_1[0] - array_2[array_2_index])
    result = []
    for tmp_value in array_1:
        
        delta = abs(tmp_value - array_2[array_2_index])
        new_delta = delta
        while (new_delta <= delta or array_2[array_2_index] < array_2[array_2_index-1]) and array_2_index < len(array_2)-1: # iterate until we find a greater delta
            #print("comparing: ", tmp_value, " with: ", array_2[array_2_index])
            array_2_index = array_2_index + 1
            delta = new_delta
            new_delta = abs(tmp_value - array_2[array_2_index])
            #print("new delta comparing: ", tmp_value, " with: ", array_2[array_2_index])
        #print("adding index: ", array_2_index)
        result.append(array_2_index-1)

        if array_2_index > 0:
            array_2_index = array_2_index - 1
    #print(result)
    return result

def readjust_array(i_array):
    result = []

    for item in i_array:
        result.append(item-i_array[0])

    return result


def item_in_array(lookup_value, array):
    for item in array:
        if item == lookup_value:
            return True
    return False

class Plot():
    def __init__(self, i_config_obj, i_section):
        self.colorChooser = ColorQueue(0)
        self.second_colorChooser = ColorQueue(3)

        self.section = i_section
        
        self.plotList = []
        self.import_metrics(i_config_obj)
        
        # self.fig, (self.ax, self.ax2) = plt.subplots(1, 2)

        self.x_array = [] # array of data
        self.x_labels = [] # array of data stringified
        self.plot_data = []
        self.second_plot_data = []
    
    def setXlabel(self, input_label):
        self.ax.set_xlabel(input_label, fontsize=12)
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(MAX_MAJOR_TICKS))

    def finish_plot(self):
        self.ax.grid(axis='y')
        self.ax.grid(axis='x')

        yLabel_color = "#000"
        #if self.second_metricName is not "":
        #    yLabel_color = colorMap[i_client_obj.name]
        
        self.ax.set_ylabel(self.yLabel, color=yLabel_color)

        # self.ax.set_title(self.graphTitle)
        self.fig.suptitle(self.graphTitle, fontsize=16)
        
        self.ax.xaxis.set_minor_locator(AutoMinorLocator())
        self.ax.set_ylim([self.min_y_value, self.max_y_value])

        second_yLabel_color = "#000"
        #if self.second_metricName != "":
        #    second_yLabel_color = secondColorMap['prysm']

        if self.second_data_index != -1:
            self.ax2.set_ylabel(self.second_yLabel, color=second_yLabel_color)
            self.ax2.set_ylim([self.min_second_y_value, self.max_second_y_value])
        
        self.do_legend()

        plt.tight_layout()
        #self.ax.tick_params(axis="x", which="both", rotation=45)
        #plt.show()
        plt.savefig(self.storePath)

    def do_legend(self):
        handles,labels = [],[]
        for ax in self.fig.axes:
            for h,l in zip(*ax.get_legend_handles_labels()):
                handles.append(h)
                labels.append(l)
        self.ax.legend(handles,labels, loc=self.legendLocation, fontsize= 'x-small', markerscale=5/self.markerSize)

    def calculate_xArray(self, i_startValue, i_maxValue):
        stepSize = (i_maxValue - i_startValue)
        stepSize = max(stepSize / self.num_of_ticks, 1) # step Size / jump size for plotting
        self.x_array = np.arange (i_startValue, i_maxValue, stepSize)
        print("Array X: ", i_startValue, i_maxValue)
    
    def plot(self, i_ax, i_x_labels, i_plot_data, i_label, i_color, i_marker, i_type = 'line'):
        if i_type == 'line':
            i_ax.plot(i_x_labels, i_plot_data, label=i_label, color=i_color)
        
        elif i_type == 'scatter':
            i_ax.plot(i_x_labels, i_plot_data, label=i_label, marker=i_marker, markersize=self.markerSize, linestyle='None', color=i_color)

    # i_x_index = the array from the client obj to use as x (usually seqNumber or timestamp or currentSlot)
    def add_plot_data(self, i_client_obj, i_x_index, client_index):
        
        data_indices = find_nearest_spots(self.x_array, i_client_obj.data[i_x_index])

        self.plot_data.append([])
        self.second_plot_data.append([])
        
        #print(i_client_obj.name, data_indices)
        #print(self.x_array)
        for item in data_indices:
            self.plot_data[-1].append(i_client_obj.data[self.data_index][item])
            # in case a second plot
            if self.second_data_index != -1:
                self.second_plot_data[-1].append(i_client_obj.data[self.second_data_index][item])

        if self.data_index == ClientData.netReceived or self.data_index == ClientData.netSent:
            self.plot_data[-1] = readjust_array(self.plot_data[-1])
        self.plot(self.ax, self.x_labels, self.plot_data[-1], i_client_obj.name + " " + self.legend, self.colorChooser.obtain_next_color(i_client_obj.name), self.marker[client_index], self.plotType)
 
        if self.second_data_index != -1:
            color = self.second_colorChooser.obtain_next_color(i_client_obj.name)
            if self.secondPlotType == "scatter":
                color = self.colorChooser.obtain_next_color(i_client_obj.name)
            
            if self.second_data_index == ClientData.netReceived or self.second_data_index == ClientData.netSent:
                self.second_plot_data[-1] = readjust_array(self.second_plot_data[-1])
            self.plot(self.ax2, self.x_labels, self.second_plot_data[-1], i_client_obj.name + " " + self.second_legend, color, self.marker[client_index], self.secondPlotType)

        
    def import_metrics(self, config_obj):
        self.metricName = str(config_obj.get(self.section, "METRIC_NAME")) 
        self.plotType = str(config_obj.get(self.section, "PLOT_TYPE")) 

        self.second_metricName = str(config_obj.get(self.section, "SECOND_METRIC_NAME"))
        self.secondPlotType = str(config_obj.get(self.section, "SECOND_PLOT_TYPE")) 
        
        self.num_of_ticks = int(config_obj.get(self.section, "NUM_OF_POINTS")) 
        #self.initial_timestamp = datetime.datetime.strptime(config_obj.get(self.section, "INITIAL_DATE"), '%d/%m/%Y %H:%M:%S').timestamp() #print("Initial timestamp: " + str(num_of_ticks))
        self.secs_interval = int(config_obj.get(self.section, "INTERVAL_SECS")) 
        
        self.xaxis_mode = str(config_obj.get(self.section, "XAXIS")) 
        self.start_x = int(config_obj.get(self.section, "START_X")) 
        
        self.min_y_value = int(config_obj.get(self.section, "MIN_Y_VALUE")) 
        self.max_y_value = int(config_obj.get(self.section, "MAX_Y_VALUE")) 
        self.min_second_y_value = int(config_obj.get(self.section, "MIN_SECOND_Y_VALUE"))
        self.max_second_y_value = int(config_obj.get(self.section, "MAX_SECOND_Y_VALUE"))
        
        self.client_allowlist = str(config_obj.get(self.section, "CLIENT_ALLOWLIST")).split(",")

        self.storePath = str(config_obj.get(self.section, "STORE_PATH"))
        self.legendLocation = "upper left"
        if config_obj.has_option(self.section,"LEGEND_LOCATION"):
            self.legendLocation = str(config_obj.get(self.section, "LEGEND_LOCATION"))

        self.maxX = 0
        if config_obj.has_option(self.section,"END_X"):
            self.maxX = int(config_obj.get(self.section, "END_X"))

        self.plotMode = 1
        if config_obj.has_option(self.section,"PLOT_MODE"):
            self.plotMode = int(config_obj.get(self.section, "PLOT_MODE"))
        
        self.marker = [".",".",".",".",".",".",".",".",".",".","."]
        if config_obj.has_option(self.section,"MARKER"):
            self.marker  = str(config_obj.get(self.section, "MARKER")).split(",")

        self.markerSize = float(0.1)
        if config_obj.has_option(self.section,"MARKER_SIZE"):
            self.markerSize  = float(config_obj.get(self.section, "MARKER_SIZE"))
        
        # self.legenLabel = str(config_obj.get(self.section, "LABEL"))

        # 0 for DiskUsage, 1 for CPUUsage, 2 for MemUSage

        self.yLabel = ""
        self.second_yLabel = ""
        self.graphTitle = ""
        self.data_index = -1
        self.second_data_index =-1

        if self.metricName in PlotMetadata:
            self.legend = PlotMetadata[self.metricName]['legend']
            self.graphTitle = PlotMetadata[self.metricName]['graphTitle']
            self.yLabel = PlotMetadata[self.metricName]['yLabel']
            self.data_index = PlotMetadata[self.metricName]['data_index']
        else:
            print("Unknown metric type.")
            exit(0)
        
        if self.second_metricName in PlotMetadata:
            self.second_legend = PlotMetadata[self.second_metricName]['legend']
            self.graphTitle = self.graphTitle + " vs " + PlotMetadata[self.second_metricName]['graphTitle']
            self.second_yLabel = PlotMetadata[self.second_metricName]['yLabel']
            self.second_data_index = PlotMetadata[self.second_metricName]['data_index']

class OnePlot(Plot):
    def __init__(self, i_config_obj, i_section):
        super().__init__(i_config_obj, i_section)
        self.fig, self.ax = plt.subplots()
        
        if self.second_metricName != "":
            self.ax2 = self.ax.twinx()


class TwoSubPlotsbyMetric(Plot):

    def __init__(self, i_config_obj, i_section):
        super().__init__(i_config_obj, i_section)
        numberPlotsX = 1
        numberPlotsY = 1

        numberPlotsY = 2
        self.fig, (self.ax, self.ax2) = plt.subplots(numberPlotsX, numberPlotsY)
        self.ax2.grid(axis='y')
        self.ax2.grid(axis='x')

    def setXlabel(self, input_label):
        self.ax.set_xlabel(input_label, fontsize=12)
        self.ax2.set_xlabel(input_label, fontsize=12)

        self.ax.xaxis.set_major_locator(plt.MaxNLocator(MAX_MAJOR_TICKS))
        self.ax2.xaxis.set_major_locator(plt.MaxNLocator(MAX_MAJOR_TICKS))
    
    def do_legend(self):
        self.ax.legend(loc=self.legendLocation, fontsize= 'small', markerscale=5/self.markerSize)
        self.ax2.legend(loc=self.legendLocation, fontsize= 'small', markerscale=5/self.markerSize)
        self.ax2.set_xlabel(self.ax.get_xlabel(), fontsize=12)
        print(self.ax.get_xlabel())

    # i_x_index = the array from the client obj to use as x (usually seqNumber or timestamp or currentSlot)
    def add_plot_data(self, i_client_obj, i_x_index, client_index):
        
        data_indices = find_nearest_spots(self.x_array, i_client_obj.data[i_x_index])

        self.plot_data.append([])
        self.second_plot_data.append([])
        for item in data_indices:
            self.plot_data[-1].append(i_client_obj.data[self.data_index][item])
            # in case a second plot
            if self.second_data_index != -1:
                self.second_plot_data[-1].append(i_client_obj.data[self.second_data_index][item])
        
        self.plot(self.ax, self.x_labels, self.plot_data[-1], i_client_obj.name + " " + self.legend, self.colorChooser.obtain_next_color(i_client_obj.name), self.marker[client_index], self.plotType)
 
        if self.second_data_index != -1:
            color = self.second_colorChooser.obtain_next_color(i_client_obj.name)
            if self.secondPlotType == "scatter":
                color = self.colorChooser.obtain_next_color(i_client_obj.name)

            self.plot(self.ax2, self.x_labels, self.second_plot_data[-1], i_client_obj.name + " " + self.second_legend, color, self.marker[client_index], self.secondPlotType)

class SeveralSubPlots(Plot):
    def __init__(self, i_config_obj, i_section):
        super().__init__(i_config_obj, i_section)
        number_clients = len(self.client_allowlist)
        self.fig, self.ax_array = plt.subplots(number_clients)

        if self.second_metricName != "":
            self.ax2_array = []
            for ax in self.ax_array:
                self.ax2_array.append(ax.twinx())

    def setXlabel(self, input_label):

        for ax in self.ax_array:
            ax.set_xlabel(input_label, fontsize=12)
            ax.xaxis.set_major_locator(plt.MaxNLocator(MAX_MAJOR_TICKS))
    
    def finish_plot(self):

        for idx, ax in enumerate(self.ax_array):
            ax.grid(axis='y')
            ax.grid(axis='x')

            yLabel_color = "#000"
            
            ax.set_ylabel(self.yLabel, color=yLabel_color)

            self.fig.suptitle(self.graphTitle, fontsize=16)
            
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.set_ylim([self.min_y_value, self.max_y_value])

            second_yLabel_color = "#000"

            if self.second_data_index != -1:
                self.ax2_array[idx].set_ylabel(self.second_yLabel, color=second_yLabel_color)
                self.ax2_array[idx].set_ylim([self.min_second_y_value, self.max_second_y_value])
        
        self.do_legend()

        plt.tight_layout()
        #self.ax.tick_params(axis="x", which="both", rotation=45)
        #plt.show()
        plt.savefig(self.storePath)

    def do_legend(self):
        for idx, ax in enumerate(self.ax_array):
            ax.legend(loc=self.legendLocation, fontsize= 'small', markerscale=5/self.markerSize)
            self.ax2_array[idx].legend(loc=self.legendLocation, fontsize= 'small', markerscale=5/self.markerSize)
            #self.ax2.set_xlabel(self.ax.get_xlabel(), fontsize=12)
            #print(self.ax.get_xlabel())

    # i_x_index = the array from the client obj to use as x (usually seqNumber or timestamp or currentSlot)
    def add_plot_data(self, i_client_obj, i_x_index, client_index):
        
        ax_index = self.client_allowlist.index(i_client_obj.name)

        data_indices = find_nearest_spots(self.x_array, i_client_obj.data[i_x_index])

        self.plot_data.append([])
        self.second_plot_data.append([])
        for item in data_indices:
            self.plot_data[-1].append(i_client_obj.data[self.data_index][item])
            # in case a second plot
            if self.second_data_index != -1:
                self.second_plot_data[-1].append(i_client_obj.data[self.second_data_index][item])
        
        self.plot(self.ax_array[ax_index], self.x_labels, self.plot_data[-1], i_client_obj.name + " " + self.legend, self.colorChooser.obtain_next_color(i_client_obj.name), self.marker[client_index], self.plotType)
 
        if self.second_data_index != -1:
            color = self.second_colorChooser.obtain_next_color(i_client_obj.name)
            if self.secondPlotType == "scatter":
                color = self.colorChooser.obtain_next_color(i_client_obj.name)

            self.plot(self.ax_array[ax_index], self.x_labels, self.second_plot_data[-1], i_client_obj.name + " " + self.second_legend, color, self.marker[client_index], self.secondPlotType)
    


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
        
        plot_obj = OnePlot(config_obj, section)
        print("Plot mode: ", plot_obj.plotMode)
        if plot_obj.plotMode == 2:
            plot_obj = TwoSubPlotsbyMetric(config_obj, section)
        if plot_obj.plotMode == 3:
            plot_obj = SeveralSubPlots(config_obj, section)

        client_object_subarray = []
        
        for client in client_object_array:
            
            if item_in_array(client.name, plot_obj.client_allowlist):
                client_object_subarray.append(client)

        print("AllowList:", plot_obj.client_allowlist)
        print("Plot List:", [x.name for x in client_object_subarray])   
        if len(client_object_subarray) > 0:
            if plot_obj.xaxis_mode == 'date':
                
                minimumDate = max([x.data[ClientData.timestamp][0] for x in client_object_subarray])

                minimumDate = minimumDate + (plot_obj.start_x * 3600)

                # calculate the minimum last date
                maximumDate = min([x.data[ClientData.timestamp][-1] for x in client_object_subarray])
                if plot_obj.maxX > 0:
                    maximumDate = min(minimumDate + plot_obj.maxX * 3600, maximumDate)

                plot_obj.calculate_xArray(minimumDate, maximumDate)
                # plot_obj.x_labels = [datetime.datetime.utcfromtimestamp(x) for x in plot_obj.x_array]
                print(plot_obj.x_array[0])
                plot_obj.x_labels = [float((x - plot_obj.x_array[0]) / 3600.0) for x in plot_obj.x_array]

                for idx, client in enumerate(client_object_subarray):
                    plot_obj.add_plot_data(client, ClientData.timestamp, idx)
                
                #majorTicksFormat = mdates.DateFormatter('%d/%m-%H:%M')
                #plot_obj.ax.xaxis.set_major_formatter(majorTicksFormat)
                plot_obj.ax.tick_params(axis='x', labelsize=8)
                #plot_obj.fig.autofmt_xdate(rotation=30)
                #plot_obj.ax.set_xlabel("Date", fontsize=12)
                plot_obj.ax.set_xlabel("Hours", fontsize=12)

            if plot_obj.xaxis_mode == 'seq':
                
                maxValue = min([x.data[ClientData.seqNumber][-1] for x in client_object_subarray])
                if plot_obj.maxX > 0:
                    maxValue = min(plot_obj.maxX, maxValue)
                minValue = max([x.data[ClientData.seqNumber][0] for x in client_object_subarray])
                plot_obj.start_x = max(plot_obj.start_x, minValue)
                plot_obj.calculate_xArray(plot_obj.start_x, maxValue)
                plot_obj.x_labels = [plot_obj.secs_interval*x/3600 for x in plot_obj.x_array]

                for idx, client in enumerate(client_object_subarray):
                    plot_obj.add_plot_data(client, ClientData.seqNumber, idx)

                plot_obj.setXlabel("Hours")
            
            if plot_obj.xaxis_mode == 'slot':

                maxValue = min([x.data[ClientData.currentSlot][-1] for x in client_object_subarray])
                
                if plot_obj.maxX > 0:
                    maxValue = min(plot_obj.maxX, maxValue)
                
                minValue = max([x.data[ClientData.currentSlot][0] for x in client_object_subarray])

                plot_obj.start_x = max(plot_obj.start_x, minValue)
                plot_obj.calculate_xArray(plot_obj.start_x, maxValue)
                
                plot_obj.x_labels = plot_obj.x_array
                
                print("X Range: ", plot_obj.x_labels[0], " - ", plot_obj.x_labels[-1])
                for idx, client in enumerate(client_object_subarray):
                    plot_obj.add_plot_data(client, ClientData.currentSlot, idx)

                    plot_obj.ax.ticklabel_format(axis='x', style='plain', scilimits=(-3, 3), useMathText=True)

                plot_obj.setXlabel("Slot")


            plot_obj.finish_plot()
        


if __name__ == "__main__":
    main()