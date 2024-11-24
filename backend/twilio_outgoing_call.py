# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from dotenv import load_dotenv
import time
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

dotenv_path = '.env'
load_dotenv(dotenv_path, override=True)

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
from_number = os.environ.get("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

active_call_sid = None

@app.route("/start_call", methods=["POST"])
def start_call():
    global active_call_sid
    data = request.json
    to_number = data.get("to_number")
    if not to_number:
        return jsonify({"error": "Invalid phone number"}), 400
    
    try:
        call = client.calls.create(
            url=os.environ.get("TWIML_URL"),
            to=to_number,
            from_=os.environ.get("FROM_NUMBER"),
        )

        active_call_sid = call.sid
        print(f"Call SID: {active_call_sid}")

        call_status = client.calls(active_call_sid).fetch()
        print(f"Call Status: {call_status.status}")
        return jsonify({"status": call_status.status, "call_sid": active_call_sid}), 200
    except Exception as e:
        print(f"Error starting call: {e}")
        return jsonify({"error": "Error starting call"}), 500

@app.route("/stop_call", methods=["POST"])
def stop_call():
    global active_call_sid

    if not active_call_sid:
        return jsonify({"error": "No active call to stop"}), 400

    try:
        # Update the status of the ongoing call to "completed"
        client.calls(active_call_sid).update(status="completed")
        print(f"Call SID {active_call_sid} stopped.")
        active_call_sid = None
        return jsonify({"status": "Call stopped", "call_sid": active_call_sid}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/status", methods=["GET"])
def call_status():
    global active_call_sid

    if not active_call_sid:
        return jsonify({"status": "No active call"}), 200

    try:
        call_status = client.calls(active_call_sid).fetch()
        return jsonify({"status": call_status.status}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
        

if __name__ == "__main__":
    app.run(port=5785)