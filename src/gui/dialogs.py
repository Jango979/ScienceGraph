import customtkinter as ctk
from src.core.exporter import get_preset_names


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
        self.result = {
            "text": text,
            "font_size": size,
            "color": self._color_var.get() or "#000000",
        }
        self.destroy()


class ExportDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Exportar composicion")
        self.geometry("380x320")
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

        ctk.CTkLabel(self, text="Tamaño destino (px) — opcional:",
                     text_color="gray").pack(pady=(10, 2), padx=16, anchor="w")
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=16)
        self._tw_var = ctk.StringVar()
        self._th_var = ctk.StringVar()
        ctk.CTkLabel(row, text="W:").pack(side="left")
        ctk.CTkEntry(row, textvariable=self._tw_var, width=80).pack(side="left", padx=4)
        ctk.CTkLabel(row, text="H:").pack(side="left", padx=(8, 0))
        ctk.CTkEntry(row, textvariable=self._th_var, width=80).pack(side="left", padx=4)

        note = ctk.CTkLabel(self, text="Si no especificas W/H se usa el tamaño del canvas",
                            text_color="gray", font=ctk.CTkFont(size=11))
        note.pack(padx=16, pady=2, anchor="w")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=10)
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
            "target_w": int(self._tw_var.get()) if self._tw_var.get() else None,
            "target_h": int(self._th_var.get()) if self._th_var.get() else None,
        }
        self.destroy()
