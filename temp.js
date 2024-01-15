voice_id = "29vD33N1CtxCmqQRPOHJ"

url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

body = {
  "model_id": "eleven_monolingual_v1",
  "text": text,
  "voice_settings": {
    "similarity_boost": 123,
    "stability": 123,
    "style": 123,
    "use_speaker_boost": True
  }
}

headers = {
  "Content-Type": "application/json",
  "accept": "audio/mpeg",
  "xi-api-key": elevenlabs_key
}

try:
response = requests.post(url, json = body, headers = headers)
if response.status_code == 200:
  return response.content
else:
print("Something went wrong!")
    except Exception as e:
print(e)

