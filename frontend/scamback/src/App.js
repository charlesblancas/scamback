import React, { useState, useEffect } from "react";
import "./App.css";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPhoneSlash } from '@fortawesome/free-solid-svg-icons';

function App() {
  const [stage, setStage] = useState("idle"); // Stages: idle, summary, in-progress
  const [callState, setCallState] = useState(null); // Call states: queued, ringing, in-progress, completed
  const [audioUrl, setAudioUrl] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [savedTranscript, setSavedTranscript] = useState([]);
  const [savedAudioUrl, setSavedAudioUrl] = useState(null);

  // Set document title on component mount
  useEffect(() => {
    document.title = "Scamback";
  }, []);

  const handleCall = async () => {
    if (stage === "idle") {
      setStage("in-progress");
      setCallState("queued");
      setPhoneNumber("+1-800-SCAMMER"); // Example: Dynamic number from API

      try {
        // Simulate a queued state transition
        setTimeout(() => setCallState("ringing"), 20);

        // Simulate ringing and transition to in-progress
        setTimeout(async () => {
          setCallState("in-progress");

          // Simulate API fetching for streams
          const audioResponse = await fetch("http://localhost:5000/call/audio");
          const transcriptResponse = await fetch("http://localhost:5000/call/transcript");

          if (!audioResponse.ok || !transcriptResponse.ok) {
            throw new Error("Failed to fetch call streams.");
          }

          const audioBlob = await audioResponse.blob();
          const transcriptStream = transcriptResponse.body.getReader();

          setAudioUrl(URL.createObjectURL(audioBlob));

          // Read and display transcript
          const decoder = new TextDecoder("utf-8");
          let done = false;
          while (!done) {
            const { value, done: streamDone } = await transcriptStream.read();
            done = streamDone;
            if (value) {
              setTranscript((prev) => [...prev, decoder.decode(value)]);
            }
          }
        }, 5000); // Ringing for 3 seconds before call starts
      } catch (error) {
        console.error(error.message);
      }
    } else if (stage === "in-progress") {
      // Transition to completed state
      setStage("summary");
      setCallState("completed");
      setSavedAudioUrl(audioUrl);
      setSavedTranscript(transcript);
      setAudioUrl(null);
      setTranscript([]);
      setPhoneNumber("");
    } else if (stage === "summary") {
      // Reset to idle
      setStage("idle");
      setCallState(null);
      setSavedAudioUrl(null);
      setSavedTranscript([]);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        {stage === "idle" && (
          <>
            <h1>Scamback</h1>
            <button className="call-button" onClick={handleCall}>
              📞 Call a Scammer
            </button>
          </>
        )}

        {stage === "in-progress" && (
          <>
            <h1>Call in Progress</h1>
            <p>Phone Number: {phoneNumber}</p>
            {audioUrl && (
              <div className="audio-section">
                {/* <h2>Call Audio</h2> */}
                <audio autoPlay src={audioUrl} />
              </div>
            )}
            <div className="transcript-section">
              <h2>Transcript</h2>
              <div className="transcript-box">
                {transcript.map((line, index) => (
                  <p key={index}>{line}</p>
                ))}
              </div>
            </div>
            <button className="call-button hangup" onClick={handleCall}>
              <FontAwesomeIcon icon={faPhoneSlash} size="lg" /> Hang Up
            </button>
          </>
        )}

        {stage === "summary" && (
          <>
            <h1>Call Summary</h1>
            <div className="audio-section">
              <h2>Call Audio</h2>
              {savedAudioUrl && <audio controls src={savedAudioUrl} />}
            </div>
            <div className="transcript-section">
              <h2>Transcript</h2>
              <div className="transcript-box">
                {savedTranscript.map((line, index) => (
                  <p key={index}>{line}</p>
                ))}
              </div>
            </div>
            <button className="call-button" onClick={handleCall}>
              📞 Call Another Scammer
            </button>
          </>
        )}
      </header>
    </div>
  );
}

export default App;
