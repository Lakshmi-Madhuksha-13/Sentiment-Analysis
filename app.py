import streamlit as st
import json
import os
from textblob import TextBlob

# --- DATA SETTINGS ---
DB_FILE = "reviews_db.json"

def load_data():
    if not os.path.exists(DB_FILE):
        # Initialize with 30 sample products
        initial_products = {f"Product {i}": [] for i in range(1, 31)}
        return initial_products
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def get_sentiment(text):
    # Returns a sentiment label and an emoji
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return "Positive", "😊"
    elif analysis.sentiment.polarity < -0.1:
        return "Negative", "😠"
    else:
        return "Neutral", "😐"

# --- STREAMLIT UI ---
st.set_page_config(page_title="Sentiment Review Pro", layout="wide")
data = load_data()

st.title("📊 Product Review & Sentiment Predictor")
st.markdown("Submit a review, and our AI will predict the sentiment automatically.")

# --- SIDEBAR: ADD REVIEW ---
with st.sidebar:
    st.header("Add a New Review")
    prod_name = st.text_input("Product Name").strip()
    user_review = st.text_area("Write your review here...")
    
    if st.button("Submit & Predict"):
        if prod_name and user_review:
            # 1. Sentiment Prediction Logic
            label, emoji = get_sentiment(user_review)
            
            # 2. Add product if it doesn't exist
            if prod_name not in data:
                data[prod_name] = []
                st.toast(f"New product '{prod_name}' added to database!", icon="🆕")
            
            # 3. Save Review
            new_entry = {
                "review": user_review,
                "sentiment": label,
                "emoji": emoji
            }
            data[prod_name].append(new_entry)
            save_data(data)
            
            st.success(f"Predicted Sentiment: {label} {emoji}")
        else:
            st.error("Please fill in both fields.")

# --- MAIN PAGE: VIEW REVIEWS ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Select Product")
    selected_prod = st.selectbox("Choose a product to view feedback:", sorted(list(data.keys())))

with col2:
    st.subheader(f"Reviews for {selected_prod}")
    if data[selected_prod]:
        for item in reversed(data[selected_prod]): # Show newest first
            with st.expander(f"{item['emoji']} {item['sentiment']} Review"):
                st.write(f"\"{item['review']}\"")
    else:
        st.info("No reviews yet for this product.")
