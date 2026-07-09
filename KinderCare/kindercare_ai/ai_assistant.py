import os
from typing import Dict, Any, Optional
from openai import OpenAI
import json
from .prompt_templates import SYSTEM_PROMPT, SAFETY_DISCLAIMER, format_context

st.write("OpenAI key prefix:", os.getenv("OPENAI_API_KEY")[:3])
st.write("SendGrid key prefix:", os.getenv("SENDGRID_API_KEY")[:3])


class KinderCareAI:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the KinderCare AI Assistant.
        
        Args:
            api_key: OpenAI API key. If None, tries to fetch from environment variable OPENAI_API_KEY.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-3.5-turbo" # Cost-effective, change to gpt-4 if needed

    def get_ai_response(self, user_input: str, child_context: Dict[str, Any] = None, disease_context: list = None) -> str:
        """
        Get a response from the AI assistant based on user input and context.
        
        Args:
            user_input: The user's question or query.
            child_context: Dictionary containing selected child's details (vaccinations, age, etc.).
            disease_context: List of common diseases/remedies to reference.
            
        Returns:
            str: The AI's response text.
        """
        
        # 1. Prepare Context
        context_str = format_context(child_context, disease_context)
        
        # 2. Construct Messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"CURRENT CONTEXT DATA:\n{context_str}"},
            {"role": "user", "content": user_input}
        ]
        
        try:
            # 3. Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            ai_text = response.choices[0].message.content
            
            # 4. Append Disclaimer if not present (double safety)
            if "medical advice" not in ai_text.lower():
                ai_text += f"\n\n_{SAFETY_DISCLAIMER}_"
                
            return ai_text
            
        except Exception as e:
            return f"I apologize, but I'm having trouble connecting to the service right now. Error: {str(e)}"

    def transcribe_audio(self, audio_file) -> str:
        """
        Transcribe audio input to text using OpenAI Whisper.
        
        Args:
            audio_file: File-like object containing audio data.
            
        Returns:
            str: Transcribed text.
        """
        try:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            return transcript.text
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
