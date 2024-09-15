import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st
from googletrans import Translator  # Translator for language translation
from pydub import AudioSegment
import tempfile


# Initialize the Groq client
client = Groq(api_key="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")

# Initialize Google Translate API
translator = Translator()

# Streamlit frontend for audio input and translation
st.title("Audio Translation App")

# Audio file input
audio_file = st.file_uploader("Upload an audio file", type=["m4a", "mp3", "wav"])

# Text input for target language (e.g., 'hi' for Hindi, 'fr' for French)
target_language = st.text_input("Enter target language code (e.g., 'hi' for Hindi)", value="en")

# Button to trigger translation
if st.button("Translate Audio"):
    if audio_file:
        # Save the uploaded file to a temporary directory
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_file.read())
            filename = temp_file.name

        # Load the audio using pydub
        audio = AudioSegment.from_file(filename)

        # Define chunk length (10 seconds = 10000 ms)
        chunk_length_ms = 10000  # 10 seconds per chunk
        total_duration_ms = len(audio)  # Total audio duration in ms

        # Divide audio into chunks of 10 seconds
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, total_duration_ms, chunk_length_ms)]

        # Variables to store full transcription and translation
        full_transcription = ""
        full_translation = ""

        # Process each chunk
        for i, chunk in enumerate(chunks):
            # Save the chunk to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as chunk_file:
                chunk.export(chunk_file.name, format="wav")

                # Transcribe the chunk using Groq API
                with open(chunk_file.name, "rb") as file:
                    transcription = client.audio.translations.create(
                        file=(chunk_file.name, file.read()),  # Required audio file
                        model="whisper-large-v3",  # Required model for transcription
                        response_format="json",  # Optional
                        temperature=0.0  # Optional
                    )

                # Append the chunk transcription to full transcription
                chunk_transcription_text = transcription.text
                full_transcription += chunk_transcription_text + " "

                # Translate the chunk transcription
                translation = translator.translate(chunk_transcription_text, dest=target_language)

                # Append the chunk translation to full translation
                full_translation += translation.text + " "

            # Show progress on the frontend
            st.write(f"Processed chunk {i+1}/{len(chunks)}")
            st.write(f"Chunk Transcription: {chunk_transcription_text}")
            st.write(f"Chunk Translation: {translation.text}")

        # Show the final combined transcription and translation
        st.write("Final Transcription:")
        st.write(full_transcription)

        st.write(f"Final Translated Result ({target_language}):")
        st.write(full_translation)

    else:
        st.error("Please upload an audio file.")
