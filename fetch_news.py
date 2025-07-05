import os
import json
from datetime import date
import feedparser
from newspaper import Article
from textblob import TextBlob

# 1. Configuration
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.npr.org/1001/rss.xml",
    # add more RSS URLs here
]

NEGATIVE_KEYWORDS = ["war", "conflict", "crime", "shooting", "disaster", "violence"]

OUTPUT_DIR = "today_uplifting_summaries"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. Fetch today's feed items
def fetch_feed_articles():
    today = date.today().isoformat()
    articles = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            # Use published date if string contains today's date
            if today in entry.get("published", ""):
                articles.append({
                    "title": entry.title,
                    "url": entry.link,
                    "published": entry.get("published", "")
                })
    return articles

# 3. Extract, sentiment check, and summarize
def process_article(item):
    art = Article(item["url"])
    art.download(); art.parse(); art.nlp()
    text = art.text or ""
    title = art.title or item["title"]
    
    # Exclude based on keywords
    txt_l = f"{title} {text}".lower()
    if any(kw in txt_l for kw in NEGATIVE_KEYWORDS):
        return None
    
    # Sentiment intensity
    polarity = TextBlob(text).sentiment.polarity
    if polarity < 0.1:
        return None
    
    return {
        "title": title,
        "source": art.source_url or item["url"].split("/")[2],
        "timestamp": item["published"],
        "topic": art.meta_keywords or [],
        "url": item["url"],
        "summary": art.summary,
        "sentiment": polarity
    }

# 4. Save to JSON files
def save_summary(summary):
    fname = f"{summary['source']}_{summary['timestamp'].replace(' ', '_').replace(':','-')}.json"
    path = os.path.join(OUTPUT_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Saved: {path}")

def main():
    print("Fetching today's articles...")
    items = fetch_feed_articles()
    print(f"Found {len(items)} items. Processing...")
    
    processed = []
    for item in items:
        result = process_article(item)
        if result:
            processed.append(result)
    
    processed = sorted(processed, key=lambda x: x["sentiment"], reverse=True)[:5]
    print(f"Got {len(processed)} uplifting articles. Saving...")
    for s in processed:
        save_summary(s)

if __name__ == "__main__":
    main()
