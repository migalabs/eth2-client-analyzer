

import configparser
import csv
from datetime import datetime, timedelta
import os
# seed the pseudorand number generator
from random import seed
import random as rand
import sys
import traceback

import requests
from async_timeout import timeout
import numpy as np
from urllib3 import HTTPConnectionPool

LOCALHOST = "http://localhost:"
MAX_VALIDATOR = 21063
TIMEOUT = 10
TAB_SIZE = 10

class RandomPaths:

    def __init__(self, i_config):
        
        config_obj = i_config
        
        self.num_of_queries = int(config_obj.get("BASIC", "NUM_QUERIES"))
        self.max_rand = int(config_obj.get("BASIC", "MAX_RANDOM")) # generate random numbers between 0 and this
        
        self.result = []

class BlockPath(RandomPaths):
    pass

class StatePath(RandomPaths):
    def __init__(self, i_config):
        super().__init__(i_config)
        self.random_block_numbers = []
        self.random_val_index = []
    
    def execute(self, i_port):
        for _ in range(0, self.num_of_queries, 1):
            random_block = np.random.randint(0, self.max_rand)
            random_val = np.random.randint(0, MAX_VALIDATOR)
            self.random_block_numbers.append(random_block)
            self.random_val_index.append(random_val)


            full_path = LOCALHOST + str(i_port) + "/eth/v1/beacon/states/" + str(random_block) + "/validator_balances?id=" + str(random_val)
            self.result.append(full_path)


# rand_numbers will be the same length as num_of_queries
# this function basically performs as many requests as random numbers are given
def do_random_requests(i_name, i_rand_paths):
    result = []

    # fill the result matrix with basic data
    for i in range(0, len(i_rand_paths), 1):
        result.append([])
        result[-1].append(i_name)
        result[-1].append(str(datetime.now()))
        result[-1].append(i_rand_paths[i])

    # measure whole time
    first_whole_timestamp = datetime.now()

    for idx in range(0, len(i_rand_paths), 1):
        try:
            # each query measure time lapse separately as well
            first_timestamp = datetime.now()
            response = requests.get(result[idx][2], timeout = TIMEOUT) # in each line, position 2 is the url
            second_timestamp = datetime.now()
            delta = (second_timestamp - first_timestamp)
            delta = delta / timedelta(milliseconds=1) #individual time lapse
            result[idx].append(response.elapsed.total_seconds()*1000) # time lapse python package provides
            result[idx].append(delta)
            result[idx].append(int(response.status_code))
            
        except requests.exceptions.ReadTimeout as e: # probably a timeout
            result[idx].append(TIMEOUT * 1000) # time lapse python package provides
            result[idx].append(TIMEOUT * 1000)
            result[idx].append(408)

    # calculate full time lapse and avergae
    second_whole_timestamp = datetime.now()
    whole_delta = second_whole_timestamp - first_whole_timestamp # delta
    whole_delta = whole_delta / timedelta(milliseconds=1) # microseconds
    whole_delta = whole_delta / len(i_rand_paths) # average
    print("Start time:                        ", str(first_whole_timestamp))
    print("Finish time:                       ", str(second_whole_timestamp))
    print("Average Delta (Finish - Start):    ", f"{whole_delta:<10}",  "MILISECONDS")
    
    return result



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

    section_base_name = "SET"
    section_number = 1

    section_name = str(section_base_name + str(section_number))

    num_of_queries = int(config_obj.get("BASIC", "NUM_QUERIES"))
    max_rand = int(config_obj.get("BASIC", "MAX_RANDOM")) # generate random numbers between 0 and this
    rand_paths = []

    while config_obj.has_section(section_name): # for each section of type SETx

        


        i_port = int(config_obj.get(section_name, "PORT"))
        i_mode = str(config_obj.get(section_name, "MODE"))
        i_name = str(config_obj.get(section_name, "NAME"))
        i_csv_path = str(config_obj.get(section_name, "CSV_FILE_PATH"))


        # read file containing ranom paths in case it exists
        if config_obj.get(section_name, "RANDOM_PATHS_FILE") != "":
            random_paths_file = str(config_obj.get(section_name, "RANDOM_PATHS_FILE"))
            with open(random_paths_file, newline='') as csvfile:
                reader = csv.reader(csvfile)
                rand_paths = [line[0] for line in reader]
        else:
            random_obj = StatePath(config_obj)
            random_obj.execute(i_port)
            rand_paths = random_obj.result

        print(i_name)
        print("Number of queries:", num_of_queries)

        result = np.array(do_random_requests(i_name, rand_paths))

        #Calculate stats
        min_value_index = result[:,3].astype(np.float64).argmin()
        max_value_index = result[:,3].astype(np.float64).argmax()
        req_mean = "{:.2f}".format(result[:,3].astype(np.float64).mean())
        row_delta_mean = "{:.2f}".format(result[:,4].astype(np.float64).mean())
        best_score = "{:.2f}".format(result[min_value_index][4].astype(np.float64))
        worst_score = "{:.2f}".format(result[max_value_index][4].astype(np.float64))


        print("Average Req:                       ", f"{req_mean:<10}", "MILISECONDS")
        print("Average Row Delta:                 ", f"{row_delta_mean:<10}", "MILISECONDS")
        print("Best score:                        ", f"{best_score:<10}",   "MILISECONDS", result[min_value_index][2])
        print("Worst score:                       ", f"{worst_score:<10}",   "MILISECONDS", result[max_value_index][2])
        print("200 score:                         ", result[:,5].tolist().count("200") / num_of_queries * 100, "%")

        result = np.insert(result, 0, np.array(["NAME", "TIMESTAMP", "PATH", "REQ_TIME", "DELTA_TIME", "RESPONSE_CODE"]), 0)
        np.savetxt(i_csv_path, result, delimiter=',', fmt='%s')
        

        np.savetxt("./random1.csv", rand_paths, delimiter=',', fmt='%s')

        section_number = section_number + 1
        section_name = str(section_base_name + str(section_number))


if __name__ == "__main__":
    main()