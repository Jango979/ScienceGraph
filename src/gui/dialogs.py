import customtkinter as ctk
from PIL import ImageTk
from src.core.exporter import get_preset_names

PRESET_PAGES = {
    "Personalizado":        None,
    "A4 vertical (300 DPI)": (2480, 3508),
    "A4 horizontal (300 DPI)": (3508, 2480),
    "Letter vertical (300 DPI)": (2550, 3300),
    "Columna simple revista (300 DPI)": (1004, 1400),
    "Doble columna revista (300 DPI)": (2071, 1400),
    "HD 1920x1080": (1920, 1080),
}


class TextDialog(ctk.CTkToplevel):
    def __init__(self, master, use_latex: bool = False):
        super().__init__(master)
        self.title("Agregar expresion LaTeX" if use_latex else "Agregar texto")
        self.geometry("440x300")
        self.resizable(False, False)
        self.grab_set()
        self.result: dict | None = None

        label = "Expresion LaTeX (sin $):" if use_latex else "Texto:"
        ctk.CTkLabel(self, text=label).pack(pady=(16, 4), padx=16, anchor="w")
        self._text = ctk.CTkTextbox(self, height=90)
        self._text.pack(fill="x", padx=16)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(row, text="Tamaño:").pack(side="left")
        self._size_var = ctk.StringVar(value="14")
        ctk.CTkEntry(row, textvariable=self._size_var, width=55).pack(side="left", padx=(4, 16))
        ctk.CTkLabel(row, text="Color (hex):").pack(side="left")
        self._color_var = ctk.StringVar(value="#000000")
        ctk.CTkEntry(row, textvariable=self._color_var, width=90).pack(side="left", padx=4)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=6)
        ctk.CTkButton(btn_row, text="Cancelar", width=100,
                      fg_color="gray", command=self.destroy).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Aceptar", width=100,
                      command=self._accept).pack(side="left", padx=6)

    def _accept(self):
        text = self._text.get("1.0", "end").strip()
        if not text:
            return
        try:
            size = int(self._size_var.get())
        except ValueError:
            size = 14
        self.result = {"text": text, "font_size": size,
                       "color": self._color_var.get() or "#000000"}
        self.destroy()


class CanvasSettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, current_w: int, current_h: int, current_bg: str):
        super().__init__(master)
        self.title("Configurar lienzo")
        self.geometry("380x360")
        self.resizable(False, False)
        self.grab_set()
        self.result: dict | None = None

        ctk.CTkLabel(self, text="Preset de tamaño:").pack(pady=(16, 2), padx=16, anchor="w")
        self._preset_var = ctk.StringVar(value="Personalizado")
        ctk.CTkOptionMenu(self, variable=self._preset_var,
                          values=list(PRESET_PAGES.keys()),
                          command=self._on_preset).pack(padx=16, fill="x")

        ctk.CTkLabel(self, text="Ancho (px):").pack(pady=(10, 2), padx=16, anchor="w")
        self._w_var = ctk.StringVar(value=str(current_w))
        ctk.CTkEntry(self, textvariable=self._w_var).pack(padx=16, fill="x")

        ctk.CTkLabel(self, text="Alto (px):").pack(pady=(6, 2), padx=16, anchor="w")
        self._h_var = ctk.StringVar(value=str(current_h))
        ctk.CTkEntry(self, textvariable=self._h_var).pack(padx=16, fill="x")

        ctk.CTkLabel(self, text="Color de fondo (hex):").pack(pady=(10, 2), padx=16, anchor="w")
        self._bg_var = ctk.StringVar(value=current_bg)
        color_row = ctk.CTkFrame(self, fg_color="transparent")
        color_row.pack(padx=16, fill="x")
        ctk.CTkEntry(color_row, textvariable=self._bg_var).pack(side="left", fill="x", expand=True)
        for color, label in [("#ffffff", "Blanco"), ("#f5f5f5", "Gris claro"),
                             ("#000000", "Negro"), ("#1e1e1e", "Oscuro")]:
            ctk.CTkButton(color_row, text=label, width=68, height=28,
                          command=lambda c=color: self._bg_var.set(c)).pack(side="left", padx=2)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=14)
        ctk.CTkButton(btn_row, text="Cancelar", width=100,
                      fg_color="gray", command=self.destroy).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Aplicar", width=100,
                      command=self._accept).pack(side="left", padx=6)

    def _on_preset(self, choice: str):
        size = PRESET_PAGES.get(choice)
        if size:
            self._w_var.set(str(size[0]))
            self._h_var.set(str(size[1]))

    def _accept(self):
        try:
            w = int(self._w_var.get())
            h = int(self._h_var.get())
        except ValueError:
            return
        self.result = {"w": w, "h": h, "bg": self._bg_var.get() or "#ffffff"}
        self.destroy()


