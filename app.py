import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st
# import googletrans 
from streamlit_mic_recorder import mic_recorder
from pydub import AudioSegment
import tempfile
import wave
import io


# Initialize the Groq client
client = Groq(api_key="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")

# # Initialize Google Translate API
# translator = googletrans.Translator()

# Streamlit frontend for audio input and translation
st.title("Audio Translation App")

# Audio file input
uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "ogg", "flac", "m4a"])
st.audio(uploaded_file, format="wav")
mic_audio = mic_recorder(start_prompt="🎙️ Start Recording", stop_prompt="🎙️ Stop Recording", key='recorder')
if mic_audio:
    st.write("mic audio through bytes")
    st.audio(mic_audio['bytes'], format='wav')
mic_audio_file_name='temp_mic_audio.wav'
if mic_audio:
    # Get the byte data from the audio recorder
    audio_bytes = mic_audio['bytes']
    audio_file_like = io.BytesIO(audio_bytes)
    with wave.open(mic_audio_file_name, 'wb') as wav_file:
        sample_width = 2  # Sample width in bytes (16 bits)
        channels = 1      # Mono
        framerate = 44100 # Sample rate

        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(framerate)
        wav_file.writeframes(audio_bytes)
    # st.write("mic audio through wav")
    # st.audio(audio_file_like, format='wav')

def translate_text(text, targ_lang):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"Translate this text to '{targ_lang}'. Text:{text}. ONLY RETURN TRANSLATED TEXT DO NOT WRITE ANYTHING ELSE",
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content 
        # print(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# # languages = googletrans.LANGUAGES
# # language_options = list(languages.values())
# selected_lang_src = st.selectbox("Select the source language for audio", ['hi', 'fr', 'en', 'de', 'ja','gu','ar'])
selected_lang_tar = st.selectbox("Select the target language for translation", ['afrikaans', 'albanian', 'amharic', 'arabic', 'armenian', 'azerbaijani', 'basque', 'belarusian', 'bengali', 'bosnian', 'bulgarian', 'catalan', 'cebuano', 'chichewa', 'chinese (simplified)', 'chinese (traditional)', 'corsican', 'croatian', 'czech', 'danish', 'dutch', 'english', 'esperanto', 'estonian', 'filipino', 'finnish', 'french', 'frisian', 'galician', 'georgian', 'german', 'greek', 'gujarati', 'haitian creole', 'hausa', 'hawaiian', 'hebrew', 'hebrew', 'hindi', 'hmong', 'hungarian', 'icelandic', 'igbo', 'indonesian', 'irish', 'italian', 'japanese', 'javanese', 'kannada', 'kazakh', 'khmer', 'korean', 'kurdish (kurmanji)', 'kyrgyz', 'lao', 'latin', 'latvian', 'lithuanian', 'luxembourgish', 'macedonian', 'malagasy', 'malay', 'malayalam', 'maltese', 'maori', 'marathi', 'mongolian', 'myanmar (burmese)', 'nepali', 'norwegian', 'odia', 'pashto', 'persian', 'polish', 'portuguese', 'punjabi', 'romanian', 'russian', 'samoan', 'scots gaelic', 'serbian', 'sesotho', 'shona', 'sindhi', 'sinhala', 'slovak', 'slovenian', 'somali', 'spanish', 'sundanese', 'swahili', 'swedish', 'tajik', 'tamil', 'telugu', 'thai', 'turkish', 'ukrainian', 'urdu', 'uyghur', 'uzbek', 'vietnamese', 'welsh', 'xhosa', 'yiddish', 'yoruba', 'zulu'])

# # Text input for target language (e.g., 'hi' for Hindi, 'fr' for French)
# target_language = st.text_input("Enter target language code (e.g., 'hi' for Hindi)", value="en")

