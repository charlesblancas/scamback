import base64
import json
import os
import logging
from flask import Flask, session
import flask_sockets
from response_generation.speech_to_text import start_speech_to_text
from player import AudioPlayer
from threading import Thread
import requests
import numpy as np
import audioop
import random
from scipy.io import wavfile
from scipy.signal import resample
from flask_socketio import SocketIO, emit, disconnect

HTTP_SERVER_PORT = 5770
TTS_SERVER_URL = "http://localhost:5000/tts"
PROB_SOUND_EFFECT = 0.3
SOUND_EFFECTS_FOLDER = "./sound_effects"

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
active_call = False
connected_frontend = False
sound_effects = [os.path.join(SOUND_EFFECTS_FOLDER, f) for f in os.listdir(SOUND_EFFECTS_FOLDER) if os.path.isfile(os.path.join(SOUND_EFFECTS_FOLDER, f))]
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("connect")
def handle_connect():
    global connected_frontend
    if connected_frontend:
        disconnect()
    logger.info("Frontend connected")
    connected_frontend = True

@socketio.on("disconnect")
def handle_disconnect():
    global connected_frontend
    logger.info("Frontend disconnected")
    connected_frontend = False

@sockets.route("/media", websocket=True)
def echo(ws):
    global sid, speech2text, active_call
    if active_call:
        logger.info("A session is already active. Rejecting new connection.")
        ws.close()
        return
    
    active_call = True
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
                if connected_frontend:
                    socketio.send("audio", {"from": "scammer", "value": base64.b64encode(raw_decoded_audio).decode("utf-8")})

    except Exception as e:
        logger.error(f"Error in WebSocket handling: {e}", exc_info=True)
    finally:
        logger.info(f"Session closed. Cleaning up.")
        audio_player.stop_recording()
        audio_player.cleanup()
        if speech2text and speech2text.is_alive():
            speech2text.join()
        active_call = False


def received_text(received_text, generated_text, ws):
    socketio.emit("text", {"from": "scammer", "value": received_text})
    socketio.emit("text", {"from": "ai", "value": generated_text})
    logger.info(f"Text2Speech: {generated_text}")

    # Randomly play sound effect before speaking
    if random.random() < PROB_SOUND_EFFECT:
        sound_effect_file = random.choice(sound_effects)
        sample_rate, audio = wavfile.read(sound_effect_file)
        number_of_samples = int(len(audio) * 8000 / sample_rate)                # Convert to 8 Khz sample rate
        audio = resample(audio, number_of_samples)
        if audio.dtype != np.int16:                                             # Convert to int 16
            audio = audio.astype(np.int16)
        clipped_audio = audio[:int(8000 * 1.)]                                  # Clip to 1 second
        if connected_frontend:
            socketio.send("audio", {"from": "ai", "value": base64.b64encode(clipped_audio).decode("utf-8")})
        mu_law_chunk = audioop.lin2ulaw(clipped_audio, 2)                       # pcm 16 bit to mulaw
        mu_law_encoded_chunk = base64.b64encode(mu_law_chunk).decode("utf-8")   # mulaw encoded as base64 string
        send_audio(ws, sid, mu_law_encoded_chunk)

    # Call the TTS API here with a post request
    response = requests.post(TTS_SERVER_URL, json={"text": generated_text})
    if response.status_code == 200:
        logger.info("TTS audio received.")
        # Play the audio on the call
        chunk = response.json()["audio"]

        # Encode the audio in x-mulaw format
        if connected_frontend:
            socketio.send("audio", {"from": "ai", "value": chunk})
        decoded_chunk = np.frombuffer(base64.b64decode(chunk), dtype=np.int16)  # base64 string to pcm 16-bit numpy
        mu_law_chunk = audioop.lin2ulaw(decoded_chunk, 2)                       # pcm 16 bit to mulaw
        mu_law_encoded_chunk = base64.b64encode(mu_law_chunk).decode("utf-8")   # mulaw encoded as base64 string
        send_audio(ws, sid, mu_law_encoded_chunk)

def send_audio(ws, sid, chunk):
    if not ws.closed:
        ws.send(
            json.dumps(
                {
                    "event": "media",
                    "streamSid": sid,
                    "media": {"payload": chunk},
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
