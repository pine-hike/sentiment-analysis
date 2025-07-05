from gnews import GNews
from newspaper import Article
from textblob import TextBlob
import json, os
from datetime import date

OUTPUT = "uplift_news"
os.makedirs(OUTPUT, exist_ok=True)
google_news = GNews(
    language='en',               # English-language articles (change to 'de', 'es', etc. as needed)
    country='ALL',               # Special flag for global coverage
    period='2d',                 # Last 1 day
    max_results=10              # Fetch up to 100 articles
)

def fetch_positive():
    today = date.today().isoformat()
    search =  google_news.get_top_news()
    items = [i for i in search]
    result = []
    for entry in items:
        art = Article(entry["url"])
        art.download(); art.parse(); art.nlp()
        text = art.text.lower()
        if any(kw in text for kw in ["war","crime","conflict"]):
            continue
        if TextBlob(text).sentiment.polarity < 0.1:
            continue
        result.append({
            "title": art.title,
            "source": entry.get("source"),
            "timestamp": entry.get("published date"),
            "topic": entry.get("topic", "General"),
            "url": entry.get("url"),
            "summary": art.summary
        })
    print(f"Found {len(result)} articles.")
    return sorted(result, key=lambda x: TextBlob(x["summary"]).sentiment.polarity, reverse=True)[:5]

def save(item):
    fname = f"{item['title'][:50].replace(' ','_')}.json"
    with open(os.path.join(OUTPUT, fname), "w", encoding="utf-8") as f:
        json.dump(item, f, indent=2)
    print("Saved:", fname)

if __name__=="__main__":
    for art in fetch_positive():
        save(art)
