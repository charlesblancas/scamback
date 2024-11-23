# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from dotenv import load_dotenv

dotenv_path = '.env'
load_dotenv(dotenv_path)

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

call = client.calls.create(
    url="https://handler.twilio.com/twiml/EH9e1f33f37203a3d2b278e1287ceb0a7a",
    to="+15148501367",
    from_="+14388061753",
)

print(call.sid)