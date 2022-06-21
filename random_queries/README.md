# Random queries test

This folder contains the necessary files to perform a simple queries test on any of the main Ethereum clients.
This is a first version where we are mainly testing the time it takes for a client to answer after a request to the Beacon API.

Keep in mind that for now you can either input a file containing urls to query or the tool will generate random numbers (block numbers).
In the random mode, the tool can only generate numbers, so only paths where the input value is a number are supported.

Execution example:

```
python3 queries.py config_queries.ini
```

Before using this tool, please install the following dependencies:

```
pip3 install requests
pip3 install async_timeout
pip3 install numpy

```
or you may install dependencies by:

```
pip3 install -r requirements.txt
```


Config file example:

```
# basic is used for all the tests you are performing below

[BASIC]
NUM_QUERIES = 10 
MAX_RANDOM = 3390009                # random_number between 0 and this value
RANDOM_PATHS_FILE = ./random.csv    # in case you have a file containig the paths you want to query


[SET1]

PORT = 5052                                     # port of the Beacon API
PATH = /eth/v2/beacon/blocks/xyz                # base path to query (replace "/xyz" with the random number)
NAME = lighthouse                               # csv labelling
CSV_FILE_PATH = csv_files/test/test_LH.csv      # where to store csv results file

```
