import os
import speech_recognition as sr
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv
import json
from emails_utils import draft_email
from file_utils import organize_files

# Load environment variables
load_dotenv()
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Initialize LLM (Mistral-7B-Instruct-v0.1)
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mixtral-7B-Instruct-v0.3",
    max_new_tokens=512,
    temperature=0.7,
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
)

# Command parser prompt
parser_prompt = PromptTemplate(
    input_variables=["command"],
    template="""
Analyze the following command and classify it into one of these intents:
- 'email': Drafting or sending an email
- 'file_organize': Organizing files
- 'unknown': Unrecognized command

Extract relevant parameters (e.g., recipient, subject, body for email; directory, sorting method for files).
For email commands, if no body is provided, generate a concise, professional email body (2-3 sentences) based on the subject.
Return a JSON object with '{{intent}}' and '{{parameters}}'. Ensure the JSON is valid and properly formatted.

Command: {command}

Example outputs:
- Email with body provided: {{"intent": "email", "parameters": {{"recipient": "john@example.com", "subject": "Meeting", "body": "Let's meet tomorrow at 10 AM"}}}}
- Email without body: {{"intent": "email", "parameters": {{"recipient": "john@example.com", "subject": "Meeting", "body": "Hi John, I'd like to schedule a meeting tomorrow. Please let me know your availability."}}}}
- File: {{"intent": "file_organize", "parameters": {{"directory": "~/Downloads", "method": "type"}}}}
- Unknown: {{"intent": "unknown", "parameters": {{}}}}
"""
)

# Create parser chain using RunnableSequence
parser_chain = parser_prompt | llm

# Capture voice or text input
def get_command(use_voice=True):
    if use_voice:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio)
                print(f"Recognized: {command}")
                return command
            except sr.UnknownValueError:
                print("Could not understand audio, could you please repeat.")
                return ""
            except sr.RequestError:
                print("Speech recognition service unavailable.")
                return ""
    else:
        return input("Enter Command Please: ")

# Parse command
def parse_command(command):
    if not command:
        return {"intent": "unknown", "parameters": {}}
    try:
        result = parser_chain.invoke({"command": command})
        return json.loads(result)
    except json.JSONDecodeError:
        print("Error parsing LLM output:(")
        return {"intent": "unknown", "parameters": {}}
    except Exception as e:
        print(f"Error in parse_command: {e}")
        return {"intent": "unknown", "parameters": {}}

# Main loop
def main():
    while True:
        command = get_command(use_voice=False)  # Set to False since you used text input
        parsed = parse_command(command)
        intent = parsed["intent"]
        params = parsed["parameters"]

        if intent == "email":
            recipient = params.get("recipient", "default@example.com")
            subject = params.get("subject", "No Subject")
            body = params.get("body", "Generated email body")
            draft_email(recipient, subject, body)
        elif intent == "file_organize":
            directory = params.get("directory", "~/Downloads")
            method = params.get("method", "type")
            organize_files(directory, method)
        else:
            print("Unknown command. Try 'draft email to john@example.com about meeting' or 'organize files in Downloads'.")

if __name__ == "__main__":
    main()