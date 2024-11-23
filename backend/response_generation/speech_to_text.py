import json
import os
from dotenv import load_dotenv
import pyaudio
from rev_ai.models import MediaConfig
from rev_ai.streamingclient import RevAiStreamingClient
from six.moves import queue
from chat import chat_with_edna

"""
Insert your access token here
"""
dotenv_path = ".env"
load_dotenv(dotenv_path)
access_token = os.environ.get("REV_AI_TOKEN")


class MicrophoneStream(object):
    """
    Opens a recording stream as a generator yielding the audio chunks.
    """

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        """
        Create a thread-safe buffer of audio data
        """
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        """
        Signal the generator to terminate so that the client's
        streaming_recognize method will not block the process termination.
        """
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """
        Continuously collect data from the audio stream, into the buffer.
        """
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            """
            Use a blocking get() to ensure there's at least one chunk of
            data, and stop iteration if the chunk is None, indicating the
            end of the audio stream.
            """
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            """
            Now consume whatever other data's still buffered.
            """
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b"".join(data)


"""
Sampling rate of your microphone and desired chunk size
"""
rate = 44100
chunk = int(rate / 10)
"""
Creates a media config with the settings set for a raw microphone input
"""
example_mc = MediaConfig("audio/x-raw", "interleaved", 44100, "S16LE", 1)
streamclient = RevAiStreamingClient(access_token, example_mc)
"""
Opens microphone input. The input will stop after a keyboard interrupt.
"""
with MicrophoneStream(rate, chunk) as stream:
    """
    Uses try method to enable users to manually close the stream
    """
    try:
        """
        Starts the server connection and thread sending microphone audio
        """
        response_gen = streamclient.start(stream.generator())
        """
        Iterates through responses and prints them
        """
        for response in response_gen:
            res = json.loads(response)
            if res["type"] == "final":
                ai_response = chat_with_edna(
                    ("".join([elem["value"] for elem in res["elements"]]))
                )
                print(ai_response.text)
    except KeyboardInterrupt:
        """
        Ends the WebSocket connection.
        """
        streamclient.end()
        pass