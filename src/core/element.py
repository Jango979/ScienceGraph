import uuid
from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image


@dataclass
class Element:
    uid: str
    x: float
    y: float
    w: float
    h: float
    image: Image.Image
    name: str = ""
    source_path: Path | None = None
    # text
    is_text: bool = False
    text_content: str = ""
    use_latex: bool = False
    # style
    font_size: int = 14
    font_color: str = "#000000"
    font_family: str = "Arial"
    font_bold: bool = False
    font_italic: bool = False
    # display
    show_border: bool = False
    border_color: str = "#444444"

    @property
    def x2(self): return self.x + self.w

    @property
    def y2(self): return self.y + self.h

    @property
    def cx(self): return self.x + self.w / 2

    @property
    def cy(self): return self.y + self.h / 2

    def contains(self, px: float, py: float) -> bool:
        return self.x <= px <= self.x2 and self.y <= py <= self.y2

    def overlaps(self, other: "Element") -> bool:
        return (self.x < other.x2 and self.x2 > other.x and
                self.y < other.y2 and self.y2 > other.y)

    def copy_style(self) -> dict:
        return {
            "font_size": self.font_size,
            "font_color": self.font_color,
            "font_family": self.font_family,
            "font_bold": self.font_bold,
            "font_italic": self.font_italic,
            "show_border": self.show_border,
            "border_color": self.border_color,
        }

    def paste_style(self, style: dict):
        self.font_size = style.get("font_size", self.font_size)
        self.font_color = style.get("font_color", self.font_color)
        self.font_family = style.get("font_family", self.font_family)
        self.font_bold = style.get("font_bold", self.font_bold)
        self.font_italic = style.get("font_italic", self.font_italic)
        self.show_border = style.get("show_border", self.show_border)
        self.border_color = style.get("border_color", self.border_color)

    def duplicate(self) -> "Element":
        import copy
        clone = copy.copy(self)
        clone.uid = str(uuid.uuid4())
        clone.x += 20
        clone.y += 20
        clone.name = self.name + " (copia)"
        return clone


def new_uid() -> str:
    return str(uuid.uuid4())
