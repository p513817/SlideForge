"""Video composition helpers."""

import os
import subprocess
from pathlib import Path

from . import runtime as cfg

def image_audio_to_clip_with_gifs(image_path: str, audio_path: str,
                                   output_path: str, gifs: list[dict]):
    """Combine a slide image, GIF overlays, and audio into one video clip."""
    if not gifs:
        image_audio_to_clip(image_path, audio_path, output_path)
        return

    inputs = ["-loop", "1", "-i", image_path]
    for g in gifs:
        inputs += ["-stream_loop", "-1", "-i", g["path"]]
    inputs += ["-i", audio_path]

    # Scale and overlay each GIF in sequence.
    filter_parts = []
    prev = "0:v"
    for i, g in enumerate(gifs):
        filter_parts.append(
            f"[{i+1}:v]scale={g['width']}:{g['height']}[g{i}]"
        )
        filter_parts.append(
            f"[{prev}][g{i}]overlay={g['left']}:{g['top']}[v{i}]"
        )
        prev = f"v{i}"

    audio_idx = len(gifs) + 1

    subprocess.run([
        "ffmpeg", *inputs,
        "-filter_complex", ";".join(filter_parts),
        "-map", f"[{prev}]",
        "-map", f"{audio_idx}:a",
        "-c:v", "libx264",
        "-g", "1",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-y", output_path
    ], check=True, capture_output=True)


def image_audio_to_clip(image_path: str, audio_path: str, output_path: str):
    """Combine one slide image and one audio file into a video clip."""
    subprocess.run([
        "ffmpeg",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-g", "1",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-y", output_path
    ], check=True, capture_output=True)


def concatenate_clips(clip_paths: list[str], output_path: str):
    """Concatenate all slide clips into the final video."""
    list_file = str(cfg.TEMP_DIR / "_clips_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{Path(p).name}'\n")

    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", "_clips_list.txt",
        "-c", "copy", "-y",
        str(Path(output_path).resolve())
    ], check=True, capture_output=True, cwd=str(cfg.TEMP_DIR))

    os.remove(list_file)


def get_media_duration(media_path: str) -> float:
    """Get media duration in seconds with ffprobe."""
    result = subprocess.run([
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        media_path,
    ], check=True, capture_output=True, text=True)
    return float(result.stdout.strip())


def find_existing_clip_durations(output_dir: Path, slide_count: int) -> list[float] | None:
    durations = []
    for i in range(1, slide_count + 1):
        clip_path = output_dir / f"clip_{i:03d}.mp4"
        if not clip_path.exists():
            return None
        durations.append(get_media_duration(str(clip_path)))
    return durations


