"""Generate the VisoMaster-Modern application icon.

Run from the repo root:  .venv\\Scripts\\python.exe tools\\make_icon.py
Output: app/ui/core/media/modern_icon.png (loaded at runtime, not embedded in media_rc).
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "app" / "ui" / "core" / "media" / "modern_icon.png"
ICO_OUT = OUT.with_suffix(".ico")

SIZE = 256
BG = (79, 172, 201, 255)      # accent #4facc9
FG = (255, 255, 255, 255)
DARK = (20, 32, 40, 255)

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\seguisb.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "DejaVuSans-Bold.ttf",
]


def _load_font(size: int):
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = 10
    draw.rounded_rectangle(
        [margin, margin, SIZE - margin, SIZE - margin],
        radius=52,
        fill=BG,
        outline=DARK,
        width=6,
    )

    font = _load_font(120)
    text = "VM"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(
        ((SIZE - text_w) / 2 - bbox[0], (SIZE - text_h) / 2 - bbox[1]),
        text,
        font=font,
        fill=FG,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    # Multi-size .ico for the Windows taskbar / alt-tab / shortcuts.
    img.save(ICO_OUT, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"wrote {OUT}")
    print(f"wrote {ICO_OUT}")


if __name__ == "__main__":
    main()
