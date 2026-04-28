# ScienceGraph

Local desktop tool for composing and exporting scientific figures for research articles.
Built with Python — no internet connection required.

---

## What it does

ScienceGraph lets you load scientific images (from MATLAB, Python, or any other tool),
arrange them on a configurable canvas (like a journal page), apply basic edits,
control spacing precisely, and export at publication-ready resolution.

---

## Installation

Requires Python 3.10 or later.

```bash
cd ScienceGraph
pip install -r requirements.txt
python -m src.main
```

> On first run, `matplotlib` will cache fonts. This may take a few extra seconds.

---

## Features

### Canvas (workspace)

| What | How |
|---|---|
| Scroll up / down | Mouse wheel |
| Scroll left / right | Shift + mouse wheel |
| Zoom in / out | Ctrl + mouse wheel |
| Zoom to fit page | Zoom bar → "Ajustar a vista" |
| Set zoom level | Zoom bar dropdown (10 % – 500 %) |
| Select element | Click |
| Move element | Click and drag |
| Resize element | Drag any of the 8 handles on the selection border |
| Multi-select | Shift + click (adds / removes from selection, shown in red) |
| Delete selected | Delete key, or right-click → Eliminar |
| Duplicate | Right-click → Duplicar |
| Bring to front / back | Right-click menu |
| Deselect | Click on empty area |

### Adding content

- **Imagen** — opens a file picker (supports PNG, TIFF, JPEG, BMP, SVG, EPS, PDF).
  Multiple files can be selected at once; each becomes an independent element.
- **Texto** — plain text with configurable font, size, and color.
- **LaTeX** — mathematical expression rendered via matplotlib (write without `$`, e.g. `\frac{a}{b}`).

### Properties panel (right side)

Appears when an element is selected.

| Section | What you can do |
|---|---|
| Nombre | Rename the element |
| Posicion (px) | Set exact X / Y position — press Enter to apply |
| Tamaño (px) | Set exact W / H — press Enter to apply |
| Mantener proporcion | Lock aspect ratio when resizing |
| Escala rapida | Type a percentage (e.g. `50`) and click Aplicar |
| Imagen original | Shows native resolution of the loaded image |
| Borde | Toggle visible border + set border color (hex) |
| Estilo de texto | Shown only for text/LaTeX elements: font family, bold, italic, size, color. Changes re-render the element automatically. |
| Separacion a vecinos | Shown when **Guias** are active. Displays current gap (px) to the nearest element in each direction. Type a new value and press Enter to move the element to that exact distance. |

### Toolbar (left side)

#### Agregar
- **Imagen** — load one or more image files
- **Texto** — add a plain-text element
- **LaTeX** — add a LaTeX-rendered expression

#### Vista
- **Guias OFF / ON** — toggle spacing arrows between elements (shows distances in px)
- **Colision OFF / ON** — when ON, elements cannot overlap each other or leave the page area
- **Preview** — opens a clean preview window (no handles or guides)

#### Lienzo
- **Configurar** — set page width, height (px), and background color.
  Presets available: A4, Letter, single/double journal column, HD 1080p, custom.

#### Edicion
- **Copiar estilo** — copies font, color, border settings from the selected element
- **Pegar estilo** — applies copied style to the selected element (re-renders text elements)
- **Distribuir** — distributes selected elements (Shift+click to pick them) with a uniform gap.
  Modes: horizontal, vertical, grid. If elements reach the page boundary they are placed as close as possible.

#### Archivo
- **Exportar** — opens the export dialog

### Export dialog

| Setting | Description |
|---|---|
| Formato | TIFF uncompressed, TIFF LZW, PNG, JPEG (various quality), PDF, EPS |
| DPI | Resolution for the exported file (default 300) |
| Exportar solo area del lienzo | Crops output to the page rectangle |
| Tamaño destino (px) | Optional override of output pixel dimensions |

---

## Supported input formats

| Format | Notes |
|---|---|
| PNG | Full transparency support |
| TIFF / TIF | Scientific TIFF with high bit-depth (16/32-bit auto-normalized) |
| JPEG / JPG | Standard photos |
| BMP | Basic bitmap |
| SVG | Rendered via cairosvg at 300 DPI |
| EPS / PDF | Opened via Pillow (requires Ghostscript for EPS) |

---

## Keyboard shortcuts

| Key | Action |
|---|---|
| Delete | Delete selected element(s) |
| Ctrl + Scroll Up | Zoom in |
| Ctrl + Scroll Down | Zoom out |
| Scroll Up/Down | Scroll canvas vertically |
| Shift + Scroll | Scroll canvas horizontally |
| Shift + Click | Add / remove element from multi-selection |

---

## Project structure

```
ScienceGraph/
├── src/
│   ├── core/
│   │   ├── element.py          # Element data model
│   │   ├── image_loader.py     # Multi-format image loading
│   │   ├── image_editor.py     # Crop, rotate, flip, brightness, contrast
│   │   ├── exporter.py         # Export presets (TIFF, PNG, JPEG, PDF, EPS)
│   │   ├── spacing.py          # Nearest-gap calculator between elements
│   │   └── latex_renderer.py   # LaTeX and text rendering via matplotlib / Pillow
│   ├── gui/
│   │   ├── app.py              # Main application window
│   │   ├── canvas_workspace.py # Interactive canvas (zoom, drag, resize, spacing)
│   │   ├── toolbar.py          # Left toolbar
│   │   ├── properties.py       # Right properties panel
│   │   └── dialogs.py          # Text, LaTeX, canvas settings, distribute, export dialogs
│   └── main.py                 # Entry point
├── tests/
├── samples/                    # Place test images here
└── requirements.txt
```

---

## Requirements

```
Pillow >= 10.0
customtkinter >= 5.2
tifffile >= 2023.1
matplotlib >= 3.7
cairosvg >= 2.7
numpy >= 1.24
```

> `rawpy` is listed in requirements but optional (for RAW camera files).
> `cairosvg` requires the Cairo graphics library. On Windows install it via the
> [GTK for Windows Runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases).
