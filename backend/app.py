import base64
import json
import logging
from flask import Flask
import flask_sockets
from response_generation.speech_to_text import start_speech_to_text
from player import AudioPlayer

HTTP_SERVER_PORT = 5770

def add_url_rule(self, rule, _, f, **options):
    self.url_map.add(flask_sockets.Rule(rule, endpoint=f, websocket=True))
flask_sockets.Sockets.add_url_rule = add_url_rule

app = Flask(__name__)
sockets = flask_sockets.Sockets(app)
audio_player = AudioPlayer()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@sockets.route('/media', websocket=True)
def echo(ws):
    logger.info("WebSocket connection accepted")
    audio_player.start_stream()
    audio_player.start_recording()
    start_speech_to_text(audio_player.stream, received_text)

    try:
        while not ws.closed:
            message = ws.receive()
            if message is None:
                continue

            data = json.loads(message)
            
            if data['event'] == "media":
                payload = data['media']['payload']
                chunk = base64.b64decode(payload)
                audio_player.add_audio(chunk)
            
    except Exception as e:
        logger.error(f"Error in WebSocket handling: {e}", exc_info=True)
    finally:
        audio_player.stop_recording()
        logger.info(f"Connection closed.")

def received_text(text):
    logger.info(f"Text2Speech: {text}")

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