from swiftapi import SwiftClient
from datetime import datetime

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
    elif command == "clear-data":
        client.clear_data()
    elif command.startswith("add-data"):
        client.add_data(int(command.split()[1]))
    elif command == "data-movement":
        client.get_data_movement_logs()