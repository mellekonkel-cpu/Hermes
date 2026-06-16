#!/usr/bin/env python3
"""
Generic Pillow-only color grading template.
Usage: uv run python3 color_grade.py <image_path>
"""
from PIL import Image, ImageEnhance, ImageFilter
import os, sys


def build_curve(mid=128, shadows_lift=1.0, highlights_pull=1.0,
                shadow_th=50, highlight_th=200):
    """Build a 256-entry LUT for per-channel curve adjustment."""
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


def color_grade(
    src_path: str,
    dst_path: str = None,
    # Per-channel curve multipliers (see build_curve signature)
    r_shadows=1.05, r_highlights=1.12,
    g_shadows=1.08, g_highlights=0.96,
    b_shadows=1.10, b_highlights=0.88,
    # Global adjustments
    contrast=1.15,
    saturation=1.20,
    brightness=1.03,
    # Warm overlay (RGB tuple for the overlay color)
    overlay_color=(232, 185, 67),
    overlay_alpha=0.06,
    # Sharpening (UnsharpMask params)
    sharpen_radius=0.8,
    sharpen_percent=80,
):
    """Apply color grading to an image using pure Pillow."""
    if dst_path is None:
        base, ext = os.path.splitext(src_path)
        dst_path = f"{base}_graded{ext}"

    img = Image.open(src_path).convert("RGB")
    w, h = img.size
    print(f"Loaded: {w}x{h}")

    R, G, B = img.split()

    R = R.point(lambda v: build_curve(shadows_lift=r_shadows,
                 highlights_pull=r_highlights)[v])
    G = G.point(lambda v: build_curve(shadows_lift=g_shadows,
                 highlights_pull=g_highlights)[v])
    B = B.point(lambda v: build_curve(shadows_lift=b_shadows,
                 highlights_pull=b_highlights)[v])

    graded = Image.merge("RGB", (R, G, B))

    graded = ImageEnhance.Contrast(graded).enhance(contrast)
    graded = ImageEnhance.Color(graded).enhance(saturation)

    overlay = Image.new("RGB", (w, h), overlay_color)
    graded = Image.blend(graded, overlay, alpha=overlay_alpha)

    graded = ImageEnhance.Brightness(graded).enhance(brightness)
    graded = graded.filter(ImageFilter.UnsharpMask(
        radius=sharpen_radius, percent=sharpen_percent, threshold=3))

    graded.save(dst_path, quality=95)
    print(f"Saved -> {dst_path}  ({os.path.getsize(dst_path)} bytes)")
    return dst_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python3 color_grade.py <image_path> [dst_path]")
        sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    color_grade(src, dst)
