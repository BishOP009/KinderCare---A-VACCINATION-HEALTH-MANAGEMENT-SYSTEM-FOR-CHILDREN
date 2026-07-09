import os
import streamlit as st

def get_gemini_client():
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
        if not api_key:
            return None
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",  
            system_instruction=(
                "You are KinderCare AI — a friendly, knowledgeable pediatric health assistant. "
                "You help parents with questions about child vaccinations, health milestones, "
                "common illnesses, and general child wellness. "
                "Always give clear, practical advice in simple language. "
                "Always remind parents to consult a real doctor for serious concerns. "
                "Keep responses concise and easy to read."
            )
        )
        return model
    except ImportError:
        return None

def chat_with_history(conversation_history: list) -> str:
    model = get_gemini_client()

    if model is None:
        return (
            "⚠️ AI Assistant is not configured. "
            "Please add your GOOGLE_API_KEY in Streamlit Cloud secrets."
        )

    try:
        gemini_history = []
        for msg in conversation_history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({
                "role": role,
                "parts": [msg["content"]]
            })

        chat = model.start_chat(history=gemini_history)
        last_message = conversation_history[-1]["content"]
        response = chat.send_message(last_message)
        return response.text

    except Exception as e:
        return f"⚠️ Error communicating with AI: {str(e)}"


def get_quick_responses():
    return [
        "When is my child's next vaccination due?",
        "What should I do if my child has a fever?",
        "What are common side effects after vaccination?",
        "When should I take my child to a doctor immediately?"
    ]
