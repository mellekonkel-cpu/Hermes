# Pillow Color Grading — 琉璃金 Tri-Color Anchor Technique

A technique for grading street photography with strong red/gold/blue elements
(e.g. Chinese architecture with lanterns, pagoda roofs, and sky).

## Strategy

Identify **three color anchors** in the image and control them independently
via per-channel curves:

| Anchor | Element | Target HEX | Channel Strategy |
|--------|---------|------------|------------------|
| 🏮 Red | Lanterns, walls, window frames | `#C72B2B` 中国红 | Boost R in mids/highlights (+5% shadows, +12% highlights) |
| ✨ Gold | Pagoda roof, decorations | `#D4AF37` 琉璃金 | R +12% highlights, B -12% highlights (warm glow) |
| 🔵 Sky | Background sky | `#1E73C8` 晴空蓝 | B +10% shadows (deep blue), B -12% highlights (warm gold sky) |

## Typical Parameters

```python
from pillow_color_grade_template import color_grade

color_grade(
    "input.jpg", "output.jpg",
    r_shadows=1.05, r_highlights=1.12,   # gold glow
    g_shadows=1.08, g_highlights=0.96,   # gentle S-curve
    b_shadows=1.10, b_highlights=0.88,   # deep sky, warm highlights
    overlay_color=(232, 185, 67),        # #E8B943 gold tint
    overlay_alpha=0.06,                  # subtle warm cast
    contrast=1.15,
    saturation=1.20,
    brightness=1.03,
    sharpen_radius=0.8,
    sharpen_percent=80,
)
```

## When to Use

- Street / architectural photography with traditional Chinese elements
- Images containing lanterns + sky + gold roof details
- User asks for "调色" on a warm-toned scene with strong red/gold/blue
- Target aesthetic: "古风" (ancient style), golden hour, cinematic warm
