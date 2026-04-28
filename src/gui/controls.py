import customtkinter as ctk
from src.core.exporter import get_preset_names


class ControlPanel(ctk.CTkFrame):
    def __init__(self, master, on_open, on_export, on_rotate, on_flip_h, on_flip_v,
                 on_brightness, on_contrast, **kwargs):
        super().__init__(master, **kwargs)

        ctk.CTkButton(self, text="Abrir imagen", command=on_open).pack(pady=(12, 4), padx=12, fill="x")

        ctk.CTkLabel(self, text="Rotacion").pack(pady=(10, 0))
        self._rotate_var = ctk.DoubleVar(value=0)
        ctk.CTkSlider(self, from_=-180, to=180, variable=self._rotate_var,
                      command=lambda v: on_rotate(float(v))).pack(padx=12, fill="x")

        ctk.CTkLabel(self, text="Brillo").pack(pady=(10, 0))
        self._brightness_var = ctk.DoubleVar(value=1.0)
        ctk.CTkSlider(self, from_=0.1, to=3.0, variable=self._brightness_var,
                      command=lambda v: on_brightness(float(v))).pack(padx=12, fill="x")

        ctk.CTkLabel(self, text="Contraste").pack(pady=(10, 0))
        self._contrast_var = ctk.DoubleVar(value=1.0)
        ctk.CTkSlider(self, from_=0.1, to=3.0, variable=self._contrast_var,
                      command=lambda v: on_contrast(float(v))).pack(padx=12, fill="x")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=8, padx=12, fill="x")
        ctk.CTkButton(btn_frame, text="Voltear H", command=on_flip_h).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(btn_frame, text="Voltear V", command=on_flip_v).pack(side="left", expand=True, padx=2)

        ctk.CTkLabel(self, text="Formato de exportacion").pack(pady=(12, 0))
        self._preset_var = ctk.StringVar(value=get_preset_names()[0])
        ctk.CTkOptionMenu(self, variable=self._preset_var, values=get_preset_names()).pack(padx=12, fill="x")

        ctk.CTkLabel(self, text="DPI").pack(pady=(8, 0))
        self._dpi_var = ctk.StringVar(value="300")
        ctk.CTkEntry(self, textvariable=self._dpi_var).pack(padx=12, fill="x")

        ctk.CTkButton(self, text="Exportar", fg_color="#2d7a2d",
                      command=lambda: on_export(self._preset_var.get(), int(self._dpi_var.get()))
                      ).pack(pady=12, padx=12, fill="x")

    @property
    def preset(self) -> str:
        return self._preset_var.get()

    @property
    def dpi(self) -> int:
        return int(self._dpi_var.get())
