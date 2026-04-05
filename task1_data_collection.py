import requests
import time
import json
import os
from datetime import datetime

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

# Headers
headers = {"User-Agent": "TrendPulse/1.0"}

CATEGORIES = {
    "technology": ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm"],
    "worldnews": ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports": ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship"],
    "science": ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome"],
    "entertainment": ["movie", "film", "music", "netflix", "game", "book", "show", "award", "streaming"]
}

# Max stories per category
MAX_PER_CATEGORY = 25


def fetch_top_story_ids():
    try:
        response = requests.get(TOP_STORIES_URL, headers=headers)
        response.raise_for_status()
        return response.json()[:500]
    except Exception as e:
        print("Error fetching top stories:", e)
        return []


def fetch_story(story_id):
    try:
        response = requests.get(ITEM_URL.format(story_id), headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching story {story_id}:", e)
        return None


def assign_category(title):
    if not title:
        return None

    title_lower = title.lower()

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category
    return None


def main():
    story_ids = fetch_top_story_ids()

    collected_data = []
    category_counts = {cat: 0 for cat in CATEGORIES}

    for story_id in story_ids:
        story = fetch_story(story_id)
        if not story:
            continue

        title = story.get("title", "")
        category = assign_category(title)

        if category and category_counts[category] < MAX_PER_CATEGORY:
            data = {
                "post_id": story.get("id"),
                "title": title,
                "category": category,
                "score": story.get("score", 0),
                "num_comments": story.get("descendants", 0),
                "author": story.get("by", "unknown"),
                "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            collected_data.append(data)
            category_counts[category] += 1

        # Stop if all categories are filled
        if all(count >= MAX_PER_CATEGORY for count in category_counts.values()):
            break

        # Sleep once per category fill cycle (not per request)
        if sum(category_counts.values()) % MAX_PER_CATEGORY == 0:
            time.sleep(2)

    # Create data folder if not exists
    os.makedirs("data", exist_ok=True)

    # Filename with date
    filename = f"data/trends_{datetime.now().strftime('%Y%m%d')}.json"

    # Save to JSON
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(collected_data, f, indent=4)

    print(f"Collected {len(collected_data)} stories. Saved to {filename}")


if __name__ == "__main__":
    main()
