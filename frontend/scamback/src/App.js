import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [callStatus, setCallStatus] = useState("");
  const [audioUrl, setAudioUrl] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [isCalling, setIsCalling] = useState(false);

  useEffect(() => {
    document.title = 'Scamback';
  }, []);

  const handleCall = async () => {
    if (isCalling) {
      // Handle hang-up action
      setIsCalling(false);
      setCallStatus("Call ended.");
      setAudioUrl(null);
      setTranscript([]);
      return;
    }

    // Start call
    setIsCalling(true);
    setCallStatus("Connecting to a scammer...");
    setAudioUrl(null);
    setTranscript([]);

    try {
      // Simulate API call to fetch audio and transcript streams
      const audioResponse = await fetch("/call/audio");
      const transcriptResponse = await fetch("/call/transcript");

      if (!audioResponse.ok || !transcriptResponse.ok) {
        throw new Error("Failed to connect to the call service.");
      }

      const audioBlob = await audioResponse.blob();
      const transcriptStream = transcriptResponse.body.getReader();

      // Set the audio for playback
      const audioObjectUrl = URL.createObjectURL(audioBlob);
      setAudioUrl(audioObjectUrl);

      // Read the transcript stream
      const decoder = new TextDecoder("utf-8");
      let done = false;
      while (!done && isCalling) {
        const { value, done: streamDone } = await transcriptStream.read();
        done = streamDone;
        if (value) {
          setTranscript((prev) => [...prev, decoder.decode(value)]);
        }
      }

      if (isCalling) {
        setCallStatus("Call in progress...");
      }
    } catch (error) {
      setCallStatus(`Error: ${error.message}`);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Scamback</h1>
        <button className="call-button" onClick={handleCall}>
          {isCalling ? "🔴 Hang Up" : "📞 Call a Scammer"}
        </button>
        <p>{callStatus}</p>

        {audioUrl && (
          <div className="audio-section">
            <h2>Call Audio</h2>
            <audio controls src={audioUrl} />
          </div>
        )}

        {transcript.length > 0 && (
          <div className="transcript-section">
            <h2>Transcript</h2>
            <div className="transcript-box">
              {transcript.map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
