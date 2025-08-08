import requests
import json
import time
import random
from pathlib import Path
from datetime import datetime
from config import CLUBS

class FFPDataScraper:
    def __init__(self):
        self.base_url = "https://www.transfermarkt.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def scrape_club_financials(self, club_id):
        """Scrape financial data for a specific club"""
        try:
            print(f"Scraping financial data for {club_id}...")
            
            # Mock data for POC - replace with actual scraping logic
            mock_data = {
                "club": club_id,
                "year": 2023,
                "revenue": random.randint(200, 700) * 1_000_000,
                "wages": random.randint(100, 400) * 1_000_000,
                "transfer_spending": random.randint(50, 250) * 1_000_000,
                "net_spend": random.randint(-50, 150) * 1_000_000,
                "profit_loss": random.randint(-50, 100) * 1_000_000,
                "debt": random.randint(100, 500) * 1_000_000,
                "squad_cost": random.randint(300, 1000) * 1_000_000,
                "ffp_compliance": random.random() > 0.3,
                "scraped_at": datetime.now().isoformat()
            }
            
            # Simulate network delay
            time.sleep(1)
            return mock_data
            
        except Exception as e:
            print(f"Error scraping {club_id}: {e}")
            return None
    
    def scrape_all_clubs(self):
        """Scrape financial data for all clubs"""
        results = []
        
        for club in CLUBS:
            data = self.scrape_club_financials(club["id"])
            if data:
                results.append(data)
        
        # Save to file
        output_path = Path(__file__).parent.parent / "data" / "ffp_data_2023.json"
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Data saved to {output_path}")
        return results

if __name__ == "__main__":
    scraper = FFPDataScraper()
    data = scraper.scrape_all_clubs()
    print(f"Scraped data for {len(data)} clubs")