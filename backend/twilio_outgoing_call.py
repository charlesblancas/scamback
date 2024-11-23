import os
from twilio.rest import Client
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse
from flask import Flask, request, jsonify

dotenv_path = ".env"
load_dotenv(dotenv_path, override=True)

# Twilio credentials from .env file
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
from_number = os.environ.get("FROM_NUMBER")
to_number = os.environ.get("TO_NUMBER")

client = Client(account_sid, auth_token)

app = Flask(__name__)


# Endpoint to handle call response
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    gather = response.gather(
        input="speech",
        action="/transcribe",  # Webhook to handle the transcription
        method="POST",
    )
    gather.say("Please tell us your message after the beep.")
    response.pause(length=5)  # Wait for additional input
    response.say("Thank you. Goodbye!")
    return str(response)


# Endpoint to handle transcription results
@app.route("/transcribe", methods=["POST"])
def transcribe():
    transcription = request.form.get("SpeechResult")
    confidence = request.form.get("Confidence")
    print(f"Transcription: {transcription} (Confidence: {confidence})")
    return jsonify({"transcription": transcription, "confidence": confidence})


# Function to trigger a call
def make_call():
    call = client.calls.create(
        to=to_number,
        from_=from_number,
        url="https://grc0xglp7f.sharedwithexpose.com/voice",  # Replace with your ngrok or live URL
    )
    print(f"Call initiated: {call.sid}")


# Trigger the call when the Flask app starts
if __name__ == "__main__":
    # Call the function to initiate the call when the app starts
    make_call()

    # Start the Flask app
    app.run(debug=True)
