import streamlit as st
import os
from groq import Groq

# Initialize the Groq client
client = Groq()

# Streamlit frontend for audio input and translation
st.title("Audio Translation App")

# Audio file input
audio_file = st.file_uploader("Upload an audio file", type=["m4a", "mp3", "wav"])

# Text input for target language (just for context, although Groq handles Whisper model directly)
target_language = st.text_input("Enter target language (context)", value="en")

# Button to trigger translation
if st.button("Translate Audio"):
    if audio_file:
        # Save the uploaded file temporarily
        filename = os.path.join(os.getcwd(), audio_file.name)
        with open(filename, "wb") as f:
            f.write(audio_file.read())
        
        # Open the saved file and use Groq API to translate
        with open(filename, "rb") as file:
            translation = client.audio.translations.create(
                file=(filename, file.read()),  # Required audio file
                model="whisper-large-v3",  # Required model to use for translation
                prompt=f"Translation to {target_language}",  # Context provided for translation
                response_format="json",  # Optional
                temperature=0.0  # Optional
            )
        
        # Show the translation result on the frontend
        st.write("Translation Result:")
        st.write(translation.text)
    else:
        st.error("Please upload an audio file.")
