from PIL import Image, ImageEnhance, ImageOps


def crop(img: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    """box = (left, upper, right, lower) in pixels"""
    return img.crop(box)


def rotate(img: Image.Image, degrees: float, expand: bool = True) -> Image.Image:
    return img.rotate(degrees, expand=expand, resample=Image.BICUBIC)


def flip_horizontal(img: Image.Image) -> Image.Image:
    return ImageOps.mirror(img)


def flip_vertical(img: Image.Image) -> Image.Image:
    return ImageOps.flip(img)


def adjust_brightness(img: Image.Image, factor: float) -> Image.Image:
    """factor: 1.0 = original, <1 darker, >1 brighter"""
    return ImageEnhance.Brightness(img).enhance(factor)


def adjust_contrast(img: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Contrast(img).enhance(factor)


def resize(img: Image.Image, width: int, height: int) -> Image.Image:
    return img.resize((width, height), Image.LANCZOS)


def resize_to_dpi(img: Image.Image, target_dpi: int, current_dpi: int = 72) -> Image.Image:
    scale = target_dpi / current_dpi
    new_w = int(img.width * scale)
    new_h = int(img.height * scale)
    return resize(img, new_w, new_h)
