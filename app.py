import streamlit as st
import joblib
import re
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# --- STEP 1: FIX NLTK DOWNLOADS ---
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

# --- STEP 2: LOAD COMPRESSED ASSETS ---
@st.cache_resource
def load_assets():
    # Ensure these files were exported from Colab using joblib.dump()
    model = joblib.load('sentiment_model.pkl')
    tfidf = joblib.load('tfidf_vectorizer.pkl')
    return model, tfidf

model, tfidf = load_assets()

# --- STEP 3: PREPROCESSING ---
def clean_text(text):
    text = re.sub(r'<.*?>', '', text) # Remove HTML
    text = re.sub('[^a-zA-Z]', ' ', text).lower() # Clean special chars
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words]
    return ' '.join(words)

# --- STEP 4: SESSION STATE (Database Memory) ---
if 'movie_db' not in st.session_state:
    st.session_state.movie_db = {
        "Inception": ["A masterpiece of sci-fi.", "The ending left me confused, but visuals were stunning."],
        "The Dark Knight": ["Heath Ledger's Joker is the greatest villain.", "Best Batman movie ever made."],
        "The Room": ["So bad it is actually funny.", "Total waste of time. I don't understand the cult following."]
    }

# --- STEP 5: STREAMLIT UI ---
st.set_page_config(page_title="Sentify Pro", page_icon="🍿", layout="wide")

st.title("🍿 Sentify Pro: Interactive Movie Sentiment Hub")
st.markdown("Analyze individual reviews or aggregate sentiment for entire movies in real-time.")

tab1, tab2, tab3 = st.tabs(["🎬 Movie Explorer", "📝 Add a Review", "🔍 Manual Tester"])

# --- TAB 1: MOVIE EXPLORER (Aggregated Sentiment) ---
with tab1:
    st.subheader("Select a Movie to Analyze Overall Sentiment")
    selected_movie = st.selectbox("Pick from our database:", list(st.session_state.movie_db.keys()))
    
    reviews = st.session_state.movie_db[selected_movie]
    
    st.markdown(f"**Current Reviews for {selected_movie}:**")
    for r in reviews:
        st.write(f"- {r}")
        
    if st.button(f"Analyze Overall Sentiment for {selected_movie}"):
        cleaned = [clean_text(r) for r in reviews]
        vecs = tfidf.transform(cleaned)
        preds = model.predict(vecs)
        
        pos_percent = (sum(preds) / len(preds)) * 100
        
        st.divider()
        col1, col2 = st.columns(2)
        col1.metric("Overall Approval", f"{pos_percent:.1f}%")
        col2.metric("Verdict", "Positive 😊" if pos_percent > 50 else "Negative ☹️")
        st.progress(pos_percent / 100)

# --- TAB 2: ADD A REVIEW (Interactive Feature) ---
with tab2:
    st.subheader("Contribute to the Database")
    target_movie = st.selectbox("Which movie are you reviewing?", list(st.session_state.movie_db.keys()), key="add_rev")
    new_review = st.text_area("Write your review here:")
    
    if st.button("Submit Review"):
        if new_review.strip():
            st.session_state.movie_db[target_movie].append(new_review)
            st.success(f"Review added to {target_movie}! Go to the Explorer tab to see the updated score.")
        else:
            st.warning("Please enter some text.")

# --- TAB 3: MANUAL TESTER ---
with tab3:
    st.subheader("Test Individual Sentences")
    user_input = st.text_area("Paste a custom review:", placeholder="The acting was great...")
    if st.button("Predict"):
        if user_input:
            res = model.predict(tfidf.transform([clean_text(user_input)]))[0]
            if res == 1:
                st.success("Positive Sentiment 😊")
            else:
                st.error("Negative Sentiment ☹️")

# Footer
st.sidebar.info("Model: Random Forest\n\nFeatures: TF-IDF + N-Grams\n\nLibrary: Scikit-Learn & NLTK")
