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
    "Phone ringing",
    "Scammer: Hello, is this Edna?",
    "You: Yes, this is Edna. Who’s calling?",
    "Scammer: Hi Edna, this is Sarah from Amazon’s fraud prevention department. I’m calling to inform you that we’ve detected suspicious activity on your Amazon account. Someone has made an unauthorized purchase, and we need to verify your identity immediately to prevent further issues.",
    "You: Oh no, what kind of purchase?",
    "Scammer: We’ve noticed a large purchase made from your account for an iPhone 15, worth $1,200, and it was shipped to an address we don’t recognize. To resolve this issue and secure your account, we need to confirm a few details. Are you near a computer or mobile device right now?",
    "You: Yes, I am. What should I do?",
    "Scammer: Great! We’ll first need you to log into your Amazon account and verify some security information. Open Amazon and sign in. Once you're in, I’ll guide you through the rest.",
    "You: Okay, I’m logging in now.",
    "Scammer: Once you’re logged in, can you please confirm the last four digits of the bank account linked to your Amazon account? This is to make sure we’re talking to the account holder.",
    "You: Wait, you need the bank account information?",
    "Scammer: Yes, for security reasons. If you’re worried about the security of your account, I can help you reset your bank details. We just need to confirm it to stop any fraudulent activity. You can also receive a verification code through email if you prefer.",
    "You: Uh, I don’t think I should give that over the phone…",
    "Scammer: I understand your concern, but this is an urgent matter. If you don’t confirm the details, your account might be permanently suspended, and you could lose access to your order and payment methods.",
    "You: I’m not sure. Can you send me something in writing?",
    "Scammer: We can’t send emails for security reasons. This is the fastest way to resolve the issue. Just confirm your account details, and we’ll help you protect it from further unauthorized charges. I’m here to assist you, [Your Name].",
    "You: Sorry, I’m not giving out my information like this. I’ll contact Amazon directly.",
    "Scammer: Wait, don’t hang up! You could lose your account and money if you don’t act fast!",
    "You: Goodbye."
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
