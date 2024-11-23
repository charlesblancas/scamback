from six.moves import queue
import numpy as np
from datetime import datetime
import pyaudio
import logging
import wave

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    
class MuLawEncoder:
    def __init__(self, mu=255):
        self.mu = mu

    def encode(self, pcm_data):
        pcm16_normalized = pcm_data / 32768.0
        ulaw_encoded = np.sign(pcm16_normalized) * np.log1p(self.mu * np.abs(pcm16_normalized)) / np.log1p(self.mu)
        ulaw_encoded = ((ulaw_encoded + 1) / 2 * 255).astype(np.uint8)
        return ulaw_encoded

class AudioPlayer:
    def __init__(self, sample_rate = 8000, sample_width = 2, channels = 1):
        self.audio_interface = pyaudio.PyAudio()
        self.input_audio_queue = queue.Queue()
        self.is_playing = False
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.channels = channels
        
        # For recording functionality
        self.recording = False
        self.recorded_frames = []
        
    def start_stream(self):
        logger.info("Starting audio stream...")
        self.is_playing = True

    def generator(self):
        while self.is_playing:
            chunk = self.input_audio_queue.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self.input_audio_queue.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)
    
    def add_input_audio_chunk(self, pcm_data):
        try:
            # Add to queue for playback
            self.input_audio_queue.put(pcm_data)
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
                wf.setsampwidth(self.sample_width)
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.recorded_frames))
            
            logger.info(f"Recording saved successfully to {filename}")
        except Exception as e:
            logger.error(f"Error saving recording: {e}")
        
    def cleanup(self):
        logger.info("Cleaning up audio resources...")
        self.is_playing = False
        self.audio_interface.terminate()