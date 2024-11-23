import assemblyai as aai
import os
from dotenv import load_dotenv

dotenv_path = '.env'
load_dotenv(dotenv_path, override=True)
aai.settings.api_key = os.environ.get("ASSEMBLYAI_API_KEY")

transcriber = aai.Transcriber()

transcript = transcriber.transcribe("./recording_20241123_124449.wav")

print(transcript.text)