#!/bin/bash

# set -e

SLEEP_TIME=3840 # 10 epochs, let each client run
TWO_EPOCHS=768 # 2 epochs, transition between stopping validators in one client and running them in the next client
TWO_EPOCHS=1 # now lets try not waiting
while true
do
echo "Sleeping 768 for security..."
sleep 768
# Prysm

echo "Prysm Client"

# Import slashing protection
echo "Prysm: Importing slashing protection..."

# TODO: Import the last slashing protection from the last client executed in the first run

validator-kl slashing-protection-history import --datadir=/home/ethereum/.pry-geth/kiln/testnet-pry --slashing-protection-json-file=/home/ethereum/lodestar_logs/slashing_protection.json

# Import validators (already done)

# Import validators (already done but simulate we do)
# echo "Prysm: Importing validators..."

# for d in /home/ethereum/kiln_validators/assigned_data_0_249/secrets/*; do
# 	final_d=$(basename $d)
# 	validator-kl accounts import --keys-dir=/home/ethereum/kiln_validators/assigned_data_0_249/keys/$final_d --account-password-file=$d --wallet-dir /home/ethereum/.pry-geth/kiln/testnet-pry --wallet-password-file=/home/ethereum/prysm_logs/wallet_password.txt | tee -a import_log.txt
# done

# Run geth
echo "Prysm: Running Geth...."

# sudo systemctl start geth-pry.service

# Run Prysm Beacon node
echo "Prysm: Running Beacon Node...."
sudo systemctl start pry-geth-beacon.service

# Run the Prysm Validator node
echo "Prysm: Running the Validator Node..."
sudo systemctl start pry-geth-validator.service

echo "Prysm: Sleeping to let the client run"
sleep $SLEEP_TIME


# Stop the validator node
echo "Prysm: Stopping the Validator Node..."
sudo systemctl stop pry-geth-validator.service

# Stop Prysm Beacon node
echo "Prysm: Stopping the Beacon Node..."
sudo systemctl stop pry-geth-beacon.service

# Stop geth
echo "Prysm: Stopping Geth..."
# sudo systemctl stop geth-pry.service


