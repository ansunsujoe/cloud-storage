from swiftapi import SwiftClient

# Initialization of client
client = SwiftClient()

# Ask for command input
while True:
    print("swish> ", end="")
    command = input()

    # Command conditions
    if command == "datacount":
        client.datacount()
    elif command == "dataloc":
        client.dataloc()
    elif command == "restart":
        client.restart_nodes()
    elif command == "build-ring":
        client.create_ring()
    elif command == "clear-data":
        client.clear_data()
    elif command == "init":
        client.initconfig()
    elif command == "force-clear-data":
        client.force_clear_data()
    elif command.startswith("add-data"):
        client.add_data(int(command.split()[1]))
    elif command.startswith("generate-data"):
        client.add_data_container(int(command.split()[1]))
    elif command.startswith("set-weight"):
        arr = command.split()
        client.set_weight(arr[1], arr[2])
    elif command == "data-movement":
        client.get_data_movement_stats_v2()
    elif command == "data-movement-logs":
        client.get_data_movement_logs()
    elif command == "read-req":
        client.generate_read_req()
    elif command == "read-stats":
        client.get_read_req_stats()
    elif command == "write-req":
        client.generate_write_req()
    elif command == "write-stats":
        client.get_write_req_stats()
    elif command == "shutdown":
        client.shutdown_nodes()
    elif command == "startup":
        client.startup_nodes()
    elif command == "print-ring":
        client.print_cluster_info()
    elif command == "test":
        client.test()
    elif command == "":
        continue
    elif command == "exit":
        break