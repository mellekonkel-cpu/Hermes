# Battery Energy Density Infographic — Prompt Recipes

Generated during a session for 武士淳 (lithium metal battery research, 天津工业大学).

## Target: Clean Academic Comparison Diagram

### Approach 1: Nature Journal Style
**Model**: Qwen-Image  
**Prompt pattern**: Nature journal Figure 1 style. Side-by-side comparison diagram of {topic}. Left panel: {traditional_system}, schematic of {traditional_cell_type} with labeled layers {anode}/{cathode}, bar chart at {traditional_value}. Right panel: {advanced_system}, schematic of {advanced_cell_type} with labeled layers, taller glowing bar chart at {advanced_value}. Center arrow. White background, Nature journal figure formatting, clean Helvetica font, professional blue and teal colors, minimalist scientific illustration, publication-quality.

**Example** (477KB, ~17s):
> Nature journal Figure 1 style. Side-by-side comparison diagram of battery energy density. Left panel: Traditional System, graphite anode + NCM cathode, schematic of cylindrical 18650 cell with labeled layers Graphite and NCM, bar chart at 250 Wh/kg. Right panel: Advanced System, lithium metal anode + LRMO cathode, schematic of pouch cell with labeled layers Lithium Metal and LRMO, taller glowing bar chart at 450+ Wh/kg. Center arrow with Energy Density Enhancement label. White background, Nature journal figure formatting, clean Helvetica font, professional blue and teal colors, minimalist scientific illustration, publication-quality.

### Approach 2: ACS Graphical Abstract Style
**Model**: Qwen-Image  
**Prompt pattern**: ACS journal Graphical Abstract style. Comparison infographic of {topic}. Left: {traditional} cylindrical cell drawing, bar {value}. Right: {advanced} pouch cell drawing, bar {value} with glow. Center arrow labeled {label}. ACS journal style, white background, clean Arial font, blue and teal ACS color palette, crisp lines, professional chemistry materials science journal figure, minimal text.

**Example** (459KB, ~10s):
> ACS journal Graphical Abstract style. Comparison infographic of battery energy density. Left: graphite anode + NCM cathode, cylindrical cell drawing, energy density bar 250 Wh/kg. Right: lithium metal anode + LRMO cathode, pouch cell drawing, energy density bar 450+ Wh/kg with glow. Center arrow labeled Energy Density Boost. ACS journal style, white background, clean Arial font, blue and teal ACS color palette, crisp lines, professional chemistry materials science journal figure, minimal text.

## Model Comparison (From This Session)

| # | Model | Prompt | Size | Time | Notes |
|---|---|---|---|---|---|
| 1 | Qwen-Image | Original (infographic style) | 810KB | 14s | Dark bg, modern dashboard feel |
| 2 | Kolors | Original (infographic style) | 1.6MB | 4s | Artistic, poor infographic rendering |
| 3 | Z-Image-Turbo | Academic style | 695KB | 2.5s | Fast but mid quality |
| 4 | Qwen-Image | Academic style (white bg) | 481KB | 10s | Cleaner, closer to journal style |
| 5 | Qwen-Image | Nature style | 477KB | 17s | Best academic result |
| 6 | Qwen-Image | ACS style | 459KB | 10s | Good, clean lines |

## How to Present to the User

When delivering multiple generated images:
1. Organize into a subdirectory: `photo/电池能量密度对比_各版本/`
2. Prefix filenames with numbers: `01_Qwen-Image_原始prompt.png`
3. Present as a comparison table with model/time/size
4. Ask specific question: "哪版最接近你想要的？" — not "你觉得怎么样？"
5. If none work, offer concrete named alternatives: "Nature风格？ACS风格？一般学术白底？"
6. If user says "都不行", stop generating and ask for a specific style reference

## Fallback: HTML/CSS + Puppeteer

When image gen API unavailable:
1. Create an HTML infographic with dark/teal gradient background, CSS battery cell diagrams, animated glowing bar charts
2. Use Puppeteer to screenshot -> PNG
3. Save both .html and .png for user