class PreviewDialog(ctk.CTkToplevel):
    def __init__(self, master, composite_image):
        super().__init__(master)
        self.title("Vista previa")
        self.geometry("900x700")

        img = composite_image.copy()
        img.thumbnail((860, 640))
        self._photo = ImageTk.PhotoImage(img)

        ctk.CTkLabel(self, text=f"Tamaño real: {composite_image.width} x {composite_image.height} px",
                     text_color="gray").pack(pady=(10, 4))
        lbl = ctk.CTkLabel(self, image=self._photo, text="")
        lbl.pack(expand=True)
        ctk.CTkButton(self, text="Cerrar", command=self.destroy).pack(pady=10)


class ExportDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Exportar composicion")
        self.geometry("400x360")
        self.resizable(False, False)
        self.grab_set()
        self.result: dict | None = None

        ctk.CTkLabel(self, text="Formato:").pack(pady=(16, 2), padx=16, anchor="w")
        self._preset_var = ctk.StringVar(value=get_preset_names()[0])
        ctk.CTkOptionMenu(self, variable=self._preset_var,
                          values=get_preset_names()).pack(padx=16, fill="x")

        ctk.CTkLabel(self, text="DPI de exportacion:").pack(pady=(10, 2), padx=16, anchor="w")
        self._dpi_var = ctk.StringVar(value="300")
        ctk.CTkEntry(self, textvariable=self._dpi_var).pack(padx=16, fill="x")

        self._page_only_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self, text="Exportar solo area del lienzo",
                        variable=self._page_only_var).pack(padx=16, pady=8, anchor="w")

        ctk.CTkLabel(self, text="Tamaño destino (px) — opcional:",
                     text_color="gray").pack(pady=(4, 2), padx=16, anchor="w")
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=16)
        self._tw_var = ctk.StringVar()
        self._th_var = ctk.StringVar()
        ctk.CTkLabel(row, text="W:").pack(side="left")
        ctk.CTkEntry(row, textvariable=self._tw_var, width=80).pack(side="left", padx=4)
        ctk.CTkLabel(row, text="H:").pack(side="left", padx=(8, 0))
        ctk.CTkEntry(row, textvariable=self._th_var, width=80).pack(side="left", padx=4)

        ctk.CTkLabel(self, text="Si no especificas W/H se exporta al tamaño del canvas.",
                     text_color="gray", font=ctk.CTkFont(size=11),
                     wraplength=350).pack(padx=16, pady=2, anchor="w")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=12)
        ctk.CTkButton(btn_row, text="Cancelar", width=100,
                      fg_color="gray", command=self.destroy).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Exportar", width=100,
                      fg_color="#2d7a2d", command=self._accept).pack(side="left", padx=6)

    def _accept(self):
        try:
            dpi = int(self._dpi_var.get())
        except ValueError:
            dpi = 300
        self.result = {
            "preset": self._preset_var.get(),
            "dpi": dpi,
            "page_only": self._page_only_var.get(),
            "target_w": int(self._tw_var.get()) if self._tw_var.get() else None,
            "target_h": int(self._th_var.get()) if self._th_var.get() else None,
        }
        self.destroy()