# Export slashing protection
rm /home/ethereum/prysm_logs/prysm_slashing_protection/*
echo "Prysm: Exporting Slashing protection..."
validator-kl slashing-protection-history export --datadir=/home/ethereum/.pry-geth/kiln/testnet-pry --slashing-protection-export-dir=/home/ethereum/prysm_logs/prysm_slashing_protection/

echo "Prysm: Finished. Stopping for 2 epochs..."
sleep $TWO_EPOCHS

# ------------------------------------------------------

# Lighthouse
echo "Lighthouse"
# Import slashing protection
echo "Lighthouse: Importing Slashing Protection..."
lighthouse-kl --network kiln account validator slashing-protection import /home/ethereum/prysm_logs/prysm_slashing_protection/slashing_protection.json --datadir=/home/ethereum/.lh-geth/kiln/testnet-lh

# Import validators (already done but simulating we do)
# echo "Lighthouse: Importing Validators..."
# for d in /home/ethereum/kiln_validators/assigned_data_0_249/secrets/*; do
# 	final_d=$(basename $d)
#         lighthouse-kl --network kiln account validator import --directory /home/ethereum/kiln_validators/assigned_data_0_249/keys/$final_d --datadir=/home/ethereum/.lh-geth/kiln/testnet-lh --password-file $d --reuse-password | tee -a /home/ethereum/lighthouse_logs/import.log
# done


# Run geth
echo "Lighthouse: Running Geth..."
# sudo systemctl start geth-lh.service

# Run Lighthouse Beacon node
echo "Lighthouse: Running the Beacon Node..."
sudo systemctl start lh-geth-beacon.service

# Run Lighthouse Validator node
echo "Lighthouse: Running the Validator Node"
sudo systemctl start lh-geth-validator.service
echo "Lighthouse: Sleeping for 10 epochs"
sleep $SLEEP_TIME


# Stop Lighthouse Validator node
echo "Lighthouse: Stopping the Validator Node..."
sudo systemctl stop lh-geth-validator.service

# Stop Lighthosue Beacon node
echo "Lighthouse: Stopping the Beacon Node..."
sudo systemctl stop lh-geth-beacon.service

# Stop Geth
echo "Lighthouse: Stopping Geth..."
# sudo systemctl stop geth-lh.service

# Export Slashing protection
rm /home/ethereum/lighthouse_logs/slashing_protection.json
echo "Lighthouse: Exporting Slashing Protection..."
lighthouse-kl account validator slashing-protection export /home/ethereum/lighthouse_logs/slashing_protection.json --datadir=/home/ethereum/.lh-geth/kiln/testnet-lh --network kiln
echo "Lighthouse: finished. Sleeping for 2 epochs..."
sleep $TWO_EPOCHS
# ------------------------------------------------------------------------------

# Nimbus

echo "Nimbus"
# Import slashing protection
echo "Nimbus: Importing the Slahing Protection..."
/home/ethereum/nimbus-eth2_Linux_arm64v8_22.6.1_2444e994/build/nimbus_beacon_node slashingdb import /home/ethereum/lighthouse_logs/slashing_protection.json --data-dir=/home/ethereum/.nim-geth/kiln/testnet-nim

# Import validators
# echo "Nimbus: Importing Validators..."
# for d in /home/ethereum/kiln_validators/assigned_data_0_249/secrets/*; do
# 	final_d=$(basename $d)
# 	# password=`cat $d`
# 	# echo "$password"
#	echo "$password" | tee | nimbus_beacon_node-kl deposits import --data-dir=/home/ethereum/.nim-geth/kiln/testnet-nim "/home/ethereum/kiln_validators/assigned_data_0_249/keys/$final_d"
# done


# Run Geth
echo "Nimbus: Running Geth..."
# sudo systemctl start geth-nim.service

# Run Nimbus
echo "Nimbus: Running the Beacon + Validator Node"
sudo systemctl start nim-geth.service

echo "Nimbus: Leaving it run for 10 epochs..."
sleep $SLEEP_TIME


# Stop Nimbus
echo "Nimbus: Stopping the Beacon + Validator Node..."
sudo systemctl stop nim-geth.service

# Stop Geth
echo "Nimbus: Stopping Geth..."
# sudo systemctl stop geth-nim.service


# Export Slashing protection
rm /home/ethereum/nimbus_logs/slashing_protection.json
echo "Nimbus: Exporting Slashing Protection..."
/home/ethereum/nimbus-eth2_Linux_arm64v8_22.6.1_2444e994/build/nimbus_beacon_node slashingdb export /home/ethereum/nimbus_logs/slashing_protection.json --data-dir=/home/ethereum/.nim-geth/kiln/testnet-nim

echo "Nimbus: finished. Waiting 2 epochs..."
sleep $TWO_EPOCHS

# -----------------------------------------------------------------------

# Teku
echo "Teku"
# Import Slashing protection
echo "Teku: Importing Slashing Protection..."
teku-kl slashing-protection import --from /home/ethereum/nimbus_logs/slashing_protection.json --data-path /home/ethereum/.teku-geth/kiln/datadir-teku

# Import validators (already done, already copied keys and secrets)


# Run Geth
echo "Teku: Running Geth..."
# sudo systemctl start geth-teku.service

# Run Teku
echo "Teku: Running the Beacon + Validator Node..."
sudo systemctl start teku-geth.service

echo "Teku: Leaving it run for 10 epochs..."
sleep $SLEEP_TIME

# Stop Teku
echo "Teku: Stopping Beacon + Validator Node..."
sudo systemctl stop teku-geth.service


# Stop Geth
echo "Teku: Stopping Geth..."
# sudo systemctl stop geth-teku.service


# Export Slashing Protection
rm /home/ethereum/teku_logs/slashing_protection.json
echo "Teku: Exporting Slashing Protection..."
teku-kl slashing-protection export --data-path /home/ethereum/.teku-geth/kiln/datadir-teku --to /home/ethereum/teku_logs/slashing_protection.json

echo "Teku: finished. Waiting for 2 epochs..."
sleep $TWO_EPOCHS


# ----------------------------------------------------------------


# Grandine

echo "Grandine"

cd /home/ethereum/grandine_logs

# Import Slashing protection

echo "Grandine: Importing slashing protection..."

./grandine-0.2.0_beta3_arm64 --network kiln --data-dir /home/ethereum/.grandine interchange import /home/ethereum/teku_logs/slashing_protection.json

# Import validators (already imported)

# echo "Grandine: Importing validators... (already imported)"


# Run Geth

echo "Grandine: Running Geth..."

# sudo systemctl start geth

# Run Grandine

echo "Grandine: Running Client"

sudo systemctl start grandine

echo "Grandine: Letting the client run..."

sleep $SLEEP_TIME

# Stop Grandine

echo "Grandine: Stopping Client..."

sudo systemctl stop grandine

# (we stop geth as Lodestar will use its own geth docker)

# Export Slashing protection
rm /home/ethereum/grandine_logs/slashing_protection.json
echo "Exporting Slashing Protection..."

./grandine-0.2.0_beta3_arm64 --network kiln interchange export /home/ethereum/grandine_logs/slashing_protection.json
sleep $TWO_EPOCHS
# -----------------------------------------------------------------------------

# Lodestar

echo "Lodestar"

echo "Lodestar: Moving to Lodestar folder..."

# Run Lodestar Beacon Node

echo "Lodestar: Running whole setup without validators..."

sudo systemctl start lodestar

# Import Slashing protection

echo "Lodestar: Importing Slashing protection..."

# /home/ethereum/lodestar_logs/lodestar/lodestar validator slashing-protection import --network kiln --file /home/ethereum/grandine_logs/slashing_protection.json --rootDir /home/ethereum/lodestar_logs/lodestar-beacondata/
sleep 100

su - ethereum -c "/home/ethereum/lodestar_logs/lodestar/import_slashing.sh"
# Importing validators (already imported)

# Running validators

sudo systemctl start lodestar_val

echo "Lodestar: Let the client run..."

sleep $SLEEP_TIME

# Stop the Lodestar setup

echo "Lodestar: Stopping validators..."

sudo systemctl stop lodestar_val

# Export Slashing Protection

echo "Lodestar: Exporting Slashing protection..."

rm /home/ethereum/lodestar_logs/slashing_protection.json

# /home/ethereum/lodestar_logs/lodestar/lodestar validator slashing-protection export --network kiln --file /home/ethereum/lodestar_logs/slashing_protection.json --rootDir /home/ethereum/lodestar_logs/lodestar-beacondata/
su - ethereum -c "/home/ethereum/lodestar_logs/lodestar/export_slashing.sh"
echo "Lodestar: Stopping Beacon Node..."
sudo systemctl stop lodestar
done
