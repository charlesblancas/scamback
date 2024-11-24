import base64
import json
import logging
from flask import Flask
import flask_sockets
from response_generation.speech_to_text import start_speech_to_text
from player import AudioPlayer
from threading import Thread
import requests
import numpy as np
import audioop
from flask_socketio import SocketIO, emit

HTTP_SERVER_PORT = 5770
TTS_SERVER_URL = "http://localhost:5000/tts"

def add_url_rule(self, rule, _, f, **options):
    self.url_map.add(flask_sockets.Rule(rule, endpoint=f, websocket=True))
flask_sockets.Sockets.add_url_rule = add_url_rule

app = Flask(__name__)
sockets = flask_sockets.Sockets(app)
audio_player = AudioPlayer()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
speech2text = None  # To init later as Thread
sid = None          # To init later
active_session = False

# Replace `socketio.Server` with Flask-SocketIO integration
socketio = SocketIO(app, cors_allowed_origins="*")

# Define namespaces and events
@socketio.on("connect")
def handle_connect():
    logger.info("Frontend connected")
    emit("status", {"message": "Connected to WebSocket"})


@socketio.on("disconnect")
def handle_disconnect():
    logger.info("Frontend disconnected")


@sockets.route("/media", websocket=True)
def echo(ws):
    global sid, speech2text, active_session
    if active_session:
        logger.info("A session is already active. Rejecting new connection.")
        ws.close()
        return
    
    logger.info("New connection accepted")
    audio_player.start_stream()
    audio_player.start_recording()
    speech2text = Thread(
        target=start_speech_to_text, args=(audio_player, received_text, ws)
    )
    speech2text.start()

    try:
        while not ws.closed:
            message = ws.receive()
            if message is None:
                continue

            data = json.loads(message)

            if data["event"] == "media":
                payload = data["media"]["payload"]
                sid = data["streamSid"]
                decoded_chunk = base64.b64decode(payload)                   # base64 to mulaw
                raw_decoded_audio = audioop.ulaw2lin(decoded_chunk, 2)      # mulaw to pcm
                audio_player.add_input_audio_chunk(raw_decoded_audio)

    except Exception as e:
        logger.error(f"Error in WebSocket handling: {e}", exc_info=True)
    finally:
        logger.info(f"Session closed. Cleaning up.")
        audio_player.stop_recording()
        audio_player.cleanup()
        if speech2text and speech2text.is_alive():
            speech2text.join()


def received_text(text, ws):
    socketio.emit("text", {"text": text})
    logger.info(f"Text2Speech: {text}")

    # Call the TTS API here with a post request
    response = requests.post(TTS_SERVER_URL, json={"text": text})
    if response.status_code == 200:
        logger.info("TTS audio received.")
        # Play the audio on the call
        chunk = response.json()["audio"]

        # Encode the audio in x-mulaw format
        decoded_chunk = np.frombuffer(base64.b64decode(chunk), dtype=np.int16)  # base64 string to pcm 16-bit numpy
        mu_law_chunk = audioop.lin2ulaw(decoded_chunk, 2)                       # pcm 16 bit to mulaw
        mu_law_encoded_chunk = base64.b64encode(mu_law_chunk).decode("utf-8")   # mulaw encoded as base64 string

        if not ws.closed:
            ws.send(
                json.dumps(
                    {
                        "event": "media",
                        "streamSid": sid,
                        "media": {"payload": mu_law_encoded_chunk},
                    }
                )
            )

if __name__ == "__main__":
    try:
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler

        server = pywsgi.WSGIServer(
            ("0.0.0.0", HTTP_SERVER_PORT), app, handler_class=WebSocketHandler
        )
        print(f"Server listening on: http://localhost:{HTTP_SERVER_PORT}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
    finally:
        audio_player.cleanup()
        if speech2text and speech2text.is_alive():
            speech2text.join()
