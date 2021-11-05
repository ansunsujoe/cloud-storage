from swiftapi import SwiftClient
import time

client = SwiftClient()
client.clear_data()
client.restart_nodes()
client.add_data(50)
time.sleep(2)
client.view_data()