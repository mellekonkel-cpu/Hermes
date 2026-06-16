# SiliconFlow ASR (Audio Transcription)

SiliconFlow provides OpenAI-compatible audio transcription endpoints. The existing API key (`$SILICONFLOW_KEY`) supports ASR out of the box — no additional setup needed.

## Available ASR Models

| Model ID | Type | Best For |
|----------|------|----------|
| `TeleAI/TeleSpeechASR` | Large ASR | Chinese-dominant audio, academic/technical speech, highest accuracy |
| `FunAudioLLM/SenseVoiceSmall` | Small ASR | Faster inference, general-purpose voice transcription |

## Endpoint

OpenAI-compatible:
```
POST https://api.siliconflow.cn/v1/audio/transcriptions
```

## Usage

```bash
curl -s -X POST "https://api.siliconflow.cn/v1/audio/transcriptions" \
  -H "Authorization: Bearer $SILICONFLOW_KEY" \
  -F "file=@/path/to/audio.m4a" \
  -F "model=TeleAI/TeleSpeechASR" \
  -F "language=zh" \
  -F "response_format=json"
```

### Parameters

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `file` | Yes | Multipart audio file | Supported: m4a, wav, mp3, ogg, flac |
| `model` | Yes | See model table above | Which ASR model to use |
| `language` | No | `zh`, `en`, etc. | Hint for language detection |
| `response_format` | No | `json` (default), `text`, `srt`, `verbose_json` | Output format |
| `temperature` | No | 0.0–1.0 | Sampling temperature (default: 0) |

### Response Format

```json
{"text": "transcribed text content here"}
```

## Pre-processing with ffmpeg

For long recordings, split before transcribing:

```bash
# Get duration
ffprobe /path/to/audio.m4a 2>&1 | grep Duration

# Extract second half (from 9:00 to end)
ffmpeg -y -ss 00:09:00 -i /path/to/audio.m4a -c copy /path/to/output_后半段.m4a

# Extract specific segment (0:00 to 9:00)
ffmpeg -y -ss 00:00:00 -t 00:09:00 -i /path/to/audio.m4a -c copy /path/to/output_前半段.m4a
```

**Important**: When using `-c copy` (stream copy, no re-encode), the `-ss` before `-i` is fast-seek but may have slight time inaccuracy. For frame-accurate cuts without re-encode, this is acceptable for ASR purposes.

## Known Working Configuration

Tested with:
- File: 17:39 m4a, 130kbps, 8.1MB (second half)
- Model: `TeleAI/TeleSpeechASR`
- Language: `zh`
- Output: Accurate Chinese transcription of technical academic defense (~9 minutes of speech)
- Time: ~30s for 8-minute segment
- Cost: Minimal (fraction of a yuan per call)

## Fallback

If `TeleAI/TeleSpeechASR` fails (429 or timeout), switch to `FunAudioLLM/SenseVoiceSmall` — faster but potentially less accurate, especially with technical/domain-specific terminology.
