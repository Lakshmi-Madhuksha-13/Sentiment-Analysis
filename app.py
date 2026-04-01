import streamlit as st
import json
import os
import random
from textblob import TextBlob

# --- CONFIGURATION ---
DB_FILE = "product_database.json"

# --- DATA SEEDING ---
def seed_data():
    real_products = [
        "Apple iPhone 15 Pro", "Samsung Galaxy S24 Ultra", "Sony WH-1000XM5", 
        "MacBook Air M3", "Dell XPS 13", "Nintendo Switch OLED", 
        "Amazon Kindle Paperwhite", "Logitech MX Master 3S", "Apple AirPods Pro 2", 
        "PlayStation 5", "Bose QC Ultra", "Google Pixel 8 Pro", 
        "Dyson V15 Detect", "GoPro Hero 12", "Razer BlackWidow V4",
        "ASUS ROG Zephyrus G14", "Instant Pot Duo", "Fitbit Charge 6", 
        "Philips Hue Kit", "Sonos Beam Gen 2", "Anker 737 Power Bank", 
        "Surface Pro 9", "Canon EOS R6 Mark II", "LG C3 OLED TV", 
        "Corsair Vengeance RAM", "WD Black SN850X SSD", "Elgato Stream Deck", 
        "SteelSeries Arctis Nova", "Ember Mug 2", "Tesla Wall Connector"
    ]

    pos_pool = ["Absolutely incredible, best purchase ever!", "Works exactly as advertised.", "High quality build."]
    neu_pool = ["It's okay, nothing special.", "Average product for the price.", "Decent quality."]
    neg_pool = ["Worst experience ever.", "Total waste of money.", "Very disappointed with the quality."]

    db = {}
    for product in real_products:
        count = random.randint(12, 15)
        product_reviews = []
        for _ in range(count):
            pool = random.choice([pos_pool, neu_pool, neg_pool])
            product_reviews.append({"review": random.choice(pool)})
        db[product] = product_reviews
    return db

def load_data():
    if not os.path.exists(DB_FILE):
        data = seed_data()
        with open(DB_FILE, "w") as f:
            json.dump(data, f)
        return data
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def get_prediction(text):
    pol = TextBlob(text).sentiment.polarity
    if pol > 0.1: return "Positive", "😊"
    if pol < -0.1: return "Negative", "😠"
    return "Neutral", "😐"

# --- NAVIGATION LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_home():
    st.session_state.page = 'home'

# --- UI SETUP ---
st.set_page_config(page_title="AI Product Hub", layout="wide")
data = load_data()

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.title("🤖 Welcome to the AI Product Insight Hub")
    st.subheader("What would you like to do today?")
    st.write("Our AI engine allows you to explore thousands of reviews or contribute your own to our catalog of 30+ real-world products.")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("### 🔍 Browse & Analyze")
        st.write("View existing reviews for products like iPhone, PS5, and Dyson. Use our AI to predict the sentiment of any review instantly.")
        if st.button("Explore Reviews", use_container_width=True):
            st.session_state.page = 'browse'
            st.rerun()

    with col2:
        st.success("### ✍️ Add a Review")
        st.write("Share your experience. If a product isn't in our database, you can create it on the fly and leave the very first review.")
        if st.button("Write a Review", use_container_width=True):
            st.session_state.page = 'add'
            st.rerun()

# --- PAGE: BROWSE ---
elif st.session_state.page == 'browse':
    if st.button("⬅️ Back to Home"):
        go_home()
        st.rerun()
        
    st.header("Search & Analyze Feedback")
    selected_prod = st.selectbox("Select a Product:", sorted(data.keys()))
    
    reviews = data[selected_prod]
    st.write(f"Total reviews: **{len(reviews)}**")
    
    for i, r in enumerate(reversed(reviews)):
        with st.container(border=True):
            st.write(f"**Review Content:** \"{r['review']}\"")
            if st.button(f"Analyze Sentiment for Review #{len(reviews)-i}", key=f"btn_{i}"):
                label, emoji = get_prediction(r['review'])
                st.success(f"**AI Prediction:** {label} {emoji}")

# --- PAGE: ADD ---
elif st.session_state.page == 'add':
    if st.button("⬅️ Back to Home"):
        go_home()
        st.rerun()
        
    st.header("Contribute to the Catalog")
    with st.form("add_form"):
        p_name = st.text_input("Product Name").strip()
        r_content = st.text_area("Your Review")
        if st.form_submit_button("Save & Submit"):
            if p_name and r_content:
                if p_name not in data:
                    data[p_name] = []
                data[p_name].append({"review": r_content})
                save_data(data)
                st.success("Review Saved!")
                st.balloons()
            else:
                st.error("Please fill in all fields.")
