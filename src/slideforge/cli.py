"""Command-line entry point for SlideForge."""

import argparse
import asyncio
import sys

from . import app, runtime, settings
from .environment import doctor


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="slideforge",
        description="Convert PowerPoint speaker notes into an Edge TTS narrated video",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("pptx", nargs="?", help="PowerPoint .pptx path")
    parser.add_argument("-c", "--config", help="YAML/JSON config file path")
    parser.add_argument("--doctor", action="store_true", help="Check ffmpeg, ffprobe, and PowerPoint COM availability, then exit")
    parser.add_argument("--write-config", metavar="PATH", help="Write an example YAML config file and exit")
    parser.add_argument("-o", "--output", help="Output video path")
    parser.add_argument("--subtitled-output", help="Output video path after burning subtitles")
    parser.add_argument("--temp-dir", help="Temporary working directory")
    parser.add_argument("--voice", help="Edge TTS voice, for example zh-TW-HsiaoYuNeural")
    parser.add_argument("--rate", help="Edge TTS speaking rate, for example +20%% or -10%%")
    parser.add_argument("--width", type=int, help="Slide export width")
    parser.add_argument("--height", type=int, help="Slide export height")
    parser.add_argument("--pause", type=float, dest="pause_between_slides", help="Pause after each slide in seconds")
    parser.add_argument("--empty-slide-duration", type=float, help="Duration for slides without notes in seconds")
    parser.add_argument("--initial-delay", type=float, dest="initial_narration_delay", help="Delay narration on the first slide in seconds")
    parser.add_argument("--subtitles", action=argparse.BooleanOptionalAction, default=None, help="Generate and burn subtitles")
    parser.add_argument("--subtitles-only", action="store_true", default=None, help="Regenerate and burn subtitles from existing temporary files")
    parser.add_argument("--allow-imprecise-subtitles", action="store_true", help="Allow subtitle fallback based on average timings when TTS metadata is missing")
    parser.add_argument("--subtitle-line-chars", type=int, help="Maximum characters per subtitle line")
    parser.add_argument("--subtitle-max-lines", type=int, help="Maximum lines per subtitle block")
    parser.add_argument("--subtitle-font-name", help="Subtitle font name")
    parser.add_argument("--subtitle-fonts-dir", help="Subtitle fonts directory")
    parser.add_argument("--subtitle-font-size", type=int, help="Subtitle font size")
    parser.add_argument("--subtitle-primary-colour", help="Subtitle text colour in ASS format, for example &H00FFFFFF")
    parser.add_argument("--subtitle-outline-colour", help="Subtitle outline colour in ASS format, for example &H00000000")
    parser.add_argument("--subtitle-border-style", type=int, help="ASS BorderStyle")
    parser.add_argument("--subtitle-outline", type=int, help="Subtitle outline thickness")
    parser.add_argument("--subtitle-shadow", type=int, help="Subtitle shadow size")
    parser.add_argument("--subtitle-alignment", type=int, help="ASS alignment value, where 2 is bottom-center")
    parser.add_argument("--subtitle-margin-v", type=int, help="Subtitle vertical margin")
    return parser


def collect_overrides(args: argparse.Namespace) -> dict[str, object]:
    overrides = {}
    if args.config:
        overrides.update(settings.load_config_file(args.config))

    cli_overrides = {
        "pptx": args.pptx,
        "output": args.output,
        "subtitled_output": args.subtitled_output,
        "temp_dir": args.temp_dir,
        "voice": args.voice,
        "rate": args.rate,
        "width": args.width,
        "height": args.height,
        "pause_between_slides": args.pause_between_slides,
        "empty_slide_duration": args.empty_slide_duration,
        "initial_narration_delay": args.initial_narration_delay,
        "subtitles": args.subtitles,
        "subtitles_only": args.subtitles_only,
        "subtitle_line_chars": args.subtitle_line_chars,
        "subtitle_max_lines": args.subtitle_max_lines,
        "subtitle_font_name": args.subtitle_font_name,
        "subtitle_fonts_dir": args.subtitle_fonts_dir,
        "subtitle_font_size": args.subtitle_font_size,
        "subtitle_primary_colour": args.subtitle_primary_colour,
        "subtitle_outline_colour": args.subtitle_outline_colour,
        "subtitle_border_style": args.subtitle_border_style,
        "subtitle_outline": args.subtitle_outline,
        "subtitle_shadow": args.subtitle_shadow,
        "subtitle_alignment": args.subtitle_alignment,
        "subtitle_margin_v": args.subtitle_margin_v,
    }
    if args.allow_imprecise_subtitles:
        cli_overrides["require_precise_subtitle_timing"] = False

    overrides.update({key: value for key, value in cli_overrides.items() if value is not None})
    return overrides


def configure_from_cli(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.write_config:
        settings.write_example_config(args.write_config)
        print(f"Example config written: {args.write_config}")
        sys.exit(0)

    if args.doctor:
        sys.exit(0 if doctor() else 1)

    app.apply_config(collect_overrides(args))
    if not runtime.PPTX_PATH:
        parser.error("Please provide a PPTX path, for example: slideforge slides.pptx, or use --config config.yaml")


def main(argv: list[str] | None = None) -> None:
    configure_from_cli(argv)
    asyncio.run(app.main())
