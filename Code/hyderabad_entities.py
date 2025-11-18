"""
Script 1: Entity Collection for Hyderabad Cultural Network
Collects and stores entities (foods, places, monuments) related to Hyderabad
"""

import json
import requests
from bs4 import BeautifulSoup
import time

class HyderabadEntityCollector:
    def __init__(self):
        # EXPANDED Food Items - Traditional Hyderabadi cuisine
        self.food_items = [
            # Main dishes
            "Hyderabadi Biryani", "Haleem", "Nihari", "Paya", "Pathar ka Gosht",
            "Dum Pukht", "Keema", "Lukhmi", "Shikampuri Kebab", "Dalcha",
            
            # Breads and accompaniments
            "Osmania Biscuit", "Sheermal", "Khameeri Roti", "Roomali Roti",
            
            # Curries and gravies
            "Mirchi ka Salan", "Bagara Baingan", "Khatti Dal", "Dahi ki Chutney",
            
            # Snacks
            "Keema Samosa", "Irani Chai", "Bun Maska", "Kheema Pav",
            "Chakli", "Murukku", "Karachi Biscuit",
            
            # Desserts
            "Qubani ka Meetha", "Double ka Meetha", "Gil-e-Firdaus", "Shahi Tukda",
            "Khubani ka Meetha", "Seviyan", "Phirni", "Gajar ka Halwa",
            
            # Beverages
            "Irani Chai", "Sulaimani Chai", "Falooda", "Lassi"
        ]
        
        # EXPANDED Restaurants and Cafes
        self.restaurants = [
            # Famous biryani places
            "Paradise Restaurant", "Bawarchi", "Cafe Bahar", "Shah Ghouse",
            "Shadab", "Cafe Niloufer", "Alpha Hotel", "Bismillah Hotel",
            
            # Historic restaurants
            "Hotel Shadab", "Nimrah Cafe", "Grand Hotel", "Meridian",
            
            # Haleem specialists
            "Pista House", "Sarvi", "Madina Hotel",
            
            # Modern restaurants
            "Ohri's", "AB's", "Jewel of Nizam", "Exotica", "Over The Moon",
            "Bidri", "Chicha's", "Fusion 9",
            
            # Bakeries
            "Karachi Bakery", "Taj Mahal Bakery", "Almond House", "Hot Breads",
            
            # Street food spots
            "Gokul Chat", "Ram Ki Bandi"
        ]
        
        # EXPANDED Monuments and Heritage Sites
        self.monuments = [
            # Major monuments
            "Charminar", "Golconda Fort", "Qutb Shahi Tombs", "Chowmahalla Palace",
            "Falaknuma Palace", "Purani Haveli",
            
            # Religious sites
            "Mecca Masjid", "Birla Mandir", "Spanish Mosque", "Toli Masjid",
            "Sanghi Temple",
            
            # Museums
            "Salar Jung Museum", "Nizam Museum", "City Museum", "Sudha Cars Museum",
            
            # Historic structures
            "Paigah Tombs", "Taramati Baradari", "Raymond's Tomb", "Toli Masjid",
            "Badshahi Ashurkhana", "Khairtabad Ganesh", "Moula Ali Dargah"
        ]
        
        # EXPANDED Tourist Places and Attractions
        self.tourist_places = [
            # Lakes and parks
            "Hussain Sagar Lake", "Lumbini Park", "Durgam Cheruvu", "Osman Sagar",
            "Himayat Sagar", "Shamirpet Lake", "Secret Lake",
            
            # Entertainment
            "Ramoji Film City", "Wonderla", "Snow World", "Jalavihar Water Park",
            "Mount Opera", "Ocean Park",
            
            # Nature and wildlife
            "Nehru Zoological Park", "Botanical Garden", "KBR National Park",
            "Mrugavani National Park", "Mahavir Harina Vanasthali",
            
            # Cultural centers
            "Shilparamam", "Ravindra Bharathi", "Lamakaan",
            
            # Modern attractions
            "NTR Gardens", "Sanjeevaiah Park", "Lal Bahadur Shastri Stadium",
            
            # Shopping areas
            "Laad Bazaar", "Begum Bazaar", "Moazzam Jahi Market"
        ]
    
    def get_all_entities(self):
        """Returns all entities as a flat list and categorized dict"""
        all_entities = (self.food_items + self.restaurants + 
                       self.monuments + self.tourist_places)
        
        categorized = {
            'food_items': self.food_items,
            'restaurants': self.restaurants,
            'monuments': self.monuments,
            'tourist_places': self.tourist_places
        }
        
        return list(set(all_entities)), categorized
    
    def save_entities(self, filename='hyderabad_entities.json'):
        """Save entities to JSON file"""
        all_entities, categorized = self.get_all_entities()
        
        data = {
            'all_entities': all_entities,
            'categorized': categorized,
            'total_count': len(all_entities)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(all_entities)} entities to {filename}")
        print("\nEntity Summary:")
        print(f"  Food items: {len(self.food_items)}")
        print(f"  Restaurants: {len(self.restaurants)}")
        print(f"  Monuments: {len(self.monuments)}")
        print(f"  Tourist places: {len(self.tourist_places)}")
        print(f"  Total: {len(all_entities)}")
        
        return data

if __name__ == "__main__":
    collector = HyderabadEntityCollector()
    entities_data = collector.save_entities()