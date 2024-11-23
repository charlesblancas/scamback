import React, { useState } from "react";
import "./App.css";

function App() {
  const [callStatus, setCallStatus] = useState("");
  const [callLog, setCallLog] = useState([]);

  const handleCall = () => {
    const timestamp = new Date().toLocaleString();
    setCallStatus("Calling a scammer...");
    setCallLog((prevLog) => [
      ...prevLog,
      `Called a scammer on ${timestamp}`,
    ]);

    // Simulate a delay for the call
    setTimeout(() => {
      setCallStatus("Call ended. Hopefully saved someone today!");
    }, 3000);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Scamback</h1>
        <button className="call-button" onClick={handleCall}>
          📞 Call a Scammer
        </button>
        <p>{callStatus}</p>

        <h2>Call Log</h2>
        <ul>
          {callLog.map((log, index) => (
            <li key={index}>{log}</li>
          ))}
        </ul>

        <footer>
          <p>Always act ethically and legally. Report scammers to the authorities!</p>
        </footer>
      </header>
    </div>
  );
}

export default App;
