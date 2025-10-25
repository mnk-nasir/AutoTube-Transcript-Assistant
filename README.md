# AutoTube-Transcript-Assistant```markdown
# YouTube Video Analysis (Generative Language companion)

This small Python companion replicates the logic in the n8n workflow
"Turn YouTube Videos into Summaries, Transcripts, and Visual Insights".

It:
- Accepts a public YouTube URL.
- Selects one of several prompt templates (transcript, timestamps, summary, scene, clips, fallback).
- Calls Google Generative Language `generateContent` (model default `gemini-1.5-flash`) with `file_data.file_uri` set to the YouTube URL.
- Prints the AI-generated output and can save it to `outputs/`.

Files:
- `main.py` — script to run the workflow logic.
- `requirements.txt` — minimal dependencies.
- `.env.example` — environment variable examples.

Requirements
- Python 3.9+
- A Google API key that can access the Generative Language endpoint. See:
  https://ai.google.dev/generativelanguage/overview

Setup
1. Create a `.env` from `.env.example` and set `GOOGLE_API_KEY`.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run:
   ```
   python main.py --youtube-url "https://www.youtube.com/watch?v=..." --prompt-type summary --save
   ```

Prompt types (value for --prompt-type)
- transcript — verbatim transcript only
- timestamps — timestamped transcript lines ([hh:mm:ss] Dialogue)
- summary — nested-bullet concise summary
- scene — visual scene description
- clips — suggested social media clips (timestamp, transcript, rationale)
- fallback — actionable insights summary

Notes
- The script mirrors the payload shape used in your n8n HTTP node (parts with text + file_data.file_uri).
- Real-world usage might require additional file-hosting or vision-specific model configuration.
- Response extraction is heuristic: it attempts to read `candidates[0].content.parts[0].text` like your Set Fields node.
```
