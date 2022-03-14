# Data Plotting
This subfolder contains the tool used to plot the output data from the eth2-client-analyzer.

This tool does not reveal / create / modify any data, it purely reads and represents the collected data into a plot.
This tool has been developed in Python.

Maintained by [migalabs](http://migalabs.es)


## Requirements

<strong>This tool has been tested using Python 3.8.10</strong>
It merely needs the Python interpreter to run it.


## Execution

The Execution command looks like the following:

```
python3 plot_data.py <config-file> csv-files

Example:
python3 plot_data.py configs/config_plot_NEvs_cpu.ini mainnet2/grandine_sample_13300.csv mainnet2/NE_grandine.csv

```
Keep in mind that there are three different keywords we can give as metricType argument:
- "mem" --> Outputs the Memory consumption plot
- "cpu" --> Outputs the CPU consumption plot
- "disk" --> Outputs the Disk Usage plot

For the data_file argument, we may input the file we want to read the data from.


(pending to document)
Config file

```
[PLOT1]
METRIC_NAME = disk (choose between disk, cpu, mem, slot, peers, netSent, netReceived)
PLOT_TYPE = line (choose between line, scatter)
SECOND_METRIC_NAME =
SECOND_PLOT_TYPE = scatter
NUM_OF_POINTS = 100
INITIAL_DATE = 11/02/2022 14:21:32
XAXIS = slot
INTERVAL_SECS = 30
START_X = 0
MIN_Y_VALUE = 0
MAX_Y_VALUE = 120
MIN_SECOND_Y_VALUE = 0
MAX_SECOND_Y_VALUE = 100
CLIENT_ALLOWLIST = grandine,NE_grandine
STORE_PATH = figures/mainnet/disk/sync_grandine_NE
```