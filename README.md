# SlideForge

SlideForge 會讀取 PowerPoint speaker notes，使用 Edge TTS 產生旁白，再把投影片、音訊與字幕合成 MP4。建議用 YAML 管理專案設定，再用 CLI 參數做臨時覆蓋。

## ✨ 特色功能

> 從一份簡報，鍛造成一支有旁白、有字幕、可直接分享的影片。

```text
PowerPoint notes 📝
        ↓
Edge TTS 旁白 🎙️
        ↓
投影片影像 + 音訊 + 字幕 🎬
        ↓
MP4 成品 🚀
```

| 功能 | 可以做什麼 |
| --- | --- |
| 📝 讀取 speaker notes | 把每張投影片的備忘稿當成旁白腳本，不必另外維護文字檔。 |
| 🎙️ Edge TTS 產生旁白 | 可指定語音與語速，例如 `zh-TW-HsiaoYuNeural` 搭配 `+20%` 或 `+55%`。 |
| 🎬 自動合成 MP4 | 將投影片圖片、旁白音訊與停頓時間串成完整影片。 |
| 💬 燒錄字幕 | 依旁白產生 SRT，並用 FFmpeg/libass 燒進影片。 |
| 🎯 精準字幕時間軸 | 優先使用 Edge TTS word-boundary metadata，讓字幕更貼近實際語音。 |
| ⚙️ YAML 優先設定 | 專案設定集中在 `config.yaml`，臨時調整再用 CLI 覆蓋。 |
| ♻️ 字幕快速重做 | `--subtitles-only` 可利用既有暫存檔重做字幕樣式，不必重新產生整支影片。 |
| 🩺 環境健檢 | `slideforge --doctor` 會檢查 FFmpeg、ffprobe 與 PowerPoint COM 是否可用。 |

## Demo

這支影片是使用 SlideForge 產生的輸出範例：

