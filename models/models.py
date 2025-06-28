import whisper
import json
import re
import requests
import google.generativeai as genai

from config import GOOGLE_API_KEY, MISTRAL_API_KEY, LLM_BACKEND

model = whisper.load_model("base")

def transcribe_audio(audio_path: str) -> str:
    result = model.transcribe(audio_path)
    return result["text"]

def extract_tasks(transcript):
    lines = transcript.split(". ")
    tasks = []
    for line in lines:
        if re.search(r'(?i)\b(should|must|need to|assign|complete|by|deadline|responsible for|follow up|send|update)\b', line):
            tasks.append(line.strip())
    return tasks

def extract_json_from_text(text: str) -> dict | None:
    try:
        start = text.find('{')
        end = text.rfind('}') + 1

        if start == -1 or end == -1 or start >= end:
            return None
        json_str = text[start:end]
        json_obj = json.loads(json_str)
        json_obj["error"] = ""
        return json_obj

    except json.JSONDecodeError:
        return None

prompt_format = """
Analyze the following meeting transcript and return a **structured JSON** response with the following fields:

{
    "summary": "A concise 3-4 line summary of the key meeting discussions.",
    "action_items": [
        {
            "task": "Clearly stated task",
            "assignee": "Name of the responsible person (if mentioned)",
            "due_date": "YYYY-MM-DD format or null if not mentioned",
            "category": "e.g. technical, admin, client-related"
        },
        {
            "task": "Clearly stated task",
            "assignee": "Name of the responsible person (if mentioned)",
            "due_date": "YYYY-MM-DD format or null if not mentioned",
            "category": "e.g. technical, admin, client-related"
        }
    ]
}

Transcript:

"""

def summarize_with_geminai(transcript_text: str):
    genai.configure(api_key=GOOGLE_API_KEY)
    prompt_full = prompt_format + transcript_text
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest') # Updated model name
        response = model.generate_content(prompt_full)
        extracted = extract_json_from_text(response.text)
        return extracted

    except Exception as e:
        print(f"Error calling Gemini API or parsing response: {e}")
        
        return {
            "error": str(e),
            "summary": "LLM summarization failed. Falling back to rule-based task extraction.",
            "action_items": extract_tasks(transcript_text),
        }

def summarize_with_mistral(transcript_text):
    MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
    try:
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        prompt = prompt_format + transcript_text

        data = {
            "model": "mistral-medium",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
        result = response.json()
        extracted = extract_json_from_text(result['choices'][0]['message']['content'])
        return extracted

    except Exception as e:
        print(f"Error calling Gemini API or parsing response: {e}")
        
        return {
            "error": str(e),
            "summary": "LLM summarization failed. Falling back to rule-based task extraction.",
            "action_items": extract_tasks(transcript_text),
        }

def summarize_transcript(transcript_text):
    if LLM_BACKEND == "gemini":
        return summarize_with_geminai(transcript_text)
    return summarize_with_mistral(transcript_text)