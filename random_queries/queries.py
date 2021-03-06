

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
TIMEOUT = 50
TAB_SIZE = 10

summary = ""

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
    global summary
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
    summary = summary + "\nStart time:                        " + str(first_whole_timestamp) + "\n" + \
    "Finish time:                       " + str(second_whole_timestamp) + "\n" + \
    "Average Delta (Finish - Start):    " + str(f"{whole_delta:<10}") + "MILISECONDS"
    
    return result



def main():
    global summary
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

        summary = summary + i_name + "\n" + "Number of queries: " + str(num_of_queries)

        result = np.array(do_random_requests(i_name, rand_paths))

        #Calculate stats
        min_value_index = result[:,3].astype(np.float64).argmin()
        max_value_index = result[:,3].astype(np.float64).argmax()
        req_mean = "{:.2f}".format(result[:,3].astype(np.float64).mean())
        row_delta_mean = "{:.2f}".format(result[:,4].astype(np.float64).mean())
        best_score = "{:.2f}".format(result[min_value_index][4].astype(np.float64))
        worst_score = "{:.2f}".format(result[max_value_index][4].astype(np.float64))


        summary = summary + "\nAverage Req:                       " + str(f"{req_mean:<10}") + "MILISECONDS " + "\n" + \
        "Average Row Delta:                 " +  str(f"{row_delta_mean:<10}") + "MILISECONDS " + "\n" + \
        "Best score:                        " +  str(f"{best_score:<10}") +   "MILISECONDS " + result[min_value_index][2] + "\n" + \
        "Worst score:                       " +  str(f"{worst_score:<10}") +   "MILISECONDS " + result[max_value_index][2] + "\n" + \
        "200 score:                         " +  str(result[:,5].tolist().count("200") / num_of_queries * 100) + "%"

        result = np.insert(result, 0, np.array(["NAME", "TIMESTAMP", "PATH", "REQ_TIME", "DELTA_TIME", "RESPONSE_CODE"]), 0)
        
        
        mydir = os.path.join(os.getcwd(),datetime.now().strftime('%Y%m%d_%H%M'))
        os.makedirs(mydir)
        csv_path = os.path.join(mydir, 'test_' + i_name + str(len(rand_paths)) + '.csv')
        np.savetxt(csv_path, result, delimiter=',', fmt='%s')
        summary_path = os.path.join(mydir, 'summary_' + i_name + str(len(rand_paths)) + '.txt')
        text_file = open(summary_path, "w")
        n = text_file.write(summary)
        text_file.close()
        
        random_path = os.path.join(mydir, "random" + str(num_of_queries) + ".csv")
        np.savetxt(random_path, rand_paths, delimiter=',', fmt='%s')

        config_path = os.path.join(mydir, "config_" + i_name +  str(num_of_queries) + ".ini")
        os.system('cp ' + config_file + ' ' + config_path)

        section_number = section_number + 1
        section_name = str(section_base_name + str(section_number))


if __name__ == "__main__":
    main()