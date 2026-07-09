import streamlit as st
import json
import os

def load_diseases_data():
    
    # Resolve project root directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(BASE_DIR, "data", "disease_information_database.json")

    if not os.path.exists(json_path):
        st.error(f"Disease database file not found at: {json_path}")
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        st.error(f"Error reading disease database: {e}")
        return []

    # Support multiple JSON structures
    if isinstance(data, dict):
        if "diseases" in data and isinstance(data["diseases"], list):
            return data["diseases"]
        else:
            # Convert dict-based structure to list
            return [{"name": k, **v} for k, v in data.items() if isinstance(v, dict)]

    if isinstance(data, list):
        return data

    return []


def render():
    st.markdown("""
    <style>
        [data-testid="stExpander"] summary {
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 1.05em !important;
        }
        [data-testid="stExpander"] details[open] > summary {
            background-color: transparent !important;
            color: #ffffff !important;
        }
        [data-testid="stExpander"] p {
            color: #000000 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 style="color:#667eea;margin-top:0;">🏥 Common Child Diseases & Remedies</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#000;">Learn about common childhood illnesses, their symptoms, and recommended treatments</p>', unsafe_allow_html=True)

    diseases_data = load_diseases_data()

    if not diseases_data:
        st.warning("Unable to load disease information. Please try again later.")
        return

    st.divider()

    for disease in diseases_data:
        name = disease.get("name") or disease.get("disease_name", "Unknown Disease")
        emoji = disease.get("emoji", "🩺")

        symptoms = disease.get("symptoms", [])
        causes = disease.get("causes", "Information not available")
        remedies = disease.get("home_remedies", [])
        prevention = disease.get("prevention", [])
        doctor_note = disease.get("when_to_see_doctor", "Consult a healthcare professional if symptoms persist.")

        symptoms_formatted = "<br>• ".join(symptoms)
        remedies_formatted = "<br>• ".join(remedies)
        prevention_formatted = "<br>• ".join(prevention)

        with st.expander(f"{emoji} {name}", expanded=False):
            st.markdown(f"""
            <div style="color:#000;">
                <p><strong>What causes it?</strong><br>{causes}</p>
                <p><strong>Symptoms:</strong><br>• {symptoms_formatted}</p>
                <p><strong>Home Remedies:</strong><br>• {remedies_formatted}</p>
                <p><strong>When to See a Doctor:</strong><br>{doctor_note}</p>
                <p><strong>Prevention:</strong><br>• {prevention_formatted}</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="background:#f0f7ff;border-left:4px solid #667eea;padding:1.5rem;border-radius:8px;">
        <h3 style="color:#667eea;margin:0 0 0.5rem 0;">⚕️ Important Disclaimer</h3>
        <p style="color:#333;margin:0;">
            This information is for educational purposes only and should not replace professional medical advice.
            Always consult a qualified pediatrician for medical concerns.
        </p>
    </div>
    """, unsafe_allow_html=True)
