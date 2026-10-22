from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# severity -> (solid outline/text color, light fill color)
SEVERITY_COLORS = {
    "high": ((200, 0, 0), (255, 225, 225)),
    "medium": ((225, 110, 0), (255, 238, 215)),
    "low": ((185, 140, 0), (255, 247, 210)),
    "info": ((70, 100, 160), (225, 235, 250)),
}
DEFAULT_COLORS = SEVERITY_COLORS["medium"]

BANNER_CATEGORIES = {"javascript_error", "page_http_error"}
BANNER_HEIGHT = 30
MAX_BANNERS = 6


def _load_font(size=16, bold=False):
    fonts = (
        ["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]
        if bold
        else ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
    )

    for font_name in fonts:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue

    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def _colors(severity):
    return SEVERITY_COLORS.get(str(severity or "").lower(), DEFAULT_COLORS)


def _fit_text(draw, text, font, max_width):
    """Trim text with an ellipsis so it fits inside max_width pixels."""
    if draw.textlength(text, font=font) <= max_width:
        return text

    while text and draw.textlength(text + "...", font=font) > max_width:
        text = text[:-1]

    return text + "..."


def _is_banner(box):
    return bool(box.get("banner")) or box.get("category") in BANNER_CATEGORIES


def highlight_screenshot(input_path, output_path, boxes=None, scale=1.0):
    """
    Annotate a screenshot.

    boxes: list of dicts. Element boxes need x, y, width, height (CSS pixels,
           full-page coordinates). Page-level issues (JS/HTTP errors, overflow,
           layout shift ...) are drawn as banners in a header ABOVE the
           screenshot so they never cover page content.
    scale: device pixel ratio of the screenshot (CSS px -> image px).
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Screenshot not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        scale = float(scale) if scale else 1.0
    except (TypeError, ValueError):
        scale = 1.0

    with Image.open(input_path) as original:
        page_image = original.convert("RGB")

    boxes = list(boxes or [])
    banners = [b for b in boxes if _is_banner(b)]
    element_boxes = [b for b in boxes if not _is_banner(b)]

    shown_banners = banners[:MAX_BANNERS]
    hidden_banners = len(banners) - len(shown_banners)
    banner_rows = len(shown_banners) + (1 if hidden_banners else 0)
    header_height = banner_rows * BANNER_HEIGHT

    # Canvas = optional header + original screenshot
    canvas = Image.new(
        "RGB",
        (page_image.width, page_image.height + header_height),
        (255, 255, 255),
    )
    canvas.paste(page_image, (0, header_height))

    # --- Translucent fills for element boxes -----------------------------
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    placed = []

    for box in element_boxes:
        try:
            x = float(box.get("x", 0)) * scale
            y = float(box.get("y", 0)) * scale
            width = float(box.get("width", 0)) * scale
            height = float(box.get("height", 0)) * scale
        except (TypeError, ValueError):
            continue

        if width <= 0 or height <= 0:
            continue

        left = int(max(0, min(x, page_image.width - 1)))
        top = int(max(0, min(y, page_image.height - 1))) + header_height
        right = int(max(left, min(x + width, page_image.width - 1)))
        bottom = int(
            max(top, min(y + height + header_height, canvas.height - 1))
        )

        if right - left < 1 and bottom - top < 1:
            continue

        solid, _ = _colors(box.get("severity"))
        overlay_draw.rectangle(
            [left, top, right, bottom], fill=solid + (40,)
        )
        placed.append((box, left, top, right, bottom))

    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)

    label_font = _load_font(15, bold=True)
    banner_font = _load_font(16, bold=True)

    # --- Header banners ---------------------------------------------------
    for index, banner in enumerate(shown_banners):
        solid, light = _colors(banner.get("severity"))
        row_top = index * BANNER_HEIGHT

        draw.rectangle(
            [0, row_top, canvas.width - 1, row_top + BANNER_HEIGHT - 1],
            fill=light,
            outline=solid,
            width=2,
        )

        prefix = f"#{banner['id']} " if banner.get("id") else ""
        text = _fit_text(
            draw,
            prefix + str(banner.get("label", banner.get("category", "issue"))),
            banner_font,
            canvas.width - 20,
        )
        draw.text((10, row_top + 5), text, fill=solid, font=banner_font)

    if hidden_banners:
        row_top = len(shown_banners) * BANNER_HEIGHT
        draw.rectangle(
            [0, row_top, canvas.width - 1, row_top + BANNER_HEIGHT - 1],
            fill=(235, 235, 235),
            outline=(120, 120, 120),
            width=2,
        )
        draw.text(
            (10, row_top + 5),
            f"+ {hidden_banners} more page-level issue(s) - see JSON report",
            fill=(60, 60, 60),
            font=banner_font,
        )

    # --- Element boxes + labels -------------------------------------------
    for box, left, top, right, bottom in placed:
        try:
            solid, light = _colors(box.get("severity"))

            draw.rectangle([left, top, right, bottom], outline=solid, width=3)

            label = str(box.get("label", box.get("category", "issue")))
            if box.get("id") and f"#{box['id']}" not in label:
                label = f"#{box['id']} {label}"

            label = _fit_text(draw, label, label_font, max(120, canvas.width - 24))

            bbox = draw.textbbox((0, 0), label, font=label_font)
            label_width = bbox[2] - bbox[0]
            label_height = bbox[3] - bbox[1]

            label_x = min(left, max(0, canvas.width - label_width - 14))

            # Prefer above the box; fall back to inside the box's top edge.
            label_y = top - label_height - 12
            if label_y < header_height:
                label_y = top + 2

            label_y = max(0, label_y)

            draw.rectangle(
                [
                    label_x,
                    label_y,
                    min(canvas.width - 1, label_x + label_width + 12),
                    min(canvas.height - 1, label_y + label_height + 8),
                ],
                fill=light,
                outline=solid,
                width=2,
            )

            draw.text(
                (label_x + 6, label_y + 3),
                label,
                fill=solid,
                font=label_font,
            )

        except (TypeError, ValueError, KeyError):
            continue

    canvas.save(output_path)
    return str(output_path)