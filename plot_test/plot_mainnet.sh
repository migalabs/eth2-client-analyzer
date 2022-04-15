# python3 plot_data.py configs/mainnet/python/config_plot_all_cpu.ini data/default_mainnet2/*sample.csv data/default_mainnet2/NE_*.csv



# mainnet

## cpu
echo "Print CPU"
python3 plot_data.py configs/mainnet/python/config_plot_all_cpu.ini data/default_mainnet2/*sample.csv
python3 plot_data.py configs/mainnet/NE/config_plot_all_cpu.ini data/default_mainnet2/NE_*.csv
python3 plot_data.py configs/mainnet/PvsNE/config_plot_all_cpu.ini data/default_mainnet2/*sample.csv data/default_mainnet2/NE_*.csv



## mem
echo "Print Mem"
python3 plot_data.py configs/mainnet/python/config_plot_all_mem.ini data/default_mainnet2/*sample.csv
python3 plot_data.py configs/mainnet/NE/config_plot_all_mem.ini data/default_mainnet2/NE_*.csv
python3 plot_data.py configs/mainnet/PvsNE/config_plot_all_mem.ini data/default_mainnet2/*sample.csv data/default_mainnet2/NE_*.csv



## disk
echo "Print disk"
python3 plot_data.py configs/mainnet/python/config_plot_all_disk.ini data/default_mainnet2/*sample.csv


# netReceived
echo "Print NetReceived"
python3 plot_data.py configs/mainnet/python/config_plot_all_netReceived.ini data/default_mainnet2/*sample.csv
python3 plot_data.py configs/mainnet/NE/config_plot_all_netReceived.ini data/default_mainnet2/NE_*.csv
python3 plot_data.py configs/mainnet/PvsNE/config_plot_all_netReceived.ini data/default_mainnet2/*sample.csv data/default_mainnet2/NE_*.csv


# netSent 
echo "Print netSent"
python3 plot_data.py configs/mainnet/python/config_plot_all_netSent.ini data/default_mainnet2/*sample.csv
python3 plot_data.py configs/mainnet/NE/config_plot_all_netSent.ini data/default_mainnet2/NE_*.csv
python3 plot_data.py configs/mainnet/PvsNE/config_plot_all_netSent.ini data/default_mainnet2/*sample.csv data/default_mainnet2/NE_*.csv


# peers
echo "Print peers"
python3 plot_data.py configs/mainnet/python/config_plot_all_peers.ini data/default_mainnet2/*sample.csv
python3 plot_data.py configs/mainnet/NE/config_plot_all_peers.ini data/default_mainnet2/NE_*.csv
python3 plot_data.py configs/mainnet/PvsNE/config_plot_all_peers.ini data/default_mainnet2/*sample.csv data/default_mainnet2/NE_*.csv


# slot 
echo "Print Slot"
python3 plot_data.py configs/mainnet/python/config_plot_all_slot.ini data/default_mainnet2/*sample.csv
python3 plot_data.py configs/mainnet/NE/config_plot_all_slot.ini data/default_mainnet2/NE_*.csv
python3 plot_data.py configs/mainnet/PvsNE/config_plot_all_slot.ini data/default_mainnet2/*sample.csv data/default_mainnet2/NE_*.csv