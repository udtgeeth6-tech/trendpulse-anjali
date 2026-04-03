import requests
import json

import os
import time
from datetime import datetime

class TrendPulseCollector:
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.output_dir = "data"
        self.categories = {
            "technology": ["software", "ai", "apple", "google", "programming", "web"],
            "science": ["space", "nasa", "physics", "biology", "research", "climate"],
            "entertainment": ["movie", "music", "game", "nintendo", "film", "art"],
            "worldnews": ["china", "europe", "policy", "court", "government", "war"],
            "sports": ["f1", "chess", "football", "soccer", "olympics", "nba"]
        }
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def fetch_story_details(self, story_id, category):
        """Extracts the 7 required fields from a story ID."""
        try:
            url = f"{self.base_url}/item/{story_id}.json"
            response = requests.get(url)
            response.raise_for_status()
            item = response.json()

            if item and item.get('type') == 'story' and 'title' in item:
                # Required Fields (Task 2 Mapping)
                return {
                    "post_id": item.get("id"),
                    "title": item.get("title"),
                    "category": category,
                    "score": item.get("score", 0),
                    "num_comments": item.get("descendants", 0),
                    "author": item.get("by"),
                    "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        except Exception as e:
            print(f"  [!] Failed to fetch story {story_id}: {e}")
        return None

    def collect_all(self):
        print("Starting Task 1: Collection...")
        all_collected_stories = []


        # STEP 1: Increase the pool by fetching from 3 different endpoints
        # This gives us ~1,500 IDs to search through instead of just 500
        endpoints = ["topstories", "newstories", "beststories"]
        combined_ids = []
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}/{endpoint}.json"
                ids = requests.get(url, timeout=5).json()
                combined_ids.extend(ids)
            except Exception as e:
                print(f"  [!] Could not fetch {endpoint}: {e}")

        # Remove duplicate IDs to save time
        unique_ids = list(set(combined_ids))
        print(f"[*] Total unique IDs to scan: {len(unique_ids)}")
      

        for category, keywords in self.categories.items():
            print(f"Searching for {category}...")
            category_count = 0
            
            for story_id in unique_ids:
                if category_count >= 25: # Limit to 25 per category
                    break
                
                # Peek at the story to see if it matches keywords
                story_url = f"{self.base_url}/item/{story_id}.json"
                item = requests.get(story_url).json()
                
                if item and 'title' in item:
                    title_lower = item['title'].lower()
                    # Check if any keyword for this category is in the title
                    if any(kw in title_lower for kw in keywords):
                        story_data = self.fetch_story_details(story_id, category)
                        if story_data:
                            all_collected_stories.append(story_data)
                            category_count += 1
            
            # REQUIREMENT: Wait 2 seconds between each category
            time.sleep(2)

        return all_collected_stories

    def save_to_json(self, data):
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"data/trends_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        print(f"\nTask 1 Complete!")
        print(f"Collected {len(data)} stories. Saved to {filename}")
        
if __name__ == "__main__":
    collector = TrendPulseCollector()
    stories = collector.collect_all()
    collector.save_to_json(stories)
    
