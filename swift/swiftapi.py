import subprocess
from pathlib import Path
import random
import string
import json
from prettytable import PrettyTable
from datetime import datetime
import re
import time

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
        self.objects_per_container = 1000000
        self.generator = StockData()
        self.last_event_time = None
        self.last_event_type = None
        self.last_req_time = None
        self.log_fp = Path("data-movement-log.txt")
        
        # Open Swift config file
        with open("swiftconfig.json", "r") as f:
            self.ring_conf = json.load(f)
            
        # Open VM config file
        with open("../vmconfig.json", "r") as f:
            self.vm_names = json.load(f)
            
        # Set up Swift Credentials
        # subprocess.run(["source", "keystone_admin_env"])
        
    def initconfig(self):
        for ip in self.ring_conf.get("storage_nodes"):
            subprocess.run(["./stats.sh", "initconfig", ip])

    def create_ring(self):
        # Account builder
        account_replicas = self.ring_conf.get("account").get("replicas")
        account_ips = self.ring_conf.get("account").get("hosts")
        account_weights = self.ring_conf.get("account").get("weights")
        subprocess.run(["swift-ring-builder", "account.builder", "create", "10", str(account_replicas), "1"])
        for i in range(len(account_ips)):
            subprocess.run(["swift-ring-builder", "account.builder", "add", "--region", "1", "--zone", "1",
                            "--ip", account_ips[i], "--port", "6202", "--device", "sdb", "--weight", str(account_weights[i])])
        subprocess.run(["swift-ring-builder", "account.builder", "rebalance"])
        
        # Container builder
        container_replicas = self.ring_conf.get("container").get("replicas")
        container_ips = self.ring_conf.get("container").get("hosts")
        container_weights = self.ring_conf.get("container").get("weights")
        subprocess.run(["swift-ring-builder", "container.builder", "create", "10", str(container_replicas), "1"])
        for i in range(len(container_ips)):
            subprocess.run(["swift-ring-builder", "container.builder", "add", "--region", "1", "--zone", "1",
                            "--ip", container_ips[i], "--port", "6201", "--device", "sdb", "--weight", str(container_weights[i])])
        subprocess.run(["swift-ring-builder", "container.builder", "rebalance"])
        
        # Object builder
        object_replicas = self.ring_conf.get("object").get("replicas")
        object_ips = self.ring_conf.get("object").get("hosts")
        object_weights = self.ring_conf.get("object").get("weights")
        subprocess.run(["swift-ring-builder", "object.builder", "create", "10", str(object_replicas), "1"])
        for i in range(len(object_ips)):
            subprocess.run(["swift-ring-builder", "object.builder", "add", "--region", "1", "--zone", "1",
                            "--ip", object_ips[i], "--port", "6200", "--device", "sdb", "--weight", str(object_weights[i])])
        subprocess.run(["swift-ring-builder", "object.builder", "rebalance"])
        
        # Move gz files to correct place
        for ip in account_ips:
            subprocess.run(["scp", "account.ring.gz", f"root@{ip}:/etc/swift"])
        for ip in container_ips:
            subprocess.run(["scp", "container.ring.gz", f"root@{ip}:/etc/swift"])
        for ip in object_ips:
            subprocess.run(["scp", "object.ring.gz", f"root@{ip}:/etc/swift"])
        subprocess.run(["mv", "account.ring.gz", "container.ring.gz", "object.ring.gz", "/etc/swift"])
        
    def as_timestamp(self, ts):
        dt = datetime.now()
        time_array = ts.split(":")
        return datetime(dt.year, dt.month, dt.day, int(time_array[0]), int(time_array[1]), int(time_array[2]))

    def add_data_container(self, n):
        # Get current time
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_event_time = start_time
        
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
                # subprocess.run(["rm", "-rf", f"container-{self.cur_container_num}"])
                self.cur_container_num += 1
                fp = Path(f"container-{self.cur_container_num}")
                fp.mkdir(parents=True, exist_ok=True)
                
        # Data from last container
        print(f"Uploading into Container {self.cur_container_num}...")
        subprocess.run(["swift", "upload", f"container-{self.cur_container_num}", f"container-{self.cur_container_num}"])
        # subprocess.run(["rm", "-rf", f"container-{self.cur_container_num}"])
        
    def add_data(self, n):
        self.start_object_num = self.cur_object_num
        self.end_object_num = self.cur_object_num + n
        
        # Container path
        fp = Path(f"container-data-temp")
        fp.mkdir(parents=True, exist_ok=True)
        
        for i in range(self.start_object_num, self.end_object_num):
            # Increment object number and possibly container number
            subprocess.run(["cp", f"container-data/stock-data-{i}.json", "container-data-temp"])
            
        # Get current time and set as event time
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_event_time = start_time
        self.last_event_type = "add-data"
        self.cur_object_num += n
        
        # Upload info into container
        subprocess.Popen(["./data-actions.sh", "add"], stdout=subprocess.DEVNULL)
        
    def get_data_movement_stats(self):
        # Collect logs since an event
        if self.last_event_time is None:
            result = subprocess.check_output(["journalctl", "-u", "openstack-swift-proxy"], 
                                                universal_newlines=True, 
                                                timeout=3, 
                                                stderr=subprocess.DEVNULL).strip()
        else:
            result = subprocess.check_output(["journalctl", "-u", "openstack-swift-proxy", "--since", self.last_event_time], 
                                                universal_newlines=True, 
                                                timeout=3, 
                                                stderr=subprocess.DEVNULL).strip()
        
        # Parse the results
        array = [entry for entry in result.split("\n")]
        last_ts = None
        total_bytes = 0
        for entry in array:
            if "PUT /v1" in entry:
                request_array = entry.split()
                ts = request_array[2]
                last_ts = ts
                object_url = request_array[9].split("/")[-1]
                if not object_url.startswith("stock-data"):
                    continue
                object_size = int(request_array[15])
                response_time = float(request_array[20])
                total_bytes += object_size
                print(f"PUT Time: {ts}, Object: {object_url}, Object Size: {object_size}")
        
        # Calculate high level stats
        dt = datetime.now()
        time_array = last_ts.split(":")
        end_time = datetime(dt.year, dt.month, dt.day, int(time_array[0]), int(time_array[1]), int(time_array[2]))
        start_time = datetime.strptime(self.last_event_time, "%Y-%m-%d %H:%M:%S")
        delta_sec = (end_time - start_time).total_seconds()
        
        # Metrics
        print(f"Time Elapsed: {delta_sec} seconds")
        print(f"Total Data Size: {total_bytes / 1024.0} KB")
        print(f"Speed: {round(total_bytes / 1024.0 / delta_sec, 3)} KB/s")
        
    def get_data_movement_stats_v2(self):
        put_requests = []
        # Make requests to all Storage nodes
        for ip in self.ring_conf.get("storage_nodes"):
            try:
                last_event_time = self.last_event_time if self.last_event_time is not None else "None"
                result = subprocess.check_output(["./stats.sh", "object-requests", ip, "PUT", last_event_time], 
                                                    universal_newlines=True, 
                                                    timeout=3).strip()
                # Parse the results
                put_requests += [entry for entry in result.split("\n") if "PUT /sdb" in entry]
            except Exception:
                pass
        
        # New write file
        if self.log_fp.exists():
            self.log_fp.unlink()
        f = open(self.log_fp, "a")
            
        # Object add range
        target_oids = set(list(range(self.start_object_num, self.end_object_num)))
        received_oids = set()
        
        # Get stats
        last_ts = None
        total_bytes = 0
        total_response_time = 0
        total_requests = 0
        
        # Iterate through PUT requests
        for entry in put_requests:
            request_array = entry.split()
            ts = request_array[2]
            object_url = request_array[11][:-1].split("/")[-1]
            if not object_url.startswith("stock-data"):
                continue
            object_oid = int(re.split("[.-]", object_url)[2])
            # Object size
            object_size = int(subprocess.check_output(["ls", "-l", f"container-data/{object_url}"], 
                                                universal_newlines=True, 
                                                timeout=3, 
                                                stderr=subprocess.DEVNULL).strip().split()[4])
            response_time = float(request_array[19])
            received_oids.add(object_oid)
            if object_oid in target_oids:
                # Max timestamp
                if last_ts is None or self.as_timestamp(ts) > self.as_timestamp(last_ts):
                    last_ts = ts
                total_bytes += object_size
                total_requests += 1
                total_response_time += response_time
                print(f"PUT Time: {ts}, Object: {object_url}, Object Size: {object_size}, Response Time: {response_time}")
                f.write(f"PUT Time: {ts}, Object: {object_url}, Object Size: {object_size}, Response Time: {response_time}\n")
            
        # Check if we have everything
        print()
        f.close()
        if target_oids.issubset(received_oids):
            print("Status: COMPLETE")
        else:
            print("Status: INCOMPLETE")
            
        # Calculate high level stats
        if last_ts is not None:
            end_time = self.as_timestamp(last_ts)
            start_time = datetime.strptime(self.last_event_time, "%Y-%m-%d %H:%M:%S")
            delta_sec = (end_time - start_time).total_seconds()
            
            # Metrics
            print(f"Total Requests Made: {total_requests} requests")
            print(f"Time Elapsed: {delta_sec} seconds")
            print(f"Total Data Size: {total_bytes / 1024.0} KB")
            print(f"Speed: {round(total_bytes / 1024.0 / delta_sec, 3)} KB/s")
            print(f"Average Response Time: {round(total_response_time / total_requests, 3)} s")
        
        # Print that nothing has happened
        else:
            print(f"No data inserted yet.")
        
    def generate_read_req(self):
        self.req_oids = []
        self.last_req_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i in range(10):
            read_oid = random.randint(1, self.cur_object_num - 1)
            self.req_oids.append(read_oid)
            subprocess.Popen(["swift", "download", "container-1", f"container-data-temp/stock-data-{read_oid}.json"])
            time.sleep(0.2)
        
    def get_read_req_stats(self):
        result = subprocess.check_output(["journalctl", "-u", "openstack-swift-proxy", "--since", self.last_req_time], 
                                                universal_newlines=True, 
                                                timeout=3, 
                                                stderr=subprocess.DEVNULL).strip()
        get_requests = [entry for entry in result.split("\n") if "GET /v1" in entry and "stock-data" in entry]
        # Requests
        for entry in get_requests:
            request_array = entry.split()
            object_url = request_array[9].split("/")[-1]
            response_time = float(request_array[20])
            print(f"GET Object: {object_url}, Response Time: {response_time}")

    def get_data_movement_logs(self):
        with open(self.log_fp, "r") as f:
            data = f.read()
            print(data)
                
    def restart_nodes(self):
        for ip in self.ring_conf.get("storage_nodes"):
            subprocess.run(["ssh", f"root@{ip}", "./restart-storage.sh"])
        subprocess.run(["systemctl", "restart", "openstack-swift-proxy.service", "memcached.service"])
        
    def shutdown_nodes(self):
        for ip in self.vm_names.get("cluster_nodes"):
            result = subprocess.check_output(["./stats.sh", "virsh-running-nodes", ip], 
                                                    universal_newlines=True, 
                                                    timeout=3, 
                                                    stderr=subprocess.DEVNULL).strip()
            node_names = [entry.split()[1] for entry in result.split("\n")[2:]]
            for name in node_names:
                if name in self.vm_names.get("swift"):
                    subprocess.run(["./stats.sh", "virsh-shutdown", ip, name],
                                   stdout=subprocess.DEVNULL)
    
    def startup_nodes(self):
        for ip in self.vm_names.get("cluster_nodes"):
            result = subprocess.check_output(["./stats.sh", "virsh-shutoff-nodes", ip], 
                                                    universal_newlines=True, 
                                                    timeout=3, 
                                                    stderr=subprocess.DEVNULL).strip()
            node_names = [entry.split()[1] for entry in result.split("\n")[2:]]
            for name in node_names:
                if name in self.vm_names.get("swift"):
                    subprocess.run(["./stats.sh", "virsh-startup", ip, name],
                                   stdout=subprocess.DEVNULL)

    def clear_data(self):
        subprocess.run(["swift", "delete", "-a"])
        print("Data Cleared!")
        
    def force_clear_data(self):
        for ip in self.ring_conf.get("storage_nodes"):
            try:
                subprocess.run(["./stats.sh", "data-delete", ip],
                                        stdout=subprocess.DEVNULL, timeout=3)
            except Exception:
                pass
        
    def datacount(self):
        print("Number of Objects in Storage Nodes:")
        # Stats logging
        t = PrettyTable(["Node IP", "Num Objects"])
        for ip in self.ring_conf.get("storage_nodes"):
            try:
                result = subprocess.check_output(["./stats.sh", "datacount", ip], universal_newlines=True, 
                                                 timeout=3, stderr=subprocess.DEVNULL).strip()
                t.add_row([ip, result])
            except Exception:
                t.add_row([ip, 0])
        print(str(t))
        
    def dataloc(self):
        t = PrettyTable(["OID", "Storage IP"])
        location_dict = {}
        for ip in self.ring_conf.get("storage_nodes"):
            try:
                result = subprocess.check_output(["./stats.sh", "dataloc", ip], universal_newlines=True, timeout=3).strip()
                data_ids = [int(item.split(":")[1].strip()[:-1]) for item in result.split("\n")]
                for oid in data_ids:
                    location_dict[oid] = ip
            except Exception:
                pass
        for key in sorted(location_dict):
            t.add_row([key, location_dict[key]])
        print(str(t))
        
if __name__ == "__main__":
    client = SwiftClient()
    client.create_ring()
    client.restart_nodes()