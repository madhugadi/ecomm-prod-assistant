# prod_assistant/etl/data_scrapper.py

import csv
import os
import random


class AmazonScraper:
    """
    Dummy scraper that generates ingestion-safe, realistic mock data.
    NO network calls. NO scraping.
    Used to unblock vector ingestion pipeline.
    """

    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def scrape_products(self, query, max_products=5):
        """
        Generate realistic mock product data.
        All values are JSON-safe (no NaN / N/A).
        """
        products = []

        base_price = random.randint(600, 900)

        for i in range(max_products):
            rating = round(random.uniform(4.0, 4.8), 1)
            total_reviews = random.randint(500, 5000)
            price = base_price + random.randint(-50, 100)

            products.append([
                f"MOCK-{i+1}",
                f"{query} product {i+1}",
                rating,                 # float
                total_reviews,          # int
                price,                  # int
                (
                    f"Customers discussing {query} product {i+1}. "
                    f"Positive feedback on performance and design, "
                    f"with some concerns about pricing and battery life."
                )
            ])

        return products

    def save_to_csv(self, data, filename="product_reviews.csv"):
        # Respect provided path
        if os.path.dirname(filename):
            path = filename
            os.makedirs(os.path.dirname(path), exist_ok=True)
        else:
            path = os.path.join(self.output_dir, filename)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "product_id",
                "product_title",
                "rating",
                "total_reviews",
                "price",
                "top_reviews",
            ])
            writer.writerows(data)

        print(f"✅ Mock data written to {path}")
