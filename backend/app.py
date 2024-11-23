import base64
import json
import logging
from flask import Flask
import flask_sockets
from response_generation.speech_to_text import start_speech_to_text
from player import AudioPlayer, MuLawDecoder, MuLawEncoder
from threading import Thread
import requests

HTTP_SERVER_PORT = 5770

def add_url_rule(self, rule, _, f, **options):
    self.url_map.add(flask_sockets.Rule(rule, endpoint=f, websocket=True))
flask_sockets.Sockets.add_url_rule = add_url_rule

app = Flask(__name__)
sockets = flask_sockets.Sockets(app)
audio_player = AudioPlayer()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
speech2text = None # To init later as Thread

decoder = MuLawDecoder()
encoder = MuLawEncoder()
sid = None

@sockets.route('/media', websocket=True)
def echo(ws):
    global sid
    logger.info("WebSocket connection accepted")
    audio_player.start_stream()
    audio_player.start_recording()
    speech2text = Thread(target=start_speech_to_text, args=(audio_player, received_text, ws))
    speech2text.start()

    try:
        while not ws.closed:
            message = ws.receive()
            if message is None:
                continue

            data = json.loads(message)
            
            if data['event'] == "media":
                payload = data['media']['payload']
                sid = data['streamSid']
                chunk = base64.b64decode(payload)
                audio_player.add_input_audio_chunk(decoder.decode(chunk))
            
    except Exception as e:
        logger.error(f"Error in WebSocket handling: {e}", exc_info=True)
    finally:
        audio_player.stop_recording()
        logger.info(f"Connection closed.")

def received_text(text, ws):
    logger.info(f"Text2Speech: {text}")
    # Call the TTS API here with a post request
    tts_url = "http://ilr1ffu2mf.sharedwithexpose.com/tts"
    response = requests.post(tts_url, json={"text": text})
    if response.status_code == 200:
        logger.info("TTS API response 200 received")
        # Play the audio on the call
        chunk = response.json()["audio"]
        #decode base64
        decoded_chunk = base64.b64decode(chunk)
        mu_law_encoded_chunk = encoder.encode_array(decoded_chunk)
        chunk_to_send = base64.b64encode(mu_law_encoded_chunk).decode("utf-8")
        ws.send(json.dumps({"event": "media", "streamSid": sid, "media": {"payload": chunk_to_send}}))
        # Encode the audio in x-mulaw format

if __name__ == '__main__':
    try:
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler
        
        server = pywsgi.WSGIServer(('0.0.0.0', HTTP_SERVER_PORT), app, handler_class=WebSocketHandler)
        print(f"Server listening on: http://localhost:{HTTP_SERVER_PORT}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
    finally:
        audio_player.cleanup()
        speech2text.join()