import React, { useEffect, useRef, useState } from 'react';
import io from 'socket.io-client';

const AudioStream = ({url, transcript, setTranscript}) => {
    const socketRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const audioContextRef = useRef(null);
    const audioBufferListRef = useRef([]);

    useEffect(() => {
        socketRef.current = io(url);
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();

        socketRef.current.on('audio', (data) => {
          const from = data.from;
          const arrayBuffer = base64ToArrayBuffer(data.value);
    
          // audioContextRef.current.decodeAudioData(arrayBuffer, (buffer) => {
          //   audioBufferListRef.current.push(buffer);
          //   if (!isPlaying) {
          //     playAudio();
          //   }
          // }, (error) => {
          //   console.error('Error decoding audio:', error);
          // });
    
        });

        socketRef.current.on('text', (data) => {
          const from = data.from;
          const text = data.value;
          console.log(from + ": " + text)
          setTranscript([
            ...transcript,
            from + text
          ])
        });

        return () => {
            if (socketRef.current) {
              socketRef.current.disconnect();
            }
          };
    
      }, []);
    
      const base64ToArrayBuffer = (base64) => {
        const binaryString = window.atob(base64); // Decode base64 to binary string
        const length = binaryString.length;
        const arrayBuffer = new ArrayBuffer(length);
        const uintArray = new Uint8Array(arrayBuffer);
    
        for (let i = 0; i < length; i++) {
          uintArray[i] = binaryString.charCodeAt(i); // Convert each character to byte
        }
    
        return arrayBuffer;
      };
    
      const playAudio = () => {
        if (isPlaying) return;
    
        setIsPlaying(true);
    
        const playNextChunk = () => {
          if (audioBufferListRef.current.length === 0) {
            setTimeout(playNextChunk, 100); // Check for new chunks after 100ms
            return;
          }
    
          const buffer = audioBufferListRef.current.shift();
    
          // Create an AudioBufferSourceNode for each chunk
          const sourceNode = audioContextRef.current.createBufferSource();
          sourceNode.buffer = buffer;
          sourceNode.connect(audioContextRef.current.destination);
    
          // Schedule the chunk to start after the current time
          sourceNode.start(audioContextRef.current.currentTime);
    
          // Update currentTime for the next chunk
          // currentTimeRef.current += buffer.duration;
    
          sourceNode.onended = playNextChunk; // Play next chunk when the current one ends
        };
    
        playNextChunk();
      };

    return (
        <div>
        </div>
      );
};

export default AudioStream;