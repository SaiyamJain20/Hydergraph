"""
Script 2: Enhanced Web Scraper for Hyderabad Content
Focuses on cross-category connections (food ↔ places, restaurants ↔ monuments)
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
import re

class HyderabadContentScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.scraped_data = []
    
    def scrape_food_near_monuments(self):
        """Scrape articles about food near monuments - CROSS-CATEGORY!"""
        print("\n🔗 Scraping food near monuments (cross-category content)...")
        
        urls = [
            # Food near famous places
            'https://www.tripadvisor.in/RestaurantsNear-g297586-d324067-Charminar-Hyderabad_Hyderabad_District_Telangana.html',
            'https://www.zomato.com/hyderabad/charminar-restaurants',
            'https://www.zomato.com/hyderabad/golconda-restaurants',
            
            # Food tourism
            'https://www.thrillophilia.com/things-to-do/food-in-hyderabad',
            'https://www.holidify.com/pages/food-of-hyderabad-1660.html',
        ]
        
        for url in urls:
            try:
                print(f"  Fetching: {url}")
                time.sleep(3)
                response = requests.get(url, headers=self.headers, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Remove unwanted elements
                    for unwanted in soup(["script", "style", "nav", "footer"]):
                        unwanted.decompose()
                    
                    text_parts = []
                    for tag in soup.find_all(['p', 'div', 'span', 'article']):
                        text = tag.get_text(strip=True)
                        if len(text) > 40:
                            text_parts.append(text)
                    
                    if text_parts:
                        self.scraped_data.append({
                            'source': url,
                            'type': 'food_near_monuments',
                            'text': ' '.join(text_parts),
                            'timestamp': datetime.now().isoformat()
                        })
                        print(f"    ✓ Extracted content")
                    
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    def scrape_restaurant_travel_guides(self):
        """Scrape travel guides that mention both restaurants AND places"""
        print("\n🔗 Scraping restaurant & travel guides (cross-category)...")
        
        urls = [
            # Combined food and sightseeing
            'https://www.makemytrip.com/travel-guide/hyderabad/local-food.html',
            'https://traveltriangle.com/blog/hyderabad-street-food/',
            'https://www.fabhotels.com/blog/food-in-hyderabad/',
            'https://www.oyorooms.com/travel-guide/famous-food-of-hyderabad/',
            
            # Food tours and experiences
            'https://www.thrillophilia.com/tours/heritage-walk-and-food-tour-in-hyderabad',
            'https://www.tripadvisor.in/Attractions-g297586-Activities-c42-Hyderabad_Hyderabad_District_Telangana.html',
        ]
        
        for url in urls:
            try:
                print(f"  Fetching: {url}")
                time.sleep(3)
                response = requests.get(url, headers=self.headers, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    for unwanted in soup(["script", "style"]):
                        unwanted.decompose()
                    
                    text_parts = []
                    for p in soup.find_all('p'):
                        text = p.get_text(strip=True)
                        if len(text) > 40:
                            text_parts.append(text)
                    
                    if text_parts:
                        self.scraped_data.append({
                            'source': url,
                            'type': 'restaurant_travel_guide',
                            'text': ' '.join(text_parts),
                            'timestamp': datetime.now().isoformat()
                        })
                        print(f"    ✓ Extracted content")
                        
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    def scrape_heritage_food_blogs(self):
        """Scrape blogs about heritage food and places together"""
        print("\n🔗 Scraping heritage & food blogs (cross-category)...")
        
        urls = [
            # Heritage and food combined
            'https://www.cntraveller.in/story/hyderabad-food-guide-best-restaurants/',
            'https://www.lonelyplanet.com/india/telangana/hyderabad/restaurants',
            'https://www.eatingasia.com/category/india/hyderabad/',
            
            # Cultural food experiences
            'https://www.tasteatlas.com/hyderabad/restaurants',
            'https://www.timeout.com/india/restaurants/best-restaurants-in-hyderabad',
        ]
        
        for url in urls:
            try:
                print(f"  Fetching: {url}")
                time.sleep(3)
                response = requests.get(url, headers=self.headers, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    for unwanted in soup(["script", "style"]):
                        unwanted.decompose()
                    
                    text_parts = []
                    for tag in soup.find_all(['p', 'article']):
                        text = tag.get_text(strip=True)
                        if len(text) > 40:
                            text_parts.append(text)
                    
                    if text_parts:
                        self.scraped_data.append({
                            'source': url,
                            'type': 'heritage_food_blog',
                            'text': ' '.join(text_parts),
                            'timestamp': datetime.now().isoformat()
                        })
                        print(f"    ✓ Extracted content")
                        
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    def scrape_travel_blogs(self):
        """Scrape comprehensive travel blogs"""
        print("\n📖 Scraping travel blogs...")
        
        urls = [
            'https://www.thrillophilia.com/hyderabad',
            'https://traveltriangle.com/blog/places-to-visit-in-hyderabad/',
            'https://www.holidify.com/places/hyderabad/',
            'https://www.tripadvisor.in/Tourism-g297586-Hyderabad_Hyderabad_District_Telangana-Vacations.html',
            'https://www.lonelyplanet.com/india/telangana/hyderabad',
            'https://www.fabhotels.com/blog/places-to-visit-in-hyderabad/',
        ]
        
        for url in urls:
            try:
                print(f"  Fetching: {url}")
                time.sleep(3)
                response = requests.get(url, headers=self.headers, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    for unwanted in soup(["script", "style"]):
                        unwanted.decompose()
                    
                    text_parts = []
                    for p in soup.find_all('p'):
                        text = p.get_text(strip=True)
                        if len(text) > 50:
                            text_parts.append(text)
                    
                    if text_parts:
                        self.scraped_data.append({
                            'source': url,
                            'type': 'travel_blog',
                            'text': ' '.join(text_parts),
                            'timestamp': datetime.now().isoformat()
                        })
                        print(f"    ✓ Extracted content")
                        
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    def scrape_wikipedia(self):
        """Scrape Wikipedia articles"""
        print("\n📚 Scraping Wikipedia...")
        
        urls = [
            'https://en.wikipedia.org/wiki/Hyderabad',
            'https://en.wikipedia.org/wiki/Hyderabadi_cuisine',
            'https://en.wikipedia.org/wiki/Tourism_in_Hyderabad',
            'https://en.wikipedia.org/wiki/Culture_of_Hyderabad',
            'https://en.wikipedia.org/wiki/Charminar',
            'https://en.wikipedia.org/wiki/Golconda_Fort',
            'https://en.wikipedia.org/wiki/Hyderabadi_biryani',
            'https://en.wikipedia.org/wiki/Hyderabadi_haleem',
            'https://en.wikipedia.org/wiki/Qutb_Shahi_Tombs',
            'https://en.wikipedia.org/wiki/Ramoji_Film_City',
            'https://en.wikipedia.org/wiki/Chowmahalla_Palace',
            'https://en.wikipedia.org/wiki/Hussain_Sagar',
        ]
        
        for url in urls:
            try:
                print(f"  Fetching: {url}")
                time.sleep(2)
                response = requests.get(url, headers=self.headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    content = soup.find('div', {'id': 'mw-content-text'})
                    if content:
                        paragraphs = content.find_all('p')
                        text = ' '.join([p.get_text() for p in paragraphs])
                        
                        self.scraped_data.append({
                            'source': url,
                            'type': 'wikipedia',
                            'text': text,
                            'timestamp': datetime.now().isoformat()
                        })
                        print(f"    ✓ Extracted article")
                        
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    def scrape_food_blogs(self):
        """Scrape pure food blogs"""
        print("\n🍽️ Scraping food blogs...")
        
        urls = [
            'https://www.seriouseats.com/hyderabadi-biryani',
            'https://www.eatingasia.com/hyderabadi-biryani/',
            'https://www.thespruceeats.com/hyderabadi-biryani-recipe-1957743',
        ]
        
        for url in urls:
            try:
                print(f"  Fetching: {url}")
                time.sleep(3)
                response = requests.get(url, headers=self.headers, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    for unwanted in soup(["script", "style"]):
                        unwanted.decompose()
                    
                    text_parts = []
                    for p in soup.find_all('p'):
                        text = p.get_text(strip=True)
                        if len(text) > 30:
                            text_parts.append(text)
                    
                    if text_parts:
                        self.scraped_data.append({
                            'source': url,
                            'type': 'food_blog',
                            'text': ' '.join(text_parts),
                            'timestamp': datetime.now().isoformat()
                        })
                        print(f"    ✓ Extracted content")
                        
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    def scrape_old_city_guides(self):
        """Scrape Old City guides that mention both food and heritage"""
        print("\n🏛️ Scraping Old City guides (food + heritage)...")
        
        urls = [
            'https://www.lonelyplanet.com/india/telangana/hyderabad/old-city',
            'https://www.thrillophilia.com/things-to-do/old-city-hyderabad',
            'https://traveltriangle.com/blog/old-city-hyderabad/',
        ]
        
        for url in urls:
            try:
                print(f"  Fetching: {url}")
                time.sleep(3)
                response = requests.get(url, headers=self.headers, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    for unwanted in soup(["script", "style"]):
                        unwanted.decompose()
                    
                    text_parts = []
                    for p in soup.find_all('p'):
                        text = p.get_text(strip=True)
                        if len(text) > 40:
                            text_parts.append(text)
                    
                    if text_parts:
                        self.scraped_data.append({
                            'source': url,
                            'type': 'old_city_guide',
                            'text': ' '.join(text_parts),
                            'timestamp': datetime.now().isoformat()
                        })
                        print(f"    ✓ Extracted content")
                        
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    def save_scraped_data(self, filename='scraped_data.json'):
        """Save all scraped data to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✓ Saved {len(self.scraped_data)} documents to {filename}")
        
        # Print statistics
        types = {}
        total_chars = 0
        for doc in self.scraped_data:
            doc_type = doc['type']
            types[doc_type] = types.get(doc_type, 0) + 1
            total_chars += len(doc['text'])
        
        print(f"\nDocument types:")
        for doc_type, count in sorted(types.items()):
            print(f"  {doc_type}: {count}")
        
        print(f"\nTotal characters scraped: {total_chars:,}")
        print(f"Average chars per document: {total_chars//len(self.scraped_data):,}")
        
        # Highlight cross-category content
        cross_category = sum([types.get(t, 0) for t in [
            'food_near_monuments', 'restaurant_travel_guide', 
            'heritage_food_blog', 'old_city_guide'
        ]])
        print(f"\n🔗 Cross-category documents: {cross_category} ({cross_category/len(self.scraped_data)*100:.1f}%)")
        print(f"{'='*70}")
        
        return self.scraped_data
    
    def run_all_scrapers(self):
        """Run all scrapers with focus on cross-category content"""
        print("="*70)
        print("ENHANCED WEB SCRAPING - Focus on Cross-Category Connections")
        print("="*70)
        
        # PRIORITIZE cross-category content first!
        self.scrape_food_near_monuments()
        self.scrape_restaurant_travel_guides()
        self.scrape_heritage_food_blogs()
        self.scrape_old_city_guides()
        
        # Then get broader content
        self.scrape_wikipedia()
        self.scrape_travel_blogs()
        self.scrape_food_blogs()
        
        return self.save_scraped_data()

if __name__ == "__main__":
    scraper = HyderabadContentScraper()
    scraped_data = scraper.run_all_scrapers()
    print(f"\n🎉 Scraping complete! Total documents: {len(scraped_data)}")