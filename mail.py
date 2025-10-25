#!/usr/bin/env python3
"""
main.py

Turn a YouTube URL into a transcript, timestamped transcript, summary,
scene description, or shareable clips via the Google Generative Language endpoint.

This script mirrors the logic in your n8n workflow:
- Choose promptType (transcript, timestamps, summary, scene, clips, fallback)
- Use a prompt template per type
- Call Google generateContent API with a file_data.file_uri set to the YouTube URL
- Print and optionally save the result

Usage:
  python main.py --youtube-url "https://www.youtube.com/watch?v=..." --prompt-type transcript

Or set defaults in a .env file and run:
  python main.py
"""
import os
import sys
import json
import argparse
from typing import Dict, Any
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
DEFAULT_YOUTUBE_URL = os.getenv("YOUTUBE_URL", "")
DEFAULT_PROMPT_TYPE = os.getenv("PROMPT_TYPE", "transcript")

PROMPTS = {
    "scene": (
        "Please provide a detailed description of the scene in the video, including:\n\n"
        "Setting: Where the scene takes place (e.g., indoors, outdoors, specific location). Be specific - is it a forest, a city street, a living room?\n\n"
        "Objects: Prominent objects visible in the scene (e.g., furniture, vehicles, natural elements). Include details like color, size, and material if discernible.\n\n"
        "People: Description of any people present, including their appearance (clothing, hair, etc.), approximate age, and any actions they are performing.\n\n"
        "Lighting: The overall lighting of the scene (e.g., bright, dim, natural, artificial). Note any specific light sources (lamps, sunlight).\n\n"
        "Colors: Dominant colors and color palettes used in the scene.\n\n"
        "Camera Angle/Movement: Describe the camera perspective (e.g., close-up, wide shot, aerial view) and any camera movement (panning, zooming, static).\n\n"
        "Start output directly with the response -- do not include any introductory text or explanations."
    ),
    "summary": (
        "Provide a concise summary of the main points in nested bullets, using quotes only when absolutely essential for clarity. Start output directly with the response."
    ),
    "transcript": (
        "Transcribe the video. Return only the spoken dialogue, verbatim. Omit any additional text or descriptions."
    ),
    "timestamps": (
        "Generate a timestamped transcript of the video. Each line must follow this format precisely: [hh:mm:ss] Dialogue. Return only the timestamp and spoken content; omit any other text or formatting."
    ),
    "clips": (
        "Extract shareable clips for social media. Each clip must include:\n\n"
        "* **Timestamp:** [hh:mm:ss]-[hh:mm:ss]\n"
        "* **Transcript:** Verbatim dialogue/text within the clip.\n"
        "* **Rationale:** A concise explanation (under 20 words) of the clip's social media appeal (e.g., \"humorous,\" \"controversial,\" \"inspiring,\" \"informative\"). Focus on virality, engagement potential (shares, likes, comments).\n\n"
        "Start output directly with the response -- do not include any introductory text or explanations."
    ),
    "fallback": (
        "Summarize this YouTube video with a focus on actionable insights. Use nested bullets and include relevant quotes. Specifically, highlight any recommended tools, strategies, or resources mentioned."
    ),
}


def build_payload(model: str, prompt_text: str, youtube_url: str) -> Dict[str, Any]:
    """Construct JSON payload to match workflow's HTTP body."""
    return {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text},
                    {"file_data": {"file_uri": youtube_url}},
                ]
            }
        ]
    }


def call_google_generate(model: str, api_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call the Google Generative Language generateContent endpoint."""
    if not api_key:
        raise ValueError("Google API key not set (GOOGLE_API_KEY).")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        # If Google returns a JSON body with error details, try to include them
        try:
            err = resp.json()
        except Exception:
            err = {"status_code": resp.status_code, "text": resp.text}
        raise RuntimeError(f"Google API error: {err}") from exc
    return resp.json()


def extract_main_text(response_json: Dict[str, Any]) -> str:
    """
    Attempt to extract the generated text similarly to the Set Fields node in the workflow:
    - candidates[0].content.parts[0].text or first available textual field.
    """
    # Typical GL responses contain candidates -> content -> parts
    try:
        candidates = response_json.get("candidates")
        if candidates and len(candidates) > 0:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts and len(parts) > 0 and "text" in parts[0]:
                return parts[0]["text"]
    except Exception:
        pass
    # Fallback to stringifying the whole response
    return json.dumps(response_json, indent=2, ensure_ascii=False)


def save_output(out_text: str, prompt_type: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{timestamp}_{prompt_type}.txt"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(out_text)
    return path


def parse_args():
    parser = argparse.ArgumentParser(description="YouTube → Generative Language processing")
    parser.add_argument("--youtube-url", "-y", default=DEFAULT_YOUTUBE_URL, help="Public YouTube URL to analyze")
    parser.add_argument("--prompt-type", "-p", default=DEFAULT_PROMPT_TYPE, choices=list(PROMPTS.keys()), help="Prompt type to run")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help="Model name to call (default from env)")
    parser.add_argument("--save", action="store_true", help="Save result to outputs/ (or OUTPUT_DIR)")
    parser.add_argument("--api-key", default=GOOGLE_API_KEY, help="Google API key (optionally override env)")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.youtube_url:
        print("Error: No YouTube URL provided. Use --youtube-url or set YOUTUBE_URL in .env.", file=sys.stderr)
        sys.exit(1)

    prompt_type = args.prompt_type.lower()
    if prompt_type not in PROMPTS:
        print(f"Error: Unknown prompt type '{prompt_type}'. Valid: {', '.join(PROMPTS.keys())}", file=sys.stderr)
        sys.exit(1)

    prompt_text = PROMPTS[prompt_type]
    payload = build_payload(args.model, prompt_text, args.youtube_url)

    print(f"Calling Google model={args.model} for prompt_type={prompt_type} on URL={args.youtube_url}...")
    try:
        response_json = call_google_generate(args.model, args.api_key, payload)
    except Exception as e:
        print("Error calling Google Generative API:", file=sys.stderr)
        print(str(e), file=sys.stderr)
        sys.exit(2)

    out_text = extract_main_text(response_json)
    print("\n--- Generated Output START ---\n")
    print(out_text)
    print("\n--- Generated Output END ---\n")

    if args.save:
        path = save_output(out_text, prompt_type, OUTPUT_DIR)
        print(f"Saved output to: {path}")


if __name__ == "__main__":
    main()
