import io
from PIL import Image

WINDOWS_FONTS = {
    "Arial":           {"r": "arial.ttf",    "b": "arialbd.ttf",  "i": "ariali.ttf",  "bi": "arialbi.ttf"},
    "Times New Roman": {"r": "times.ttf",    "b": "timesbd.ttf",  "i": "timesi.ttf",  "bi": "timesbi.ttf"},
    "Courier New":     {"r": "cour.ttf",     "b": "courbd.ttf",   "i": "couri.ttf",   "bi": "courbi.ttf"},
    "Verdana":         {"r": "verdana.ttf",  "b": "verdanab.ttf", "i": "verdanai.ttf","bi": "verdanaz.ttf"},
    "Calibri":         {"r": "calibri.ttf",  "b": "calibrib.ttf", "i": "calibrii.ttf","bi": "calibriz.ttf"},
    "Georgia":         {"r": "georgia.ttf",  "b": "georgiab.ttf", "i": "georgiai.ttf","bi": "georgiaz.ttf"},
    "Cambria":         {"r": "cambria.ttc",  "b": "cambriab.ttf", "i": "cambriai.ttf","bi": "cambriaz.ttf"},
}

FONT_FAMILIES = list(WINDOWS_FONTS.keys())


def render_latex(expr: str, fontsize: int = 14, dpi: int = 200, color: str = "black") -> Image.Image:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0)
    fig.text(0, 0, f"${expr}$", fontsize=fontsize, color=color)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                transparent=True, pad_inches=0.08)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).copy().convert("RGBA")


def render_text(text: str, fontsize: int = 14, dpi: int = 150, color: str = "black",
                font_family: str = "Arial", bold: bool = False, italic: bool = False) -> Image.Image:
    from PIL import ImageDraw, ImageFont
    import os

    key = "bi" if (bold and italic) else ("b" if bold else ("i" if italic else "r"))
    font_file = WINDOWS_FONTS.get(font_family, WINDOWS_FONTS["Arial"])[key]
    font_size_px = max(12, int(fontsize * 1.8))

    font = None
    search_paths = [
        font_file,
        os.path.join("C:\\Windows\\Fonts", font_file),
    ]
    for path in search_paths:
        try:
            font = ImageFont.truetype(path, font_size_px)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()

    dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    pad = 10
    w = bbox[2] - bbox[0] + pad * 2
    h = bbox[3] - bbox[1] + pad * 2

    img = Image.new("RGBA", (max(w, 20), max(h, 20)), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.text((pad - bbox[0], pad - bbox[1]), text, font=font, fill=color)
    return img
