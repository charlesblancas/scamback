from voice import TTSModel, resample_voice
from flask import Flask, request, jsonify
from scipy.io.wavfile import write
import base64
import numpy as np
import audioop

HOST = '0.0.0.0'
PORT = 5000

tts = TTSModel()
app = Flask(__name__)

@app.route("/status", methods = ["GET"])
def status():
    return "OK", 200

@app.route("/tts", methods = ["POST"])
def text_to_speech():
    data = request.get_json()
    if not 'text' in data:
        return jsonify({"error": "no \'text\' parameter provided"})
    
    text = data["text"]
    audio, sr = tts.generate(text)
    target_sr = 8000
    resampled_audio = resample_voice(audio, sr, target_sr)
    resampled_audio = np.int16(resampled_audio / np.max(np.abs(resampled_audio)) * 32767)

    encoded_audio = base64.b64encode(resampled_audio).decode('utf-8')
    
    return jsonify({
        "audio": encoded_audio,
        "sample_rate": target_sr
    })

if __name__ == '__main__':
    app.run(debug=False, host=HOST, port=PORT)