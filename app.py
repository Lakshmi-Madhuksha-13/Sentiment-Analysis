import streamlit as st
import joblib  # Using joblib because your file was too large
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# 1. Setup NLTK (Required for cloud)
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

# 2. Load the Compressed Files
# Make sure you exported these from Colab using joblib.dump()
model = joblib.load('sentiment_model.pkl')
tfidf = joblib.load('tfidf_vectorizer.pkl')

def clean_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub('[^a-zA-Z]', ' ', text).lower()
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words]
    return ' '.join(words)

# 3. Streamlit UI
st.set_page_config(page_title="Sentify AI", page_icon="🎬")
st.title("🎬 Sentify: Movie Review Classifier")

user_input = st.text_area("Paste your movie review here:", height=150)

if st.button("Predict Sentiment"):
    if user_input.strip():
        # Process input
        cleaned = clean_text(user_input)
        vectorized = tfidf.transform([cleaned])
        
        # Predict
        prediction = model.predict(vectorized)[0]
        prob = model.predict_proba(vectorized)
        
        # Display Result
        if prediction == 1:
            st.success(f"### Positive Sentiment 😊 (Confidence: {prob[0][1]*100:.1f}%)")
        else:
            st.error(f"### Negative Sentiment ☹️ (Confidence: {prob[0][0]*100:.1f}%)")
    else:
        st.warning("Please enter some text first!")
