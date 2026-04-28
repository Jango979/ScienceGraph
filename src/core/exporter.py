from pathlib import Path
from PIL import Image

EXPORT_PRESETS = {
    "TIFF (sin compresion)":  {"format": "TIFF", "compression": "none",       "ext": ".tif"},
    "TIFF (LZW lossless)":    {"format": "TIFF", "compression": "tiff_lzw",   "ext": ".tif"},
    "TIFF (300 dpi)":         {"format": "TIFF", "compression": "none",       "ext": ".tif", "dpi": 300},
    "PNG (sin compresion)":   {"format": "PNG",  "compress_level": 0,         "ext": ".png"},
    "PNG (comprimido)":       {"format": "PNG",  "compress_level": 6,         "ext": ".png"},
    "JPEG (alta calidad)":    {"format": "JPEG", "quality": 95,               "ext": ".jpg"},
    "JPEG (publicacion)":     {"format": "JPEG", "quality": 85,               "ext": ".jpg"},
    "PDF":                    {"format": "PDF",                                "ext": ".pdf"},
    "EPS":                    {"format": "EPS",                                "ext": ".eps"},
}


def export(img: Image.Image, output_path: str | Path, preset_name: str, dpi: int = 300) -> Path:
    output_path = Path(output_path)
    preset = EXPORT_PRESETS.get(preset_name)
    if preset is None:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(EXPORT_PRESETS)}")

    fmt = preset["format"]
    save_kwargs: dict = {"dpi": (dpi, dpi)}

    if fmt == "TIFF":
        save_kwargs["compression"] = preset.get("compression", "none")
    elif fmt == "PNG":
        save_kwargs["compress_level"] = preset.get("compress_level", 6)
    elif fmt == "JPEG":
        save_kwargs["quality"] = preset.get("quality", 95)
        img = img.convert("RGB")
    elif fmt in {"PDF", "EPS"}:
        img = img.convert("RGB")

    output_path = output_path.with_suffix(preset["ext"])
    img.save(output_path, format=fmt, **save_kwargs)
    return output_path


def get_preset_names() -> list[str]:
    return list(EXPORT_PRESETS.keys())
