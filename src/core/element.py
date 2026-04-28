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
    is_text: bool = False
    text_content: str = ""
    use_latex: bool = False
    font_size: int = 14
    font_color: str = "#000000"

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

    def copy_style(self) -> dict:
        return {"font_size": self.font_size, "font_color": self.font_color}

    def paste_style(self, style: dict):
        self.font_size = style.get("font_size", self.font_size)
        self.font_color = style.get("font_color", self.font_color)

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
