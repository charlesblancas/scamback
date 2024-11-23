import json
import os
from dotenv import load_dotenv
from rev_ai.models import MediaConfig
from rev_ai.streamingclient import RevAiStreamingClient
from .chat import chat_with_edna

load_dotenv(".env")
access_token = os.environ.get("REV_AI_TOKEN")

def start_speech_to_text(audio_stream, callback):
    """
    Creates a media config with the settings set for a raw microphone input
    """
    example_mc = MediaConfig("audio/x-raw", "interleaved", 8000, "S16LE", 1)

    streamclient = RevAiStreamingClient(access_token, example_mc)

    try:
        """
        Starts the server connection and thread sending microphone audio
        """
        response_gen = streamclient.start(audio_stream.generator())

        """
        Iterates through responses and prints them
        """
        for response in response_gen:
            res = json.loads(response)
            if res["type"] == "final":
                ai_response = chat_with_edna(
                    ("".join([elem["value"] for elem in res["elements"]]))
                )
                callback(ai_response.text)

    except KeyboardInterrupt:
        """
        Ends the WebSocket connection.
        """
        streamclient.end()
        pass
