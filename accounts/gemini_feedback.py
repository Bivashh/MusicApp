import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def generate_gemini_feedback(*, title: str, pitch_score: float, rhythm_score: float, auto_score: float,
                             pitch_err_semitones: float | None = None,
                             tempo_ref: float | None = None,
                             tempo_student: float | None = None) -> str:
    """
    Returns a short coaching paragraph (3–6 sentences) + 2 bullet action steps.
    Uses Gemini generateContent endpoint.
    """

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")

    prompt = f"""
You are a music teacher. Give practical, encouraging feedback for a student submission.

Assessment: {title}

Scores:
- Auto score: {auto_score:.1f}/100
- Pitch score: {pitch_score:.1f}/100
- Rhythm score: {rhythm_score:.1f}/100

Optional stats (if present):
- Avg pitch error (semitones): {pitch_err_semitones if pitch_err_semitones is not None else "N/A"}
- Reference tempo (BPM): {tempo_ref if tempo_ref is not None else "N/A"}
- Student tempo (BPM): {tempo_student if tempo_student is not None else "N/A"}

Rules:
- 3–6 sentences max.
- End with exactly 2 bullet points titled "Next steps".
- No emojis.
""".strip()

    # Use generateContent (official docs)
    # Endpoint format: generativelanguage.googleapis.com
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 220
        }
    }

    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()

    data = r.json()
    # Typical response: candidates[0].content.parts[0].text
    return data["candidates"][0]["content"]["parts"][0]["text"]