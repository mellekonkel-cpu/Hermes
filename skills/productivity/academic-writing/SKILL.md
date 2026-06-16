---
title: Academic & Research Writing (Thesis-Support)
name: academic-writing
description: Comprehensive academic writing support for materials science graduate thesis work. Covers C-E academic translation, battery electrochemistry data interpretation & academic phrasing, thesis defense speech generation from PDF+PPTX, and structured academic output formatting.
trigger: User asks to translate Chinese academic text, interpret battery electrochemistry data (CV/dQ/dV/GITT/EIS), generate a defense speech/答辩稿, or write/revise academic Chinese for thesis chapters.
---

# Academic & Research Writing

This umbrella covers the academic output workflow for a materials science graduate student (battery electrolytes, Li-rich Mn-based cathodes, dual-additive systems). All three subsections share the same user, the same domain terminology, and the same audience (thesis committee → academic journal).

## Shared Style Rules (ALL Output)

These apply to every translation, summary, thesis section, defense speech, and academic Chinese phrasing produced under this skill:

1. **No em-dashes (—), en-dashes (–), or Chinese quotation marks (「」《》)**. Use commas, periods, or restructure the sentence. Hyphens within compound words (e.g., "Li-rich") are fine.
2. **No quotation marks ("")** in academic text unless directly quoting a source. Present terms plainly.
3. **No parentheses** unless the content requires them (e.g., chemical formulas LiPF6).
4. **Concise and direct** — deliver the equivalent without explanatory notes or alternatives unless asked.
5. **Always include implications** — never state an observation without saying what it means for performance.
6. **Structured vs. flowing output** — Use (1)...(2)...(3)... format for analytical discussion, mechanism comparison, or multi-parameter analysis. Use flowing paragraph (一段话) when user explicitly requests a "总结" of defined length (e.g., "400字总结"), or for thesis conclusions and closing remarks. When in doubt, default to flowing paragraph for user's thesis-specific summaries — user prefers macro-level narrative over enumerated points for summary-style output.

7. **润色 (polish/rephrase) rule: NEVER split into bullet points unless explicitly asked** — When user says "润色一下" or "帮我润色一段", return a single continuous paragraph. Do NOT restructure their text into (1)(2)(3) or bullet-point format. If the original text is already one paragraph, keep it as one paragraph. If the user provided multiple sentences, combine them into a coherent paragraph without enumerating or sectioning. The user will explicitly say "分点" if they want structured output. Violating this = immediate user frustration.

8. **No unsolicited action ("不要脑补" rule)** — Do NOT execute file writes, downloads, modifications, or any system-modifying action unless the user explicitly asks. If the user says "我可不可以..." or "是否能够...", answer the question — do not interpret it as a command and start doing it. Only ask "需要我...吗？" or state what is possible, then wait for explicit instruction. Unsolicited action without asking first is the #1 cause of user frustration.

9. **整合成一段 (integrate-into-one-paragraph) rule** — When user says "整合成一段，别老给我分点" or "整合删掉废话"，combine all separate items/points into ONE flowing paragraph. Remove transitional phrases like "关于...关于...关于..." — just knit the content together naturally. Eliminate "respectively", "in addition", "furthermore" and other filler. If the user explicitly says "不要分点", they want a paragraph. If they say "别老", it means you've done this wrong before — fix the pattern permanently.

10. **Rewriting rule: avoid similarity when user asks** — When user says "改写一下，不要和之前类似", generate a structurally different version: change opening angle, sentence pattern, logical flow order, and closing phrasing. Do not just swap synonyms while keeping the same skeleton.

11. **Capitalization (English only)** — capitalize proper nouns and sentence-first words only.

12. **Drop redundant Chinese qualifiers** (型, 式, 类, 化) where English naturally omits them in compounds.

13. **Superscript/subscript check** — When writing `g^{-1}` or similar in LaTeX/markdown formulas, wrap in single `$` (e.g., `$mAh·g^{-1}$`). Never use bare `{}` syntax like `g{-1}` outside math mode — it renders as visible braces and looks突兀. For plain-text (non-LaTeX) contexts, use Unicode superscript characters: `⁻¹` rather than `^-1`. **Self-check**: after writing any document containing `^{-1}`, `_{}`, or `g{-1}`, visually scan for exposed curly braces — they are the #1 cause of "上下标看上去很突兀" complaints from reviewers.

