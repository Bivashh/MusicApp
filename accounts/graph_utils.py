import os
import uuid
import numpy as np
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import librosa

from django.conf import settings


def _save_plot(fig, subfolder="assessment_graphs"):
    os.makedirs(os.path.join(settings.MEDIA_ROOT, subfolder), exist_ok=True)
    filename = f"{uuid.uuid4().hex}.png"
    rel_path = os.path.join(subfolder, filename)
    abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    fig.savefig(abs_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return rel_path  


def generate_pitch_plot(reference_path: str, student_path: str) -> str:
    sr = 22050
    ref_y, _ = librosa.load(reference_path, sr=sr, mono=True)
    stu_y, _ = librosa.load(student_path, sr=sr, mono=True)

    ref_y, _ = librosa.effects.trim(ref_y, top_db=25)
    stu_y, _ = librosa.effects.trim(stu_y, top_db=25)

    fmin = librosa.note_to_hz("C2")
    fmax = librosa.note_to_hz("C6")

    ref_f0 = librosa.yin(ref_y, fmin=fmin, fmax=fmax, sr=sr)
    stu_f0 = librosa.yin(stu_y, fmin=fmin, fmax=fmax, sr=sr)

    # time axes
    ref_t = np.linspace(0, len(ref_y) / sr, num=len(ref_f0))
    stu_t = np.linspace(0, len(stu_y) / sr, num=len(stu_f0))

    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(111)
    ax.plot(ref_t, ref_f0, label="Reference", linewidth=1.5)
    ax.plot(stu_t, stu_f0, label="Student", linewidth=1.2)
    ax.set_title("Pitch over Time (Hz)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.25)

    return _save_plot(fig)


def generate_rhythm_plot(reference_path: str, student_path: str) -> str:
    sr = 22050
    ref_y, _ = librosa.load(reference_path, sr=sr, mono=True)
    stu_y, _ = librosa.load(student_path, sr=sr, mono=True)

    ref_y, _ = librosa.effects.trim(ref_y, top_db=25)
    stu_y, _ = librosa.effects.trim(stu_y, top_db=25)

    ref_onset = librosa.onset.onset_strength(y=ref_y, sr=sr)
    stu_onset = librosa.onset.onset_strength(y=stu_y, sr=sr)

    ref_t = librosa.times_like(ref_onset, sr=sr)
    stu_t = librosa.times_like(stu_onset, sr=sr)

    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(111)
    ax.plot(ref_t, ref_onset, label="Reference", linewidth=1.5)
    ax.plot(stu_t, stu_onset, label="Student", linewidth=1.2)
    ax.set_title("Rhythm Energy (Onset Strength)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Onset Strength")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.25)

    return _save_plot(fig)