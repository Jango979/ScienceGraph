import customtkinter as ctk


class Toolbar(ctk.CTkFrame):
    def __init__(self, master, on_add_image, on_add_text, on_add_latex,
                 on_toggle_spacing, on_toggle_collision, on_canvas_settings,
                 on_preview, on_copy_style, on_paste_style, on_export, **kwargs):
        super().__init__(master, width=104, **kwargs)
        self._spacing_btn: ctk.CTkButton | None = None
        self._collision_btn: ctk.CTkButton | None = None
        self._build(on_add_image, on_add_text, on_add_latex,
                    on_toggle_spacing, on_toggle_collision, on_canvas_settings,
                    on_preview, on_copy_style, on_paste_style, on_export)

    def _build(self, on_add_image, on_add_text, on_add_latex,
               on_toggle_spacing, on_toggle_collision, on_canvas_settings,
               on_preview, on_copy_style, on_paste_style, on_export):
        self._section("Agregar")
        self._btn("Imagen", on_add_image)
        self._btn("Texto", on_add_text)
        self._btn("LaTeX", on_add_latex)

        self._section("Vista")
        self._spacing_btn = self._btn("Guias OFF", on_toggle_spacing, ret=True)
        self._collision_btn = self._btn("Colision OFF", on_toggle_collision, ret=True)
        self._btn("Preview", on_preview)

        self._section("Lienzo")
        self._btn("Configurar", on_canvas_settings)

        self._section("Estilo")
        self._btn("Copiar\nestilo", on_copy_style)
        self._btn("Pegar\nestilo", on_paste_style)

        self._section("Archivo")
        self._btn("Exportar", on_export, color="#2d7a2d")

    def _section(self, label: str):
        ctk.CTkLabel(self, text=label, text_color="gray",
                     font=ctk.CTkFont(size=10)).pack(pady=(10, 2))

    def _btn(self, text: str, cmd, color=None, ret=False) -> ctk.CTkButton | None:
        kw = {"text": text, "command": cmd, "width": 92, "height": 32}
        if color:
            kw["fg_color"] = color
        b = ctk.CTkButton(self, **kw)
        b.pack(pady=2, padx=6)
        return b if ret else None

    def set_spacing_state(self, active: bool):
        if self._spacing_btn:
            self._spacing_btn.configure(
                text="Guias ON" if active else "Guias OFF",
                fg_color="#b36b00" if active else ["#3B8ED0", "#1F6AA5"],
            )

    def set_collision_state(self, active: bool):
        if self._collision_btn:
            self._collision_btn.configure(
                text="Colision ON" if active else "Colision OFF",
                fg_color="#7a2d7a" if active else ["#3B8ED0", "#1F6AA5"],
            )
