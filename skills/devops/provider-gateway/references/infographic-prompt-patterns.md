# Infographic / Scientific Figure Prompt Patterns

## Prompt Anatomy

A good SiliconFlow image generation prompt has these layers:

```
[STYLE] + [LAYOUT] + [CONTENT LEFT] + [CONTENT RIGHT] + [CENTER ELEMENT] + [COLOR/VISUAL SPECS]
```

## Style Keywords

| Desired Style | Key Phrases |
|---|---|
| Academic journal (学术期刊) | `academic journal style figure`, `scientific illustration`, `publication-ready`, `clean technical lines`, `white background`, `Nature/ACS journal quality`, `minimalist data visualization` |
| Infographic/Dashboard (信息图) | `modern infographic`, `professional dashboard feel`, `subtle gradient colors`, `dark background`, `stylized technical illustration`, `sleek UI design` |
| Hand-drawn/Schematic (手绘) | `hand-drawn style`, `sketch`, `technical schematic`, `blueprint style`, `line art` |
| Conceptual/Artistic (概念图) | `conceptual illustration`, `artistic rendering`, `cinematic lighting`, `creative visualization` |

## Academic Style Template

```
Academic journal style figure, side-by-side comparison of [TOPIC].
Left panel labeled 'Traditional': [LEFT CONTENT], [LEFT DIAGRAM], simple bar chart at [VALUE].
Right panel labeled 'Advanced': [RIGHT CONTENT], [RIGHT DIAGRAM], glowing bar chart at [VALUE] with highlight effect.
Center arrow labeled '[LABEL]' with energy particles.
Scientific illustration style, white background, [COLOR SCHEME] professional color scheme,
clean technical lines, minimal text, publication-ready infographic.
```

## Pitfalls

- **Text rendering is unreliable** -- keep labels to 1-3 words max. Long Chinese labels will be garbled.
- **Models ignore negative prompts** -- phrase everything positively. Instead of "no noise", say "clean, minimalist, uncluttered".
- **Qwen-Image** handles structured layouts best. Kolors ignores layout instructions and generates artistic compositions instead.
- **Seed parameter** -- if you get a good composition but wrong style, note the seed. Same model + same seed = same composition.