# Button to trigger translation
if st.button("Transcribe Audio"):
    if uploaded_file is not None:
        # Save the uploaded file to a temporary directory
        with open("temp_audio_file", "wb") as f:
            f.write(uploaded_file.getbuffer())
        audio_path = "temp_audio_file"

        # Load the audio using pydub
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1)  # Ensure mono channel
        audio = audio.set_frame_rate(16000)  # Ensure frame rate is 16000 Hz

        # # Get the language code
        # selected_lang_code_src = list(languages.keys())[language_options.index(selected_lang_src)]
        # selected_lang_code_tar = list(languages.keys())[language_options.index(selected_lang_tar)]

        # Split the audio into chunks (10 sec per chunk)
        chunk_duration_ms = 10000  
        chunks = [audio[i:i + chunk_duration_ms] for i in range(0, len(audio), chunk_duration_ms)]

        # Variables to store full transcription and translation
        full_transcription = ""
        full_translation = ""

        # # --------------------without chunk starts--------------------------------------------------
        # filename = f"chunk.wav"
        # audio.export(filename, format="wav")
        # with open(filename, "rb") as file:
        #     transcription = client.audio.transcriptions.create(
        #         file=(filename, file.read()),  # Required audio file
        #         model="whisper-large-v3",  # Required model for transcription
        #         prompt="transcribe",
        #         response_format="json",  # Optional
        #         temperature=0.0  # Optional
        #     )
        # # Append the chunk transcription to full transcription
        # transcription_text = transcription.text
        # full_transcription += transcription_text + " "
        # # --------------------without chunk ends--------------------------------------------------

        #----------------------------------chunk wise end----------------------------------------------------------

        # Process each chunk
        for i, chunk in enumerate(chunks):
            # Save the chunk to a temporary file
            chunk_filename = f"chunk_{i}.wav"
            chunk.export(chunk_filename, format="wav")

            # Transcribe the chunk using Groq API
            with open(chunk_filename, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(chunk_filename, file.read()),  # Required audio file
                    model="whisper-large-v3",  # Required model for transcription
                    prompt="Transcribe",
                    response_format="json",  # Optional
                    temperature=0.0  # Optional
                )
            # Append the chunk transcription to full transcription
            chunk_transcription_text = transcription.text
            full_transcription += chunk_transcription_text + " "

            # chunk_translation = lt.translate(transcription.text, source=selected_lang_src, target=selected_lang_tar)
            chunk_translation = translate_text(chunk_transcription_text, selected_lang_tar)
            full_translation += chunk_translation + " "


            # # Translate the chunk transcription
            # translation = translator.translate(chunk_transcription_text, dest=selected_lang_code_tar)
            # # Append the chunk translation to full translation
            # full_translation += translation.text + " "

            # Show progress on the frontend
            st.write(f"Processed chunk {i+1}/{len(chunks)}")
            st.audio(chunk_filename, format="wav") 
            st.write(f"Chunk Transcription: {chunk_transcription_text}")
            st.write(f"Chunk Translation: {chunk_translation}")

        #----------------------------------chunk wise end----------------------------------------------------------

        # Show the final combined transcription and translation
        st.write("Final Transcription:")
        st.write(full_transcription)

        st.write(f"Final Translatation:")
        st.write(full_translation)

    elif mic_audio is not None:
        audio_file_like.seek(0)
        buffer_data = audio_file_like.read()
        # Save the uploaded file to a temporary directory
        with open("temp_audio_file", "wb") as f:
            f.write(buffer_data)
        audio_path = "temp_audio_file"

        # Load the audio using pydub
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1)  # Ensure mono channel
        audio = audio.set_frame_rate(16000)  # Ensure frame rate is 16000 Hz

        # # Get the language code
        # selected_lang_code_src = list(languages.keys())[language_options.index(selected_lang_src)]
        # selected_lang_code_tar = list(languages.keys())[language_options.index(selected_lang_tar)]

        # Split the audio into chunks (10 sec per chunk)
        chunk_duration_ms = 10000  
        chunks = [audio[i:i + chunk_duration_ms] for i in range(0, len(audio), chunk_duration_ms)]

        # Variables to store full transcription and translation
        full_transcription = ""
        full_translation = ""

        # # --------------------without chunk starts--------------------------------------------------
        # filename = f"chunk.wav"
        # audio.export(filename, format="wav")
        # with open(filename, "rb") as file:
        #     transcription = client.audio.transcriptions.create(
        #         file=(filename, file.read()),  # Required audio file
        #         model="whisper-large-v3",  # Required model for transcription
        #         prompt="transcribe",
        #         response_format="json",  # Optional
        #         temperature=0.0  # Optional
        #     )
        # # Append the chunk transcription to full transcription
        # transcription_text = transcription.text
        # full_transcription += transcription_text + " "
        # # --------------------without chunk ends--------------------------------------------------

        #----------------------------------chunk wise end----------------------------------------------------------

        # Process each chunk
        for i, chunk in enumerate(chunks):
            # Save the chunk to a temporary file
            chunk_filename = f"chunk_{i}.wav"
            chunk.export(chunk_filename, format="wav")

            # Transcribe the chunk using Groq API
            with open(chunk_filename, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(chunk_filename, file.read()),  # Required audio file
                    model="whisper-large-v3",  # Required model for transcription
                    prompt="Transcribe",
                    response_format="json",  # Optional
                    temperature=0.0  # Optional
                )
            # Append the chunk transcription to full transcription
            chunk_transcription_text = transcription.text
            full_transcription += chunk_transcription_text + " "

            # chunk_translation = lt.translate(transcription.text, source=selected_lang_src, target=selected_lang_tar)
            chunk_translation = translate_text(chunk_transcription_text, selected_lang_tar)
            full_translation += chunk_translation + " "


            # # Translate the chunk transcription
            # translation = translator.translate(chunk_transcription_text, dest=selected_lang_code_tar)
            # # Append the chunk translation to full translation
            # full_translation += translation.text + " "

            # Show progress on the frontend
            st.write(f"Processed chunk {i+1}/{len(chunks)}")
            st.audio(chunk_filename, format="wav") 
            st.write(f"Chunk Transcription: {chunk_transcription_text}")
            st.write(f"Chunk Translation: {chunk_translation}")

        #----------------------------------chunk wise end----------------------------------------------------------

        # Show the final combined transcription and translation
        st.write("Final Transcription:")
        st.write(full_transcription)

        st.write(f"Final Translation:")
        st.write(full_translation)

    else:
        st.error("Please upload an audio file.")
