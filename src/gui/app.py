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
from src.gui.dialogs import TextDialog, CanvasSettingsDialog, PreviewDialog, ExportDialog, DistributeDialog
from src.core.spacing import nearest_gaps

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ScienceGraphApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ScienceGraph")
        self.geometry("1420x860")
        self.minsize(1100, 680)
        self._clipboard_style: dict | None = None
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._toolbar = Toolbar(
            self,
            on_add_image=self._add_image,
            on_add_text=self._add_text,
            on_add_latex=self._add_latex,
            on_toggle_spacing=self._toggle_spacing,
            on_toggle_collision=self._toggle_collision,
            on_canvas_settings=self._canvas_settings,
            on_preview=self._preview,
            on_copy_style=self._copy_style,
            on_paste_style=self._paste_style,
            on_distribute=self._distribute,
            on_export=self._export,
        )
        self._toolbar.grid(row=0, column=0, sticky="ns", padx=(8, 0), pady=8)

        self._canvas = CanvasWorkspace(
            self,
            on_select=self._on_select,
            on_change=self._on_element_change,
            on_zoom_change=self._on_zoom_change,
        )
        self._canvas.grid(row=0, column=1, sticky="nsew", padx=8, pady=(8, 0))

        self._props = PropertiesPanel(
            self,
            on_update=self._on_props_update,
            on_restyle=self._on_restyle,
            on_set_spacing=self._on_set_spacing,
        )
        self._props.grid(row=0, column=2, sticky="ns", padx=(0, 8), pady=8)

        self._zoom_bar = ZoomBar(
            self,
            on_zoom_in=self._canvas.zoom_in,
            on_zoom_out=self._canvas.zoom_out,
            on_fit=self._canvas.zoom_fit,
            on_set_zoom=self._canvas.set_zoom,
        )
        self._zoom_bar.grid(row=1, column=0, columnspan=3, sticky="ew",
                            padx=8, pady=(2, 8))

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
            # Place inside page by default
            px, py = self._canvas.page_x + 20 + offset, self._canvas.page_y + 20 + offset
            elem = Element(
                uid=new_uid(),
                x=float(px), y=float(py),
                w=ow * scale, h=oh * scale,
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
            img = (render_latex(text, fontsize=size, color=color)
                   if use_latex
                   else render_text(text, fontsize=size, color=color))
        except Exception as exc:
            messagebox.showerror("Error al renderizar", str(exc))
            return
        ow, oh = img.size
        px = float(self._canvas.page_x + 20)
        py = float(self._canvas.page_y + 20)
        elem = Element(
            uid=new_uid(),
            x=px, y=py,
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
        self._update_props_spacing()

    def _distribute(self):
        n = len(self._canvas.multi_select)
        dlg = DistributeDialog(self, n)
        self.wait_window(dlg)
        if not dlg.result:
            return
        targets = self._canvas.multi_select if n > 1 else self._canvas.elements
        if not targets:
            return
        self._canvas.distribute(targets, dlg.result["gap_x"], dlg.result["gap_y"],
                                 dlg.result["mode"])

    def _toggle_collision(self):
        self._canvas.toggle_collision()
        self._toolbar.set_collision_state(self._canvas.collision_enabled)

    def _canvas_settings(self):
        c = self._canvas
        dlg = CanvasSettingsDialog(self, c.page_w, c.page_h, c.page_bg)
        self.wait_window(dlg)
        if dlg.result:
            c.set_page(dlg.result["w"], dlg.result["h"], dlg.result["bg"])

    def _preview(self):
        if not self._canvas.elements:
            messagebox.showwarning("Canvas vacio", "Agrega al menos una imagen.")
            return
        try:
            composite = self._canvas.get_composite(page_only=False)
            PreviewDialog(self, composite)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

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
        elem = self._canvas.selected
        elem.paste_style(self._clipboard_style)
        # Re-render if text element
        if elem.is_text:
            self._on_restyle(elem)
        else:
            self._canvas.redraw()
            self._props.load(elem)

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
            composite = self._canvas.get_composite(page_only=dlg.result["page_only"])
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
        self._update_props_spacing()

    def _on_element_change(self, element: Element):
        self._props.load(element)
        self._update_props_spacing()

    def _on_props_update(self, element: Element):
        self._canvas.redraw()
        self._props.load(element)
        self._update_props_spacing()

    def _on_zoom_change(self, factor: float):
        self._zoom_bar.update(factor)

    def _update_props_spacing(self):
        if not self._canvas.show_spacing or not self._canvas.selected:
            self._props.update_spacing(None)
            return
        gaps = nearest_gaps(self._canvas.selected, self._canvas.elements)
        self._props.update_spacing(gaps)

    def _on_set_spacing(self, direction: str, distance: float):
        selected = self._canvas.selected
        if not selected:
            return
        gaps = nearest_gaps(selected, self._canvas.elements)
        gap = gaps.get(direction)
        if gap is None or gap[0] < 0:
            return
        _, other = gap
        if direction == "right":
            selected.x = other.x - distance - selected.w
        elif direction == "left":
            selected.x = other.x2 + distance
        elif direction == "bottom":
            selected.y = other.y - distance - selected.h
        elif direction == "top":
            selected.y = other.y2 + distance
        self._canvas.redraw()
        self._props.load(selected)
        self._update_props_spacing()

    def _on_restyle(self, element: Element):
        if not element.is_text:
            return
        try:
            if element.use_latex:
                img = render_latex(element.text_content,
                                   fontsize=element.font_size,
                                   color=element.font_color)
            else:
                img = render_text(element.text_content,
                                  fontsize=element.font_size,
                                  color=element.font_color,
                                  font_family=element.font_family,
                                  bold=element.font_bold,
                                  italic=element.font_italic)
            ow, oh = img.size
            element.image = img
            element.w = float(ow)
            element.h = float(oh)
            self._canvas.redraw()
            self._props.load(element)
        except Exception as exc:
            messagebox.showerror("Error al re-renderizar texto", str(exc))


class ZoomBar(ctk.CTkFrame):
    PRESETS = [10, 25, 50, 75, 100, 125, 150, 200, 300, 400, 500]

    def __init__(self, master, on_zoom_in, on_zoom_out, on_fit, on_set_zoom, **kwargs):
        super().__init__(master, height=36, **kwargs)
        self._on_set_zoom = on_set_zoom
        self._zoom_var = ctk.StringVar(value="100%")

        ctk.CTkButton(self, text="-", width=28, height=26,
                      command=on_zoom_out).pack(side="left", padx=(8, 2), pady=4)

        self._pct_menu = ctk.CTkOptionMenu(
            self, variable=self._zoom_var, width=90, height=26,
            values=[f"{p}%" for p in self.PRESETS],
            command=self._on_preset_select,
        )
        self._pct_menu.pack(side="left", padx=2, pady=4)

        ctk.CTkButton(self, text="+", width=28, height=26,
                      command=on_zoom_in).pack(side="left", padx=(2, 12), pady=4)

        ctk.CTkButton(self, text="Ajustar a vista", width=110, height=26,
                      command=on_fit).pack(side="left", padx=4, pady=4)

        ctk.CTkLabel(self, text="Ctrl + rueda para zoom",
                     text_color="gray", font=ctk.CTkFont(size=11)).pack(side="right", padx=12)

    def update(self, factor: float):
        self._zoom_var.set(f"{factor * 100:.0f}%")

    def _on_preset_select(self, value: str):
        try:
            pct = int(value.replace("%", ""))
            self._on_set_zoom(pct / 100.0)
        except ValueError:
            pass
