import customtkinter as ctk
from PIL import Image, ImageTk


class ImageViewer(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._photo = None
        self._label = ctk.CTkLabel(self, text="Arrastra o abre una imagen", text_color="gray")
        self._label.pack(expand=True, fill="both")

    def show(self, img: Image.Image):
        display = img.copy()
        display.thumbnail((700, 600))
        self._photo = ImageTk.PhotoImage(display)
        self._label.configure(image=self._photo, text="")

    def clear(self):
        self._photo = None
        self._label.configure(image=None, text="Arrastra o abre una imagen")
