
SLEEP_TIME=3840 # 10 epochs, let each client run
TWO_EPOCHS=768 # 2 epochs, transition betwee exporting and importing slashing protection
 
# Prysm

echo "Prysm Client"

# Import slashing protection
echo "Prysm: Importing slashing protection..."

# TODO: Import the last slashing protection from the last client executed in the first run
# validator-kl slashing-protection-history export --datadir=/home/ethereum/.pry-geth/kiln/testnet-pry --slashing-protection-export-dir=/home/ethereum/prysm_logs/prysm_slashing_protection/ | tee -a /home/ethereum/prysm_logs/slashing_protection_export.log

# Import validators (already done but simulate we do)
echo "Prysm: Importing validators..."

for d in /home/ethereum/kiln_validators/assigned_data_0_249/secrets/*; do
	final_d=$(basename $d)
	validator-kl accounts import --keys-dir=/home/ethereum/kiln_validators/assigned_data_0_249/keys/$final_d --account-password-file=$d --wallet-dir /home/ethereum/.pry-geth/kiln/testnet-pry --wallet-password-file=/home/ethereum/prysm_logs/wallet_password.txt | tee -a import_log.txt
done

echo "Prysm: Exporting Slashing protection...."

validator-kl slashing-protection-history export --datadir=/home/ethereum/.pry-geth/kiln/testnet-pry --slashing-protection-export-dir=/home/ethereum/prysm_logs/prysm_slashing_protection/ | tee -a /home/ethereum/prysm_logs/slashing_protection_export.log


# Run geth
echo "Prysm: Running Geth...."

sudo systemctl start geth-pry.service

# Run Prysm Beacon node
echo "Prysm: Running Beacon Node...."
sudo systemctl start pry-geth-beacon.service

# Run the Prysm Validator node
echo "Prysm: Running the Validator Node..."
sudo systemctl start pry-geth-validator.service

sleep $SLEEP_TIME


# Stop the validator node
echo "Prysm: Stopping the Validator Node..."
sudo systemctl stop pry-geth-validator.service

# Stop Prysm Beacon node
echo "Prysm: Stopping the Beacon Node..."
sudo systemctl stop pry-geth-beacon.service

# Stop geth
echo "Prysm: Stopping Geth..."
sudo systemctl stop geth-pry.service


# Export slashing protection
echo "Prysm: Exporting Slashing protection..."
validator-kl slashing-protection-history export --datadir=/home/ethereum/.pry-geth/kiln/testnet-pry --slashing-protection-export-dir=/home/ethereum/prysm_logs/prysm_slashing_protection/ | tee -a /home/ethereum/prysm_logs/slashing_protection_export.log

echo "Prysm: Finished. Stopping for 2 epochs..."
sleep $TWO_EPOCHS
# ------------------------------------------------------

# Lighthouse
echo "Lighthouse"
# Import slashing protection
echo "Lighthouse: Importing Slashing Protection..."
lighthouse-kl --network kiln account validator slashing-protection import ../prysm_logs/prysm_slashing_protection/slashing_protection.json --datadir=/home/ethereum/.lh-geth/kiln/testnet-lh | tee -a import.log

# Import validators (already done but simulating we do)
echo "Lighthouse: Importing Validators..."
for d in /home/ethereum/kiln_validators/assigned_data_0_249/secrets/*; do
	final_d=$(basename $d)
        lighthouse-kl --network kiln account validator import --directory /home/ethereum/kiln_validators/assigned_data_0_249/keys/$final_d --datadir=/home/ethereum/.lh-geth/kiln/testnet-lh --password-file $d --reuse-password | tee -a /home/ethereum/lighthouse_logs/import.log
done


# Run geth
echo "Lighthouse: Running Geth..."
sudo systemctl start geth-lh.service

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
sudo systemctl start lh-geth-validator.service

# Stop Lighthosue Beacon node
echo "Lighthouse: Stopping the Beacon Node..."
sudo systemctl start lh-geth-beacon.service

# Stop Geth
echo "Lighthouse: Stopping Geth..."
sudo systemctl start geth-lh.service

# Export Slashing protection

echo "Lighthouse: Exporting Slashing Protection..."
lighthouse-kl account validator slashing-protection export /home/ethereum/lighthouse_logs/lighthouse_slashing_protection.json --datadir=/home/ethereum/.lh-geth/kiln/testnet-lh --network kiln
echo "Lighthouse: finished. Sleeping for 2 epochs..."
sleep $TWO_EPOCHS
# ------------------------------------------------------------------------------

# Nimbus

echo "Nimbus"
# Import slashing protection
echo "Nimbus: Importing the Slahing Protection..."
nimbus_beacon_node-kl slashingdb import /home/ethereum/lighthouse_logs/lighthouse_slashing_protection.json --data-dir=/home/ethereum/.nim-geth/kiln/testnet-nim | tee -a /home/ethereum/nimbus_logs/import.log

# Import validators
echo "Nimbus: Importing Validators..."
for d in /home/ethereum/kiln_validators/assigned_data_0_249/secrets/*; do
	final_d=$(basename $d)
	# password=`cat $d`
	# echo "$password"
	echo "$password" | tee | nimbus_beacon_node-kl deposits import --data-dir=/home/ethereum/.nim-geth/kiln/testnet-nim "/home/ethereum/kiln_validators/assigned_data_0_249/keys/$final_d"
done


# Run Geth
echo "Nimbus: Running Geth..."
sudo systemctl start geth-nim.service

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
sudo systemctl stop geth-nim.service


# Export Slashing protection
echo "Nimbus: Exporting Slashing Protection..."
nimbus_beacon_node-kl slashingdb export /home/ethereum/nimbus_logs/slashing_database.json --data-dir=/home/ethereum/.nim-geth/kiln/testnet-nim | tee -a /home/ethereum/nimbus_logs/slashing_logs.log

echo "Nimbus: finished. Waiting 2 epochs..."
sleep $TWO_EPOCHS

# -----------------------------------------------------------------------

# Teku
echo "Teku"
# Import Slashing protection
echo "Teku: Importing Slashing Protection..."
teku-kl slashing-protection import --from /home/ethereum/nimbus_logs/slashing_database.json | tee -a /home/ethereum/teku_logs/slashing_import.log

# Import validators (already done, already copied keys and secrets)


# Run Geth
echo "Teku: Running Geth..."
sudo systemctl start geth-teku.service

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
sudo systemctl stop geth-teku.service


# Export Slashing Protection
echo "Teku: Exporting Slashing Protection..."
teku-kl slashing-protection export --data-path /home/ethereum/.teku-geth/kiln/datadir-teku --to /home/ethereum/teku_logs/slashing_db.json | tee -a /home/ethereum/teku_logs/slashing.log

echo "Teku: finished. Waiting for 2 epochs..."
sleep $TWO_EPOCHS



# ----------------------------------------------------------------


# Grandine



# Run Geth

sudo systemctl start geth

# Run Grandine

sudo systemctl start grandine

sleep $SLEEP_TIME

# Stop Grandine

sudo systemctl stop grandine

# Stop Geth

sudo systemctl stop geth

