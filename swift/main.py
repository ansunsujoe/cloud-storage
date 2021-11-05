from swiftapi import SwiftClient

client = SwiftClient()
client.clear_data()
client.restart_nodes()
client.add_data(200)