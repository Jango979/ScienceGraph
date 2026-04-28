import customtkinter as ctk
from src.core.element import Element
from src.core.latex_renderer import FONT_FAMILIES


class PropertiesPanel(ctk.CTkScrollableFrame):
    def __init__(self, master, on_update=None, on_restyle=None, on_set_spacing=None, **kwargs):
        super().__init__(master, width=230, **kwargs)
        self.on_update = on_update
        self.on_restyle = on_restyle
        self.on_set_spacing = on_set_spacing
        self._element: Element | None = None
        self._updating = False
        self._text_widgets: list = []
        self._build()

    # ------------------------------------------------------------------- build

    def _build(self):
        ctk.CTkLabel(self, text="Propiedades",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(12, 6))

        self._section("Nombre")
        self._name_var = ctk.StringVar()
        e = ctk.CTkEntry(self, textvariable=self._name_var)
        e.pack(fill="x", padx=10)
        e.bind("<Return>", lambda _: self._push_name())
        e.bind("<FocusOut>", lambda _: self._push_name())

        self._section("Posicion (px)")
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=10)
        self._x_var = ctk.StringVar()
        self._y_var = ctk.StringVar()
        self._xy_entry(row, "X", self._x_var, self._push_pos)
        self._xy_entry(row, "Y", self._y_var, self._push_pos)

        self._section("Tamaño (px)")
        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.pack(fill="x", padx=10)
        self._w_var = ctk.StringVar()
        self._h_var = ctk.StringVar()
        self._xy_entry(row2, "W", self._w_var, self._push_w)
        self._xy_entry(row2, "H", self._h_var, self._push_h)

        self._lock_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self, text="Mantener proporcion",
                        variable=self._lock_var).pack(padx=10, pady=4, anchor="w")

        self._section("Escala rapida")
        sr = ctk.CTkFrame(self, fg_color="transparent")
        sr.pack(fill="x", padx=10)
        self._scale_var = ctk.StringVar(value="100")
        ctk.CTkEntry(sr, textvariable=self._scale_var, width=60).pack(side="left")
        ctk.CTkLabel(sr, text="%").pack(side="left", padx=2)
        ctk.CTkButton(sr, text="Aplicar", width=60,
                      command=self._apply_scale).pack(side="left", padx=4)

        self._section("Imagen original")
        self._info_var = ctk.StringVar(value="---")
        ctk.CTkLabel(self, textvariable=self._info_var, text_color="gray",
                     font=ctk.CTkFont(size=11)).pack(padx=10, anchor="w")

        self._section("Borde")
        br = ctk.CTkFrame(self, fg_color="transparent")
        br.pack(fill="x", padx=10)
        self._border_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(br, text="Mostrar borde", variable=self._border_var,
                        command=self._push_border).pack(side="left")
        self._border_color_var = ctk.StringVar(value="#444444")
        ctk.CTkEntry(br, textvariable=self._border_color_var, width=75).pack(side="left", padx=4)
        ctk.CTkButton(br, text="OK", width=30,
                      command=self._push_border).pack(side="left")

        # Text style section (shown only for text elements)
        self._text_section_label = self._section("Estilo de texto", hidden=True)
        self._text_frame = ctk.CTkFrame(self, fg_color="transparent")

        ctk.CTkLabel(self._text_frame, text="Fuente:").pack(anchor="w")
        self._family_var = ctk.StringVar(value="Arial")
        fm = ctk.CTkOptionMenu(self._text_frame, variable=self._family_var,
                               values=FONT_FAMILIES, command=lambda _: self._push_restyle())
        fm.pack(fill="x", pady=2)
        self._text_widgets.append(fm)

        style_row = ctk.CTkFrame(self._text_frame, fg_color="transparent")
        style_row.pack(fill="x", pady=2)
        self._bold_var = ctk.BooleanVar(value=False)
        self._italic_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(style_row, text="Negrita", variable=self._bold_var,
                        command=self._push_restyle, width=90).pack(side="left")
        ctk.CTkCheckBox(style_row, text="Italica", variable=self._italic_var,
                        command=self._push_restyle, width=90).pack(side="left")

        ctk.CTkLabel(self._text_frame, text="Tamaño:").pack(anchor="w")
        self._fsize_var = ctk.StringVar(value="14")
        fse = ctk.CTkEntry(self._text_frame, textvariable=self._fsize_var)
        fse.pack(fill="x")
        fse.bind("<Return>", lambda _: self._push_restyle())
        fse.bind("<FocusOut>", lambda _: self._push_restyle())

        ctk.CTkLabel(self._text_frame, text="Color (hex):").pack(anchor="w")
        self._fcolor_var = ctk.StringVar(value="#000000")
        fce = ctk.CTkEntry(self._text_frame, textvariable=self._fcolor_var)
        fce.pack(fill="x")
        fce.bind("<Return>", lambda _: self._push_restyle())
        fce.bind("<FocusOut>", lambda _: self._push_restyle())

        # Spacing section (visible when guides active)
        self._spacing_section_label = self._section("Separacion a vecinos", hidden=True)
        self._spacing_frame = ctk.CTkFrame(self, fg_color="transparent")

        dirs = [("Derecha", "right"), ("Izquierda", "left"),
                ("Abajo", "bottom"), ("Arriba", "top")]
        self._spacing_vars: dict[str, ctk.StringVar] = {}
        self._spacing_active: dict[str, bool] = {}
        for label_text, key in dirs:
            row = ctk.CTkFrame(self._spacing_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f"{label_text}:", width=68, anchor="w").pack(side="left")
            var = ctk.StringVar(value="---")
            self._spacing_vars[key] = var
            entry = ctk.CTkEntry(row, textvariable=var, width=70)
            entry.pack(side="left", padx=2)
            entry.bind("<Return>", lambda _, k=key: self._push_spacing(k))
            ctk.CTkLabel(row, text="px").pack(side="left")
            self._spacing_active[key] = False

        self.load(None)

    def _section(self, label: str, hidden: bool = False) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(self, text=label, text_color="gray",
                           font=ctk.CTkFont(size=11, weight="bold"))
        if not hidden:
            lbl.pack(pady=(10, 2), padx=10, anchor="w")
        return lbl

    def _xy_entry(self, parent, label: str, var: ctk.StringVar, cmd):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", expand=True, fill="x", padx=2)
        ctk.CTkLabel(f, text=label, width=18).pack(side="left")
        e = ctk.CTkEntry(f, textvariable=var, width=72)
        e.pack(side="left", fill="x", expand=True)
        e.bind("<Return>", lambda _: cmd())
        e.bind("<FocusOut>", lambda _: cmd())

    # -------------------------------------------------------------------- load

    def load(self, element: Element | None):
        self._element = element
        if element is None:
            for v in (self._name_var, self._x_var, self._y_var,
                      self._w_var, self._h_var):
                v.set("")
            self._info_var.set("Sin seleccion")
            self._text_frame.pack_forget()
            self._text_section_label.pack_forget()
            return

        self._name_var.set(element.name)
        self._x_var.set(f"{element.x:.0f}")
        self._y_var.set(f"{element.y:.0f}")
        self._w_var.set(f"{element.w:.0f}")
        self._h_var.set(f"{element.h:.0f}")
        ow, oh = element.image.size
        self._info_var.set(f"{ow} x {oh} px")
        self._border_var.set(element.show_border)
        self._border_color_var.set(element.border_color)

        # Text style
        if element.is_text:
            self._text_section_label.pack(pady=(10, 2), padx=10, anchor="w")
            self._text_frame.pack(fill="x", padx=10, pady=4)
            self._updating = True
            self._family_var.set(element.font_family)
            self._bold_var.set(element.font_bold)
            self._italic_var.set(element.font_italic)
            self._fsize_var.set(str(element.font_size))
            self._fcolor_var.set(element.font_color)
            self._updating = False
        else:
            self._text_frame.pack_forget()
            self._text_section_label.pack_forget()

    # ------------------------------------------------------------------ pushes

    def _push_name(self):
        if self._element:
            self._element.name = self._name_var.get()

    def _push_pos(self):
        if self._updating or not self._element:
            return
        try:
            self._element.x = float(self._x_var.get())
            self._element.y = float(self._y_var.get())
            self._notify()
        except ValueError:
            pass

    def _push_w(self):
        if self._updating or not self._element:
            return
        try:
            new_w = float(self._w_var.get())
            if self._lock_var.get() and self._element.w > 0:
                ratio = self._element.h / self._element.w
                new_h = new_w * ratio
                self._updating = True
                self._h_var.set(f"{new_h:.0f}")
                self._updating = False
                self._element.h = new_h
            self._element.w = new_w
            self._notify()
        except ValueError:
            pass

    def _push_h(self):
        if self._updating or not self._element:
            return
        try:
            new_h = float(self._h_var.get())
            if self._lock_var.get() and self._element.h > 0:
                ratio = self._element.w / self._element.h
                new_w = new_h * ratio
                self._updating = True
                self._w_var.set(f"{new_w:.0f}")
                self._updating = False
                self._element.w = new_w
            self._element.h = new_h
            self._notify()
        except ValueError:
            pass

    def _push_border(self):
        if not self._element:
            return
        self._element.show_border = self._border_var.get()
        self._element.border_color = self._border_color_var.get()
        self._notify()

    def _push_restyle(self):
        if self._updating or not self._element or not self._element.is_text:
            return
        try:
            self._element.font_family = self._family_var.get()
            self._element.font_bold = self._bold_var.get()
            self._element.font_italic = self._italic_var.get()
            self._element.font_size = int(self._fsize_var.get())
            self._element.font_color = self._fcolor_var.get()
            if self.on_restyle:
                self.on_restyle(self._element)
        except ValueError:
            pass

    def _apply_scale(self):
        if not self._element:
            return
        try:
            pct = float(self._scale_var.get()) / 100.0
            ow, oh = self._element.image.size
            self._element.w = ow * pct
            self._element.h = oh * pct
            self.load(self._element)
            self._notify()
        except ValueError:
            pass

    def update_spacing(self, gaps: dict | None):
        """Called by app when spacing guides are active. gaps = nearest_gaps() result or None."""
        if gaps is None or not self._element:
            self._spacing_section_label.pack_forget()
            self._spacing_frame.pack_forget()
            for key in self._spacing_vars:
                self._spacing_vars[key].set("---")
                self._spacing_active[key] = False
            return

        self._spacing_section_label.pack(pady=(10, 2), padx=10, anchor="w")
        self._spacing_frame.pack(fill="x", padx=10, pady=2)

        for key, gap in gaps.items():
            if gap is not None and gap[0] >= 0:
                self._spacing_vars[key].set(f"{gap[0]:.0f}")
                self._spacing_active[key] = True
            else:
                self._spacing_vars[key].set("---")
                self._spacing_active[key] = False

    def _push_spacing(self, direction: str):
        if not self._spacing_active.get(direction):
            return
        try:
            val = float(self._spacing_vars[direction].get())
        except ValueError:
            return
        if self.on_set_spacing:
            self.on_set_spacing(direction, val)

    def _notify(self):
        if self.on_update:
            self.on_update(self._element)
