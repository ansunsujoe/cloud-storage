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
        
    def generate(self):
        # Starting variables
        cur_price = random.random() * random.randint(5, 3000)
        reviews = random.randint(5, 1000)
        positive_reviews = random.randint(1, reviews)
        avg_volume = random.randint(1000, 5000000)
        
        data = [{
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
        self.next_container_num = 1
        self.next_object_num = 1
        self.generator = StockData()

    def add_data(self, n):
        subprocess.run(["swift", "upload", "container", "file"])
        
    def generate_data(self):
        with open(f"stock-data-{self.next_object_num}.json", "w") as f:
            f.write(json.dumps(self.generator.generate(), indent=4))