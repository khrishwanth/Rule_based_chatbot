

import json
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import string
import ssl
nltk.download('punkt')
nltk.download('wordnet')
import streamlit as st

with open('C:\\Users\\gokul\\Music\\chatbot\changed1_intent.json', 'r') as json_file:
    data = json.load(json_file)

lemmatizer = WordNetLemmatizer()
documents = []
patterns = []

# Preprocess patterns and tags
dic = dict((ord(punct), None) for punct in string.punctuation)
for intent in data['intents']:
    for pattern in intent['patterns']:
        documents.append((pattern, intent['tag']))
        patterns.append(pattern.lower().translate(dic))

# Train TF-IDF
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(patterns)

# Define response function
def response(user_response):
    lemmatized_response = lemmatizer.lemmatize(user_response.lower().translate(dic))
    user_tfidf = vectorizer.transform([lemmatized_response])
    similarity_scores = cosine_similarity(user_tfidf, X).flatten()
    best_match_idx = similarity_scores.argmax()
    highest_score = similarity_scores[best_match_idx]

    if highest_score == 0:
        return "I am sorry, I don't understand you."
    else:
        return documents[best_match_idx][1]  # Return best-matching tag

# Define chatbot function
def chatbot(user_input):
    tag_or_message = response(user_input)
    if "I am sorry" in tag_or_message:
        return tag_or_message

    for intent in data['intents']:
        if intent['tag'] == tag_or_message:
            return random.choice(intent['responses'])

    return "I'm sorry, I couldn't find a matching response."

# Handle SSL for Streamlit
ssl._create_default_https_context = ssl._create_unverified_context

def main():
    # Set up the chatbot interface
    st.title("Chatbot")
    st.write("Welcome to the chatbot. Please type a message and press Enter to start the conversation.")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Define a callback to handle user input
    def process_user_input():
        user_input = st.session_state["user_input"]
        response = chatbot(user_input)  # Get response from chatbot
        st.session_state.messages.append({"user": user_input})
        st.session_state.messages.append({"bot": response})
        st.session_state["user_input"] = ""  # Clear the input

    # User input box with on_change callback
    st.text_input("You:", key="user_input", on_change=process_user_input)

# Display conversation history inside the container
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if "user" in msg:
            st.write(f"🙂 You: {msg['user']}")
        elif "bot" in msg:
            st.write(f"🤖 Chatbot: {msg['bot']}")



    # Check if the chatbot's response is a goodbye message
    if st.session_state.messages and st.session_state.messages[-1]["bot"].lower() in ['goodbye', 'bye']:
        st.write("Thank you for chatting with me. Have a great day!")
        st.stop()  # Stop the app

if __name__ == '__main__':
    main()