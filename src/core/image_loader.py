from pathlib import Path
from PIL import Image
import tifffile
import numpy as np

SUPPORTED_FORMATS = {
    ".png", ".jpg", ".jpeg", ".tif", ".tiff",
    ".bmp", ".eps", ".pdf", ".svg", ".emf"
}


def load_image(path: str | Path) -> Image.Image:
    path = Path(path)
    ext = path.suffix.lower()

    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {ext}")

    if ext in {".tif", ".tiff"}:
        return _load_tiff(path)
    if ext == ".svg":
        return _load_svg(path)
    return Image.open(path).convert("RGBA")


def _load_tiff(path: Path) -> Image.Image:
    arr = tifffile.imread(str(path))
    if arr.dtype != np.uint8:
        arr = (arr / arr.max() * 255).astype(np.uint8)
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)
    return Image.fromarray(arr).convert("RGBA")


def _load_svg(path: Path) -> Image.Image:
    import cairosvg
    import io
    png_bytes = cairosvg.svg2png(url=str(path), dpi=300)
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def get_image_info(img: Image.Image) -> dict:
    return {
        "width": img.width,
        "height": img.height,
        "mode": img.mode,
        "dpi_estimate": img.info.get("dpi", (72, 72)),
    }