---

## Section A: Chinese-English Academic Translation

### Workflow

1. User says "翻译 X" or provides a Chinese phrase/section
2. Return the English equivalent directly — no explanation, no alternatives
3. For section/chapter titles: title-case capitalization, no articles (a/an/the)
4. For compound modifiers: natural English word order, not literal character-by-character

### Terminology Reference (Battery Electrolytes Domain)

| Chinese | English (preferred) |
|---------|-------------------|
| 富锂锰基 | lithium-rich manganese-based |
| 电解液 | electrolyte |
| 添加剂 | additive |
| 阻燃 | flame retardant |
| 长循环 | long cycle / long-term cycling |
| 协同 | synergistic / cooperative |
| 双添加剂 | dual-additive / binary additive |
| 溶剂化结构 | solvation structure |
| 前线轨道 | frontier orbital |
| 静电势 (ESP) | electrostatic potential (ESP) |
| 除酸 / 清除HF | HF scavenging |
| 界面膜 / CEI | cathode electrolyte interphase (CEI) |
| 正极 | cathode |
| 负极 | anode |
| 锂金属电池 | lithium metal battery |
| 高电压 | high voltage |
| 容量保持率 | capacity retention |
| 库伦效率 | Coulombic efficiency |

### Common Translation Examples

| Input | Correct Output |
|-------|---------------|
| 安全型阻燃电解液 | Safe Flame Retardant Electrolyte |
| 长循环复合电解液 | Long Cycle Composite Electrolyte |
| 界面结构分析 | Cathode Electrolyte Interphase Structure Analysis |

### Pitfalls

- Python dicts/config files may legitimately use hyphens/quotes — only enforce style rules on natural-language translation output
- Do NOT combine translation with explanation unless asked
- When translating compound modifiers, prefer natural English word order

---

## Section B: Battery Electrochemistry Data Interpretation

### Trigger

Relevant when user asks about:
- CV (cyclic voltammetry) peak interpretation
- dQ/dV differential capacity analysis
- GITT Li⁺ diffusion coefficient discussion
- EIS / interface film characterization
- "怎么解释" / "怎么说更学术" / "组织一下语言" in battery context

### CV Peak Interpretation

**Core mechanism**: Peak = reaction kinetics (acceleration) × mass transport (brake) meeting at a specific potential.

**Key metrics for thesis**:
| Metric | Meaning | Academic Phrase Tag |
|--------|---------|-------------------|
| Peak potential (Ep) | Which redox reaction at what voltage | "氧化峰向高电位偏移且峰电流减弱" → additive forms CEI |
| Peak current (ip) | Reaction intensity | "还原峰负移且强度降低" → additive reduces to form SEI |
| ΔEp (peak separation) | Electrochemical reversibility | "含添加剂体系ΔEp缩小" → better kinetics, low-impedance film |
| Multi-cycle peak decay | Interface stability | Decay = stable film formed |

### dQ/dV Peak Assignment (Li-rich Mn-based Cathode)

| Position | Event | Phrase |
|----------|-------|--------|
| ~3.7-4.0V charge | Ni²⁺→Ni⁴⁺ (conventional layered) | — |
| ~4.5-4.8V charge (1st only) | Li₂MnO₃ activation | "不可逆氧化峰，归属于Li₂MnO₃的活化过程" |
| ~3.3-3.5V discharge | Mn⁴⁺→Mn³⁺ | — |
| ~2.8-3.0V discharge | Ni⁴⁺→Ni²⁺ | — |

### GITT — Li⁺ Diffusion Coefficient

- Higher DLi+ in additive system → interface film has good ionic conductivity
- Always add implication: "有利于减小浓度极化、提升倍率性能并改善电极反应动力学"

### Workflow: Academic Phrasing Request

1. **Simple explanation first** — use metaphors/analogies (delivery, shield, paint)
2. **Academic phrasing** — convert to formal academic Chinese
3. **Shorter version on request** — condense to 1-2 sentences
4. **Add implications** — user says "把带来的影响也加上" — always include what the result *means* for performance

See `references/battery-electrochemistry.md` for full CV/dQ/dV peak tables, additive effect interpretation templates, and reusable Chinese phrases.
See `references/reference-formatting.md` for thesis-format reference style guide and 11 battery-domain formatted examples.

---

## Section C: Thesis Defense Speech Generation

### Trigger

