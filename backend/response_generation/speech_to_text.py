import json
import os
from dotenv import load_dotenv
from rev_ai.models import MediaConfig
from rev_ai.streamingclient import RevAiStreamingClient
from .chat import chat_with_edna

load_dotenv(".env")
access_token = os.environ.get("REV_AI_TOKEN")

def start_speech_to_text(audio_player, callback, ws):
    mc = MediaConfig("audio/x-raw", "interleaved", 8000, "S16LE", 1)

    streamclient = RevAiStreamingClient(access_token, mc)

    try:
        response_gen = streamclient.start(audio_player.generator())

        for response in response_gen:
            res = json.loads(response)
            if res["type"] == "final":
                ai_response = chat_with_edna(
                    ("".join([elem["value"] for elem in res["elements"]]))
                )
                callback(ai_response.text, ws)

    except KeyboardInterrupt:
        streamclient.end()
