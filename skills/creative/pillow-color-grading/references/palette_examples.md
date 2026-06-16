# Palette → Curve Mapping

## 琉璃金 (Glazed Gold) — #D4AF37

The session prototype. Warm gold highlights, cool shadow base.

| Chan | Shadows | Highlights | Effect |
|------|---------|------------|--------|
| R | +5% | +12% | Gold glow in bright areas |
| G | +8% | -4% | Slight S-curve, natural mids |
| B | +10% | -12% | Warm highlights, deep sky |

**Overlay:** `(232, 185, 67)` @ 6%  
**Saturation:** 1.20 | **Contrast:** 1.15

---

## Vintage Kodachrome

Warm amber shadows, teal-tinted highlights.

| Chan | Shadows | Highlights |
|------|---------|------------|
| R | +15% | — |
| G | +5% | -5% |
| B | -8% | -10% |

**Overlay:** `(220, 180, 100)` @ 4%  
**Saturation:** 1.10 | **Contrast:** 1.20

---

## Cool Cinematic (Teal-Orange)

Teal shadows, orange skin tones.

| Chan | Shadows | Highlights |
|------|---------|------------|
| R | — | +8% |
| G | -8% | — |
| B | +15% | -5% |

**Overlay:** none (cool bias from B channel)  
**Saturation:** 0.90 | **Contrast:** 1.25

---

## Mono High-Contrast

All channels equalized, then converted to grayscale.

```python
gray = img.convert("L")
graded = ImageEnhance.Contrast(gray).enhance(1.5)
graded = graded.filter(ImageFilter.UnsharpMask(radius=1.0, percent=120, threshold=2))
```

---

## Golden Hour (Cinematic)

Warm mids, lifted shadows, desaturated B.

| Chan | Shadows | Highlights |
|------|---------|------------|
| R | +10% | +8% |
| G | +3% | -2% |
| B | -5% | -15% |

**Overlay:** `(255, 200, 100)` @ 5%  
**Saturation:** 1.05 | **Contrast:** 1.10
