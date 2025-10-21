#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎨 GENERADOR DE FONDO PROFESIONAL PARA DMG
Crea una imagen de fondo estilo institucional HUV para el instalador DMG
Versión: 1.0.0
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ ERROR: PIL (Pillow) no está instalado")
    print("   Solución: pip install Pillow")
    sys.exit(1)


class DMGBackgroundGenerator:
    """Generador de fondo profesional para DMG de macOS"""

    # Dimensiones del fondo (tamaño de ventana del DMG)
    WIDTH = 600
    HEIGHT = 400

    # Colores institucionales HUV (estilo médico profesional)
    COLOR_BACKGROUND = (245, 248, 250)  # Azul muy claro (casi blanco)
    COLOR_HEADER = (41, 128, 185)        # Azul institucional
    COLOR_TEXT_DARK = (44, 62, 80)       # Gris oscuro
    COLOR_TEXT_LIGHT = (127, 140, 141)   # Gris claro
    COLOR_ACCENT = (52, 152, 219)        # Azul brillante
    COLOR_SUCCESS = (46, 204, 113)       # Verde éxito

    # Posiciones de iconos (se coordinarán con create_dmg.sh)
    APP_ICON_X = 140
    APP_ICON_Y = 160
    APPS_FOLDER_X = 460
    APPS_FOLDER_Y = 160

    def __init__(self, output_path):
        """
        Inicializa el generador

        Args:
            output_path: Ruta donde guardar la imagen generada
        """
        self.output_path = Path(output_path)
        self.image = Image.new('RGB', (self.WIDTH, self.HEIGHT), self.COLOR_BACKGROUND)
        self.draw = ImageDraw.Draw(self.image)

    def draw_header(self):
        """Dibuja el encabezado institucional"""
        # Barra superior azul
        self.draw.rectangle(
            [(0, 0), (self.WIDTH, 60)],
            fill=self.COLOR_HEADER
        )

        # Título principal
        try:
            # Intentar usar fuente del sistema
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
            font_subtitle = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        except:
            # Fallback a fuente por defecto
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()

        # Texto del título
        title = "🏥 EVARISIS - Cirugía Oncológica"
        subtitle = "Hospital Universitario del Valle • Cali, Colombia"

        # Centrar título
        title_bbox = self.draw.textbbox((0, 0), title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.WIDTH - title_width) // 2

        self.draw.text(
            (title_x, 15),
            title,
            fill=(255, 255, 255),
            font=font_title
        )

        # Centrar subtítulo
        subtitle_bbox = self.draw.textbbox((0, 0), subtitle, font=font_subtitle)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (self.WIDTH - subtitle_width) // 2

        self.draw.text(
            (subtitle_x, 38),
            subtitle,
            fill=(255, 255, 255, 200),
            font=font_subtitle
        )

    def draw_arrow(self):
        """Dibuja una flecha indicando arrastra aquí"""
        # Flecha desde app hacia Applications
        arrow_y = self.APP_ICON_Y + 60

        # Línea de la flecha
        self.draw.line(
            [(self.APP_ICON_X + 80, arrow_y), (self.APPS_FOLDER_X - 20, arrow_y)],
            fill=self.COLOR_ACCENT,
            width=3
        )

        # Punta de la flecha (triángulo)
        arrow_head = [
            (self.APPS_FOLDER_X - 20, arrow_y),
            (self.APPS_FOLDER_X - 35, arrow_y - 10),
            (self.APPS_FOLDER_X - 35, arrow_y + 10)
        ]
        self.draw.polygon(arrow_head, fill=self.COLOR_ACCENT)

        # Texto sobre la flecha
        try:
            font_arrow = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        except:
            font_arrow = ImageFont.load_default()

        arrow_text = "Arrastra aquí"
        arrow_text_bbox = self.draw.textbbox((0, 0), arrow_text, font=font_arrow)
        arrow_text_width = arrow_text_bbox[2] - arrow_text_bbox[0]
        arrow_text_x = (self.APP_ICON_X + 80 + self.APPS_FOLDER_X - 20) // 2 - arrow_text_width // 2

        self.draw.text(
            (arrow_text_x, arrow_y - 25),
            arrow_text,
            fill=self.COLOR_ACCENT,
            font=font_arrow
        )

    def draw_instructions(self):
        """Dibuja instrucciones de instalación en la parte inferior"""
        try:
            font_inst = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
            font_inst_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
        except:
            font_inst = ImageFont.load_default()
            font_inst_small = ImageFont.load_default()

        # Línea divisoria
        self.draw.line(
            [(30, 280), (self.WIDTH - 30, 280)],
            fill=self.COLOR_TEXT_LIGHT,
            width=1
        )

        # Instrucciones paso a paso
        instructions = [
            "1. Arrastra EVARISIS a la carpeta Applications",
            "2. Abre la aplicación desde Launchpad",
            "3. Si macOS pregunta, haz click derecho → 'Abrir'",
        ]

        y_pos = 295
        for instruction in instructions:
            self.draw.text(
                (40, y_pos),
                instruction,
                fill=self.COLOR_TEXT_DARK,
                font=font_inst_small
            )
            y_pos += 18

        # Nota sobre Tesseract
        note = "✅ Tesseract OCR ya está instalado en este Mac"
        self.draw.text(
            (40, y_pos + 8),
            note,
            fill=self.COLOR_SUCCESS,
            font=font_inst_small
        )

    def draw_version_info(self):
        """Dibuja información de versión en esquina inferior derecha"""
        try:
            font_version = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 9)
        except:
            font_version = ImageFont.load_default()

        # Leer versión desde version_info.py si existe
        version = "v2.1.6"
        version_file = Path(__file__).parent.parent / "config" / "version_info.py"

        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'VERSION = ' in line:
                            version = line.split('"')[1]
                            break
            except:
                pass

        version_text = f"EVARISIS {version} • macOS"

        self.draw.text(
            (self.WIDTH - 140, self.HEIGHT - 20),
            version_text,
            fill=self.COLOR_TEXT_LIGHT,
            font=font_version
        )

    def draw_decorative_elements(self):
        """Dibuja elementos decorativos sutiles"""
        # Círculos decorativos en las esquinas
        decorative_color = (self.COLOR_ACCENT[0], self.COLOR_ACCENT[1], self.COLOR_ACCENT[2], 30)

        # Esquina superior izquierda (muy sutil)
        for i in range(3):
            radius = 50 + (i * 30)
            self.draw.ellipse(
                [(-radius + 30, 60 - radius//2), (radius + 30, 60 + radius//2)],
                outline=self.COLOR_ACCENT,
                width=1
            )

        # Esquina inferior derecha
        for i in range(3):
            radius = 50 + (i * 30)
            self.draw.ellipse(
                [(self.WIDTH - radius - 30, self.HEIGHT - radius + 30),
                 (self.WIDTH + radius - 30, self.HEIGHT + radius + 30)],
                outline=self.COLOR_ACCENT,
                width=1
            )

    def generate(self):
        """Genera la imagen completa"""
        print("🎨 Generando fondo profesional para DMG...")

        # Dibujar todos los elementos en orden
        self.draw_decorative_elements()
        self.draw_header()
        self.draw_arrow()
        self.draw_instructions()
        self.draw_version_info()

        # Guardar la imagen
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(self.output_path, 'PNG')

        # Verificar que se guardó
        if self.output_path.exists():
            size_kb = self.output_path.stat().st_size / 1024
            print(f"✅ Fondo generado exitosamente")
            print(f"   📁 Ubicación: {self.output_path}")
            print(f"   📏 Dimensiones: {self.WIDTH}x{self.HEIGHT}")
            print(f"   💾 Tamaño: {size_kb:.1f} KB")
            return True
        else:
            print(f"❌ Error al guardar la imagen")
            return False


def main():
    """Función principal"""
    print("")
    print("=" * 80)
    print("            🎨 GENERADOR DE FONDO PARA DMG - EVARISIS HUV")
    print("=" * 80)
    print("")

    # Determinar ruta de salida
    script_dir = Path(__file__).parent
    output_dir = script_dir / "imagenes"
    output_file = output_dir / "dmg_background.png"

    # Crear directorio si no existe
    output_dir.mkdir(exist_ok=True)

    # Generar el fondo
    generator = DMGBackgroundGenerator(output_file)
    success = generator.generate()

    if success:
        print("")
        print("=" * 80)
        print("                        ✅ FONDO GENERADO CORRECTAMENTE")
        print("=" * 80)
        print("")
        print("📝 Próximos pasos:")
        print("   1. Revisa el fondo: open imagenes/dmg_background.png")
        print("   2. Si te gusta, ejecuta: ./crear_dmg_visual.sh")
        print("   3. El DMG usará automáticamente este fondo")
        print("")
    else:
        print("")
        print("=" * 80)
        print("                        ❌ ERROR AL GENERAR FONDO")
        print("=" * 80)
        print("")
        sys.exit(1)


if __name__ == "__main__":
    main()