[Watch the SlideForge demo on YouTube](https://youtu.be/YZXfiuHfQug)

## 需求

- Windows
- Microsoft PowerPoint desktop app
- Python 3.10+
- FFmpeg / ffprobe

## 支援平台

SlideForge 目前的主流程只支援 Windows。投影片匯出圖片時會透過 Microsoft PowerPoint COM automation 操作本機 PowerPoint，因此執行環境必須安裝 PowerPoint desktop app。

macOS、Linux、PowerPoint Online 與沒有 PowerPoint 的 Windows 環境目前不支援完整轉檔流程。這些環境仍可安裝 package 或讀取設定，但無法執行需要 PowerPoint COM 的投影片匯出步驟。

## 安裝

從目前 repo 安裝 CLI：

```bash
pip install .
```

開發模式安裝：

```bash
pip install -e .
```

確認本機環境是否可用。這會檢查 FFmpeg、ffprobe 與 PowerPoint COM：

```bash
slideforge --doctor
```

如果 FFmpeg 尚未安裝，可以使用其中一種方式：

```bash
winget install Gyan.FFmpeg
```

```bash
choco install ffmpeg
```

```bash
scoop install ffmpeg
```

安裝後請重新開啟 terminal，並確認：

```bash
ffmpeg -version
ffprobe -version
```

## 建議用法：YAML 優先

先產生一份設定檔：

```bash
slideforge --write-config config.yaml
```

編輯 `config.yaml`，至少設定 PowerPoint 路徑：

```yaml
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
```

執行：

```bash
slideforge --config config.yaml
```

CLI 參數會覆蓋 YAML，適合臨時調整：

```bash
slideforge --config config.yaml --rate "+20%" --no-subtitles
```

也可以直接用 module 呼叫：

```bash
python -m slideforge --config config.yaml
```

## YAML 設定說明

`input.pptx` 是要轉換的 PowerPoint 檔案。SlideForge 會讀取每一頁 speaker notes 作為旁白文字。

`output.video` 是不含燒錄字幕的影片輸出。`output.subtitled_video` 是燒錄字幕後的影片輸出。`output.temp_dir` 是暫存資料夾，預設放在 `output/.slideforge`。`output.width` 與 `output.height` 控制輸出解析度。

`tts.voice` 是 Edge TTS 語音名稱，例如 `zh-TW-HsiaoYuNeural` 或 `zh-TW-YunJheNeural`。`tts.rate` 是語速，例如 `"+55%"`、`"+20%"` 或 `"-10%"`。

`timing.pause_between_slides` 是每張投影片之間的停頓秒數。`timing.empty_slide_duration` 是沒有旁白的投影片要停留多久。`timing.initial_narration_delay` 是投影片出現後多久才開始旁白。

`subtitles.enabled` 控制是否輸出燒錄字幕影片。`subtitles.only` 只重做字幕，不重新產生 TTS 與投影片片段，適合已經有暫存檔時快速調整字幕樣式。`subtitles.require_precise_timing` 會要求 TTS 提供精準 word boundary，否則直接失敗，避免字幕時間軸不準。

字幕斷行與時間：

- `line_chars`: 每行建議字數
- `max_lines`: 單段字幕最多行數
- `min_chars`: 單段字幕最少字數
- `min_duration`: 單段字幕最短秒數
- `max_duration`: 單段字幕最長秒數

字幕樣式會轉成 FFmpeg/libass 的 `force_style`：

- `font_name`: 字型名稱
- `fonts_dir`: 字型資料夾
- `font_size`: 字體大小
- `primary_colour`: 主要文字顏色，ASS 格式
- `outline_colour`: 外框顏色，ASS 格式
- `border_style`: ASS 邊框樣式
- `outline`: 外框粗細
- `shadow`: 陰影大小
- `alignment`: 字幕位置，`2` 是底部置中
- `margin_v`: 底部距離

## 常用指令

產生範例設定：

```bash
slideforge --write-config config.yaml
```

使用 YAML 執行：

```bash
slideforge --config config.yaml
```

直接指定 PPTX：

```bash
slideforge "D:/path/to/slides.pptx"
```

指定輸出與語音：

```bash
slideforge "D:/path/to/slides.pptx" -o output/lesson.mp4 --subtitled-output output/lesson_subtitled.mp4 --voice zh-TW-HsiaoYuNeural --rate "+35%"
```

不產生燒錄字幕影片：

```bash
slideforge --config config.yaml --no-subtitles
```

只重新產生字幕影片：

```bash
slideforge --config config.yaml --subtitles-only
```

允許沒有精準 word boundary 時用估算時間軸：

```bash
slideforge --config config.yaml --allow-imprecise-subtitles
```

檢查環境：

```bash
slideforge --doctor
```

## 輸出資料夾

預設輸出都放在 `output/`：

- `output/output.mp4`: 不含燒錄字幕的影片
- `output/output_subtitled.mp4`: 燒錄字幕後的影片
- `output/.slideforge/`: 暫存的投影片圖片、音訊、字幕與片段

`.gitignore` 預設只忽略 `output/`，避免把產出的影片與暫存檔提交進 repo。

## 專案結構

```text
src/slideforge/
  __init__.py
  __main__.py
  app.py
  audio.py
  cli.py
  environment.py
  powerpoint.py
  runtime.py
  settings.py
  subtitles.py
  video.py

config.example.yaml
pyproject.toml
README.md
```

`app.py` 負責主要流程。`cli.py` 負責命令列介面。`settings.py` 負責預設值、YAML 讀取與 CLI 覆蓋。`environment.py` 負責檢查 FFmpeg、ffprobe 與 PowerPoint COM。其餘模組分別處理音訊、影片、PowerPoint 匯出、字幕與 runtime state。

## 致謝

感謝 summer51202@gmail.com 提供第一個版本。

## 發佈到 PyPI

安裝建置工具：

```bash
pip install build twine
```

建立 wheel 與 source distribution：

```bash
python -m build
```

檢查 package metadata：

```bash
python -m twine check dist/*
```

先上傳到 TestPyPI：

```bash
python -m twine upload --repository testpypi dist/*
```

確認沒有問題後上傳到 PyPI：

```bash
python -m twine upload dist/*
```

正式發佈前，請確認 [pyproject.toml](pyproject.toml) 裡的 `name`、`version`、`authors`、`description` 與 `project.urls` 都已調整成正式資訊。
