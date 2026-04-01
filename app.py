import streamlit as st
import json
import os
from textblob import TextBlob

# --- DATA STORAGE ---
DB_FILE = "product_reviews.json"

def load_data():
    if not os.path.exists(DB_FILE):
        # 30 Real Product Names with default reviews
        default_products = {
            "Apple iPhone 15": [{"review": "Amazing camera and fast performance.", "sentiment": "Positive", "emoji": "😊"}],
            "Samsung Galaxy S24": [{"review": "Great screen, but the battery life is average.", "sentiment": "Neutral", "emoji": "😐"}],
            "Sony WH-1000XM5": [{"review": "The noise cancelling is world-class.", "sentiment": "Positive", "emoji": "😊"}],
            "MacBook Air M3": [{"review": "Super light and incredibly powerful.", "sentiment": "Positive", "emoji": "😊"}],
            "Dell XPS 13": [{"review": "Beautiful design but it gets a bit hot.", "sentiment": "Neutral", "emoji": "😐"}],
            "Nintendo Switch OLED": [{"review": "The screen makes games look vibrant.", "sentiment": "Positive", "emoji": "😊"}],
            "Kindle Paperwhite": [{"review": "Best way to read books, period.", "sentiment": "Positive", "emoji": "😊"}],
            "Logitech MX Master 3S": [{"review": "Very ergonomic and smooth scrolling.", "sentiment": "Positive", "emoji": "😊"}],
            "AirPods Pro 2": [{"review": "Seamless connection with my phone.", "sentiment": "Positive", "emoji": "😊"}],
            "PlayStation 5": [{"review": "The controller haptics are next gen.", "sentiment": "Positive", "emoji": "😊"}],
            "Bose QuietComfort Ultra": [{"review": "Extremely comfortable for long flights.", "sentiment": "Positive", "emoji": "😊"}],
            "Google Pixel 8 Pro": [{"review": "The AI features are actually useful.", "sentiment": "Positive", "emoji": "😊"}],
            "Dyson V15 Detect": [{"review": "Expensive, but it cleans better than any other vacuum.", "sentiment": "Positive", "emoji": "😊"}],
            "GoPro Hero 12": [{"review": "Stabilization is great, but it overheats in 4K.", "sentiment": "Negative", "emoji": "😠"}],
            "Razer BlackWidow V4": [{"review": "Clicky and responsive, love the RGB.", "sentiment": "Positive", "emoji": "😊"}],
            "ASUS ROG Zephyrus G14": [{"review": "Best gaming laptop for portability.", "sentiment": "Positive", "emoji": "😊"}],
            "Instant Pot Duo": [{"review": "Saves me so much time in the kitchen.", "sentiment": "Positive", "emoji": "😊"}],
            "Fitbit Charge 6": [{"review": "Tracking is accurate but the strap is annoying.", "sentiment": "Neutral", "emoji": "😐"}],
            "Philips Hue Starter Kit": [{"review": "Overpriced for just some light bulbs.", "sentiment": "Negative", "emoji": "😠"}],
            "Sonos Beam Gen 2": [{"review": "Crisp sound for a compact soundbar.", "sentiment": "Positive", "emoji": "😊"}],
            "Anker 737 Power Bank": [{"review": "Fast charging and huge capacity.", "sentiment": "Positive", "emoji": "😊"}],
            "Microsoft Surface Pro 9": [{"review": "Good for drawing, but keyboard sold separately is annoying.", "sentiment": "Neutral", "emoji": "😐"}],
            "Canon EOS R6": [{"review": "Perfect for low light photography.", "sentiment": "Positive", "emoji": "😊"}],
            "LG C3 OLED TV": [{"review": "Perfect blacks and amazing for gaming.", "sentiment": "Positive", "emoji": "😊"}],
            "Corsair Vengeance RAM": [{"review": "Reliable and fast for my PC build.", "sentiment": "Positive", "emoji": "😊"}],
            "WD Black SN850X SSD": [{"review": "Load times in games are non-existent now.", "sentiment": "Positive", "emoji": "😊"}],
            "Elgato Stream Deck": [{"review": "Essential for my productivity workflow.", "sentiment": "Positive", "emoji": "😊"}],
            "SteelSeries Arctis Nova Pro": [{"review": "Audio quality is great, but price is high.", "sentiment": "Neutral", "emoji": "😐"}],
            "Ember Mug 2": [{"review": "Battery died after only 3 months. Disappointing.", "sentiment": "Negative", "emoji": "😠"}],
            "Tesla Wall Connector": [{"review": "Works perfectly for home charging.", "sentiment": "Positive", "emoji": "😊"}],
        }
        with open(DB_FILE, "w") as f:
            json.dump(default_products, f)
        return default_products
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def predict_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return "Positive", "😊"
    elif analysis.sentiment.polarity < -0.1:
        return "Negative", "😠"
    else:
        return "Neutral", "😐"

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Product Sentiment Hub", layout="wide")
data = load_data()

st.title("🛒 Real-World Product Review & Sentiment Analysis")
st.markdown("Select a real product or add your own. The AI will predict the sentiment of your review instantly.")

# --- MAIN LAYOUT ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("📝 Add a Review")
    
    # Text input for product (can be existing or new)
    product_name = st.text_input("Product Name (Type to add new or select below)", placeholder="e.g. iPhone 15 or New Product")
    
    # Suggestion box from existing list
    selected_from_list = st.selectbox("Or choose from existing catalog:", ["---"] + sorted(list(data.keys())))
    
    # Priority logic: if box is selected, use it; if text is typed, use that.
    final_name = product_name if product_name else (selected_from_list if selected_from_list != "---" else "")
    
    review_text = st.text_area("Your Review Content", placeholder="What do you think about this product?", height=150)
    
    if st.button("Submit & Analyze Sentiment", use_container_width=True):
        if final_name and review_text:
            label, emoji = predict_sentiment(review_text)
            
            # Add to data if missing
            if final_name not in data:
                data[final_name] = []
                st.toast(f"'{final_name}' added as a new product!", icon="✨")
            
            # Save the review
            data[final_name].append({"review": review_text, "sentiment": label, "emoji": emoji})
            save_data(data)
            
            st.success(f"**Prediction:** This review is **{label}** {emoji}")
        else:
            st.warning("Please provide both a product name and a review.")

with col2:
    st.header("🔍 Browse Reviews")
    
    browse_name = st.selectbox("Select a product to view its history:", sorted(list(data.keys())), key="browse")
    
    if data[browse_name]:
        st.write(f"Showing {len(data[browse_name])} reviews for **{browse_name}**:")
        for r in reversed(data[browse_name]):
            with st.container(border=True):
                st.markdown(f"**{r['emoji']} {r['sentiment']}**")
                st.write(r['review'])
    else:
        st.info("This product has no reviews yet. Be the first to write one!")
