# python3 plot_data.py configs/kiln/python/config_plot_all_cpu.ini data/kiln/sample*.csv data/kiln/NE_*.csv



# mainnet

## cpu

python3 plot_data.py configs/kiln/python/config_plot_all_cpu.ini data/kiln/sample*.csv
python3 plot_data.py configs/kiln/NE/config_plot_all_cpu.ini data/kiln/NE_*.csv
python3 plot_data.py configs/kiln/PvsNE/config_plot_all_cpu.ini data/kiln/sample*.csv data/kiln/NE_*.csv



## mem

python3 plot_data.py configs/kiln/python/config_plot_all_mem.ini data/kiln/sample*.csv
python3 plot_data.py configs/kiln/NE/config_plot_all_mem.ini data/kiln/NE_*.csv
python3 plot_data.py configs/kiln/PvsNE/config_plot_all_mem.ini data/kiln/sample*.csv data/kiln/NE_*.csv



## disk

# python3 plot_data.py configs/kiln/python/config_plot_all_disk.ini data/kiln/sample*.csv


# netReceived

python3 plot_data.py configs/kiln/python/config_plot_all_netReceived.ini data/kiln/sample*.csv
python3 plot_data.py configs/kiln/NE/config_plot_all_netReceived.ini data/kiln/NE_*.csv
python3 plot_data.py configs/kiln/PvsNE/config_plot_all_netReceived.ini data/kiln/sample*.csv data/kiln/NE_*.csv


# netSent 
python3 plot_data.py configs/kiln/python/config_plot_all_netSent.ini data/kiln/sample*.csv
python3 plot_data.py configs/kiln/NE/config_plot_all_netSent.ini data/kiln/NE_*.csv
python3 plot_data.py configs/kiln/PvsNE/config_plot_all_netSent.ini data/kiln/sample*.csv data/kiln/NE_*.csv


# peers

python3 plot_data.py configs/kiln/python/config_plot_all_peers.ini data/kiln/sample*.csv
python3 plot_data.py configs/kiln/NE/config_plot_all_peers.ini data/kiln/NE_*.csv
python3 plot_data.py configs/kiln/PvsNE/config_plot_all_peers.ini data/kiln/sample*.csv data/kiln/NE_*.csv