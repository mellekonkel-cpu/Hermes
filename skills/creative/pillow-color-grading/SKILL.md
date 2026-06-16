---
name: pillow-color-grading
description: Color-grade photos using pure Pillow (no numpy/OpenCV) — per-channel curves, split-toning, warm/cool palette overlays, and global adjustments.
category: creative
---

# Pillow Color Grading

Apply professional color grading to photographs using only Python's Pillow library. No numpy, no OpenCV, no external runtime deps.

## When to Use

- You have an image that needs palette-based color grading (warm gold, cool blue, vintage, etc.)
- You're in an environment where only Pillow is available (`Pillow` ≥ 10.x)
- The user asks to "调色" (color grade / tone) a photo
- You need reproducible, deterministic color transforms without a GUI

## Workflow

### 1. Load & Inspect

```python
from PIL import Image
img = Image.open(path).convert("RGB")
```

Always convert to RGB — RGBA/CMYK/grayscale input will break channel splitting.

### 2. Define Your Palette

Pick a **hero color** (e.g., `#D4AF37` 琉璃金) and derive the curve strategy:

| Palette | Effect | R curve | G curve | B curve |
|---------|--------|---------|---------|---------|
| Warm gold | Golden hour, nostalgic | Lift highlights | Slight S-curve | Pull highlights |
| Cool vintage | Moody, cinematic | Pull highlights | Neutral | Lift shadows |
| High-contrast BW | Dramatic monochrome | Equalize | Equalize | Equalize |
| Teal-orange | Blockbuster film look | Lift midtones | Pull highlights | Lift shadows, pull mids |

### 3. Apply Per-Channel Curves

Use `Image.split()` + `Image.point()` + `Image.merge()`:

```python
R, G, B = img.split()
R = R.point(lambda v: r_lut[v])  # r_lut = [0..255] mapping
G = G.point(lambda v: g_lut[v])
B = B.point(lambda v: b_lut[v])
graded = Image.merge("RGB", (R, G, B))
```

Build LUTs with a helper:

```python
def build_curve(mid=128, shadows_lift=1.0, highlights_pull=1.0,
                shadow_th=50, highlight_th=200):
    curve = []
    for v in range(256):
        if v < shadow_th:
            f = shadows_lift
        elif v > highlight_th:
            f = highlights_pull
        elif v <= mid:
            t = (v - shadow_th) / (mid - shadow_th) if mid > shadow_th else 1.0
            f = shadows_lift + (1.0 - shadows_lift) * t
        else:
            t = (v - mid) / (highlight_th - mid) if highlight_th > mid else 1.0
            f = 1.0 + (highlights_pull - 1.0) * t
        curve.append(min(255, max(0, int(v * f))))
    return curve
```

### 4. Global Adjustments (in order)

```python
from PIL import ImageEnhance, ImageFilter

graded = ImageEnhance.Contrast(graded).enhance(1.15)   # contrast
graded = ImageEnhance.Color(graded).enhance(1.20)       # saturation
graded = ImageEnhance.Brightness(graded).enhance(1.03)  # brightness
graded = graded.filter(ImageFilter.UnsharpMask(radius=0.8, percent=80, threshold=3))
```

### 5. Warm/Cool Overlay

```python
gold = Image.new("RGB", (w, h), (232, 185, 67))  # #E8B943
graded = Image.blend(graded, gold, alpha=0.06)
```

Adjust alpha for subtlety — 0.03–0.08 is typical for a natural look.

### 6. Save

```python
graded.save("output.jpg", quality=95)
```

## Pitfalls

- **No RGBA/CMYK**: Convert to `RGB` first, or channel ops will misbehave.
- **Large images**: For images > 4000px, downscale first with `img.thumbnail((2000, 2000))`, grade, then composite back onto the original.
- **Over-saturation**: Saturation > 1.35 flattens highlight detail. Stay under 1.25 unless the brief is deliberately psychedelic.
- **Black clipping**: `build_curve` with aggressive shadow lifting can clip blacks. Verify with `min(R.getextrema()[0])`.
- **Pillow version**: `UnsharpMask` params differ slightly across versions. On Pillow < 8, use `ImageFilter.SHARPEN` instead.
- **Reversible pipeline**: Always keep the original — `graded.save()` is destructive. Never overwrite in place.

## Linked Files

- `scripts/color_grade_template.py` — reusable script with per-channel curve builder and overlay support
- `references/palette_examples.md` — palette:curve mapping tables
- `references/palette-tricolor-anchor.md` — tri-color anchor technique for Chinese street photography (red/gold/blue)
