"""Configuration loading and option metadata for SlideForge."""

import json
from pathlib import Path

DEFAULT_CONFIG = {
    "PPTX_PATH": "",
    "OUTPUT_VIDEO": "output/output.mp4",
    "OUTPUT_VIDEO_WITH_SUBTITLES": "output/output_subtitled.mp4",
    "ENABLE_SUBTITLES": True,
    "SUBTITLES_ONLY": False,
    "REQUIRE_PRECISE_SUBTITLE_TIMING": True,
    "INITIAL_NARRATION_DELAY": 0.0,
    "VOICE": "zh-TW-HsiaoYuNeural",
    "RATE": "+55%",
    "SLIDE_WIDTH": 1920,
    "SLIDE_HEIGHT": 1080,
    "PAUSE_BETWEEN_SLIDES": 0.5,
    "EMPTY_SLIDE_DURATION": 1.0,
    "SUBTITLE_LINE_CHARS": 28,
    "SUBTITLE_MAX_LINES": 2,
    "SUBTITLE_MIN_CHARS": 14,
    "SUBTITLE_MIN_DURATION": 1.0,
    "SUBTITLE_MAX_DURATION": 4.0,
    "SUBTITLE_FONT_NAME": "Microsoft JhengHei",
    "SUBTITLE_FONTS_DIR": r"C:\Windows\Fonts",
    "SUBTITLE_FONT_SIZE": 12,
    "SUBTITLE_PRIMARY_COLOUR": "&H00FFFFFF",
    "SUBTITLE_OUTLINE_COLOUR": "&H00000000",
    "SUBTITLE_BORDER_STYLE": 1,
    "SUBTITLE_OUTLINE": 1,
    "SUBTITLE_SHADOW": 1,
    "SUBTITLE_ALIGNMENT": 2,
    "SUBTITLE_MARGIN_V": 10,
    "TEMP_DIR": Path("output/.slideforge"),
}

