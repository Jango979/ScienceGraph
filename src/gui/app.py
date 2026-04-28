import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image

from src.core.image_loader import load_image, SUPPORTED_FORMATS
from src.core.element import Element, new_uid
from src.core.exporter import export
from src.core.latex_renderer import render_latex, render_text
from src.gui.canvas_workspace import CanvasWorkspace
from src.gui.toolbar import Toolbar
from src.gui.properties import PropertiesPanel
from src.gui.dialogs import TextDialog, ExportDialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ScienceGraphApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ScienceGraph")
        self.geometry("1380x820")
        self.minsize(1050, 650)
        self._clipboard_style: dict | None = None
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._toolbar = Toolbar(
            self,
            on_add_image=self._add_image,
            on_add_text=self._add_text,
            on_add_latex=self._add_latex,
            on_toggle_spacing=self._toggle_spacing,
            on_copy_style=self._copy_style,
            on_paste_style=self._paste_style,
            on_export=self._export,
        )
        self._toolbar.grid(row=0, column=0, sticky="ns", padx=(8, 0), pady=8)

        self._canvas = CanvasWorkspace(
            self,
            on_select=self._on_select,
            on_change=self._on_element_change,
        )
        self._canvas.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        self._props = PropertiesPanel(self, on_update=self._on_props_update)
        self._props.grid(row=0, column=2, sticky="ns", padx=(0, 8), pady=8)

    # ---------------------------------------------------------------- actions

    def _add_image(self):
        exts = " ".join(f"*{e}" for e in SUPPORTED_FORMATS)
        paths = filedialog.askopenfilenames(
            title="Seleccionar imagen(es)",
            filetypes=[("Imagenes soportadas", exts), ("Todos los archivos", "*.*")],
        )
        offset = 0
        for path in paths:
            try:
                img = load_image(path)
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudo cargar:\n{path}\n\n{exc}")
                continue
            ow, oh = img.size
            scale = min(500 / ow, 500 / oh, 1.0)
            elem = Element(
                uid=new_uid(),
                x=60 + offset,
                y=60 + offset,
                w=ow * scale,
                h=oh * scale,
                image=img,
                name=Path(path).stem,
                source_path=Path(path),
            )
            self._canvas.add_element(elem)
            offset += 24

    def _add_text(self):
        dlg = TextDialog(self, use_latex=False)
        self.wait_window(dlg)
        if dlg.result:
            self._create_text_element(dlg.result, use_latex=False)

    def _add_latex(self):
        dlg = TextDialog(self, use_latex=True)
        self.wait_window(dlg)
        if dlg.result:
            self._create_text_element(dlg.result, use_latex=True)

    def _create_text_element(self, result: dict, use_latex: bool):
        text = result["text"]
        size = result["font_size"]
        color = result["color"]
        try:
            img = render_latex(text, fontsize=size, color=color) if use_latex \
                  else render_text(text, fontsize=size, color=color)
        except Exception as exc:
            messagebox.showerror("Error al renderizar", str(exc))
            return
        ow, oh = img.size
        elem = Element(
            uid=new_uid(),
            x=80, y=80,
            w=float(ow), h=float(oh),
            image=img,
            name=text[:30],
            is_text=True,
            text_content=text,
            use_latex=use_latex,
            font_size=size,
            font_color=color,
        )
        self._canvas.add_element(elem)

    def _toggle_spacing(self):
        self._canvas.toggle_spacing()
        self._toolbar.set_spacing_state(self._canvas.show_spacing)

    def _copy_style(self):
        if not self._canvas.selected:
            messagebox.showwarning("Sin seleccion", "Selecciona un elemento primero.")
            return
        self._clipboard_style = self._canvas.selected.copy_style()

    def _paste_style(self):
        if not self._clipboard_style:
            messagebox.showwarning("Sin estilo", "Primero copia el estilo de un elemento.")
            return
        if not self._canvas.selected:
            messagebox.showwarning("Sin seleccion", "Selecciona un elemento primero.")
            return
        self._canvas.selected.paste_style(self._clipboard_style)
        self._canvas.redraw()

    def _export(self):
        if not self._canvas.elements:
            messagebox.showwarning("Canvas vacio", "Agrega al menos una imagen al canvas.")
            return
        dlg = ExportDialog(self)
        self.wait_window(dlg)
        if not dlg.result:
            return

        path = filedialog.asksaveasfilename(
            title="Guardar figura",
            defaultextension=".tif",
            filetypes=[("TIFF", "*.tif"), ("PNG", "*.png"),
                       ("JPEG", "*.jpg"), ("PDF", "*.pdf"),
                       ("Todos", "*.*")],
        )
        if not path:
            return

        try:
            composite = self._canvas.get_composite()
            tw = dlg.result["target_w"]
            th = dlg.result["target_h"]
            if tw and th:
                composite = composite.resize((tw, th), Image.LANCZOS)
            out = export(composite, Path(path), dlg.result["preset"], dlg.result["dpi"])
            messagebox.showinfo("Exportado", f"Figura guardada en:\n{out}")
        except Exception as exc:
            messagebox.showerror("Error al exportar", str(exc))

    # --------------------------------------------------------------- callbacks

    def _on_select(self, element: Element | None):
        self._props.load(element)

    def _on_element_change(self, element: Element):
        self._props.load(element)

    def _on_props_update(self, element: Element):
        self._canvas.redraw()
        self._props.load(element)
