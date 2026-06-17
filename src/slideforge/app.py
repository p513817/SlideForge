"""Pipeline orchestration for SlideForge."""

import sys
from pathlib import Path

from . import runtime as cfg
from .audio import add_pause_to_audio, generate_all_audio, prepend_silence_to_audio
from .environment import check_ffmpeg, check_powerpoint
from .powerpoint import export_slides_as_images, get_gif_overlays, get_slide_notes
from .subtitles import (
    burn_subtitles,
    find_existing_subtitle_audio_paths,
    get_effective_first_slide_delay,
    warn_missing_word_boundaries,
    write_subtitles,
    write_subtitles_from_word_boundaries,
)
from .video import concatenate_clips, find_existing_clip_durations, get_media_duration, image_audio_to_clip_with_gifs

apply_config = cfg.apply_config
reset_runtime_config = cfg.reset_runtime_config


def ensure_output_directories(include_temp: bool = True) -> None:
    if include_temp:
        cfg.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    Path(cfg.OUTPUT_VIDEO).parent.mkdir(parents=True, exist_ok=True)
    Path(cfg.OUTPUT_VIDEO_WITH_SUBTITLES).parent.mkdir(parents=True, exist_ok=True)


def rerender_subtitles_from_temp():
    """Regenerate subtitles and burn them into an existing output video."""
    print("=" * 50)
    print("  SlideForge -> Subtitle Rerender")
    print("=" * 50)

    check_ffmpeg()

    if not Path(cfg.PPTX_PATH).exists():
        print(f"ERROR: PPTX file not found: {cfg.PPTX_PATH}")
        sys.exit(1)
    if not cfg.TEMP_DIR.exists():
        print(f"ERROR: Temporary directory not found: {cfg.TEMP_DIR}")
        sys.exit(1)
    if not Path(cfg.OUTPUT_VIDEO).exists():
        print(f"ERROR: Source video not found: {cfg.OUTPUT_VIDEO}")
        sys.exit(1)
    ensure_output_directories(include_temp=False)

    print("\nReading speaker notes...")
    notes = get_slide_notes(cfg.PPTX_PATH)
    audio_paths = find_existing_subtitle_audio_paths(cfg.TEMP_DIR, len(notes))
    first_slide_delay = get_effective_first_slide_delay(audio_paths)
    slide_durations = find_existing_clip_durations(cfg.TEMP_DIR, len(notes))
    if slide_durations:
        print("   Using existing clip_*.mp4 durations to align cumulative subtitle timing")
    else:
        print("   WARNING: Complete clip_*.mp4 files were not found. Falling back to audio durations; later subtitles may drift.")

    subtitle_path = cfg.TEMP_DIR / "subtitles.srt"
    print("\nRegenerating subtitle file...")
    if write_subtitles_from_word_boundaries(notes, audio_paths, subtitle_path, first_slide_delay, slide_durations):
        print("   Generated subtitles from Edge TTS word-boundary metadata")
    else:
        warn_missing_word_boundaries(audio_paths)
        if cfg.REQUIRE_PRECISE_SUBTITLE_TIMING:
            raise RuntimeError(
                "No usable TTS word-boundary metadata was found. Run a full render first with subtitles.only=false "
                "to generate files such as audio_001_metadata.jsonl, then rerender subtitles."
            )
        print("   WARNING: Falling back to average timings; subtitles may be inaccurate")
        write_subtitles(notes, audio_paths, subtitle_path, first_slide_delay, slide_durations)
    print(f"   Subtitle file: {subtitle_path}")

    print("\nBurning subtitles...")
    burn_subtitles(cfg.OUTPUT_VIDEO, subtitle_path, cfg.OUTPUT_VIDEO_WITH_SUBTITLES)

    subtitled_size = Path(cfg.OUTPUT_VIDEO_WITH_SUBTITLES).stat().st_size / (1024 * 1024)
    print("\nDone.")
    print(f"   Subtitled video: {cfg.OUTPUT_VIDEO_WITH_SUBTITLES}  ({subtitled_size:.1f} MB)")
    print(f"   Subtitle file: {subtitle_path}")


