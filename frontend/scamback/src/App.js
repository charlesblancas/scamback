import React, { useState, useEffect, useRef } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPhone, faPhoneSlash, faDownload } from "@fortawesome/free-solid-svg-icons";
import { useStatusUpdater } from "./useStatusUpdater";
import "./App.css";
import CallInterface from "./CallInterface";

const PHONE_NUMBER = "+14388305880"
const URL_CALL_API = "http://localhost:5785"

function App() {
  const [stage, setStage] = useState("idle"); // Stages: idle, summary
  const [callState, setCallState] = useState(null); // Call states: queued, ringing, in-progress, completed
  const [audioUrl, setAudioUrl] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [savedTranscript, setSavedTranscript] = useState([]);
  const [savedAudioUrl, setSavedAudioUrl] = useState(null);

  const dialingSoundRef = useRef(null); // dialing sound audio element
  const transcriptEndRef = useRef(null); // bottom of the transcript box
  const status = useStatusUpdater();

  useEffect(() => {
    document.title = "ScamBack";
  }, []);

  useEffect(() => {
    if (status === "queued") {
      return;
    } else if (status === "ringing") {
      return;
    } else if (status === "in-progress") {
      setStage("in-progress");
      setCallState("in-progress");
      // handleCall();
    } else if (status === "completed") {
      setStage("summary");
      setCallState("completed");
      setSavedTranscript(transcript);
    }
  }, [status]);

  const handleCall = async () => {
    if (stage === "idle") {
      setStage("in-progress");
      setCallState("queued");
      setPhoneNumber(PHONE_NUMBER); 
      setTranscript([]);
      try {
        const response = await fetch(URL_CALL_API + "/start_call", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
          },
          body: JSON.stringify({
              to_number: PHONE_NUMBER, // Replace with the actual phone number
          }),
      });
    
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

      const response = await fetch(URL_CALL_API + "/stop_call", {
        method: "POST",
      });

    } else if (stage === "summary") {
      // Reset to idle
      setStage("idle");
      setCallState(null);
      setSavedAudioUrl(null);
      setSavedTranscript(transcript);
    }
  };

  useEffect(() => {
    if (callState === "ringing") {
      // Play dialing sound on loop when in the ringing state
      if (dialingSoundRef.current) {
        dialingSoundRef.current.play();
      }
    } else {
      // Stop the dialing sound when not in the ringing state
      if (dialingSoundRef.current) {
        dialingSoundRef.current.pause();
        dialingSoundRef.current.currentTime = 0;
      }
    }
  }, [callState]);

  const processTranscriptLine = (line) => {
    let processedLine = line;
    let color = "#fff"; // default

    if (line.startsWith("Scammer:")) {
      color = "#61dafb";
    }

    return { text: processedLine, color };
  };

  // Scroll to the bottom when new transcript lines are added
  useEffect(() => {
    if (transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [transcript]);

  return (
    <div className="App">
      <CallInterface transcript={transcript} setTranscript={setTranscript}/>
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
            {audioUrl && <audio autoPlay src={audioUrl} />}
            <div className="transcript-section">
              <h2>Transcript</h2>
              <div className="transcript-box">
                {transcript.map((line, index) => {
                  const { text, color } = processTranscriptLine(line);
                  return (
                    <p key={index} style={{ color: color }}>
                      {text}
                    </p>
                  );
                })}
                <div ref={transcriptEndRef}></div>
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
                <h2>
                  Call Audio
                  {savedAudioUrl && (
                    <a
                      href={savedAudioUrl}
                      download="call_audio.mp3"
                      className="download-icon"
                      title="Download Call Audio"
                    >
                      <FontAwesomeIcon icon={faDownload} style={{ color: "white", marginLeft: "10px" }} />
                    </a>
                  )}
                </h2>
                {savedAudioUrl && <audio controls src={savedAudioUrl} />}
              </div>
              <div className="transcript-section">
                <h2>
                  Transcript
                  <a
                    href={`data:text/plain;charset=utf-8,${encodeURIComponent(savedTranscript.join("\n"))}`}
                    download="call_transcript.txt"
                    className="download-icon"
                    title="Download Transcript"
                  >
                    <FontAwesomeIcon icon={faDownload} style={{ color: "white", marginLeft: "10px" }} />
                  </a>
                </h2>
                <div className="transcript-box">
                  {savedTranscript.map((line, index) => {
                    const { text, color } = processTranscriptLine(line);
                    return (
                      <p key={index} style={{ color: color }}>
                        {text}
                      </p>
                    );
                  })}
                </div>
              </div>
            </div>
            <button className="call-button another-scammer" onClick={handleCall}>
              <FontAwesomeIcon icon={faPhone} /> Call Another Scammer
            </button>
          </>
        )}
      </header>
      <div className="status">{status}</div>
      <audio ref={dialingSoundRef} loop>
        <source src="/dialing-sound.mp3" type="audio/mp3" />
      </audio>
    </div>
  );
}

export default App;
