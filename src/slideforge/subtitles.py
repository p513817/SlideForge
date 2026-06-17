"""Subtitle generation and rendering helpers."""

import json
import math
import re
import subprocess
from pathlib import Path

from . import runtime as cfg
from .video import get_media_duration

def escape_ffmpeg_filter_path(path: str | Path) -> str:
    """Escape Windows paths for use inside ffmpeg filter arguments."""
    return str(Path(path).resolve()).replace("\\", "/").replace(":", r"\:")


def format_srt_time(seconds: float) -> str:
    """Format seconds as an SRT timestamp."""
    milliseconds = int(round(seconds * 1000))
    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000
    minutes = milliseconds // 60_000
    milliseconds %= 60_000
    secs = milliseconds // 1000
    millis = milliseconds % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def split_subtitle_text(text: str, max_chars: int | None = None) -> list[str]:
    """Split speaker notes into subtitle chunks that are easier to read."""
    if max_chars is None:
        max_chars = cfg.SUBTITLE_LINE_CHARS
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return []

    sentences = [
        part.strip()
        for part in re.split(r"(?<=[。！？!?；;])\s*", cleaned)
        if part.strip()
    ]

    chunks = []
    for sentence in sentences:
        while len(sentence) > max_chars:
            cut = sentence.rfind("，", 0, max_chars + 1)
            if cut <= 0:
                cut = sentence.rfind("、", 0, max_chars + 1)
            if cut <= 0:
                cut = max_chars
            chunks.append(sentence[:cut + 1].strip())
            sentence = sentence[cut + 1:].strip()
        if sentence:
            chunks.append(sentence)
    return chunks


