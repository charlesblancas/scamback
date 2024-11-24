import os
from dotenv import load_dotenv
import google.generativeai as genai
from flask import Flask, request, jsonify
import random
from personas import personas

# Load environment variables
dotenv_path = ".env"
load_dotenv(dotenv_path)
model_name = "gemini-1.5-flash-8b"

# Configure the Google Generative AI API key
genai.configure(api_key=os.environ.get("GOOGLE_CHAT_API_KEY"))

# Initialize the model
model = genai.GenerativeModel(
    model_name=model_name, system_instruction=random.choice(personas)
)
chat = model.start_chat()


def chat_with_edna(user_input: str):
    if not user_input:
        return None

    return chat.send_message(user_input)


def reset_chat():
    # Reset the chat by re-initializing the chat object
    global model
    global chat
    persona = random.choice(personas)
    print(persona)
    model = genai.GenerativeModel(model_name=model_name, system_instruction=personas)
    chat = model.start_chat()  # Starts a new chat session


if __name__ == "__main__":
    while True:
        inp = input("User: ")

        if inp == "reset":
            reset_chat()
            continue

        print(chat_with_edna(inp))
