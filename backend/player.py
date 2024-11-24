from six.moves import queue
import numpy as np
from datetime import datetime
import pyaudio
import logging
import wave

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        self.input_audio_queue.put(None)
        self.audio_interface.terminate()