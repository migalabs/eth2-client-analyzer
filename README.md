# eth2-client-analyzer
This repository includes the code and configurations to run and analyze the five main clients of Eth2.

Prysm, Lighthouse, Teku, Nimbus and Lodestar can be set and launched from the different shell scripts. 

The repository also includes a Resource monitor tool to read the five clients at the same time.

Please note that this toll does not reveal any information about the blockchain, node or host. This tool purely provides machine resource information about the conifgured PIDs.

Maintained by [migalabs](http://migalabs.es)



## Execution command

An example of execution command would be: 

```

python3 python_monitor.py config_file.ini

```



## Config File

It is needed to provide a configuration file through the argument of the execution. In this configuration file we may input all needed variables to make the script work for our specific case.


Please do not change the section names (the ones in [])

- PIDS: We may provide a list of PIDs to monitor.

- FOLDERS: We may provide a list of Folders to monitor.



<strong>Please keep in mind that order is important. This way, the first folder in the list will be assigned to the pid in the list. The same would apply to the second, third...

It is very important that we provide the same amount of pids and folders, otherwise the script will terminate.</strong>



In case you found that the folders are not being properly monitored, it is recommended to use an absolute path.

- OUTPUT_FILE: the name of the output file we want the script to write to. If this file does not exist, the script will create automatically.


- SLEEP_INTERVAL (in seconds): this variable represnts the time betweeneach time the script monitors resources. By default we have applied 30, which would mean that every 30 seconds there is a new line added to the output file for each pid.
    - Minimum is 1 second.

With an interval of 30 seconds and 5 clients running at the same time, the script generates an output file of 4MB a week.


```

[BASIC]

PIDS = 1,2,3,4,5

FOLDERS = ~/.eth2/,~/.lighthouse/,~/.local/share/teku/,~/eth2_clients/nimbus/,~/.local/share/lodestar/

OUTPUT_FILE = output_file.csv

SLEEP_INTERVAL = 30


[NAMES]

java = teku
node = lodestar
beacon-chain-v1 = prysm
nimbus_beacon_node = nimbus


```



