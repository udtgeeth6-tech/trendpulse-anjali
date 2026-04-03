import requests
import pandas as pd

# header for request (as given)
headers = {"User-Agent": "TrendPulse/1.0"}

# keyword dictionary for categories
categories = {
    "technology": ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm"],
    "worldnews": ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports": ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship"],
    "science": ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome"],
    "entertainment": ["movie", "film", "music", "netflix", "game", "book", "show", "award", "streaming"]
}

# function to assign category
def get_category(title):
    title = title.lower()
    for category, keywords in categories.items():
        for word in keywords:
            if word in title:
                return category
    return "other"

def fetch_data():
    # Step 1: get top stories
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(url, headers=headers)
    ids = response.json()

    # take first 500
    ids = ids[:500]

    data_list = []

    # Step 2: fetch each story
    for story_id in ids:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        res = requests.get(item_url, headers=headers)
        item = res.json()

        # skip if no title
        if item is None or "title" not in item:
            continue

        title = item["title"]

        data_list.append({
            "title": title,
            "url": item.get("url", ""),
            "score": item.get("score", 0),
            "category": get_category(title)
        })

    # convert to dataframe
    df = pd.DataFrame(data_list)

    # save to csv
    df.to_csv("hn_trending_raw.csv", index=False)
   
    print("Data collected successfully!")
    
# run function
fetch_data()
from google.colab import files

# After you have written your code to the file
files.download("task1_data_collection.py")
