import base64
import json
import logging
from flask import Flask
import flask_sockets
import pyaudio
import wave
import os
from datetime import datetime
import threading
from queue import Queue
import numpy as np
import array
from scipy import signal
from response_generation.speech_to_text import speech_to_text

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

HTTP_SERVER_PORT = 5770

def add_url_rule(self, rule, _, f, **options):
    self.url_map.add(flask_sockets.Rule(rule, endpoint=f, websocket=True))
flask_sockets.Sockets.add_url_rule = add_url_rule

class MuLawDecoder:
    def __init__(self):
        # Standard mu-law decoding table
        self.table = np.array([
            -32124, -31100, -30076, -29052, -28028, -27004, -25980, -24956,
            -23932, -22908, -21884, -20860, -19836, -18812, -17788, -16764,
            -15996, -15484, -14972, -14460, -13948, -13436, -12924, -12412,
            -11900, -11388, -10876, -10364, -9852, -9340, -8828, -8316,
            -7932, -7676, -7420, -7164, -6908, -6652, -6396, -6140,
            -5884, -5628, -5372, -5116, -4860, -4604, -4348, -4092,
            -3900, -3772, -3644, -3516, -3388, -3260, -3132, -3004,
            -2876, -2748, -2620, -2492, -2364, -2236, -2108, -1980,
            -1884, -1820, -1756, -1692, -1628, -1564, -1500, -1436,
            -1372, -1308, -1244, -1180, -1116, -1052, -988, -924,
            -876, -844, -812, -780, -748, -716, -684, -652,
            -620, -588, -556, -524, -492, -460, -428, -396,
            -372, -356, -340, -324, -308, -292, -276, -260,
            -244, -228, -212, -196, -180, -164, -148, -132,
            -120, -112, -104, -96, -88, -80, -72, -64,
            -56, -48, -40, -32, -24, -16, -8, 0,
            32124, 31100, 30076, 29052, 28028, 27004, 25980, 24956,
            23932, 22908, 21884, 20860, 19836, 18812, 17788, 16764,
            15996, 15484, 14972, 14460, 13948, 13436, 12924, 12412,
            11900, 11388, 10876, 10364, 9852, 9340, 8828, 8316,
            7932, 7676, 7420, 7164, 6908, 6652, 6396, 6140,
            5884, 5628, 5372, 5116, 4860, 4604, 4348, 4092,
            3900, 3772, 3644, 3516, 3388, 3260, 3132, 3004,
            2876, 2748, 2620, 2492, 2364, 2236, 2108, 1980,
            1884, 1820, 1756, 1692, 1628, 1564, 1500, 1436,
            1372, 1308, 1244, 1180, 1116, 1052, 988, 924,
            876, 844, 812, 780, 748, 716, 684, 652,
            620, 588, 556, 524, 492, 460, 428, 396,
            372, 356, 340, 324, 308, 292, 276, 260,
            244, 228, 212, 196, 180, 164, 148, 132,
            120, 112, 104, 96, 88, 80, 72, 64,
            56, 48, 40, 32, 24, 16, 8, 0
        ], dtype=np.int16)

    def decode(self, mu_law_data):
        # Convert bytes to uint8 array
        mu_law_array = np.frombuffer(mu_law_data, dtype=np.uint8)
        # Use lookup table to convert to 16-bit PCM
        pcm_data = self.table[mu_law_array]
        return pcm_data.tobytes()

class AudioPlayer:
    def __init__(self):
        self.audio_queue = Queue()
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_playing = False
        self.sample_rate = 8000
        self.channels = 1
        self.format = pyaudio.paInt16
        self.decoder = MuLawDecoder()
        self.chunk_size = 160  # Twilio's chunk size
        
        # For recording functionality
        self.recording = False
        self.recorded_frames = []
        
    def start_stream(self):
        logger.info("Starting audio stream...")
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self.callback
        )
        self.stream.start_stream()
        self.is_playing = True
        logger.info("Audio stream started successfully")
        
    def callback(self, in_data, frame_count, time_info, status):
        try:
            # Get data from queue
            data = self.audio_queue.get_nowait()
            return (data, pyaudio.paContinue)
        except:
            # Return silence if no data available
            silence = b'\x00' * (frame_count * 2)  # 2 bytes per sample for 16-bit audio
            return (silence, pyaudio.paContinue)
    
    def add_audio(self, audio_data):
        try:
            # Decode mu-law data
            pcm_data = self.decoder.decode(audio_data)
            # Add to queue for playback
            self.audio_queue.put(pcm_data)
            # Store for recording if needed
            if self.recording:
                self.recorded_frames.append(pcm_data)
        except Exception as e:
            logger.error(f"Error processing audio data: {e}")
        
    def start_recording(self):
        logger.info("Starting recording...")
        self.recording = True
        self.recorded_frames = []
        
    def stop_recording(self):
        if not self.recording:
            return
            
        logger.info("Stopping recording...")
        self.recording = False
        
        if not self.recorded_frames:
            logger.warning("No audio frames were recorded!")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.p.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.recorded_frames))
            
            logger.info(f"Recording saved successfully to {filename}")
        except Exception as e:
            logger.error(f"Error saving recording: {e}")
        
    def cleanup(self):
        logger.info("Cleaning up audio resources...")
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()


app = Flask(__name__)
sockets = flask_sockets.Sockets(app)
audio_player = AudioPlayer()

@sockets.route('/media', websocket=True)
def echo(ws):
    logger.info("WebSocket connection accepted")
    message_count = 0
    audio_player.start_stream()
    audio_player.start_recording()
    
    try:
        #speech_to_text(audio_player.stream)
        while not ws.closed:
            message = ws.receive()
            if message is None:
                continue

            data = json.loads(message)
            
            if data['event'] == "media":
                payload = data['media']['payload']
                chunk = base64.b64decode(payload)
                audio_player.add_audio(chunk)
                message_count += 1
            
    except Exception as e:
        logger.error(f"Error in WebSocket handling: {e}", exc_info=True)
    finally:
        audio_player.stop_recording()
        logger.info(f"Connection closed. Processed {message_count} messages")

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