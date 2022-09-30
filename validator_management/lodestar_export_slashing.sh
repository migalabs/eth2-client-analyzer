#!/bin/bash
cd /home/ethereum/lodestar_logs/lodestar
source /home/ethereum/.bashrc
/home/ethereum/lodestar_logs/lodestar/lodestar validator slashing-protection export --network kiln --file /home/ethereum/lodestar_logs/slashing_protection.json --rootDir /home/ethereum/lodestar_logs/lodestar-beacondata/
