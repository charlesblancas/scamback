import React, { useEffect, useRef, useState } from 'react';

const BACKEND_URL = "http://localhost:5770/events"

const CallInterface = ({ transcript, setTranscript }) => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    var nextTime = 0;

    useEffect(() => {

      const playAudioChunk = async (base64Data, applyDelay) => {
        try {
          // Decode base64 to binary
          const binaryString = atob(base64Data); // Decode the Base64 string to binary
          const arrayBuffer = new ArrayBuffer(binaryString.length); // Create an ArrayBuffer
          const uint8Array = new Uint8Array(arrayBuffer);
    
          // Copy the binary data to the ArrayBuffer
          for (let i = 0; i < binaryString.length; i++) {
              uint8Array[i] = binaryString.charCodeAt(i);
          }
          const pcmData = new DataView(arrayBuffer);

          const lengthInSamples = pcmData.byteLength / 2; // Each 16-bit sample is 2 bytes
          const buffer = audioContext.createBuffer(1, lengthInSamples, 8000);
          const channelData = buffer.getChannelData(0);

          for (let i = 0; i < lengthInSamples; i++) {
            channelData[i] = pcmData.getInt16(i * 2, true) / 0x8000;
          }

          const source = audioContext.createBufferSource();
          source.buffer = buffer;
          source.connect(audioContext.destination);
          if (applyDelay) {
            source.start(nextTime);
            nextTime = buffer.duration;
          } else {
            source.start();
          }
        } catch (error) {
          console.error("Error playing audio chunk:", error);
        }
      };

      const processEvents = async () => {
        try {
          const res = await fetch(BACKEND_URL);
          if (!res.ok) {
            return
          }
          const parsed = await res.json();

          for (let event of parsed) {
            const from = event.from; 
            if (event.event === "text") {
              const text = event.value;
              setTranscript((prev) => [...prev, from + ": " + text])
            } else { // Audio
              const base64Audio = event.value;
              playAudioChunk(base64Audio, from === "Ai");
            }
          }

        } catch (error) {
          console.error("Error fetching event data:", error);
        }
      }

      const intervalId = setInterval(processEvents, 200);
      return () => clearInterval(intervalId)
      }, []);
    

    return (
        <div>
        </div>
      );
};

export default CallInterface;