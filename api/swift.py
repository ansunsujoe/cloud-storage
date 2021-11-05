import subprocess
from pathlib import Path

class SwiftClient():
    def __init__(self):
        self.container_mapping = {}
        self.object_mapping = {}

    def add_data():
        container = 1
        subprocess.run(["swift", "upload", container, "file"])