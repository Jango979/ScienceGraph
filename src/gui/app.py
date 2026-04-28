import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image

from src.core.image_loader import load_image, SUPPORTED_FORMATS
from src.core import image_editor as editor
from src.core.exporter import export
from src.gui.viewer import ImageViewer
from src.gui.controls import ControlPanel

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ScienceGraphApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ScienceGraph")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self._original: Image.Image | None = None
        self._current: Image.Image | None = None
        self._source_path: Path | None = None

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self._viewer = ImageViewer(self)
        self._viewer.grid(row=0, column=0, sticky="nsew", padx=(10, 4), pady=10)

        self._controls = ControlPanel(
            self,
            on_open=self._open_image,
            on_export=self._export_image,
            on_rotate=self._apply_rotate,
            on_flip_h=self._apply_flip_h,
            on_flip_v=self._apply_flip_v,
            on_brightness=self._apply_brightness,
            on_contrast=self._apply_contrast,
            width=260,
        )
        self._controls.grid(row=0, column=1, sticky="nsew", padx=(4, 10), pady=10)

    def _open_image(self):
        exts = " ".join(f"*{e}" for e in SUPPORTED_FORMATS)
        path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imagenes soportadas", exts), ("Todos los archivos", "*.*")]
        )
        if not path:
            return
        self._source_path = Path(path)
        self._original = load_image(self._source_path)
        self._current = self._original.copy()
        self._viewer.show(self._current)

    def _export_image(self, preset: str, dpi: int):
        if self._current is None:
            messagebox.showwarning("Sin imagen", "Primero abre una imagen.")
            return
        default_name = self._source_path.stem if self._source_path else "figura"
        path = filedialog.asksaveasfilename(
            title="Guardar figura",
            initialfile=default_name,
            defaultextension=".tif",
        )
        if not path:
            return
        out = export(self._current, Path(path), preset, dpi)
        messagebox.showinfo("Exportado", f"Figura guardada en:\n{out}")

    def _apply_rotate(self, degrees: float):
        if self._original is None:
            return
        self._current = editor.rotate(self._original, degrees)
        self._viewer.show(self._current)

    def _apply_flip_h(self):
        if self._current is None:
            return
        self._current = editor.flip_horizontal(self._current)
        self._original = self._current.copy()
        self._viewer.show(self._current)

    def _apply_flip_v(self):
        if self._current is None:
            return
        self._current = editor.flip_vertical(self._current)
        self._original = self._current.copy()
        self._viewer.show(self._current)

    def _apply_brightness(self, factor: float):
        if self._original is None:
            return
        self._current = editor.adjust_brightness(self._original, factor)
        self._viewer.show(self._current)

    def _apply_contrast(self, factor: float):
        if self._original is None:
            return
        self._current = editor.adjust_contrast(self._original, factor)
        self._viewer.show(self._current)
