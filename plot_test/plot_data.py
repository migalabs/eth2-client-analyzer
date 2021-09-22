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




from os import spawnl, sysconf
import matplotlib.pyplot as plt
import csv
import datetime
import sys

import numpy as np
import os




# this function will calculate the time difference to the first timestamp.
# if the difference with the last timestamp is less than 1 second, this new timestamp is ignored
# if there is more than 1 second difference, we calculate the difference to the first timestamp
# and append a new time to the array to be shown in the plot

def add_time_to_array(input_array, last_datetime_str, new_datetime_str):

    first_datetime = datetime.datetime.strptime(replace_month_name(input_array[0]), "%b %d %H:%M:%S:%f")
    last_datetime = datetime.datetime.strptime(replace_month_name(last_datetime_str), "%b %d %H:%M:%S:%f")
    new_datetime = datetime.datetime.strptime(replace_month_name(new_datetime_str), "%b %d %H:%M:%S:%f")



    time_difference = new_datetime - first_datetime
    
    last_time_difference = new_datetime - last_datetime

    if last_time_difference.seconds >= 1:

        seconds = int(time_difference.seconds % 60)
        rest = int(time_difference.seconds / 60)

        minutes = int(rest % 60)
        rest = int(rest / 60)

        hours = int(rest % 60)

        time_string = ""

       
        time_string = str(hours).zfill(2) + ":" + str(minutes).zfill(2) + ":" + str(seconds).zfill(2)

        input_array.append(time_string)

    return input_array


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

    def __init__(self, input_pid, input_name):
        
        self.pid = input_pid
        self.name = input_name
        self.diskUsage = []
        self.cpuUsage = []
        self.memUsage = []


        
    def append_diskUsage_value(self, input_value):
        float_value = float(input_value)

        self.diskUsage.append(float("{:.2f}".format(float_value / 1000)))
        
    
    def append_cpuUsage_value(self, input_value):

        float_value = float(input_value)
        self.cpuUsage.append(float("{:.2f}".format(float_value)))
    

    def append_memUsage_value(self, input_value):

        float_value = float(input_value)
        self.memUsage.append(float("{:.2f}".format(float_value)))
    
    # this method truncates data arrays to the specified length and removes the extra positions
    def truncate_data_arrays(self, input_len):
        
        self.diskUsage = self.diskUsage[1:len]
        self.cpuUsage = self.cpuUsage[1:len]
        self.memUsage = self.memUsage[1:len]
    

    # checks if the specified name exists in an array of ClientData objects
    # returns the index of the specified client name in case of found.
    # Otherwise, return -1
    @classmethod
    def check_clientName_exists(cls, input_str, input_client_array):

        for idx, client in enumerate(input_client_array):
            if client.name == input_str:
                return idx
        
        return -1


def main():
    x = []
    y = []

    metricInterval = 0


    metricName =  str(sys.argv[1]) 
    metricType = 0 # default
    # 0 for DiskUsage, 1 for CPUUsage, 2 for MemUSage
    
    if metricName == 'disk':
        metricType = 1
    elif metricName == 'cpu':
        metricType = 2
    elif metricName == 'mem':
        metricType = 3
    else:
        print("Unknown metric type. Default (disk) applied.")
        metricType = 1
    
    
    # adjust path of file
    data_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), str(sys.argv[2]))

    client_object_array = []
    x_array_time = []
    last_datetime_str = ""

    # open the file containing the data
    with open(data_file,'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        row_counter = 0
        
        for row in csv_reader:

            row_counter = row_counter + 1
            if row_counter == 1:
                # this is the title row
                continue

            if row_counter == 2:
                # first data row
                x_array_time.append(row[2])
                last_datetime_str = x_array_time[-1]
                
            client_pid = row[0]
            client_name = row[1]
            
            # get the position in our array to identify the client
            client_index = ClientData.check_clientName_exists(client_name, client_object_array)
            
            if client_index == -1:
                # this means we need to add the client object to the array
                # this client did not exist in our array
                client_object_array.append(ClientData(client_pid, client_name))
            
            # there is already an object for the specified client where to add the data

            client_object_array[client_index].append_diskUsage_value(row[3])
            client_object_array[client_index].append_cpuUsage_value(row[4])
            client_object_array[client_index].append_memUsage_value(row[5])
            
                
            x_array_time = add_time_to_array(x_array_time, last_datetime_str, row[2])

            last_datetime_str = row[2]
        
        

    # check if data (y) and time (x) arrays have the same length
    if len(x_array_time) > len(client_object_array[0].cpuUsage):
        pass



    yLabel = ""
    graphTitle = ""

    plt.xlabel("Measure time (HH:MM:SS) since: " + x_array_time[0], fontsize=12)
    x_array_time[0] = "00:00:00"
    print("You chose metric: ", metricType)

    # obtain the client with less data
    # we can use any of the arrays inside a ClientData object, as all of them get data
    # appended and the same time. They should have the same length
    minimumDataLength = min([len(x.diskUsage) for x in client_object_array])
    timesTamp_length = len(x_array_time)

    min_x_data = min(minimumDataLength, timesTamp_length)


    i = 1
    # atempting to get 20 indexes in x axis
    data_jump = int(min_x_data / 40)

    # plot for each client
    for client in client_object_array:

        if metricType == 1:
            plt.plot(x_array_time[0:min_x_data:data_jump], client.diskUsage[0:min_x_data:data_jump], label=client.name)
            graphTitle = "Disk_Usage"
            yLabel = "Disk Usage in GB"
        
        elif metricType == 2:
            
            plt.plot(x_array_time[0:min_x_data:data_jump], client.cpuUsage[0:min_x_data:data_jump], label=client.name)
            graphTitle = "CPU_Usage"
            yLabel = "CPU %"
        
        elif metricType == 3:

            plt.plot(x_array_time[0:min_x_data:data_jump], client.memUsage[0:min_x_data:data_jump], label=client.name)
            graphTitle = "MEM_Usage"
            yLabel = "Memory [MB]"



    plt.xticks(range(len(x_array_time[0:min_x_data:data_jump])), x_array_time[0:min_x_data:data_jump], rotation=45, ha="right")

    plt.ylabel(yLabel)
    plt.title(graphTitle)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()