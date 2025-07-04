import os
import re
import nltk
import pandas as pd
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
from wordcloud import WordCloud

# Initialize NLTK resources
nltk.download('stopwords')
nltk.download('punkt')

# Retrieve YouTube API key from environment variable
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")

# Set up YouTube API client
YOUTUBE = build('youtube', 'v3', developerKey=API_KEY)

# Define sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Fetch trending Shorts
def fetch_trending_shorts(region_code='US', max_results=10):
    request = YOUTUBE.videos().list(
        part='snippet,statistics',
        chart='mostPopular',
        regionCode=region_code,
        videoCategoryId='0',  # '0' for all categories
        maxResults=max_results
    )
    response = request.execute()
    return response['items']

# Analyze sentiment of comments
def analyze_sentiment(comments):
    sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}
    for comment in comments:
        score = analyzer.polarity_scores(comment)
        if score['compound'] >= 0.05:
            sentiments['positive'] += 1
        elif score['compound'] <= -0.05:
            sentiments['negative'] += 1
        else:
            sentiments['neutral'] += 1
    return sentiments

# Extract keywords from text
def extract_keywords(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return filtered_words

# Generate word cloud
def generate_word_cloud(keywords):
    word_freq = Counter(keywords)
    wordcloud = WordCloud(width=800, height=400).generate_from_frequencies(word_freq)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

# Main function to gather insights
def main():
    shorts = fetch_trending_shorts()
    all_comments = []
    all_keywords = []

    for short in shorts:
        title = short['snippet']['title']
        video_id = short['id']
        print(f"Analyzing: {title}")

        # Fetch comments
        comments = []  # Replace with actual comment fetching logic
        all_comments.extend(comments)

        # Extract keywords
        keywords = extract_keywords(title)
        all_keywords.extend(keywords)

        # Analyze sentiment
        sentiments = analyze_sentiment(comments)
        print(f"Sentiment Analysis: {sentiments}")

    # Generate word cloud for keywords
    generate_word_cloud(all_keywords)

    # Display overall sentiment distribution
    sentiment_counts = Counter([analyze_sentiment([comment]) for comment in all_comments])
    plt.bar(sentiment_counts.keys(), sentiment_counts.values())
    plt.title('Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.show()

if __name__ == '__main__':
    main()
