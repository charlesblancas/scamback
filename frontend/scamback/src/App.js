import React, { useState, useEffect, useRef } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPhone, faPhoneSlash } from "@fortawesome/free-solid-svg-icons";
import "./App.css";

function App() {
  const [stage, setStage] = useState("idle"); // Stages: idle, summary
  const [callState, setCallState] = useState(null); // Call states: queued, ringing, in-progress, completed
  const [audioUrl, setAudioUrl] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [savedTranscript, setSavedTranscript] = useState([]);
  const [savedAudioUrl, setSavedAudioUrl] = useState(null);

  useEffect(() => {
    document.title = "ScamBack";
  }, []);

  const handleCall = async () => {
    if (stage === "idle") {
      setStage("in-progress");
      setCallState("queued");
      setPhoneNumber("+1-800-314-5421"); // Example: Dynamic number from API
      setTranscript([]);

      try {
        // Simulate a queued state transition
        setTimeout(() => setCallState("ringing"), 200);

        // Simulate ringing and transition to in-progress
        setTimeout(async () => {
          setCallState("in-progress");

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
        }, 2000); // Ringing for 200ms before call starts
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
            <img src="/logo.png" alt="Scamback Logo" className="logo" />
            <h1>ScamBack</h1>
            <button className="call-button large" onClick={handleCall}>
              <FontAwesomeIcon icon={faPhone} /> Call a Scammer
            </button>
          </>
        )}

        {stage === "in-progress" && (
          <>
            <h1>Call in Progress</h1>
            <p>Phone Number: {phoneNumber}</p>
            {audioUrl && (
              <audio autoPlay src={audioUrl} />
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
              <FontAwesomeIcon icon={faPhoneSlash} /> Hang Up
            </button>
          </>
        )}

        {stage === "summary" && (
          <>
            <h1>Call Summary</h1>
            <p>Phone Number: {phoneNumber}</p>
            <div className="summary-layout">
              <div className="audio-section">
                <h2>Call Audio</h2>
                {savedAudioUrl && <audio controls src={savedAudioUrl} />}
                <a
                  href={savedAudioUrl}
                  download="call_audio.mp3"
                  className="download-button"
                >
                  Download
                </a>
              </div>
              <div className="transcript-section">
                <h2>Transcript</h2>
                <div className="transcript-box">
                  {savedTranscript.map((line, index) => (
                    <p key={index}>{line}</p>
                  ))}
                </div>
                <a
                  href={`data:text/plain;charset=utf-8,${encodeURIComponent(
                    savedTranscript.join("\n")
                  )}`}
                  download="call_transcript.txt"
                  className="download-button"
                >
                  Download
                </a>
              </div>
            </div>
            <button className="call-button" onClick={handleCall}>
              <FontAwesomeIcon icon={faPhone} /> Call Another Scammer
            </button>
          </>
        )}
      </header>
    </div>
  );
}

export default App;
