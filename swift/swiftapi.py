import subprocess
from pathlib import Path
import random
import string
import json

class StockData():
    def __init__(self):
        self.sectors = ["communication", "energy", "materials", "industrials", "utilities",
               "healthcare", "financials", "consumer discretionary", "consumer staples",
               "infotech", "real estate"]
        
    def generate(self, oid):
        # Starting variables
        cur_price = random.random() * random.randint(5, 3000)
        reviews = random.randint(5, 1000)
        positive_reviews = random.randint(1, reviews)
        avg_volume = random.randint(1000, 5000000)
        
        data = [{
            "oid": oid,
            "ticker": "".join(random.choices(string.ascii_letters, k=4)).upper(),
            "sector": random.choice(self.sectors),
            "reviews": {
                "total": reviews,
                "positive": positive_reviews,
                "negative": reviews - positive_reviews
            },
            "history": [],
        }]
        for j in range(20):
            increase_factor = random.random() * 0.05 - 0.02
            data[0]["history"].append({
                "time_id": j + 1000,
                "open": cur_price,
                "close": cur_price * (1.0 + increase_factor),
                "percentChange": increase_factor * 100.0,
                "volume": avg_volume * (random.random() * 0.2 + 0.9)
            })
            cur_price *= (1.0 + increase_factor)
        return data

    
class SwiftClient():
    def __init__(self):
        self.cur_container_num = 1
        self.cur_object_num = 1
        self.objects_per_container = 100
        self.generator = StockData()
        with open("config.json", "r") as f:
            self.ring_conf = json.load(f)

    def create_ring(self):
        # Account builder
        account_replicas = self.ring_conf.get("account").get("replicas")
        account_ips = self.ring_conf.get("account").get("hosts")
        subprocess.run(["swift-ring-builder", "account.builder", "create", "10", str(account_replicas), "1"])
        for ip in account_ips:
            subprocess.run(["swift-ring-builder", "account.builder", "add", "--region", "1", "--zone", "1",
                            "--ip", ip, "--port", "6202", "--device", "sdb", "--weight", "100"])
        subprocess.run(["swift-ring-builder", "account.builder", "rebalance"])
        
        # Container builder
        container_replicas = self.ring_conf.get("container").get("replicas")
        container_ips = self.ring_conf.get("container").get("hosts")
        subprocess.run(["swift-ring-builder", "container.builder", "create", "10", str(container_replicas), "1"])
        for ip in container_ips:
            subprocess.run(["swift-ring-builder", "container.builder", "add", "--region", "1", "--zone", "1",
                            "--ip", ip, "--port", "6201", "--device", "sdb", "--weight", "100"])
        subprocess.run(["swift-ring-builder", "container.builder", "rebalance"])
        
        # Object builder
        object_replicas = self.ring_conf.get("object").get("replicas")
        object_ips = self.ring_conf.get("object").get("hosts")
        subprocess.run(["swift-ring-builder", "object.builder", "create", "10", str(object_replicas), "1"])
        for ip in object_ips:
            subprocess.run(["swift-ring-builder", "object.builder", "add", "--region", "1", "--zone", "1",
                            "--ip", ip, "--port", "6200", "--device", "sdb", "--weight", "100"])
        subprocess.run(["swift-ring-builder", "object.builder", "rebalance"])
        
        # Move gz files to correct place
        for ip in account_ips:
            subprocess.run(["scp", "account.ring.gz", f"root@{ip}:/etc/swift"])
        for ip in container_ips:
            subprocess.run(["scp", "container.ring.gz", f"root@{ip}:/etc/swift"])
        for ip in object_ips:
            subprocess.run(["scp", "object.ring.gz", f"root@{ip}:/etc/swift"])
        subprocess.run(["mv", "account.ring.gz", "container.ring.gz", "object.ring.gz", "/etc/swift"])

    def add_data(self, n):
        # Container path
        fp = Path(f"container-{self.cur_container_num}")
        fp.mkdir(parents=True, exist_ok=True)
        
        for i in range(n):
            # Generate file and upload it
            with open(fp / f"stock-data-{self.cur_object_num}.json", "w") as f:
                f.write(json.dumps(self.generator.generate(oid=self.cur_object_num), indent=4))
            
            # Increment object number and possibly container number
            self.cur_object_num += 1
            if self.cur_object_num % self.objects_per_container == 0:
                print(f"Uploading into Container {self.cur_container_num}...")
                subprocess.run(["swift", "upload", f"container-{self.cur_container_num}", f"container-{self.cur_container_num}"])
                subprocess.run(["rm", "-rf", f"container-{self.cur_container_num}"])
                self.cur_container_num += 1
                fp = Path(f"container-{self.cur_container_num}")
                fp.mkdir(parents=True, exist_ok=True)
                
    def restart_nodes(self):
        for ip in self.ring_conf.get("storage_nodes"):
            subprocess.run(["ssh", f"root@{ip}", "./restart-storage.sh"])
        subprocess.run(["systemctl", "restart", "openstack-swift-proxy.service", "memcached.service"])

    def clear_data(self):
        subprocess.run(["swift", "delete", "-a"])
        print("Data Cleared!")
        
if __name__ == "__main__":
    client = SwiftClient()
    client.create_ring()
    client.restart_nodes()