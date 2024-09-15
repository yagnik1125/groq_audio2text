import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st
import googletrans 
from pydub import AudioSegment
import tempfile


# Initialize the Groq client
client = Groq(api_key="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")

# Initialize Google Translate API
translator = googletrans.Translator()

# Streamlit frontend for audio input and translation
st.title("Audio Translation App")

# Audio file input
uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "ogg", "flac", "m4a"])


languages = googletrans.LANGUAGES
language_options = list(languages.values())
selected_lang = st.selectbox("Select the target language for translation", language_options)

# # Text input for target language (e.g., 'hi' for Hindi, 'fr' for French)
# target_language = st.text_input("Enter target language code (e.g., 'hi' for Hindi)", value="en")

# Button to trigger translation
if st.button("Translate Audio"):
    if uploaded_file is not None:
        # Save the uploaded file to a temporary directory
        with open("temp_audio_file", "wb") as f:
            f.write(uploaded_file.getbuffer())
        audio_path = "temp_audio_file"

        # Load the audio using pydub
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1)  # Ensure mono channel
        audio = audio.set_frame_rate(16000)  # Ensure frame rate is 16000 Hz

        # Get the language code
        selected_lang_code = list(languages.keys())[language_options.index(selected_lang)]

        # Split the audio into chunks (10 sec per chunk)
        chunk_duration_ms = 10000  
        chunks = [audio[i:i + chunk_duration_ms] for i in range(0, len(audio), chunk_duration_ms)]

        # Variables to store full transcription and translation
        full_transcription = ""
        full_translation = ""

        # Process each chunk
        for i, chunk in enumerate(chunks):
            # Save the chunk to a temporary file
            chunk_filename = f"chunk_{i}.wav"
            chunk.export(chunk_filename, format="wav")

            # Transcribe the chunk using Groq API
            with open(chunk_filename, "rb") as file:
                transcription = client.audio.translations.create(
                    file=(chunk_filename, file.read()),  # Required audio file
                    model="whisper-large-v3",  # Required model for transcription
                    response_format="json",  # Optional
                    temperature=0.0  # Optional
                )
            # Append the chunk transcription to full transcription
            chunk_transcription_text = transcription.text
            full_transcription += chunk_transcription_text + " "
            # Translate the chunk transcription
            translation = translator.translate(chunk_transcription_text, dest=selected_lang_code)
            # Append the chunk translation to full translation
            full_translation += translation.text + " "

            # Show progress on the frontend
            st.write(f"Processed chunk {i+1}/{len(chunks)}")
            st.write(f"Chunk Transcription: {chunk_transcription_text}")
            st.write(f"Chunk Translation: {translation.text}")

        # Show the final combined transcription and translation
        st.write("Final Transcription:")
        st.write(full_transcription)

        st.write(f"Final Translated Result ({selected_lang}):")
        st.write(full_translation)

    else:
        st.error("Please upload an audio file.")
