# Academic/Scientific Infographic Prompt Patterns

Prompt patterns that work for battery/energy infographics on SiliconFlow Qwen-Image.

## Style Anchor Words

| Desired Style | Must-include words | Avoid |
|---|---|---|
| **Nature journal** | `Nature journal Figure 1 style. White background, Nature journal figure formatting, clean Helvetica font, professional blue and teal colors, minimalist scientific illustration, publication-quality.` | `infographic`, `dashboard`, `modern design` |
| **ACS journal** | `ACS journal Graphical Abstract style. ACS journal style, white background, clean Arial font, blue and teal ACS color palette, crisp lines, professional chemistry materials science journal figure, minimal text.` | `infographic`, `modern`, `tech` |
| **General academic** | `Academic journal style figure. Clean white background, scientific illustration, blue and teal professional color scheme, clean technical lines, minimal text, research journal quality.` | `infographic`, `creative`, `artistic` |
| **Blank/simple** | `Simple side-by-side comparison. White background, clean lines, minimal labels.` | Any style descriptors |

## Proven Prompt Template

```
{journal_style} Side-by-side comparison diagram of battery energy density.
Left panel: Traditional System, graphite anode + NCM cathode,
  schematic of cylindrical 18650 cell with labeled layers Graphite and NCM,
  bar chart at 250 Wh/kg.
Right panel: Advanced System, lithium metal anode + LRMO cathode,
  schematic of pouch cell with labeled layers Lithium Metal and LRMO,
  taller glowing bar chart at 450+ Wh/kg.
Center arrow with Energy Density Enhancement label.
{style_elements}
```

## Known Limitations

- Qwen-Image sometimes ignores "white background" and produces dark/colorful backgrounds. Emphasize "white background" with more specific constraints.
- Chinese text labels in prompts often render as English. Short labels (1-2 words) in English work best.
- "Glowing" effects on bar charts are hit-or-miss. Acceptable results without explicit glow words.
- Account balance depletes after ~4-5 Qwen-Image generations (~1-2 CNY each). Pre-warn user if generating many variants.
