
SLEEP_TIME=3840 # 10 epochs, let each client run
TWO_EPOCHS=768 # 2 epochs, transition betwee exporting and importing slashing protection
 
# Prysm

# Import slashing protection
validator-kl slashing-protection-history export --datadir=/home/ethereum/.pry-geth/kiln/testnet-pry --slashing-protection-export-dir=/home/ethereum/prysm_logs/prysm_slashing_protection/ | tee -a /home/ethereum/prysm_logs/slashing_protection_export.log

# Import validators (already done but simulate we do)

for d in /home/ethereum/kiln_validators/assigned_data_0_249/secrets/*; do
	final_d=$(basename $d)
	validator-kl accounts import --keys-dir=/home/ethereum/kiln_validators/assigned_data_0_249/keys/$final_d --account-password-file=$d --wallet-dir /home/ethereum/.pry-geth/kiln/testnet-pry --wallet-password-file=/home/ethereum/prysm_logs/wallet_password.txt | tee -a import_log.txt
done


# Run geth

sudo systemctl start geth-pry.service

# Run Prysm Beacon node

sudo systemctl start pry-geth-beacon.service

# Run the validator node

sudo systemctl start pry-geth-validator.service

sleep $SLEEP_TIME


# Stop the validator node

sudo systemctl stop pry-geth-validator.service

# Stop Prysm Beacon node

sudo systemctl stop pry-geth-beacon.service

# Stop geth

sudo systemctl stop geth-pry.service


# Export slashing protection

validator-kl slashing-protection-history export --datadir=/home/ethereum/.pry-geth/kiln/testnet-pry --slashing-protection-export-dir=/home/ethereum/prysm_logs/prysm_slashing_protection/ | tee -a /home/ethereum/prysm_logs/slashing_protection_export.log

sleep $TWO_EPOCHS
# ------------------------------------------------------

# Lighthouse

# Import slashing protection

lighthouse-kl --network kiln account validator slashing-protection import ../prysm_logs/prysm_slashing_protection/slashing_protection.json --datadir=/home/ethereum/.lh-geth/kiln/testnet-lh | tee -a import.log

# Import validators (already done but simulating we do)

for d in /home/ethereum/kiln_validators/assigned_data_0_249/secrets/*; do
	final_d=$(basename $d)
        lighthouse-kl --network kiln account validator import --directory /home/ethereum/kiln_validators/assigned_data_0_249/keys/$final_d --datadir=/home/ethereum/.lh-geth/kiln/testnet-lh --password-file $d --reuse-password | tee -a /home/ethereum/lighthouse_logs/import.log
done


# Run geth

sudo systemctl start geth-lh.service

# Run Lighthouse Beacon node

sudo systemctl start lh-geth-beacon.service

# Run Lighthouse Validator node

sudo systemctl start lh-geth-validator.service

sleep $SLEEP_TIME


# Stop Lighthouse Validator node

sudo systemctl start lh-geth-validator.service

# Stop Lighthosue Beacon node

sudo systemctl start lh-geth-beacon.service

# Stop Geth

sudo systemctl start geth-lh.service

# Export Slashing protection


lighthouse-kl account validator slashing-protection export /home/ethereum/lighthouse_logs/lighthouse_slashing_protection.json --datadir=/home/ethereum/.lh-geth/kiln/testnet-lh --network kiln

sleep $TWO_EPOCHS
# ------------------------------------------------------------------------------

# Nimbus

# Import slashing protection

nimbus_beacon_node-kl slashingdb import /home/ethereum/lighthouse_logs/lighthouse_slashing_protection.json --data-dir=/home/ethereum/.nim-geth/kiln/testnet-nim | tee -a /home/ethereum/nimbus_logs/import.log

# Import validators

for d in /home/ethereum/kiln_validators/assigned_data_0_249/secrets/*; do
	final_d=$(basename $d)
	# password=`cat $d`
	# echo "$password"
	echo "$password" | tee | nimbus_beacon_node-kl deposits import --data-dir=/home/ethereum/.nim-geth/kiln/testnet-nim "/home/ethereum/kiln_validators/assigned_data_0_249/keys/$final_d"
done


# Run Geth

sudo systemctl start geth-nim.service

# Run Nimbus

sudo systemctl start nim-geth.service


sleep $SLEEP_TIME


# Stop Nimbus

sudo systemctl stop nim-geth.service

# Stop Geth

sudo systemctl stop geth-nim.service


# Export Slashing protection

nimbus_beacon_node-kl slashingdb export /home/ethereum/nimbus_logs/slashing_database.json --data-dir=/home/ethereum/.nim-geth/kiln/testnet-nim | tee -a /home/ethereum/nimbus_logs/slashing_logs.log


sleep $TWO_EPOCHS

# -----------------------------------------------------------------------

# Teku

# Import Slashing protection

teku-kl slashing-protection import --from /home/ethereum/nimbus_logs/slashing_database.json | tee -a /home/ethereum/teku_logs/slashing_import.log

# Import validators (already done, already copied keys and secrets)


# Run Geth

sudo systemctl start geth-teku.service

# Run Teku

sudo systemctl start teku-geth.service

sleep $SLEEP_TIME

# Stop Teku

sudo systemctl stop teku-geth.service


# Stop Geth

sudo systemctl stop geth-teku.service


# Export Slashing Protection

teku-kl slashing-protection export --data-path /home/ethereum/.teku-geth/kiln/datadir-teku --to /home/ethereum/teku_logs/slashing_db.json | tee -a /home/ethereum/teku_logs/slashing.log

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