CONFIG_ALIASES = {
    "pptx": "PPTX_PATH",
    "input.pptx": "PPTX_PATH",
    "output": "OUTPUT_VIDEO",
    "output.video": "OUTPUT_VIDEO",
    "output_video": "OUTPUT_VIDEO",
    "subtitled_output": "OUTPUT_VIDEO_WITH_SUBTITLES",
    "output.subtitled": "OUTPUT_VIDEO_WITH_SUBTITLES",
    "output.subtitled_video": "OUTPUT_VIDEO_WITH_SUBTITLES",
    "output_video_with_subtitles": "OUTPUT_VIDEO_WITH_SUBTITLES",
    "subtitles": "ENABLE_SUBTITLES",
    "subtitle.enabled": "ENABLE_SUBTITLES",
    "subtitles.enabled": "ENABLE_SUBTITLES",
    "enable_subtitles": "ENABLE_SUBTITLES",
    "subtitles_only": "SUBTITLES_ONLY",
    "subtitle.only": "SUBTITLES_ONLY",
    "subtitles.only": "SUBTITLES_ONLY",
    "require_precise_subtitle_timing": "REQUIRE_PRECISE_SUBTITLE_TIMING",
    "subtitle.require_precise_timing": "REQUIRE_PRECISE_SUBTITLE_TIMING",
    "subtitles.require_precise_timing": "REQUIRE_PRECISE_SUBTITLE_TIMING",
    "initial_delay": "INITIAL_NARRATION_DELAY",
    "initial_narration_delay": "INITIAL_NARRATION_DELAY",
    "timing.initial_narration_delay": "INITIAL_NARRATION_DELAY",
    "voice": "VOICE",
    "tts.voice": "VOICE",
    "rate": "RATE",
    "tts.rate": "RATE",
    "width": "SLIDE_WIDTH",
    "output.width": "SLIDE_WIDTH",
    "slide_width": "SLIDE_WIDTH",
    "height": "SLIDE_HEIGHT",
    "output.height": "SLIDE_HEIGHT",
    "slide_height": "SLIDE_HEIGHT",
    "pause_between_slides": "PAUSE_BETWEEN_SLIDES",
    "timing.pause_between_slides": "PAUSE_BETWEEN_SLIDES",
    "empty_slide_duration": "EMPTY_SLIDE_DURATION",
    "timing.empty_slide_duration": "EMPTY_SLIDE_DURATION",
    "subtitle_line_chars": "SUBTITLE_LINE_CHARS",
    "subtitle.line_chars": "SUBTITLE_LINE_CHARS",
    "subtitles.line_chars": "SUBTITLE_LINE_CHARS",
    "subtitle_max_lines": "SUBTITLE_MAX_LINES",
    "subtitle.max_lines": "SUBTITLE_MAX_LINES",
    "subtitles.max_lines": "SUBTITLE_MAX_LINES",
    "subtitle_min_chars": "SUBTITLE_MIN_CHARS",
    "subtitle.min_chars": "SUBTITLE_MIN_CHARS",
    "subtitles.min_chars": "SUBTITLE_MIN_CHARS",
    "subtitle_min_duration": "SUBTITLE_MIN_DURATION",
    "subtitle.min_duration": "SUBTITLE_MIN_DURATION",
    "subtitles.min_duration": "SUBTITLE_MIN_DURATION",
    "subtitle_max_duration": "SUBTITLE_MAX_DURATION",
    "subtitle.max_duration": "SUBTITLE_MAX_DURATION",
    "subtitles.max_duration": "SUBTITLE_MAX_DURATION",
    "subtitle_font_name": "SUBTITLE_FONT_NAME",
    "subtitle.font_name": "SUBTITLE_FONT_NAME",
    "subtitles.font_name": "SUBTITLE_FONT_NAME",
    "subtitle_fonts_dir": "SUBTITLE_FONTS_DIR",
    "subtitle.fonts_dir": "SUBTITLE_FONTS_DIR",
    "subtitles.fonts_dir": "SUBTITLE_FONTS_DIR",
    "subtitle_font_size": "SUBTITLE_FONT_SIZE",
    "subtitle.font_size": "SUBTITLE_FONT_SIZE",
    "subtitles.font_size": "SUBTITLE_FONT_SIZE",
    "subtitle_primary_colour": "SUBTITLE_PRIMARY_COLOUR",
    "subtitle.primary_colour": "SUBTITLE_PRIMARY_COLOUR",
    "subtitles.primary_colour": "SUBTITLE_PRIMARY_COLOUR",
    "subtitle_primary_color": "SUBTITLE_PRIMARY_COLOUR",
    "subtitle.primary_color": "SUBTITLE_PRIMARY_COLOUR",
    "subtitles.primary_color": "SUBTITLE_PRIMARY_COLOUR",
    "subtitle_outline_colour": "SUBTITLE_OUTLINE_COLOUR",
    "subtitle.outline_colour": "SUBTITLE_OUTLINE_COLOUR",
    "subtitles.outline_colour": "SUBTITLE_OUTLINE_COLOUR",
    "subtitle_outline_color": "SUBTITLE_OUTLINE_COLOUR",
    "subtitle.outline_color": "SUBTITLE_OUTLINE_COLOUR",
    "subtitles.outline_color": "SUBTITLE_OUTLINE_COLOUR",
    "subtitle_border_style": "SUBTITLE_BORDER_STYLE",
    "subtitle.border_style": "SUBTITLE_BORDER_STYLE",
    "subtitles.border_style": "SUBTITLE_BORDER_STYLE",
    "subtitle_outline": "SUBTITLE_OUTLINE",
    "subtitle.outline": "SUBTITLE_OUTLINE",
    "subtitles.outline": "SUBTITLE_OUTLINE",
    "subtitle_shadow": "SUBTITLE_SHADOW",
    "subtitle.shadow": "SUBTITLE_SHADOW",
    "subtitles.shadow": "SUBTITLE_SHADOW",
    "subtitle_alignment": "SUBTITLE_ALIGNMENT",
    "subtitle.alignment": "SUBTITLE_ALIGNMENT",
    "subtitles.alignment": "SUBTITLE_ALIGNMENT",
    "subtitle_margin_v": "SUBTITLE_MARGIN_V",
    "subtitle.margin_v": "SUBTITLE_MARGIN_V",
    "subtitles.margin_v": "SUBTITLE_MARGIN_V",
    "temp_dir": "TEMP_DIR",
    "output.temp_dir": "TEMP_DIR",
}

