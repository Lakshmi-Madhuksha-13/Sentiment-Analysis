import streamlit as st
import joblib
import re
import nltk
import requests
import pandas as pd
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# --- Setup & Data Loading ---
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

@st.cache_resource
def load_assets():
    model = joblib.load('sentiment_model.pkl')
    tfidf = joblib.load('tfidf_vectorizer.pkl')
    return model, tfidf

model, tfidf = load_assets()

def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub('[^a-zA-Z]', ' ', text).lower()
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words]
    return ' '.join(words)

# --- NEW: Scraping Function ---
def scrape_reviews(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        # This selector works for many common review sites; adjust as needed
        reviews = [g.text for g in soup.find_all('div', class_='text show-more__control')] 
        return reviews
    except Exception as e:
        return []

# --- UI ---
st.set_page_config(page_title="Movie Pulse AI", layout="wide")
st.title("🎬 Movie Pulse: Bulk Sentiment Aggregator")

tab1, tab2 = st.tabs(["Analyze URL (Bulk)", "Manual Input"])

# TAB 1: BULK ANALYSIS
with tab1:
    st.subheader("Analyze Overall Movie Sentiment")
    movie_url = st.text_input("Paste an IMDb User Reviews URL:", placeholder="https://www.imdb.com/title/tt1375666/reviews")
    
    if st.button("Aggregate Reviews"):
        if movie_url:
            with st.spinner("Scraping and analyzing reviews..."):
                raw_reviews = scrape_reviews(movie_url)
                if raw_reviews:
                    # Predict all
                    cleaned = [clean_text(r) for r in raw_reviews]
                    vecs = tfidf.transform(cleaned)
                    preds = model.predict(vecs)
                    
                    # Calculate Metrics
                    pos_count = sum(preds)
                    total = len(preds)
                    pos_percent = (pos_count / total) * 100
                    
                    # Dashboard
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Reviews Found", total)
                    col2.metric("Positive Sentiment", f"{pos_percent:.1f}%")
                    col3.metric("Negative Sentiment", f"{100-pos_percent:.1f}%")
                    
                    if pos_percent > 60:
                        st.success(f"### Verdict: Highly Recommended! 😊")
                    elif pos_percent > 40:
                        st.warning(f"### Verdict: Mixed Reviews 😐")
                    else:
                        st.error(f"### Verdict: Mostly Negative ☹️")
                else:
                    st.error("Could not find reviews. Ensure the URL is correct and public.")
        else:
            st.warning("Please enter a valid URL.")

# TAB 2: MANUAL INPUT
with tab2:
    st.subheader("Test a Single Review")
    user_input = st.text_area("Review text:")
    if st.button("Predict"):
        res = model.predict(tfidf.transform([clean_text(user_input)]))[0]
        st.write("Positive" if res == 1 else "Negative")
