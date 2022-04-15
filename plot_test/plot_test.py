
from plot_data import find_nearest_spots, import_from_file


def test_find_spots():

    array1 = [0,1,2,3]
    array2 = [0,10,20,30,40]


    result = find_nearest_spots(array1, array2)

    assert result[0] == 0
    assert result[-1] == 0


    array1 = [0,1,2,3]
    array2 = [0,1,2,7,40]

    result = find_nearest_spots(array1, array2)

    assert result[0] == 0
    assert result[1] == 1
    assert result[2] == 2
    assert result[3] == 2

def test_csv_import():
    file = "./test.csv"
    clients_array = []
    import_from_file(file, clients_array)

    # client without NE_
    assert float("{:.2f}".format(clients_array[0].data[4][0])) == float("{:.2f}".format(2365.538304 * 1000000 / (1024 * 1024)))
    assert float("{:.2f}".format(clients_array[0].data[5][0])) == float("{:.2f}".format(7.95132500003103 * 1000000 / (1024 * 1024 * 1024)))
    assert float("{:.2f}".format(clients_array[0].data[6][0])) == float("{:.2f}".format(11.2114160000001 * 1000000 / (1024 * 1024 * 1024)))
    
    # client with NE_
    assert float("{:.2f}".format(clients_array[1].data[4][0])) == float("{:.2f}".format(2365.538304))
    assert float("{:.2f}".format(clients_array[1].data[5][0])) == float("{:.2f}".format(7.95132500003103 / 1024))
    assert float("{:.2f}".format(clients_array[1].data[6][0])) == float("{:.2f}".format(11.2114160000001 / 1024))

if __name__ == "__main__":
    test_find_spots()
    test_csv_import()
    print("Everything passed")