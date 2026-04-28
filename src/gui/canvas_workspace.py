import tkinter as tk
from PIL import ImageTk, Image

from src.core.element import Element
from src.core.spacing import nearest_gaps

HANDLE_SIZE = 8
SELECT_COLOR = "#4a9eff"
SPACING_COLOR = "#ff9900"
WORKSPACE_BG = "#1e1e1e"
GRID_COLOR = "#2a2a2a"
PAGE_SHADOW = "#111111"

ZOOM_MIN = 0.1
ZOOM_MAX = 5.0
ZOOM_STEP = 0.1


class CanvasWorkspace(tk.Frame):
    def __init__(self, master, on_select=None, on_change=None, on_zoom_change=None, **kwargs):
        super().__init__(master, bg=WORKSPACE_BG, **kwargs)

        self._canvas = tk.Canvas(self, bg=WORKSPACE_BG, highlightthickness=0, cursor="crosshair")
        self._hbar = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._canvas.xview)
        self._vbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=self._hbar.set, yscrollcommand=self._vbar.set,
                               scrollregion=(0, 0, 4000, 3000))
        self._hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self._vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Page / lienzo
        self.page_x: int = 40
        self.page_y: int = 40
        self.page_w: int = 1000
        self.page_h: int = 750
        self.page_bg: str = "#ffffff"

        # Zoom
        self._zoom: float = 1.0

        # Toggles
        self.show_spacing: bool = False
        self.collision_enabled: bool = False

        self.elements: list[Element] = []
        self.selected: Element | None = None

        self._photos: dict[str, ImageTk.PhotoImage] = {}
        self._item_uid: dict[int, str] = {}
        self._drag_data: tuple | None = None
        self._resize_handle_idx: int | None = None

        self.on_select = on_select
        self.on_change = on_change
        self.on_zoom_change = on_zoom_change

        self._canvas.bind("<Button-1>", self._on_click)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._canvas.bind("<Button-3>", self._on_right_click)
        self._canvas.bind("<Delete>", self._on_delete_key)
        self._canvas.bind("<Control-MouseWheel>", self._on_ctrl_scroll)
        self._canvas.bind("<Control-Button-4>", lambda e: self.zoom_in())   # Linux
        self._canvas.bind("<Control-Button-5>", lambda e: self.zoom_out())  # Linux
        self._canvas.focus_set()

        self.redraw()

    # ------------------------------------------------------------------- zoom

    @property
    def zoom(self) -> float:
        return self._zoom

    def zoom_in(self):
        self.set_zoom(self._zoom + ZOOM_STEP)

    def zoom_out(self):
        self.set_zoom(self._zoom - ZOOM_STEP)

    def zoom_fit(self):
        self._canvas.update_idletasks()
        vw = self._canvas.winfo_width()
        vh = self._canvas.winfo_height()
        if vw < 2 or vh < 2:
            return
        pad = 60
        scale_x = (vw - pad) / (self.page_w + self.page_x * 2)
        scale_y = (vh - pad) / (self.page_h + self.page_y * 2)
        self.set_zoom(min(scale_x, scale_y))

    def set_zoom(self, factor: float):
        self._zoom = max(ZOOM_MIN, min(ZOOM_MAX, round(factor, 2)))
        self._update_scroll_region()
        self.redraw()
        if self.on_zoom_change:
            self.on_zoom_change(self._zoom)

    def _update_scroll_region(self):
        z = self._zoom
        w = int((self.page_w + self.page_x * 2 + 200) * z)
        h = int((self.page_h + self.page_y * 2 + 200) * z)
        self._canvas.configure(scrollregion=(0, 0, max(w, 800), max(h, 600)))

    def _on_ctrl_scroll(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    # ------------------------------------------------------------------ public

    def add_element(self, elem: Element):
        self.elements.append(elem)
        self.redraw()
        self.select(elem)

    def remove_selected(self):
        if self.selected:
            self.elements = [e for e in self.elements if e.uid != self.selected.uid]
            self.selected = None
            self.redraw()
            if self.on_select:
                self.on_select(None)

    def remove_element(self, uid: str):
        self.elements = [e for e in self.elements if e.uid != uid]
        if self.selected and self.selected.uid == uid:
            self.selected = None
            if self.on_select:
                self.on_select(None)
        self.redraw()

    def select(self, elem: Element | None):
        self.selected = elem
        self.redraw()
        if self.on_select:
            self.on_select(elem)

    def toggle_spacing(self):
        self.show_spacing = not self.show_spacing
        self.redraw()

    def toggle_collision(self):
        self.collision_enabled = not self.collision_enabled

    def set_page(self, w: int, h: int, bg: str):
        self.page_w, self.page_h, self.page_bg = w, h, bg
        self._update_scroll_region()
        self.redraw()

    def bring_to_front(self, uid: str):
        idx = next((i for i, e in enumerate(self.elements) if e.uid == uid), None)
        if idx is not None:
            self.elements.append(self.elements.pop(idx))
            self.redraw()

    def send_to_back(self, uid: str):
        idx = next((i for i, e in enumerate(self.elements) if e.uid == uid), None)
        if idx is not None:
            self.elements.insert(0, self.elements.pop(idx))
            self.redraw()

    def get_composite(self, page_only: bool = False) -> Image.Image:
        if not self.elements:
            return Image.new("RGBA", (self.page_w, self.page_h), (255, 255, 255, 255))

        if page_only:
            cw, ch = self.page_w, self.page_h
            ox, oy = self.page_x, self.page_y
        else:
            min_x = min(e.x for e in self.elements)
            min_y = min(e.y for e in self.elements)
            cw = int(max(e.x2 for e in self.elements) - min_x)
            ch = int(max(e.y2 for e in self.elements) - min_y)
            ox, oy = min_x, min_y

        bg = _hex_to_rgba(self.page_bg)
        composite = Image.new("RGBA", (max(cw, 1), max(ch, 1)), bg)

        for elem in self.elements:
            img = elem.image.resize((max(1, int(elem.w)), max(1, int(elem.h))), Image.LANCZOS)
            x, y = int(elem.x - ox), int(elem.y - oy)
            if img.mode == "RGBA":
                composite.paste(img, (x, y), img)
            else:
                composite.paste(img.convert("RGBA"), (x, y))

        return composite

    # ----------------------------------------------------------------- drawing

    def redraw(self):
        self._canvas.delete("all")
        self._photos.clear()
        self._item_uid.clear()

        self._draw_workspace()
        self._draw_page()

        for elem in self.elements:
            self._draw_element(elem)

        if self.selected:
            self._draw_selection(self.selected)
            if self.show_spacing:
                self._draw_spacing(self.selected)

    def _s(self, v: float) -> int:
        """World to screen coordinate."""
        return int(v * self._zoom)

    def _draw_workspace(self):
        z = self._zoom
        step = max(10, int(40 * z))
        w = int(self._canvas.cget("scrollregion").split()[2]) if self._canvas.cget("scrollregion") else 4000
        h = int(self._canvas.cget("scrollregion").split()[3]) if self._canvas.cget("scrollregion") else 3000
        for x in range(0, w + step, step):
            self._canvas.create_line(x, 0, x, h, fill=GRID_COLOR, tags="grid")
        for y in range(0, h + step, step):
            self._canvas.create_line(0, y, w, y, fill=GRID_COLOR, tags="grid")

    def _draw_page(self):
        z = self._zoom
        px = self._s(self.page_x)
        py = self._s(self.page_y)
        pw = self._s(self.page_w)
        ph = self._s(self.page_h)
        shadow = 4
        self._canvas.create_rectangle(px + shadow, py + shadow,
                                      px + pw + shadow, py + ph + shadow,
                                      fill=PAGE_SHADOW, outline="", tags="page")
        self._canvas.create_rectangle(px, py, px + pw, py + ph,
                                      fill=self.page_bg, outline="#555555", width=1, tags="page")
        pct = int(self._zoom * 100)
        self._canvas.create_text(px + 4, py - 16,
                                  text=f"{self.page_w} x {self.page_h} px  |  {pct}%",
                                  anchor="w", fill="#666666", font=("Arial", 9), tags="page")

    def _draw_element(self, elem: Element):
        z = self._zoom
        dw = max(1, int(elem.w * z))
        dh = max(1, int(elem.h * z))
        display = elem.image.resize((dw, dh), Image.LANCZOS)
        photo = ImageTk.PhotoImage(display)
        self._photos[elem.uid] = photo
        sx, sy = self._s(elem.x), self._s(elem.y)
        item_id = self._canvas.create_image(sx, sy, anchor="nw", image=photo)
        self._item_uid[item_id] = elem.uid

        if elem.show_border:
            self._canvas.create_rectangle(sx, sy, self._s(elem.x2), self._s(elem.y2),
                                          outline=elem.border_color, width=1, tags="border")

        self._canvas.create_text(sx + 4, sy + 4, text=elem.name,
                                  anchor="nw", font=("Arial", 9), fill="#cccccc", tags="label")

    def _draw_selection(self, elem: Element):
        z = self._zoom
        pad = 2
        sx, sy = self._s(elem.x) - pad, self._s(elem.y) - pad
        ex, ey = self._s(elem.x2) + pad, self._s(elem.y2) + pad
        self._canvas.create_rectangle(sx, sy, ex, ey,
                                      outline=SELECT_COLOR, width=2, dash=(6, 3), tags="selection")
        hs = HANDLE_SIZE
        for hx, hy in self._handle_screen_positions(elem):
            self._canvas.create_rectangle(hx - hs // 2, hy - hs // 2,
                                          hx + hs // 2, hy + hs // 2,
                                          fill=SELECT_COLOR, outline="white", width=1, tags="handle")

    def _handle_world_positions(self, elem: Element) -> list[tuple]:
        x, y, x2, y2, cx, cy = elem.x, elem.y, elem.x2, elem.y2, elem.cx, elem.cy
        return [(x, y), (cx, y), (x2, y),
                (x, cy),          (x2, cy),
                (x, y2), (cx, y2), (x2, y2)]

    def _handle_screen_positions(self, elem: Element) -> list[tuple]:
        return [(self._s(hx), self._s(hy))
                for hx, hy in self._handle_world_positions(elem)]

    def _draw_spacing(self, elem: Element):
        gaps = nearest_gaps(elem, self.elements)
        for direction, gap in gaps.items():
            if gap is None:
                continue
            dist, other = gap
            if dist < 0:
                continue
            if direction == "right":
                self._arrow(elem.x2, elem.cy, other.x, elem.cy, f"{dist:.0f}px")
            elif direction == "left":
                self._arrow(elem.x, elem.cy, other.x2, elem.cy, f"{dist:.0f}px")
            elif direction == "bottom":
                self._arrow(elem.cx, elem.y2, elem.cx, other.y, f"{dist:.0f}px")
            elif direction == "top":
                self._arrow(elem.cx, elem.y, elem.cx, other.y2, f"{dist:.0f}px")

    def _arrow(self, x1, y1, x2, y2, label: str):
        sx1, sy1 = self._s(x1), self._s(y1)
        sx2, sy2 = self._s(x2), self._s(y2)
        self._canvas.create_line(sx1, sy1, sx2, sy2, fill=SPACING_COLOR, width=2,
                                 arrow=tk.BOTH, arrowshape=(8, 10, 4), tags="spacing")
        mx, my = (sx1 + sx2) / 2, (sy1 + sy2) / 2
        self._canvas.create_rectangle(mx - 22, my - 11, mx + 22, my + 11,
                                      fill="#2b2b2b", outline=SPACING_COLOR, tags="spacing")
        self._canvas.create_text(mx, my, text=label, fill=SPACING_COLOR,
                                 font=("Arial", 9, "bold"), tags="spacing")

    # ------------------------------------------------------------------ events

    def _wx(self, event) -> float:
        """Canvas event x -> world x."""
        return self._canvas.canvasx(event.x) / self._zoom

    def _wy(self, event) -> float:
        """Canvas event y -> world y."""
        return self._canvas.canvasy(event.y) / self._zoom

    def _on_click(self, event):
        cx, cy = self._wx(event), self._wy(event)
        self._canvas.focus_set()

        if self.selected:
            for i, (hx, hy) in enumerate(self._handle_screen_positions(self.selected)):
                ex = self._canvas.canvasx(event.x)
                ey = self._canvas.canvasy(event.y)
                if abs(ex - hx) <= HANDLE_SIZE and abs(ey - hy) <= HANDLE_SIZE:
                    self._resize_handle_idx = i
                    s = self.selected
                    self._drag_data = (cx, cy, s.x, s.y, s.w, s.h)
                    return

        self._resize_handle_idx = None
        elem = self._find_element_at(cx, cy)

        if elem:
            self.select(elem)
            self._drag_data = (cx, cy, elem.x, elem.y, elem.w, elem.h)
        else:
            self.select(None)
            self._drag_data = None

    def _on_drag(self, event):
        if not self._drag_data or not self.selected:
            return
        cx, cy = self._wx(event), self._wy(event)
        ox, oy, ex, ey, ew, eh = self._drag_data
        dx, dy = cx - ox, cy - oy
        s = self.selected

        if self._resize_handle_idx is not None:
            h = self._resize_handle_idx
            new_x, new_y, new_w, new_h = ex, ey, ew, eh
            if h in (0, 3, 5):
                new_x = ex + dx
                new_w = max(20, ew - dx)
            if h in (2, 4, 7):
                new_w = max(20, ew + dx)
            if h in (0, 1, 2):
                new_y = ey + dy
                new_h = max(20, eh - dy)
            if h in (5, 6, 7):
                new_h = max(20, eh + dy)
            s.x, s.y, s.w, s.h = new_x, new_y, new_w, new_h
        else:
            prev_x, prev_y = s.x, s.y
            s.x = ex + dx
            s.y = ey + dy
            if self.collision_enabled and self._has_collision(s):
                s.x, s.y = prev_x, prev_y

        self.redraw()
        if self.on_change:
            self.on_change(s)

    def _on_release(self, event):
        self._drag_data = None
        self._resize_handle_idx = None

    def _on_delete_key(self, event):
        self.remove_selected()

    def _on_right_click(self, event):
        cx, cy = self._wx(event), self._wy(event)
        elem = self._find_element_at(cx, cy)
        if not elem:
            return
        self.select(elem)
        menu = tk.Menu(self._canvas, tearoff=0)
        menu.add_command(label="Traer al frente", command=lambda: self.bring_to_front(elem.uid))
        menu.add_command(label="Enviar al fondo", command=lambda: self.send_to_back(elem.uid))
        menu.add_separator()
        menu.add_command(label="Duplicar", command=lambda: self.add_element(elem.duplicate()))
        menu.add_separator()
        menu.add_command(label="Eliminar", command=lambda: self.remove_element(elem.uid))
        menu.tk_popup(event.x_root, event.y_root)

    def _find_element_at(self, px: float, py: float) -> Element | None:
        for elem in reversed(self.elements):
            if elem.contains(px, py):
                return elem
        return None

    def _has_collision(self, moving: Element) -> bool:
        return any(moving.overlaps(other)
                   for other in self.elements if other.uid != moving.uid)


def _hex_to_rgba(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, 255)
