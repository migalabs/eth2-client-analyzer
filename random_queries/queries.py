

import configparser
import csv
from datetime import datetime, timedelta
import os
# seed the pseudorand number generator
from random import seed
import random as rand
import sys

import requests
from async_timeout import timeout
import numpy as np

LOCALHOST = "http://localhost:"
TIMEOUT = 10

# rand_numbers will be the same length as num_of_queries
# this function basically performs as many requests as random numbers are given
def do_random_requests(i_num_of_queries, i_name, i_rand_paths):
    result = []

    # fill the result matrix with basic data
    for i in range(0, i_num_of_queries, 1):
        result.append([])
        result[-1].append(i_name)
        result[-1].append(str(datetime.now()))
        result[-1].append(i_rand_paths[i])

    # measure whole time
    first_whole_timestamp = datetime.now()

    for idx in range(0, i_num_of_queries, 1):
        
        # each query measure time lapse separately as well
        first_timestamp = datetime.now()
        response = requests.get(result[idx][2], timeout = TIMEOUT) # in each line, position 2 is the url
        second_timestamp = datetime.now()
        delta = (second_timestamp - first_timestamp)
        delta = delta / timedelta(milliseconds=1) #individual time lapse
        result[idx].append(response.elapsed.microseconds/1000) # time lapse python package provides
        result[idx].append(delta)

    # calculate full time lapse and avergae
    second_whole_timestamp = datetime.now()
    whole_delta = second_whole_timestamp - first_whole_timestamp # delta
    whole_delta = whole_delta / timedelta(milliseconds=1) # microseconds
    whole_delta = whole_delta / i_num_of_queries # average
    print("Start time:                        ", str(first_whole_timestamp))
    print("Finish time:                       ", str(second_whole_timestamp))
    print("Average Delta (Finish - Start):    ", whole_delta, "  MILISECONDS")
    
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

    rand_numbers = []
    rand_paths = []
    
    # read file containing ranom paths in case it exists
    if config_obj.get("BASIC", "RANDOM_PATHS_FILE") != "":
        random_paths_file = str(config_obj.get("BASIC", "RANDOM_PATHS_FILE"))
        with open(random_paths_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            rand_paths = [line[0] for line in reader]

    for _ in range(0, num_of_queries, 1):
        rand_numbers.append(np.random.randint(0, max_rand))

    while config_obj.has_section(section_name): # for each section of type SETx

        i_port = int(config_obj.get(section_name, "PORT"))
        i_path = str(config_obj.get(section_name, "PATH"))
        i_name = str(config_obj.get(section_name, "NAME"))
        i_csv_path = str(config_obj.get(section_name, "CSV_FILE_PATH"))

        print(i_name)
        print("Number of queries:", num_of_queries)

        # in case a file containing paths to query, do not generate array of random numbers
        if len(rand_paths) == 0:
            # we did not receive any path file
            base_path = str(LOCALHOST) + str(i_port) + str(i_path)
            rand_paths = [base_path.replace("/xyz", "/"+str(x)) for x in rand_numbers] # generate the rand urls


        result = np.array(do_random_requests(num_of_queries, i_name, rand_paths))

        #Calculate stats
        min_value_index = result[:,3].astype(np.float64).argmin()
        max_value_index = result[:,3].astype(np.float64).argmax()
        print("Average Req:                       ", result[:,3].astype(np.float64).mean(), "  MILISECONDS")
        print("Average Row Delta:                 ", result[:,4].astype(np.float64).mean(), "  MILISECONDS")
        print("Best score:                        ", result[min_value_index][3],   "  MILISECONDS", result[min_value_index][2])
        print("Worst score:                       ", result[max_value_index][3],   "  MILISECONDS", result[max_value_index][2])


        np.savetxt(i_csv_path, result, delimiter=',', fmt='%s')

        # if there was no random paths file, we now save the generated one
        if config_obj.get("BASIC", "RANDOM_PATHS_FILE") != "":
            np.savetxt("./random.csv", rand_paths, delimiter=',', fmt='%s')

        section_number = section_number + 1
        section_name = str(section_base_name + str(section_number))


if __name__ == "__main__":
    main()