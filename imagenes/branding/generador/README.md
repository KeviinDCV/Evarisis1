# Generador del logo ONCONOVA

Scripts que producen **todos los activos de marca** en `imagenes/branding/`.
Concepto *"Núcleo Inteligente Oncológico"*: hexágono (célula/biomarcador) + pulso
ECG (salud/monitoreo oncológico) + red neuronal (IA), en azul institucional HUV.

## Requisitos
- **Python 3.10+** con **Pillow**: `pip install pillow`
- Fuente **Segoe UI** (incluida en Windows). En otros SO, ajustar la constante `FONTS`.
- *(Opcional, solo para previsualizar el SVG)* **Node.js** + `@resvg/resvg-js`:
  `npm install @resvg/resvg-js`

## Uso
```bash
# Genera PNG (isotipo, lockups, app icon, favicons), .ico y .svg + lámina de marca
python gen_logo.py

# (Opcional) Renderiza el SVG del isotipo a PNG para verificación
node render_svg.js
```
Los archivos se escriben en `imagenes/branding/` (un nivel arriba de esta carpeta).

## Personalización rápida (en `gen_logo.py`)
- **Paleta:** constantes `NAVY_DEEP`, `NAVY`, `BLUE`, `BLUE_BR`, `CYAN` (líneas ~25-30).
- **Texto:** wordmark `"ONCONOVA"` y tagline en `build_lockup()` / `build_lockup_vertical()`.
- **Símbolo:** geometría del hexágono, ECG y red neuronal en `build_isotipo()`.

## Salidas (en `imagenes/branding/`)
| Archivo | Uso |
|---|---|
| `onconova_logo_horizontal.png` / `_dark.png` | Logo principal (fondo claro / oscuro) |
| `onconova_logo_vertical.png` / `_dark.png` | Versión apilada |
| `onconova_isotipo.png` / `_256.png` / `.svg` | Solo símbolo (PNG y vectorial) |
| `onconova_icono_app.png` | Ícono estilo app (fondo navy) |
| `onconova_favicon_64.png` | Favicon |
| `onconova.ico` | Multi-resolución para el ejecutable/ventana |
| `onconova_muestra_marca.png` | Lámina resumen de identidad |
