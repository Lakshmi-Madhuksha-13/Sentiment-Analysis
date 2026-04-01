import streamlit as st
import json
import os
import random
from textblob import TextBlob

# --- CONFIGURATION ---
DB_FILE = "product_database.json"

# --- DATA SEEDING (Varied Reviews per Product) ---
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

    # Specialized Review Pools
    pos_pool = [
        "Absolutely incredible, best purchase I've made this year!",
        "Works exactly as advertised, very happy with the performance.",
        "High quality build and premium feel. Worth every penny.",
        "Exceeded my expectations in every way. Highly recommend.",
        "Fast shipping and great performance so far.",
        "Beautiful design and works seamlessly with my other devices.",
        "I can't imagine my daily routine without this anymore!"
    ]
    
    neu_pool = [
        "It's okay, does the job but nothing special or groundbreaking.",
        "Average product for an average price. Not bad, not great.",
        "A bit overpriced for what you get, but it is functional.",
        "Decent quality, though the initial setup was a bit tricky.",
        "Not bad, but I have seen better alternatives for less money.",
        "It works, but the software interface is a bit dated.",
        "Does what it says on the box, nothing more, nothing less."
    ]
    
    neg_pool = [
        "Worst experience ever, the device broke after only two days.",
        "Total waste of money, do not buy this product!",
        "Very disappointed with the build quality and materials used.",
        "Customer service was unhelpful and the product is clearly flawed.",
        "I really regret buying this, it's very glitchy and unreliable.",
        "Battery life is terrible compared to what was promised.",
        "It feels cheap and definitely not worth the premium price."
    ]

    db = {}
    for product in real_products:
        # Create a unique mix for every product (e.g., 12 to 15 reviews each)
        count = random.randint(12, 15)
        product_reviews = []
        
        for _ in range(count):
            # Randomly pick from the three pools to create a unique sentiment profile
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

# --- SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'browse'

# --- UI SETUP ---
st.set_page_config(page_title="AI Product Insight Engine", layout="wide")
data = load_data()

st.title("🤖 Smart Product Insight Engine")
st.markdown("Analyze consumer sentiment for real-world products using AI.")

# Navigation
col_nav1, col_nav2, _ = st.columns([1.5, 1.5, 7])
with col_nav1:
    if st.button("🔍 Browse & Analyze", use_container_width=True):
        st.session_state.page = 'browse'
with col_nav2:
    if st.button("✍️ Add Product Review", use_container_width=True):
        st.session_state.page = 'add'

st.divider()

# --- PAGE: BROWSE & ANALYZE ---
if st.session_state.page == 'browse':
    st.header("Search & Explore Reviews")
    selected_prod = st.selectbox("Select a Product:", sorted(data.keys()))
    
    reviews = data[selected_prod]
    st.info(f"Showing **{len(reviews)}** randomized reviews for **{selected_prod}**")
    
    for i, r in enumerate(reversed(reviews)):
        with st.container(border=True):
            st.write(f"**Review #{len(reviews)-i}:** \"{r['review']}\"")
            
            if st.button(f"Analyze Sentiment for Review #{len(reviews)-i}", key=f"btn_{i}"):
                label, emoji = get_prediction(r['review'])
                st.success(f"**AI Prediction:** This review is **{label} {emoji}**")

# --- PAGE: ADD REVIEW ---
elif st.session_state.page == 'add':
    st.header("Contribute a Review")
    st.write("Enter a product name. If it isn't in our list of 30, it will be added automatically.")
    
    with st.form("new_review_form"):
        p_name = st.text_input("Product Name", placeholder="e.g. iPhone 15 Pro").strip()
        r_content = st.text_area("Your Review", placeholder="Share your experience...")
        
        submitted = st.form_submit_button("Save Review")
        
        if submitted:
            if p_name and r_content:
                if p_name not in data:
                    data[p_name] = []
                    st.toast(f"New product '{p_name}' created!", icon="✨")
                
                data[p_name].append({"review": r_content})
                save_data(data)
                st.success(f"Review for '{p_name}' saved!")
                st.balloons()
            else:
                st.error("Both product name and review content are required.")
