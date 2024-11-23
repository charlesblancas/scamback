from vonage import Vonage, Auth
from vonage_voice.models import CreateCallRequest, Talk, Stream, Input
from vonage_voice.models import AudioStreamOptions
import os
from dotenv import load_dotenv
from pprint import pprint

dotenv_path = '.env'
load_dotenv(dotenv_path)

# Create an Auth instance
print(os.environ.get("VONAGE_APPLICATION_ID"))
print(os.environ.get("VONAGE_APPLICATION_PRIVATE_KEY"))
auth = Auth(application_id=os.getenv("VONAGE_APPLICATION_ID"), private_key=os.getenv("VONAGE_APPLICATION_PRIVATE_KEY"))

# Create a Vonage instance
vonage = Vonage(auth=auth)

# Make an outbound call
ncco = [Input(type=['speech'], eventUrl=['https://scamback.smithdrive.space/']), Stream(streamUrl=["https://scamback.smithdrive.space/test.wav"], loop=1, level=1)]

call = CreateCallRequest(
    to=[{'type': 'phone', 'number': os.environ.get("TO_NUMBER")}],
    ncco=ncco,
    random_from_number=True,
)

response = vonage.voice.create_call(call)
# response = vonage.voice.play_audio_into_call(response.uuid, AudioStreamOptions(stream_url=["https://nexmo-community.github.io/ncco-examples/assets/voice_api_audio_streaming.mp3"], loop=1, level=1))
pprint(response)


