#!/bin/bash
cd /home/ethereum/lodestar_logs/lodestar
source /home/ethereum/.bashrc
./lodestar beacon --rootDir="../lodestar-beacondata" --network kiln --eth1.enabled=true --execution.urls="http://127.0.0.1:8551" --network.connectToDiscv5Bootnodes --network.discv5.enabled=true --jwt-secret /etc/ethereum/kiln/jwtsecret --network.discv5.bootEnrs="enr:-Iq4QMCTfIMXnow27baRUb35Q8iiFHSIDBJh6hQM5Axohhf4b6Kr_cOCu0htQ5WvVqKvFgY28893DHAg8gnBAXsAVqmGAX53x8JggmlkgnY0gmlwhLKAlv6Jc2VjcDI1NmsxoQK6S-Cii_KmfFdUJL2TANL3ksaKUnNXvTCv1tLwXs0QgIN1ZHCCIyk" --weakSubjectivitySyncLatest --weakSubjectivityServerUrl https://lodestar-kiln.chainsafe.io
