import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def _call_gemini(prompt: str) -> str:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.6,
            "maxOutputTokens": 800,  # ✅ more room so it won’t cut
            "topP": 0.9
        }
    }

    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def generate_gemini_feedback(*, title: str, pitch_score: float, rhythm_score: float, auto_score: float,
                             pitch_err_semitones: float | None = None,
                             tempo_ref: float | None = None,
                             tempo_student: float | None = None) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")

    prompt = f"""
You are a professional music teacher. Write feedback that is SPECIFIC to the numbers.

Assessment: {title}

Scores:
- Auto score: {auto_score:.1f}/100
- Pitch score: {pitch_score:.1f}/100
- Rhythm score: {rhythm_score:.1f}/100

Extra stats (if present):
- Avg pitch error (semitones): {pitch_err_semitones if pitch_err_semitones is not None else "N/A"}
- Reference tempo (BPM): {tempo_ref if tempo_ref is not None else "N/A"}
- Student tempo (BPM): {tempo_student if tempo_student is not None else "N/A"}

Return in THIS exact format (always include all sections):

Summary:
(two sentences)

Pitch:
(two sentences; mention accuracy + one improvement tip)

Rhythm:
(two sentences; mention timing + one improvement tip)

Next steps:
- (bullet 1)
- (bullet 2)
- (bullet 3)

Rules:
- No emojis.
- Do NOT be generic.
- Even if score is high, still give 1 advanced improvement tip.
""".strip()

    text = _call_gemini(prompt)

    # ✅ retry once if Gemini returns too short
    if len(text.strip()) < 200:
        text = _call_gemini(prompt)

    return text