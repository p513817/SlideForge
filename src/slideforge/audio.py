"""Audio generation and padding helpers."""

import os
import shutil
import subprocess
from pathlib import Path

import edge_tts

from . import runtime as cfg

async def generate_audio(text: str, output_path: str, metadata_path: str | None = None):
    """Generate speech with Edge TTS and optionally save word-boundary metadata."""
    communicate = edge_tts.Communicate(text, cfg.VOICE, rate=cfg.RATE)
    await communicate.save(output_path, metadata_path)


def make_silent_audio(output_path: str, duration: float):
    """Generate a silent audio file for slides without speaker notes."""
    subprocess.run([
        "ffmpeg", "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=mono",
        "-t", str(duration),
        "-y", output_path
    ], check=True, capture_output=True)


async def generate_all_audio(notes: list[str], output_dir: Path) -> list[str]:
    """Generate narration audio for all slides."""
    paths = []
    for i, note in enumerate(notes):
        audio_path = str(output_dir / f"audio_{i+1:03d}.mp3")
        metadata_path = str(output_dir / f"audio_{i+1:03d}_metadata.jsonl")
        if note.strip():
            print(f"   Slide {i+1}/{len(notes)}...")
            await generate_audio(note, audio_path, metadata_path)
        else:
            print(f"   Slide {i+1}/{len(notes)} (empty, generating silence)")
            make_silent_audio(audio_path, cfg.EMPTY_SLIDE_DURATION)
            with open(metadata_path, "w", encoding="utf-8") as f:
                f.write("")
        paths.append(audio_path)
    return paths


def add_pause_to_audio(audio_path: str, output_path: str, pause: float):
    if pause <= 0:
        shutil.copy(audio_path, output_path)
        return

    parent = Path(audio_path).parent.resolve()
    audio_abs  = str(Path(audio_path).resolve()).replace("\\", "/")
    output_abs = str(Path(output_path).resolve())
    silent_tmp = str(parent / "_silence_tmp.mp3")

    make_silent_audio(silent_tmp, pause)

    list_file = str(parent / "_concat.txt")
    silent_abs = str(Path(silent_tmp).resolve()).replace("\\", "/")
    with open(list_file, "w", encoding="utf-8") as f:
        f.write(f"file '{audio_abs}'\n")
        f.write(f"file '{silent_abs}'\n")

    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy", "-y", output_abs
    ], check=True, capture_output=True)

    os.remove(list_file)
    os.remove(silent_tmp)


def prepend_silence_to_audio(audio_path: str, output_path: str, silence: float):
    """Prepend silence so narration does not start immediately at video start."""
    if silence <= 0:
        shutil.copy(audio_path, output_path)
        return

    parent = Path(audio_path).parent.resolve()
    audio_abs = str(Path(audio_path).resolve()).replace("\\", "/")
    output_abs = str(Path(output_path).resolve())
    silent_tmp = str(parent / "_leading_silence_tmp.mp3")

    make_silent_audio(silent_tmp, silence)

    list_file = str(parent / "_leading_concat.txt")
    silent_abs = str(Path(silent_tmp).resolve()).replace("\\", "/")
    with open(list_file, "w", encoding="utf-8") as f:
        f.write(f"file '{silent_abs}'\n")
        f.write(f"file '{audio_abs}'\n")

    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy", "-y", output_abs
    ], check=True, capture_output=True)

    os.remove(list_file)
    os.remove(silent_tmp)


