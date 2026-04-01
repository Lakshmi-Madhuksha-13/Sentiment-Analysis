import streamlit as st
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# --- STEP 1: FIX NLTK DOWNLOADS FOR CLOUD ---
# This block ensures the data is downloaded before the app tries to use it
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Initialize NLP tools
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

# --- STEP 2: LOAD MODEL ASSETS ---
# Using joblib to handle compressed files (better for large Random Forest models)
@st.cache_resource # This keeps the model in memory so the app stays fast
def load_assets():
    model = joblib.load('sentiment_model.pkl')
    tfidf = joblib.load('tfidf_vectorizer.pkl')
    return model, tfidf

model, tfidf = load_assets()

# --- STEP 3: PREPROCESSING FUNCTION ---
def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove non-alphabetic characters and lowercase
    text = re.sub('[^a-zA-Z]', ' ', text).lower()
    # Tokenize, remove stopwords, and apply Stemming
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words]
    return ' '.join(words)

# --- STEP 4: STREAMLIT USER INTERFACE ---
st.set_page_config(page_title="Sentify AI", page_icon="🎬", layout="centered")

st.title("🎬 Sentify: Movie Review Classifier")
st.markdown("""
Welcome to **Sentify**! This AI uses a *Random Forest* machine learning model 
to determine if a movie review is positive or negative.
""")

# Text input area
user_input = st.text_area("Paste your movie review here:", height=150, placeholder="The acting was incredible, but the script felt a bit rushed...")

if st.button("Predict Sentiment"):
    if user_input.strip():
        with st.spinner('Analyzing sentiment...'):
            # 1. Preprocess the input
            cleaned_text = clean_text(user_input)
            
            # 2. Vectorize the input
            vectorized_input = tfidf.transform([cleaned_text])
            
            # 3. Make Prediction
            prediction = model.predict(vectorized_input)[0]
            probabilities = model.predict_proba(vectorized_input)
            
            # 4. Display Results
            st.divider()
            if prediction == 1:
                st.success(f"### Result: Positive Sentiment 😊")
                st.write(f"**Confidence Level:** {probabilities[0][1]*100:.2f}%")
            else:
                st.error(f"### Result: Negative Sentiment ☹️")
                st.write(f"**Confidence Level:** {probabilities[0][0]*100:.2f}%")
    else:
        st.warning("Please enter a review before clicking predict.")

# Footer info
st.sidebar.markdown("---")
st.sidebar.info("Model: Random Forest\n\nFeatures: TF-IDF N-Grams\n\nDataset: IMDb 50k Reviews")
