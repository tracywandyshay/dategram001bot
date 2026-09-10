"""
Generate event card images using Pillow (PIL).
No external APIs — pure local image generation.
"""

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import date


def _load_font(size: int, bold: bool = False):
    """Try to load a common system font, fallback to default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def generate_event_card(event: dict) -> BytesIO:
    """
    Create a 1080x1080 event card image.
    Returns a BytesIO buffer ready to send to Telegram.
    """
    W, H = 1080, 1080
    BG_TOP = (18, 24, 38)
    BG_BOTTOM = (32, 44, 68)
    ACCENT = (255, 179, 71)
    TEXT_WHITE = (245, 248, 252)
    TEXT_MUTED = (170, 185, 205)

    img = Image.new("RGB", (W, H), BG_TOP)
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(H):
        ratio = y / H
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Decorative top bar
    draw.rectangle([0, 0, W, 14], fill=ACCENT)

    # Big emoji top center
    emoji = event.get("emoji", "📅")
    emoji_font = _load_font(180)
    bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
    ew = bbox[2] - bbox[0]
    draw.text(((W - ew) / 2, 100), emoji, font=emoji_font, fill=TEXT_WHITE)

    # Brand label
    brand_font = _load_font(38, bold=True)
    brand_text = "DATECRAM  •  UPCOMING EVENT"
    bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
    bw = bbox[2] - bbox[0]
    draw.text(((W - bw) / 2, 320), brand_text, font=brand_font, fill=ACCENT)

    # Event name (wrap if long)
    name = event.get("name", "Event")
    name_font = _load_font(74, bold=True)
    max_width = W - 120
    words = name.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=name_font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    y = 420
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=name_font)
        lw = bbox[2] - bbox[0]
        draw.text(((W - lw) / 2, y), line, font=name_font, fill=TEXT_WHITE)
        y += 90

    # Date line
    date_text = event.get("date", "")
    time_text = event.get("time", "")
    dt_font = _load_font(46)
    dt_line = f"{date_text}  •  {time_text}"
    bbox = draw.textbbox((0, 0), dt_line, font=dt_font)
    dw = bbox[2] - bbox[0]
    draw.text(((W - dw) / 2, y + 30), dt_line, font=dt_font, fill=ACCENT)

    # Countdown circle
    days_left = event.get("days_left", 0)
    if days_left == 0:
        countdown_text = "TODAY"
    elif days_left == 1:
        countdown_text = "TOMORROW"
    else:
        countdown_text = f"IN {days_left} DAYS"

    cd_font = _load_font(60, bold=True)
    bbox = draw.textbbox((0, 0), countdown_text, font=cd_font)
    cw = bbox[2] - bbox[0]
    ch = bbox[3] - bbox[1]

    # Circle background
    cx, cy = W / 2, 880
    radius = 110
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=ACCENT, width=6)
    draw.text(
        (cx - cw / 2, cy - ch / 2 - 8),
        countdown_text,
        font=cd_font,
        fill=ACCENT
    )

    # Footer
    footer_font = _load_font(30)
    footer = "Powered by @Dategram001bot"
    bbox = draw.textbbox((0, 0), footer, font=footer_font)
    fw = bbox[2] - bbox[0]
    draw.text(((W - fw) / 2, H - 60), footer, font=footer_font, fill=TEXT_MUTED)

    buf = BytesIO()
    buf.name = "event_card.png"
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf
