import streamlit as st
import os
from kindercare_ai.ai_assistant import KinderCareAI
from kindercare_ai.voice_input import render_voice_input
import io

# 1. Initialize AI Module
# Ensure OPENAI_API_KEY is in your .env or Streamlit secrets
if "ai_assistant" not in st.session_state:
    try:
        # You can pass api_key explicitly or set it in env
        # api_key = st.secrets["OPENAI_API_KEY"] 
        st.session_state.ai_assistant = KinderCareAI() 
    except ValueError as e:
        st.error(f"AI Setup Error: {e}")
        st.stop()

st.title("🤖 KinderCare AI Assistant")

# 2. Gather Context (Example - fetch this from your DB in the real app)
# from database import get_child, get_vaccinations...
from database import get_child, get_vaccinations
from vaccination_guidelines import categorize_vaccinations, get_age_string
from datetime import date

child = get_child(st.session_state.selected_child_id)
vaccinations = get_vaccinations(st.session_state.selected_child_id)
categories = categorize_vaccinations(vaccinations)

dob = child["date_of_birth"]
if isinstance(dob, str):
    dob = date.fromisoformat(dob)

child_context = {
    "name": child["name"],
    "age_display": get_age_string(dob),
    "upcoming_vaccines": categories["upcoming"],
    "overdue_vaccines": categories["overdue"]
}


# Load disease data from your JSON
import os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "disease_information_database.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    disease_db = json.load(f)


# 3. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Voice Input (Optional)
audio_input = render_voice_input()
transcript = ""

if audio_input:
    with st.spinner("Transcribing..."):
        # Create a file-like object for Whisper
        audio_file = io.BytesIO(audio_input)
        audio_file.name = "audio.wav"
        transcript = st.session_state.ai_assistant.transcribe_audio(audio_file)
        if transcript:
            st.info(f"You said: {transcript}")

# 5. User Input (Text or Voice Transcript)
user_query = st.chat_input("Ask about vaccines, symptoms, or remedies...")

final_input = user_query or (transcript if audio_input else None)

if final_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    # Get AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.ai_assistant.get_ai_response(
                user_input=final_input,
                child_context=child_context,
                disease_context=disease_db
            )
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- Integration Instructions ---
# 1. Copy the 'kindercare_ai' folder to your project root.
# 2. Install requirements: pip install openai streamlit-audio-recorder
# 3. Set OPENAI_API_KEY in your environment or .streamlit/secrets.toml
# 4. In your 'pages/assistant.py', import and use logic similar to above.
