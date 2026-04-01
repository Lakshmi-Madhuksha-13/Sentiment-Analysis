import streamlit as st
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download NLTK data for the cloud environment
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

# Load the saved model and vectorizer
# Ensure these files are in the same GitHub folder
model = pickle.load(open('sentiment_model.pkl', 'rb'))
tfidf = pickle.load(open('tfidf_vectorizer.pkl', 'rb'))

def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub('[^a-zA-Z]', ' ', text).lower()
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words]
    return ' '.join(words)

# --- Streamlit UI ---
st.set_page_config(page_title="Sentify AI", page_icon="🎬")
st.title("🎬 Sentify: Movie Review Classifier")
st.markdown("Analyze the sentiment of any movie review instantly using Machine Learning.")

user_input = st.text_area("Paste your review here:", height=150)

if st.button("Predict Sentiment"):
    if user_input.strip():
        cleaned = clean_text(user_input)
        vectorized = tfidf.transform([cleaned])
        prediction = model.predict(vectorized)[0]
        prob = model.predict_proba(vectorized)
        
        if prediction == 1:
            st.success(f"### Positive Sentiment 😊 (Confidence: {prob[0][1]*100:.1f}%)")
        else:
            st.error(f"### Negative Sentiment ☹️ (Confidence: {prob[0][0]*100:.1f}%)")
    else:
        st.warning("Please enter some text first!")
