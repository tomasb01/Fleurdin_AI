# Install the requests package by executing the command "pip install requests"

import requests
import time

base_url = "https://api.assemblyai.com"

headers = {
    # Replace with your chosen API key, this is the "default" account api key
    "authorization": "555ca9a7c377482183a9d40b763a2fc8"
}

# URL of the file to transcribe
FILE_URL = "https://cdn.assemblyai.com/upload/ad7ee472-d817-4279-9f2e-7dd1c6826659"

# You can set additional parameters for the transcription
config = {
  "audio_url": FILE_URL,
  "speaker_labels":True,
  "format_text":True,
  "punctuate":True,
  "speech_model":"universal",
  "language_code":"sk"
}

url = base_url + "/v2/transcript"
response = requests.post(url, json=config, headers=headers)

transcript_id = response.json()['id']
polling_endpoint = base_url + "/v2/transcript/" + transcript_id

while True:
  transcription_result = requests.get(polling_endpoint, headers=headers).json()
  transcription_text = transcription_result['text']

  if transcription_result['status'] == 'completed':
    print(f"Transcript Text:", transcription_text)
    break

  elif transcription_result['status'] == 'error':
    raise RuntimeError(f"Transcription failed: {transcription_result['error']}")

  else:
    time.sleep(3)
  