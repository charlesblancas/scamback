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
    "",
    "",
    "Test. Someone",
    "Oh wait. Oh wait.",
    "Oh my god!",
    "The audio is clear as day.",
    "So clear.",
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
