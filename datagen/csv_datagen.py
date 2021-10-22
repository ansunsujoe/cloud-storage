import json
import string
import random
import csv

if __name__ == "__main__":
    data = []
    
    # Number of files to generate
    n_tickers = 100
    for i in range(n_tickers):
        
        # Starting variables
        cur_price = random.random() * random.randint(5, 3000)
        reviews = random.randint(5, 1000)
        positive_reviews = random.randint(1, reviews)
        avg_volume = random.randint(1000, 5000000)
        ticker = "".join(random.choices(string.ascii_letters, k=4)).upper()
        
        for j in range(20000):
            increase_factor = random.random() * 0.05 - 0.02
            data.append({
                "ticker": ticker,
                "time_id": j + 1000,
                "open": cur_price,
                "close": cur_price * (1.0 + increase_factor),
                "percentChange": increase_factor * 100.0,
                "volume": avg_volume * (random.random() * 0.2 + 0.9)
            })
            cur_price *= (1.0 + increase_factor)
        
    with open('stock-data.csv', 'w', newline='') as csvfile:
        fieldnames = ["ticker", 'time_id', 'open', "close", "percentChange", "volume"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)