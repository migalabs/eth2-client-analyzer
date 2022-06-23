# eth2-client-analyzer 
This repository includes the code and configurations to run and analyze the five main clients of Eth2.

Prysm, Lighthouse, Teku, Nimbus and Lodestar can be set and launched from the different shell scripts. 

The repository also includes a Resource monitor tool to read the five clients at the same time.

Please note that this tool does not reveal any information about the blockchain, node or host. This tool purely provides machine resource information about the conifgured PIDs.

Maintained by [migalabs](http://migalabs.es)


<br></br>



## Execution command

An example of execution command would be: 

```

python3 python_monitor.py config_file.ini

```

It is recommended to use a different output_file for each execution.
Otherwise, data could get mixed and representation may not be the desired.

<br></br>
<br></br>

## Requirements

<strong>This tool has been tested using Python 3.8.10</strong>


It is recommended to create a python virtual environment. This can be done through the following command:

```
python3 -m virtualenv <venv_name>
```

(This will require you to have "virtualenv" installed)

Virtualenv can be installed via pip.

https://help.dreamhost.com/hc/es/articles/115000695551-Instalar-y-usar-virtualenv-con-Python-3


Then use the following to activate the virtual environment (from the same folder):

```
source <venv_name>/bin/activate

```

Or deactivate it:

```
deactivate

```


In case you also need to install pip:
https://pip.pypa.io/en/stable/installation/

<br></br>


Please install psUtil library using pip command:

```
pip install psutil
```

(This will require you to have pip installed)


<br></br>
<br></br>


## Config File

It is needed to provide a configuration file through the argument of the execution. In this configuration file we may input all needed variables to make the script work for our specific case.


Please do not change the section names (the ones between [ ])

<br></br>

### BASIC

- <strong>PIDS</strong>: We may provide a list of PIDs to monitor.

- <strong>FOLDERS</strong>: We may provide a list of folders to monitor.



<strong>Please keep in mind that order is important. This way, the first folder in the list will be assigned to the first PID in the list. The same would apply to the second, third and so on.

It is very important that we provide the same amount of PIDs and folders, otherwise the script will terminate.</strong>



In case you find that the folders are not being properly monitored, it is recommended to use an absolute path.

- <strong>OUTPUT_FILE</strong>: the name of the output file we want the script to write to. If this file does not exist, the script will create it automatically.


- <strong>SLEEP_INTERVAL</strong> (in seconds): this variable represents the time between each time the script monitors resources. By default we have applied 30, which would mean that every 30 seconds there is a new line added to the output file for each pid.
    - Minimum is 1 second.

With an interval of 30 seconds and 5 clients running at the same time, the script generates an output file of 4MB a week.

<br></br>

### NAMES

Here we may define the names we want to output for each process.
Usually the processes associated with a PID have a different name than what we want to output.

For example, Teku client runs under the "java" process, which means the process name would be "java".

Here we may define the name we want to give in the tool output.


```

[BASIC]

PIDS = 25102,16230,14520,24510,1250

FOLDERS = ~/.eth2/,~/.lighthouse/,~/.local/share/teku/,~/eth2_clients/nimbus/,~/.local/share/lodestar/

OUTPUT_FILE = output_file.csv

SLEEP_INTERVAL = 30


[NAMES]

java = teku
node = lodestar
beacon-chain-v1 = prysm
nimbus_beacon_node = nimbus
lighthouse = lighthouse


```