async def main():
    if cfg.SUBTITLES_ONLY:
        rerender_subtitles_from_temp()
        return

    print("=" * 50)
    print("  SlideForge -> Narrated Video Converter")
    print("=" * 50)

    # Environment checks.
    check_ffmpeg()
    check_powerpoint()

    if not Path(cfg.PPTX_PATH).exists():
        print(f"ERROR: PPTX file not found: {cfg.PPTX_PATH}")
        sys.exit(1)

    ensure_output_directories()

    # Step 1: Read speaker notes.
    print("\nStep 1 / 5  Reading speaker notes...")
    notes = get_slide_notes(cfg.PPTX_PATH)
    total = len(notes)
    filled = sum(1 for n in notes if n.strip())
    print(f"   Total slides: {total}; with notes: {filled}; empty: {total - filled}")

    # Step 2: Export slides as images.
    print("\nStep 2 / 5  Exporting slide images (PowerPoint will open briefly)...")
    slide_paths = export_slides_as_images(cfg.PPTX_PATH, cfg.TEMP_DIR)

    # Step 3: Generate narration audio.
    print(f"\nStep 3 / 5  Generating TTS narration (voice: {cfg.VOICE})...")
    audio_paths = await generate_all_audio(notes, cfg.TEMP_DIR)

    # Add pauses between slide clips.
    padded_audio_paths = []
    for i, ap in enumerate(audio_paths):
        padded = str(cfg.TEMP_DIR / f"audio_{i+1:03d}_padded.mp3")
        add_pause_to_audio(ap, padded, cfg.PAUSE_BETWEEN_SLIDES)
        if i == 0 and cfg.INITIAL_NARRATION_DELAY > 0:
            delayed = str(cfg.TEMP_DIR / f"audio_{i+1:03d}_delayed.mp3")
            prepend_silence_to_audio(padded, delayed, cfg.INITIAL_NARRATION_DELAY)
            padded = delayed
        padded_audio_paths.append(padded)

    subtitle_path = cfg.TEMP_DIR / "subtitles.srt"

    # Step 4: Compose video clips.
    print("\nStep 4 / 5  Composing video clips...")
    clip_paths = []
    for i, (img, audio) in enumerate(zip(slide_paths, padded_audio_paths)):
        clip_path = str(cfg.TEMP_DIR / f"clip_{i+1:03d}.mp4")
        gifs = get_gif_overlays(cfg.PPTX_PATH, i, cfg.TEMP_DIR)
        if gifs:
            print(f"   Slide {i+1}/{total} ({len(gifs)} GIF overlays)...")
        else:
            print(f"   Slide {i+1}/{total}...")
        image_audio_to_clip_with_gifs(img, audio, clip_path, gifs)
        clip_paths.append(clip_path)

    if cfg.ENABLE_SUBTITLES:
        print("   Generating subtitle file...")
        first_slide_delay = get_effective_first_slide_delay(padded_audio_paths)
        slide_durations = [get_media_duration(path) for path in clip_paths]
        if write_subtitles_from_word_boundaries(
            notes, padded_audio_paths, subtitle_path, first_slide_delay, slide_durations
        ):
            print("   Generated subtitles from Edge TTS word-boundary metadata and clip durations")
        else:
            warn_missing_word_boundaries(padded_audio_paths)
            if cfg.REQUIRE_PRECISE_SUBTITLE_TIMING:
                raise RuntimeError(
                    "Edge TTS did not output usable word-boundary metadata. Stopping subtitle generation to avoid misaligned subtitles."
                )
            print("   WARNING: Falling back to average timings; subtitles may be inaccurate")
            write_subtitles(notes, padded_audio_paths, subtitle_path, first_slide_delay, slide_durations)
        print(f"   Subtitle file: {subtitle_path}")

    print("\nStep 5 / 5  Concatenating clips...")
    concatenate_clips(clip_paths, cfg.OUTPUT_VIDEO)

    if cfg.ENABLE_SUBTITLES:
        print("   Burning subtitles...")
        burn_subtitles(cfg.OUTPUT_VIDEO, subtitle_path, cfg.OUTPUT_VIDEO_WITH_SUBTITLES)

    # Final summary.
    output_size = Path(cfg.OUTPUT_VIDEO).stat().st_size / (1024 * 1024)
    print("\nDone.")
    print(f"   Output video: {cfg.OUTPUT_VIDEO}  ({output_size:.1f} MB)")
    if cfg.ENABLE_SUBTITLES:
        subtitled_size = Path(cfg.OUTPUT_VIDEO_WITH_SUBTITLES).stat().st_size / (1024 * 1024)
        print(f"   Subtitled video: {cfg.OUTPUT_VIDEO_WITH_SUBTITLES}  ({subtitled_size:.1f} MB)")
        print(f"   Subtitle file: {subtitle_path}")
    print(f"   Temporary directory: {cfg.TEMP_DIR} (safe to delete manually)")
