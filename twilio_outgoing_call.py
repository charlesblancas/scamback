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
    url=os.environ.get("TWIML_URL"),
    to=os.environ.get("TO_NUMBER"),
    from_=os.environ.get("FROM_NUMBER"),
)

print(call.sid)