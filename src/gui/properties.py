import customtkinter as ctk
from src.core.element import Element


class PropertiesPanel(ctk.CTkScrollableFrame):
    def __init__(self, master, on_update=None, **kwargs):
        super().__init__(master, width=220, **kwargs)
        self.on_update = on_update
        self._element: Element | None = None
        self._updating = False
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Propiedades",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(12, 6))

        # Name
        self._section("Nombre")
        self._name_var = ctk.StringVar()
        e = ctk.CTkEntry(self, textvariable=self._name_var)
        e.pack(fill="x", padx=10)
        e.bind("<Return>", lambda _: self._push_name())
        e.bind("<FocusOut>", lambda _: self._push_name())

        # Position
        self._section("Posicion (px)")
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=10)
        self._x_var = ctk.StringVar()
        self._y_var = ctk.StringVar()
        self._xy_entry(row, "X", self._x_var, self._push_pos)
        self._xy_entry(row, "Y", self._y_var, self._push_pos)

        # Size
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

        # Image info
        self._section("Imagen original")
        self._info_var = ctk.StringVar(value="---")
        ctk.CTkLabel(self, textvariable=self._info_var, text_color="gray",
                     font=ctk.CTkFont(size=11)).pack(padx=10, anchor="w")

        # Scale control
        self._section("Escala rapida")
        scale_row = ctk.CTkFrame(self, fg_color="transparent")
        scale_row.pack(fill="x", padx=10)
        self._scale_var = ctk.StringVar(value="100")
        ctk.CTkEntry(scale_row, textvariable=self._scale_var, width=60).pack(side="left")
        ctk.CTkLabel(scale_row, text="%").pack(side="left", padx=2)
        ctk.CTkButton(scale_row, text="Aplicar", width=60,
                      command=self._apply_scale).pack(side="left", padx=4)

        self.load(None)

    def _section(self, label: str):
        ctk.CTkLabel(self, text=label, text_color="gray",
                     font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(10, 2), padx=10, anchor="w")

    def _xy_entry(self, parent, label: str, var: ctk.StringVar, cmd):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", expand=True, fill="x", padx=2)
        ctk.CTkLabel(f, text=label, width=18).pack(side="left")
        e = ctk.CTkEntry(f, textvariable=var, width=72)
        e.pack(side="left", fill="x", expand=True)
        e.bind("<Return>", lambda _: cmd())
        e.bind("<FocusOut>", lambda _: cmd())

    # ------------------------------------------------------------------ load

    def load(self, element: Element | None):
        self._element = element
        if element is None:
            for v in (self._name_var, self._x_var, self._y_var,
                      self._w_var, self._h_var):
                v.set("")
            self._info_var.set("Sin seleccion")
            return
        self._name_var.set(element.name)
        self._x_var.set(f"{element.x:.0f}")
        self._y_var.set(f"{element.y:.0f}")
        self._w_var.set(f"{element.w:.0f}")
        self._h_var.set(f"{element.h:.0f}")
        ow, oh = element.image.size
        self._info_var.set(f"{ow} x {oh} px")

    # ----------------------------------------------------------------- pushes

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

    def _notify(self):
        if self.on_update:
            self.on_update(self._element)
