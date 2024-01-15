from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
import openai
import os
import json
import requests

from openai import OpenAI
from requests.models import CONTENT_CHUNK_SIZE

load_dotenv()
app = FastAPI()

# openai.api_key = os.environ.get("OPENAI_KEY")
# openai.api_organization = os.environ.get("OPENAI_ORG")

origins = [
    "http://localhost:5174",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

elevenlabs_key = os.environ.get("ELEVEN_KEY")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/talk")
async def post_audio(file: UploadFile):
    user_message = transcribe_audio(file)
    chat_response = get_chat_response(user_message)
    audio_output = text_to_speech(chat_response)

    def iterfile():
        yield audio_output

    return StreamingResponse(iterfile(), media_type="audio/mpeg")


def transcribe_audio(file):
    audio_file = open(file.filename, "rb")
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcript


def get_chat_response(user_message):
    messages = load_messages()
    messages.append({"role": "user", "content": user_message.text})

    gpt_response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )

    parsed_gpt_response = gpt_response.choices[0].message.content

    save_messages(user_message, parsed_gpt_response)

    return parsed_gpt_response


def load_messages():
    messages = []
    file = "database.json"

    empty = os.stat(file).st_size == 0
    # If file is NOT empty - read filename
    if not empty:
        with open(file) as db_file:
            data = json.load(db_file)
            for item in data:
                messages.append(item)
    # If file is empty - add context
    else:
        messages.append(
            {
                "role": "system",
                "content": "You are interviewing the user for a front-end react developer position. Ask short questions relevant to a junior level developer. Keep responses under 30 words.",
            }
        )

    return messages


def save_messages(user_message, gpt_response):
    file = "database.json"
    messages = load_messages()
    messages.append({"role": "user", "content": user_message.text})
    messages.append({"role": "assistant", "content": gpt_response})

    with open(file, "w") as f:
        json.dump(messages, f)


def text_to_speech(text):
    voice_id = "29vD33N1CtxCmqQRPOHJ"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

    body = {
        "model_id": "eleven_monolingual_v1",
        "text": text,
        "voice_settings": {
            "similarity_boost": 0.5,
            "stability": 0.5,
            "style": 0.5,
            "use_speaker_boost": True,
        },
    }

    headers = {
        "Content-Type": "application/json",
        "accept": "audio/mpeg",
        "xi-api-key": elevenlabs_key,
    }

    try:
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            print("Something went wrong!")
    except Exception as e:
        print(e)
