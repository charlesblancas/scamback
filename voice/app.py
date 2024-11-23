from voice import TTSModel, resample_voice
from flask import Flask, request, jsonify
import base64

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
    audio = resample_voice(audio, sr, target_sr)
    encoded_audio = base64.b64encode(audio).decode('utf-8')
    return jsonify({
        "audio": encoded_audio,
        "sample_rate": target_sr
    })

if __name__ == '__main__':
    app.run(debug=False, host=HOST, port=PORT)