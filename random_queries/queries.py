

import configparser
from datetime import datetime
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

# rande_numbers will be the same length as num_of_queries
def do_replace_requests(i_port, i_path, i_num_of_queries, i_name, i_rand_numbers):
    result = []

    result.append([])
    result[-1].append("NAME")
    result[-1].append("TIMESTAMP")
    result[-1].append("PATH")
    result[-1].append("MICROSECONDS")

    for i in range(0, i_num_of_queries, 1):
        
        result.append([])
        result[-1].append(i_name)
        result[-1].append(datetime.now())
        
        argument = "/" + str(i_rand_numbers[i])
        tmp_path = str(i_path).replace("/xyz", argument)
        url = str(LOCALHOST + str(i_port) + tmp_path)


        response = requests.get(url, timeout = TIMEOUT)
        result[-1].append(tmp_path)
        result[-1].append(response.elapsed.microseconds)
    
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
    max_rand = int(config_obj.get("BASIC", "MAX_RANDOM"))

    rand_numbers = []
    for _ in range(0, num_of_queries, 1):
        rand_numbers.append(np.random.randint(0, max_rand))

    while config_obj.has_section(section_name):

        

        i_port = int(config_obj.get(section_name, "PORT"))
        i_path = str(config_obj.get(section_name, "PATH"))
        i_name = str(config_obj.get(section_name, "NAME"))
        i_csv_path = str(config_obj.get(section_name, "CSV_FILE_PATH"))


        result = np.array(do_replace_requests(i_port, i_path, num_of_queries, i_name, rand_numbers))
        #print(result)
        np.savetxt(i_csv_path, result, delimiter=',', fmt='%s')

        section_number = section_number + 1
        section_name = str(section_base_name + str(section_number))



if __name__ == "__main__":
    main()