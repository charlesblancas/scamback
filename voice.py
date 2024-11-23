from TTS.api import TTS
import librosa
import torch
import numpy as np

class TTSModel:
    def __init__(self):
        self.model_name = "tts_models/en/vctk/vits"
        self.speaker = "p227"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS(model_name=self.model_name, progress_bar=False).to(device)

    def generate(self, text):
        wav = np.array(self.tts.tts(text=text, speaker=self.speaker))
        return wav, 22050 # audio data, sample rate

def modify_voice(audio, sample_rate, pitch_shift=0.95, speed_change=1.05, add_breathiness=False):
    y_pitch_shifted = librosa.effects.pitch_shift(audio, sr=sample_rate, n_steps=pitch_shift) # Pitch
    y_resampled = librosa.effects.time_stretch(y_pitch_shifted, rate=speed_change) # Speed
    if add_breathiness:
        noise = np.random.normal(0, 0.01, len(y_resampled))
        y_resampled = y_resampled + 0.02 * noise

    y_normalized = librosa.util.normalize(y_resampled)
    return y_normalized

