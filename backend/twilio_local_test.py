from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)


@app.route("/voice", methods=["GET", "POST"])
def voice():
    response = VoiceResponse()
    response.say("Hello! Thanks for calling.")
    return Response(str(response), mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=True)
