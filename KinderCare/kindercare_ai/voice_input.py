import streamlit as st
# Note: Users will need to install streamlit-audio-recorder
# pip install streamlit-audio-recorder
from st_audio_recorder import st_audio_recorder

def render_voice_input():
    """
    Renders the voice input component in Streamlit.
    Returns the audio bytes if recording is successful, else None.
    """
    st.markdown("### 🎙️ Voice Input")
    
    # This component returns audio bytes (wav format by default)
    audio_bytes = st_audio_recorder()
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        return audio_bytes
    
    return None
