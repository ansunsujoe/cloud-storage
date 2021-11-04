import json
import argparse
import string
import random

if __name__ == "__main__":
    # Constants
    sectors = ["communication", "energy", "materials", "industrials", "utilities",
               "healthcare", "financials", "consumer discretionary", "consumer staples",
               "infotech", "real estate"]
    
    # Number of files to generate
    n_files = 10000
    for i in range(n_files):
        
        # Starting variables
        cur_price = random.random() * random.randint(5, 3000)
        reviews = random.randint(5, 1000)
        positive_reviews = random.randint(1, reviews)
        avg_volume = random.randint(1000, 5000000)
        
        data = [{
            "ticker": "".join(random.choices(string.ascii_letters, k=4)).upper(),
            "sector": random.choice(sectors),
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
        
        with open(f"../data/stock-data-{i+1}.json", "w") as f:
            f.write(json.dumps(data, indent=4))