def split_long_subtitle_text(text: str, max_chars: int | None = None) -> list[str]:
    if max_chars is None:
        max_chars = cfg.SUBTITLE_MAX_CHARS
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return []

    chunks = []
    remaining = cleaned
    preferred_breaks = "。！？!?；;，、,"

    while len(remaining) > max_chars:
        cut = -1
        for mark in preferred_breaks:
            cut = max(cut, remaining.rfind(mark, 0, max_chars + 1))
        if cut < max(cfg.SUBTITLE_MIN_CHARS, max_chars // 2):
            forward_limit = min(len(remaining), max_chars + 12)
            forward_cuts = [
                remaining.find(mark, max_chars // 2, forward_limit)
                for mark in preferred_breaks
            ]
            forward_cuts = [index for index in forward_cuts if index != -1]
            cut = min(forward_cuts) if forward_cuts else max_chars - 1
        chunks.append(remaining[:cut + 1].strip())
        remaining = remaining[cut + 1:].strip()

    if remaining:
        chunks.append(remaining)

    cleaned_chunks = []
    for chunk in chunks:
        if cleaned_chunks and re.fullmatch(r"[。！？!?；;，、,]+", chunk):
            cleaned_chunks[-1] = f"{cleaned_chunks[-1]}{chunk}"
        else:
            cleaned_chunks.append(chunk)
    return cleaned_chunks


def wrap_subtitle_text(text: str, line_chars: int | None = None,
                       max_lines: int | None = None) -> str:
    if line_chars is None:
        line_chars = cfg.SUBTITLE_LINE_CHARS
    if max_lines is None:
        max_lines = cfg.SUBTITLE_MAX_LINES
    if len(text) <= line_chars:
        return text

    lines = []
    remaining = text
    for _ in range(max_lines - 1):
        if len(remaining) <= line_chars:
            break
        cut = -1
        for mark in "，、, ":
            cut = max(cut, remaining.rfind(mark, 0, line_chars + 1))
        if cut < line_chars // 2:
            cut = line_chars - 1
        lines.append(remaining[:cut + 1].strip())
        remaining = remaining[cut + 1:].strip()

    if remaining:
        lines.append(remaining)

    cleaned_lines = []
    for line in lines:
        if cleaned_lines and re.fullmatch(r"[。！？!?；;，、,]+", line):
            cleaned_lines[-1] = f"{cleaned_lines[-1]}{line}"
        else:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def metadata_paths_for_audio(audio_path: str) -> list[Path]:
    """Infer possible word-boundary metadata paths from an audio filename."""
    match = re.search(r"audio_(\d{3})", Path(audio_path).name)
    if not match:
        stem = Path(audio_path).stem
        return [
            Path(audio_path).with_name(stem + "_metadata.jsonl"),
            Path(audio_path).with_name(stem + "_words.json"),
        ]

    slide_no = match.group(1)
    return [
        Path(audio_path).with_name(f"audio_{slide_no}_metadata.jsonl"),
        Path(audio_path).with_name(f"audio_{slide_no}_words.json"),
    ]


def metadata_path_for_audio(audio_path: str) -> Path:
    for path in metadata_paths_for_audio(audio_path):
        if path.exists():
            return path
    return metadata_paths_for_audio(audio_path)[0]


def ticks_to_seconds(value: int | float) -> float:
    """Convert Edge TTS word-boundary ticks, which use 100 ns units, to seconds."""
    return float(value) / 10_000_000


def load_word_boundaries(audio_path: str) -> list[dict]:
    metadata_path = metadata_path_for_audio(audio_path)
    if not metadata_path.exists():
        return []
    with open(metadata_path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if not raw:
        return []

    if metadata_path.suffix == ".jsonl":
        messages = [json.loads(line) for line in raw.splitlines() if line.strip()]
    else:
        parsed = json.loads(raw)
        messages = parsed if isinstance(parsed, list) else [parsed]

    return [
        message for message in messages
        if message.get("type") in ("WordBoundary", "SentenceBoundary")
    ]


def describe_word_boundary_status(audio_paths: list[str]) -> dict[str, list[str]]:
    status = {
        "missing": [],
        "empty": [],
        "no_boundaries": [],
    }

    for audio_path in audio_paths:
        metadata_path = metadata_path_for_audio(audio_path)
        label = Path(audio_path).name

        if not metadata_path.exists():
            expected = " or ".join(path.name for path in metadata_paths_for_audio(audio_path))
            status["missing"].append(f"{label} (expected: {expected})")
            continue

        raw = metadata_path.read_text(encoding="utf-8").strip()
        if not raw:
            status["empty"].append(metadata_path.name)
            continue

        if not load_word_boundaries(audio_path):
            status["no_boundaries"].append(metadata_path.name)

    return status


def warn_missing_word_boundaries(audio_paths: list[str]):
    status = describe_word_boundary_status(audio_paths)

    print("   WARNING: No usable Edge TTS WordBoundary / SentenceBoundary timeline was found. Subtitles cannot be precisely aligned.")
    if status["missing"]:
        print(f"   - Missing metadata for {len(status['missing'])} audio files")
        for item in status["missing"][:5]:
            print(f"     {item}")
        if len(status["missing"]) > 5:
            print(f"     ...and {len(status['missing']) - 5} more")
    if status["empty"]:
        print(f"   - Empty metadata files: {', '.join(status['empty'][:5])}")
        if len(status["empty"]) > 5:
            print(f"     ...and {len(status['empty']) - 5} more")
    if status["no_boundaries"]:
        print(f"   - Metadata files without WordBoundary/SentenceBoundary entries: {', '.join(status['no_boundaries'][:5])}")
        if len(status["no_boundaries"]) > 5:
            print(f"     ...and {len(status['no_boundaries']) - 5} more")


def group_word_boundaries(boundaries: list[dict],
                          max_chars: int | None = None,
                          min_chars: int | None = None,
                          max_duration: float | None = None) -> list[list[dict]]:
    if max_chars is None:
        max_chars = cfg.SUBTITLE_MAX_CHARS
    if min_chars is None:
        min_chars = cfg.SUBTITLE_MIN_CHARS
    if max_duration is None:
        max_duration = cfg.SUBTITLE_MAX_DURATION
    groups = []
    current = []
    current_text = ""

    for boundary in boundaries:
        text = str(boundary.get("text", "")).strip()
        if not text:
            continue

        if current and len(current_text + text) > max_chars:
            groups.append(current)
            current = []
            current_text = ""

        current.append(boundary)
        current_text += text

        first = current[0]
        elapsed = (
            ticks_to_seconds(boundary.get("offset", 0))
            + ticks_to_seconds(boundary.get("duration", 0))
            - ticks_to_seconds(first.get("offset", 0))
        )
        ends_sentence = re.search(r"[。！？!?；;]$", text) is not None

        if len(current_text) >= min_chars and (ends_sentence or elapsed >= max_duration):
            groups.append(current)
            current = []
            current_text = ""

    if current:
        groups.append(current)

    return groups


def write_subtitles_from_word_boundaries(notes: list[str], audio_paths: list[str],
                                         output_path: Path,
                                         first_slide_delay: float = 0.0,
                                         slide_durations: list[float] | None = None) -> bool:
    """Generate a more precise SRT file from Edge TTS word-boundary metadata."""
    if not all(metadata_path_for_audio(path).exists() for path in audio_paths):
        return False

    all_boundaries = [load_word_boundaries(path) for path in audio_paths]
    if not any(boundaries for boundaries in all_boundaries):
        return False

    subtitle_index = 1
    current_time = 0.0

    with open(output_path, "w", encoding="utf-8") as f:
        for slide_index, (audio_path, boundaries) in enumerate(zip(audio_paths, all_boundaries)):
            duration = (
                slide_durations[slide_index]
                if slide_durations and slide_index < len(slide_durations)
                else get_media_duration(audio_path)
            )
            groups = group_word_boundaries(boundaries)

            if not groups:
                current_time += duration
                continue

            subtitle_delay = first_slide_delay if slide_index == 0 else 0.0
            group_starts = [
                current_time + subtitle_delay + ticks_to_seconds(group[0].get("offset", 0))
                for group in groups
            ]

            for group_index, group in enumerate(groups):
                text = "".join(str(item.get("text", "")).strip() for item in group)
                if not text:
                    continue

                first = group[0]
                last = group[-1]
                start = current_time + subtitle_delay + ticks_to_seconds(first.get("offset", 0))
                spoken_end = (
                    current_time
                    + subtitle_delay
                    + ticks_to_seconds(last.get("offset", 0))
                    + ticks_to_seconds(last.get("duration", 0))
                    + 0.25
                )
                next_start = (
                    group_starts[group_index + 1] - 0.05
                    if group_index + 1 < len(group_starts)
                    else current_time + duration
                )
                sentence_end = min(spoken_end, next_start)
                duration_target_chunks = max(1, math.ceil((sentence_end - start) / cfg.SUBTITLE_MAX_DURATION))
                dynamic_max_chars = max(
                    cfg.SUBTITLE_MIN_CHARS,
                    min(cfg.SUBTITLE_MAX_CHARS, math.ceil(len(text) / duration_target_chunks)),
                )
                chunks = split_long_subtitle_text(text, dynamic_max_chars)
                if len(chunks) <= 1:
                    preferred_end = min(spoken_end, start + cfg.SUBTITLE_MAX_DURATION)
                    end = min(max(preferred_end, start + cfg.SUBTITLE_MIN_DURATION), next_start)
                    f.write(f"{subtitle_index}\n")
                    f.write(f"{format_srt_time(start)} --> {format_srt_time(end)}\n")
                    f.write(f"{wrap_subtitle_text(text)}\n\n")
                    subtitle_index += 1
                    continue

                end = sentence_end
                total_chars = sum(len(chunk) for chunk in chunks)
                cursor = start
                available = max(end - start, cfg.SUBTITLE_MIN_DURATION)
                for chunk_index, chunk in enumerate(chunks):
                    if chunk_index == len(chunks) - 1:
                        chunk_end = end
                    else:
                        ratio = len(chunk) / total_chars if total_chars else 1 / len(chunks)
                        chunk_end = min(cursor + max(available * ratio, cfg.SUBTITLE_MIN_DURATION), end)
                    if chunk_end <= cursor:
                        break
                    f.write(f"{subtitle_index}\n")
                    f.write(f"{format_srt_time(cursor)} --> {format_srt_time(chunk_end)}\n")
                    f.write(f"{wrap_subtitle_text(chunk)}\n\n")
                    subtitle_index += 1
                    cursor = chunk_end

            current_time += duration

    return subtitle_index > 1


def write_subtitles(notes: list[str], audio_paths: list[str], output_path: Path,
                    first_slide_delay: float = 0.0,
                    slide_durations: list[float] | None = None):
    """Generate SRT subtitles by evenly distributing notes over slide audio duration."""
    subtitle_index = 1
    current_time = 0.0

    with open(output_path, "w", encoding="utf-8") as f:
        for slide_index, (note, audio_path) in enumerate(zip(notes, audio_paths)):
            duration = (
                slide_durations[slide_index]
                if slide_durations and slide_index < len(slide_durations)
                else get_media_duration(audio_path)
            )
            chunks = split_subtitle_text(note)

            if not chunks:
                current_time += duration
                continue

            subtitle_delay = first_slide_delay if slide_index == 0 else 0.0
            readable_duration = max(duration - subtitle_delay, 0.1)
            chunk_duration = readable_duration / len(chunks)
            for i, chunk in enumerate(chunks):
                start = current_time + subtitle_delay + i * chunk_duration
                end = current_time + subtitle_delay + (i + 1) * chunk_duration
                f.write(f"{subtitle_index}\n")
                f.write(f"{format_srt_time(start)} --> {format_srt_time(end)}\n")
                f.write(f"{chunk}\n\n")
                subtitle_index += 1

            current_time += duration


def burn_subtitles(input_video: str, subtitle_path: Path, output_video: str):
    """Burn SRT subtitles into an MP4 video."""
    if not subtitle_path.exists() or subtitle_path.stat().st_size == 0:
        raise RuntimeError(f"Subtitle file does not exist or is empty: {subtitle_path}")

    style = (
        f"Fontname={cfg.SUBTITLE_FONT_NAME},"
        f"Fontsize={cfg.SUBTITLE_FONT_SIZE},"
        f"PrimaryColour={cfg.SUBTITLE_PRIMARY_COLOUR},"
        f"OutlineColour={cfg.SUBTITLE_OUTLINE_COLOUR},"
        f"BorderStyle={cfg.SUBTITLE_BORDER_STYLE},"
        f"Outline={cfg.SUBTITLE_OUTLINE},"
        f"Shadow={cfg.SUBTITLE_SHADOW},"
        f"Alignment={cfg.SUBTITLE_ALIGNMENT},"
        f"MarginV={cfg.SUBTITLE_MARGIN_V}"
    )
    filter_value = (
        f"subtitles=filename={subtitle_path.name}:"
        f"fontsdir='{escape_ffmpeg_filter_path(cfg.SUBTITLE_FONTS_DIR)}':"
        f"force_style='{style}'"
    )

    try:
        subprocess.run([
            "ffmpeg",
            "-i", str(Path(input_video).resolve()),
            "-vf", filter_value,
            "-c:a", "copy",
            "-y",
            str(Path(output_video).resolve()),
        ], check=True, capture_output=True, text=True, cwd=str(subtitle_path.parent))
    except subprocess.CalledProcessError as exc:
        print("ERROR: ffmpeg failed while burning subtitles:")
        if exc.stderr:
            print(exc.stderr)
        raise


def find_existing_subtitle_audio_paths(output_dir: Path, slide_count: int) -> list[str]:
    """Find existing audio files for subtitle-only rerendering."""
    paths = []
    for i in range(1, slide_count + 1):
        delayed = output_dir / f"audio_{i:03d}_delayed.mp3"
        padded = output_dir / f"audio_{i:03d}_padded.mp3"
        original = output_dir / f"audio_{i:03d}.mp3"

        if delayed.exists():
            paths.append(str(delayed))
        elif padded.exists():
            paths.append(str(padded))
        elif original.exists():
            paths.append(str(original))
        else:
            raise FileNotFoundError(
                f"Audio file for slide {i} was not found: {delayed.name} / {padded.name} / {original.name}"
            )
    return paths


def get_effective_first_slide_delay(audio_paths: list[str]) -> float:
    if audio_paths and "_delayed" in Path(audio_paths[0]).name:
        return cfg.INITIAL_NARRATION_DELAY
    return 0.0