CONFIG_TYPES = {
    "PPTX_PATH": str,
    "OUTPUT_VIDEO": str,
    "OUTPUT_VIDEO_WITH_SUBTITLES": str,
    "ENABLE_SUBTITLES": bool,
    "SUBTITLES_ONLY": bool,
    "REQUIRE_PRECISE_SUBTITLE_TIMING": bool,
    "INITIAL_NARRATION_DELAY": float,
    "VOICE": str,
    "RATE": str,
    "SLIDE_WIDTH": int,
    "SLIDE_HEIGHT": int,
    "PAUSE_BETWEEN_SLIDES": float,
    "EMPTY_SLIDE_DURATION": float,
    "SUBTITLE_LINE_CHARS": int,
    "SUBTITLE_MAX_LINES": int,
    "SUBTITLE_MIN_CHARS": int,
    "SUBTITLE_MIN_DURATION": float,
    "SUBTITLE_MAX_DURATION": float,
    "SUBTITLE_FONT_NAME": str,
    "SUBTITLE_FONTS_DIR": str,
    "SUBTITLE_FONT_SIZE": int,
    "SUBTITLE_PRIMARY_COLOUR": str,
    "SUBTITLE_OUTLINE_COLOUR": str,
    "SUBTITLE_BORDER_STYLE": int,
    "SUBTITLE_OUTLINE": int,
    "SUBTITLE_SHADOW": int,
    "SUBTITLE_ALIGNMENT": int,
    "SUBTITLE_MARGIN_V": int,
    "TEMP_DIR": Path,
}

EXAMPLE_CONFIG = """# SlideForge config
input:
  pptx: "D:/path/to/your/slides.pptx"

output:
  video: "output/output.mp4"
  subtitled_video: "output/output_subtitled.mp4"
  temp_dir: "output/.slideforge"
  width: 1920
  height: 1080

tts:
  voice: "zh-TW-HsiaoYuNeural"
  rate: "+55%"

timing:
  pause_between_slides: 0.5
  empty_slide_duration: 1.0
  initial_narration_delay: 0.0

subtitles:
  enabled: true
  only: false
  require_precise_timing: true
  line_chars: 28
  max_lines: 2
  min_chars: 14
  min_duration: 1.0
  max_duration: 4.0
  font_name: "Microsoft JhengHei"
  fonts_dir: "C:/Windows/Fonts"
  font_size: 12
  primary_colour: "&H00FFFFFF"
  outline_colour: "&H00000000"
  border_style: 1
  outline: 1
  shadow: 1
  alignment: 2
  margin_v: 10
"""


def str_to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    lowered = str(value).strip().lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Cannot parse boolean value: {value}")


def flatten_config(data: dict, prefix: str = "") -> dict[str, object]:
    flattened = {}
    for key, value in data.items():
        normalized_key = str(key).replace("-", "_").lower()
        full_key = f"{prefix}.{normalized_key}" if prefix else normalized_key
        if isinstance(value, dict):
            flattened.update(flatten_config(value, full_key))
        else:
            flattened[full_key] = value
    return flattened


def load_config_file(path: str | Path) -> dict[str, object]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    if config_path.suffix.lower() == ".json":
        data = json.loads(config_path.read_text(encoding="utf-8"))
    else:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("Reading YAML config files requires PyYAML. Run: pip install pyyaml") from exc
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError("The config file root must be a YAML/JSON object")
    return flatten_config(data)


def coerce_config_value(name: str, value):
    expected_type = CONFIG_TYPES[name]
    if expected_type is bool:
        return str_to_bool(value)
    if expected_type is Path:
        return Path(value)
    return expected_type(value)


def write_example_config(path: str | Path):
    Path(path).write_text(EXAMPLE_CONFIG, encoding="utf-8")
