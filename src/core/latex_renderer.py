import io
from PIL import Image


def render_latex(expr: str, fontsize: int = 14, dpi: int = 200, color: str = "black") -> Image.Image:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(8, 1.5))
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.patch.set_alpha(0)
    ax.text(0.5, 0.5, f"${expr}$", fontsize=fontsize, color=color,
            ha="center", va="center", transform=ax.transAxes)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                transparent=True, pad_inches=0.1)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).copy().convert("RGBA")


def render_text(text: str, fontsize: int = 14, dpi: int = 150, color: str = "black") -> Image.Image:
    from PIL import ImageDraw, ImageFont
    font_size_px = max(12, fontsize * 2)
    try:
        font = ImageFont.truetype("arial.ttf", font_size_px)
    except OSError:
        font = ImageFont.load_default()

    dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0] + 20
    h = bbox[3] - bbox[1] + 20

    img = Image.new("RGBA", (max(w, 40), max(h, 30)), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), text, font=font, fill=color)
    return img
