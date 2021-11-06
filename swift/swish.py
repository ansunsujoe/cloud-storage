from swiftapi import SwiftClient
import time

# Initialization of client
client = SwiftClient()

# Ask for command input
while True:
    print("swish> ", end="")
    command = input()

    # Command conditions
    if command == "datacount":
        client.view_data()
    if command == "restart":
        client.restart_nodes()