const express = require("express");
const fs = require("fs");
const path = require("path");
const cors = require("cors");

const app = express();
app.use(cors());
const port = 5000;

app.use(express.static(path.join(__dirname, "public")));

// Stream the audio file
app.get("/call/audio", (req, res) => {
  const audioFile = path.join(__dirname, "public", "audio.wav");
  const stat = fs.statSync(audioFile);
  const fileSize = stat.size;
  const range = req.headers.range;

  if (range) {
    const parts = range.replace(/bytes=/, "").split("-");

    const start = parseInt(parts[0], 10);
    const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;

    res.writeHead(206, {
      "Content-Range": `bytes ${start}-${end}/${fileSize}`,
      "Accept-Ranges": "bytes",
      "Content-Length": end - start + 1,
      "Content-Type": "audio/mpeg",
    });

    const stream = fs.createReadStream(audioFile, { start, end });
    stream.pipe(res);
  } else {
    res.writeHead(200, {
      "Content-Length": fileSize,
      "Content-Type": "audio/mpeg",
    });

    const stream = fs.createReadStream(audioFile);
    stream.pipe(res);
  }
});

// Stream a mock transcript
app.get("/call/transcript", (req, res) => {
  const transcript = [
    "S. Parker: Thank you for calling. How can I help you today?",
    "R. Williams: Hi. I got a call from this number. A recording saying to call back.",
    "Something about my tax paperwork.",
    "S. Parker: What's your name?",
    "R. Williams: My name is Richard Williams.",
    "S. Parker: Richard Williams?",
    "R. Williams: Yes.",
    "S. Parker: We don't have anybody Richard Williams.",
    "R. Williams: I'm sorry, who is this?",
    "S. Parker: Who are you?",
    "R. Williams: I got a call. Something about my tax paperwork having a problem.",
    "S. Parker: Which number you received the call? Tell me the number on which you received the call.",
    "R. Williams: 404-295-9315.",
    "S. Parker: You received the phone call today?",
    "R. Williams: Yeah, today or last night. I'm trying to find out who I'm dialing. I couldn't make out the message.",
    "S. Parker: Federal Investigation Department.",
    "R. Williams: I'm sorry?",
    "S. Parker: Federal Investigation Department.",
    "R. Williams: Federal Investigation Department?"
  ];

  let index = 0;

  const interval = setInterval(() => {
    if (index < transcript.length) {
      res.write(`${transcript[index]}\n`);
      index++;
    } else {
      clearInterval(interval);
      res.end();
    }
  }, 2000); // Simulate 2-second delays between transcript lines
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
