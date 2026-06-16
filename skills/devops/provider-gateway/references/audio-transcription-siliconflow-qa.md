# SiliconFlow ASR — Q&A Extraction Methodology

> Tested 2026-05-25 with `wsc_后半段.m4a` (8min39s, 8.1MB, AAC 48kHz stereo)

## Endpoint

```
POST https://api.siliconflow.cn/v1/audio/transcriptions
Authorization: Bearer $SILICONFLOW_KEY
```

The key is stored in `/opt/data/.env` as `SILICONFLOW_KEY=sk-...`

## Model: FunAudioLLM/SenseVoiceSmall

This is the only reliable ASR model on SiliconFlow for Chinese audio. The TeleSpeechASR model may also work but wasn't tested.

**Parameters used:**
- `model=FunAudioLLM/SenseVoiceSmall`
- `language=zh` (required for Chinese accuracy)
- `response_format=text` (plain text output)

**List available models:**
```bash
curl -s "https://api.siliconflow.cn/v1/models" \
  -H "Authorization: Bearer $SILICONFLOW_KEY" | python3 -c "
import json,sys
data = json.load(sys.stdin)
for m in data.get('data', []):
    if any(k in m.get('id','').lower() for k in ['whisper','asr','audio','transcri']):
        print(m['id'])
"
```

## Known Transcription Errors

| ASR Output | Correct Term | Context |
|------------|-------------|---------|
| FDPD | FDPT | 第一个添加剂体系 |
| TMSN | TMSN (correct) | 添加剂名称 |
| PLSN | BLSN | 第二个添加剂体系 |
| 风酸年 | 硼酸类/含硼 | CEI成分 |
| PMPN | PMPN (correct) | 添加剂名称 |
| 三甲低会低膨胀者 | 三甲(基)磷酸酯/TMP | 阻燃添加剂 |
| BMOB | 推测为结构式 | 命名来源 |
| 阻拦 | 阻燃 | 燃烧测试 |

## Post-Processing Approach for Q&A Extraction

The raw ASR output is a single text blob with no speaker separation. Extract Q&A by:

1. **Identify speaker turns** via semantic cues:
   - Questions: rising intonation patterns, "嗯？", "这个...", "那..."
   - Answers: "因为...", "就是...", "然后..."
   - Topic introductions: "我看到你...", "我看这个..."

2. **Group by topic**: The reviewer tends to discuss one topic at a time (format → additives → figures → naming). Each topic shift is a new Q.

3. **Clean the text**: Remove filler words (嗯、呃、那个、就是说), fix ASR transcription errors for domain terms.

4. **Write as structured markdown**: Q&A pairs under section headers, with a final summary of action items.

## Example Output Structure

```
# 音频问答提炼

> 来源：/path/to/audio.m4a (X分Y秒)
> 转写日期：YYYY-MM-DD

## 一、汇报内容

[summary of presented content]

## 二、问答

### Q1: [Topic]

**问：** [question text]

**答：** [answer text]

### Q2: ...

## 三、总结建议

[list of action items]
```