User asks to generate a defense speech, 答辩稿, or oral presentation script based on their thesis/defense PPT.

### Workflow Overview

1. **Locate source files** — thesis PDF and defense PPTX under `/opt/data/青桑/`
2. **Extract PPTX content** — use zipfile + XML (not python-pptx, which is not installed)
3. **Read thesis** — extract key content from each chapter (usually pre-extracted at `_正文.txt`)
4. **Map slides to thesis** — identify which thesis section corresponds to each slide
5. **Write speech** — slide-by-slide script with data points from thesis
6. **Verify** — all slides covered, data matches thesis, file saved to `/opt/data/青桑/答辩稿_.md`

### PPTX Extraction Method

```python
import zipfile, os, xml.etree.ElementTree as ET

def extract_pptx_text(pptx_path):
    out_dir = "/tmp/pptx_extracted"
    os.makedirs(out_dir, exist_ok=True)
    with zipfile.ZipFile(pptx_path, 'r') as z:
        z.extractall(out_dir)
    slides_dir = os.path.join(out_dir, "ppt/slides")
    slides = sorted([f for f in os.listdir(slides_dir) if f.endswith('.xml') and not f.startswith('_')])
    result = {}
    for i, f in enumerate(slides, 1):
        tree = ET.parse(os.path.join(slides_dir, f))
        texts = [t.text.strip() for t in tree.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t') if t.text and t.text.strip()]
        result[i] = texts
    return result
```

### Common Defense PPT Structure

| PPT Section | Typical Slides | Thesis Chapter |
|-------------|---------------|----------------|
| 封面 | 1 | — |
| 研究背景与意义 | 2-5 | Ch1 (绪论) |
| FDPT (安全型阻燃电解液) | 6-12 | Ch3 |
| BLSN (长循环复合电解液) | 13-24 | Ch4 |
| 总结与展望 | 25-26 | Ch5 |
| 致谢 | 27-28 | — |

### Speech Structure Rules

Each slide section should contain:
1. **Slide reference** — `### Slide N — Slide Title`
2. **Key content** — what to say, based on slide text + thesis
3. **Transition** — bridge to next slide/section

### Pitfalls

- PPT slides may be out of order in XML — check `presentation.xml` `p:sldIdLst` for display order
- No python-pptx available — use the zipfile approach above
- For slides with minimal text (mostly figures), extract content from thesis chapter instead
- User may request revisions on specific paragraphs — be ready to revise on demand

See `references/defense-speech.md` for the full PPTX extraction reference and speech template.

---

## Section D: Recommendation Letter & Thesis Evaluation (评语/推荐意见)

### Trigger

User asks to write or rewrite a recommendation letter, thesis evaluation, or 评语 for their own or another student's thesis/application.

### Workflow

1. **Analyze provided template** — User usually gives an example评语 for a different thesis. Extract the structural skeleton:
   - Opening: 思想/态度/学习表现
   - Middle: 研究内容 + 成果 + 能力体现
   - Closing: 总体评价 + 推荐意见
2. **Map to user's thesis** — Substitute with user's actual research topic (LRMO, dual-additive electrolytes, CEI mechanism).
   - Keep the same sentence length and rhythm as the template
   - Swap in domain-appropriate verbs: "构筑" "揭示" "提出" "验证" "构建"
3. **On "换一种" / "不要和之前类似":** Completely restructure — change the logical flow order (e.g., open with research achievement instead of personal qualities), use a different sentence opening pattern, and vary closing language. Do not just swap synonyms.

### Style Rules for 评语

- **第三称** — 该申请人 / 该生 / 其
- **评价维度必须覆盖**: 思想态度 → 学术能力 → 研究成果 → 总体结论
- **用量化成果具体化评价** — 提到具体的创新点（双添加剂协同调控、阻燃体系、长循环体系）而非空泛描述
- **模板适应**: 如果用户给了参考模板的措辞风格和句式节奏，严格贴近其节奏，而非写自己的版本
- **避免与用户提供的参考模板过于雷同** — 换用同义表达和不同句式结构

### Common Verbs for 评语

| 功能 | 动词 |
|------|------|
| 发现问题 | 凝练出、聚焦于、提炼出、洞察到 |
| 设计方案 | 构筑、构建、设计、提出 |
| 分析验证 | 揭示、阐明、验证、验证了 |
| 评价成果 | 展现了、反映出、体现了、具备了 |
