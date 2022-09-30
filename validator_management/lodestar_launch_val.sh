#!/bin/bash
cd /home/ethereum/lodestar_logs/lodestar
source /home/ethereum/.bashrc
./lodestar validator --network kiln --rootDir ../lodestar-beacondata
