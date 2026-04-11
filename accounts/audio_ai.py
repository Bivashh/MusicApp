import numpy as np
import librosa


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return float(max(lo, min(hi, x)))


def _safe_mean(a: np.ndarray) -> float:
    if a.size == 0:
        return 0.0
    return float(np.nanmean(a))


def analyze_audio(reference_path: str, student_path: str) -> dict:
    """
    Returns:
    {
      "pitch_score": float,
      "rhythm_score": float,
      "auto_score": float,
      "feedback": str
    }
    """

    # Load both files at same sample rate
    sr = 22050
    ref_y, _ = librosa.load(reference_path, sr=sr, mono=True)
    stu_y, _ = librosa.load(student_path, sr=sr, mono=True)

    # Trim silence to reduce noise influence
    ref_y, _ = librosa.effects.trim(ref_y, top_db=25)
    stu_y, _ = librosa.effects.trim(stu_y, top_db=25)

    # If audio too short, return low confidence feedback
    if len(ref_y) < sr * 1 or len(stu_y) < sr * 1:
        return {
            "pitch_score": 0.0,
            "rhythm_score": 0.0,
            "auto_score": 0.0,
            "feedback": "Audio too short. Please submit a clearer recording (at least 5–10 seconds).",
        }

    # ---------- PITCH  ----------
    # Get pitch contour (Hz). Using a reasonable human vocal range.
    fmin = librosa.note_to_hz("C2")   # ~65 Hz
    fmax = librosa.note_to_hz("C6")   # ~1046 Hz

    ref_f0 = librosa.yin(ref_y, fmin=fmin, fmax=fmax, sr=sr)
    stu_f0 = librosa.yin(stu_y, fmin=fmin, fmax=fmax, sr=sr)

    # Convert to cents for better comparison
    ref_c = librosa.hz_to_midi(ref_f0)
    stu_c = librosa.hz_to_midi(stu_f0)

    # Align sequences by resampling to same length (simple + stable)
    n = min(len(ref_c), len(stu_c))
    ref_c = ref_c[:n]
    stu_c = stu_c[:n]

    # Pitch error in semitones (midi scale)
    pitch_err = np.abs(ref_c - stu_c)
    pitch_err_mean = _safe_mean(pitch_err)

    # Converting error to score (0–100). 0 semitone error => 100.
    # ~2 semitones avg error becomes low.
    pitch_score = _clamp(100.0 - (pitch_err_mean * 35.0))

    # ---------- RHYTHM / TEMPO ----------
    # Compute tempo + beat strength
    ref_onset = librosa.onset.onset_strength(y=ref_y, sr=sr)
    stu_onset = librosa.onset.onset_strength(y=stu_y, sr=sr)

    ref_tempo, _ = librosa.beat.beat_track(onset_envelope=ref_onset, sr=sr)
    stu_tempo, _ = librosa.beat.beat_track(onset_envelope=stu_onset, sr=sr)

    # Tempo difference -> score
    tempo_diff = abs(float(ref_tempo) - float(stu_tempo))
    rhythm_score = _clamp(100.0 - (tempo_diff * 2.5))  # 10 BPM diff => -25 score

    # ---------- OVERALL ----------
    auto_score = _clamp(pitch_score * 0.65 + rhythm_score * 0.35)

    # ---------- FEEDBACK TEXT ----------
    fb = []
    if pitch_score >= 85:
        fb.append("Pitch is very consistent.")
    elif pitch_score >= 70:
        fb.append("Pitch is decent, but a few notes drift.")
    else:
        fb.append("Pitch needs improvement—try practicing slowly with a reference.")

    if rhythm_score >= 85:
        fb.append("Rhythm/tempo is well matched.")
    elif rhythm_score >= 70:
        fb.append("Rhythm is okay, but timing is slightly inconsistent.")
    else:
        fb.append("Rhythm needs work—use a metronome and keep the tempo steady.")

    fb.append(f"Auto Score: {auto_score:.1f}/100 (Pitch {pitch_score:.1f}, Rhythm {rhythm_score:.1f}).")

    return {
        "pitch_score": float(pitch_score),
        "rhythm_score": float(rhythm_score),
        "auto_score": float(auto_score),
        "feedback": " ".join(fb),
    }