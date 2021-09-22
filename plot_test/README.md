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
python3 plot_data.py <metricType> <data_file>
```
Keep in mind that there are three different keywords we can give as metricType argument:
- "mem" --> Outputs the Memory consumption plot
- "cpu" --> Outputs the CPU consumption plot
- "disk" --> Outputs the Disk Usage plot

For the data_file argument, we may input the file we want to read the data from.