# -*- coding: utf-8 -*-
"""
Generador del logo institucional ONCONOVA - Cirugia Oncologica
Hospital Universitario del Valle

Concepto "Nucleo Inteligente Oncologico":
  - Hexagono (celula / biomarcador / patologia molecular) con gradiente azul HUV
  - Linea de pulso ECG (salud, signos vitales, monitoreo del cancer)
  - Nodos de red neuronal (IA que analiza los datos)
  - Wordmark ONCONOVA + tagline institucional

Render con supersampling (SS=4) para bordes nitidos.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SS = 4  # supersampling
# Carpeta de salida = imagenes/branding (un nivel arriba de este generador).
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(OUT, exist_ok=True)

FONTS = r"C:\Windows\Fonts"

# ----------------------- Paleta institucional -----------------------
NAVY_DEEP = (20, 38, 66)      # #142642 fondo profundo
NAVY      = (45, 62, 94)      # #2D3E5E institucional exacto
BLUE      = (43, 108, 176)    # #2B6CB0 azul HUV
BLUE_BR   = (46, 134, 222)    # #2E86DE azul brillante
CYAN      = (46, 200, 235)    # #2EC8EB acento tech
CYAN_BR   = (120, 220, 250)   # cyan claro glow
WHITE     = (255, 255, 255)
INK       = (37, 49, 71)      # texto sobre fondo claro (navy ink)
MUTED     = (90, 105, 130)    # texto secundario claro


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


# ----------------------- Helpers de dibujo -----------------------
def diagonal_gradient(size, stops):
    """Gradiente diagonal (esq sup-izq -> inf-der). stops=[(pos,color),...]."""
    w, h = size
    base = Image.new("RGB", size)
    px = base.load()
    maxd = (w - 1) + (h - 1)
    # precompute lookup along diagonal param t in [0,1]
    def color_at(t):
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                tt = (t - p0) / (p1 - p0) if p1 > p0 else 0
                return lerp(c0, c1, tt)
        return stops[-1][1]
    # build per-diagonal-line color cache
    cache = [color_at(d / maxd) for d in range(maxd + 1)]
    for y in range(h):
        for x in range(w):
            px[x, y] = cache[x + y]
    return base


def hexagon_points(cx, cy, R, flat_top=True):
    pts = []
    for k in range(6):
        ang = math.radians(60 * k + (0 if flat_top else 30))
        pts.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))
    return pts


def rounded_mask(size, points, corner):
    """Mascara L con poligono de esquinas redondeadas (blur+threshold)."""
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(points, fill=255)
    if corner > 0:
        m = m.filter(ImageFilter.GaussianBlur(corner))
        m = m.point(lambda v: 255 if v >= 140 else 0)
    return m


def draw_text_tracked(draw, xy, text, fnt, fill, tracking=0, anchor_center=False):
    """Dibuja texto con letter-spacing. Devuelve ancho total."""
    x, y = xy
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if anchor_center:
        x = x - total / 2
    cx = x
    for ch, w in zip(text, widths):
        draw.text((cx, y), ch, font=fnt, fill=fill)
        cx += w + tracking
    return total


def measure_tracked(draw, text, fnt, tracking=0):
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    return sum(widths) + tracking * (len(text) - 1)


# ----------------------- Isotipo (simbolo) -----------------------
def build_isotipo(box=512, with_glow=False, transparent=True, bg=None):
    """Construye el isotipo en una imagen RGBA de box*SS y la devuelve (sin reducir)."""
    S = box * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0) if transparent else bg + (255,))

    cx = cy = S / 2
    R = S * 0.43            # radio hexagono
    pts = hexagon_points(cx, cy, R, flat_top=True)

    # --- relleno hexagono con gradiente ---
    grad = diagonal_gradient((S, S), [
        (0.0, NAVY_DEEP),
        (0.45, BLUE),
        (1.0, CYAN),
    ]).convert("RGBA")
    corner = R * 0.16
    mask_fill = rounded_mask((S, S), pts, corner)

    # sombra suave detras (solo si hay fondo)
    if not transparent:
        shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        off = int(S * 0.012)
        smask = mask_fill.filter(ImageFilter.GaussianBlur(S * 0.03))
        shimg = Image.new("RGBA", (S, S), (0, 0, 0, 90))
        img.paste(Image.new("RGBA", (S, S), (0, 0, 0, 0)), (0, 0))
        tmp = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        tmp.paste(shimg, (0, off), smask)
        img = Image.alpha_composite(img, tmp)

    # glow exterior (version oscura)
    if with_glow:
        glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        gmask = mask_fill.filter(ImageFilter.GaussianBlur(S * 0.05))
        gcol = Image.new("RGBA", (S, S), CYAN + (140,))
        glow.paste(gcol, (0, 0), gmask)
        img = Image.alpha_composite(img, glow)

    # pega gradiente con mascara
    img.paste(grad, (0, 0), mask_fill)

    # --- borde interior luminoso (anillo) ---
    inner = rounded_mask((S, S), hexagon_points(cx, cy, R * 0.985, True), corner * 0.95)
    inner_er = rounded_mask((S, S), hexagon_points(cx, cy, R * 0.90, True), corner * 0.9)
    ring = Image.new("L", (S, S), 0)
    ring.paste(inner)
    ring.paste(Image.new("L", (S, S), 0), (0, 0), inner_er)
    ring_col = Image.new("RGBA", (S, S), CYAN_BR + (120,))
    img.paste(ring_col, (0, 0), ring)

    draw = ImageDraw.Draw(img)

    def stroke_poly(points, w, col):
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=col, width=w)
        r = w / 2
        for p in points:
            draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)

    # --- linea ECG / pulso: entra desde la izquierda hacia el nucleo ---
    ecg_w = int(S * 0.026)
    baseY = cy
    amp = R * 0.36
    cxn = cx + R * 0.14            # x del nucleo (neurona)
    ecg = [
        (cx - R * 0.72, baseY),
        (cx - R * 0.42, baseY),
        (cx - R * 0.32, baseY + amp * 0.26),   # leve descenso (Q)
        (cx - R * 0.215, baseY - amp),         # pico R
        (cx - R * 0.11, baseY + amp * 0.52),   # onda S
        (cx - R * 0.02, baseY),
        (cxn, baseY),                          # entra al nucleo
    ]
    stroke_poly(ecg, ecg_w, WHITE)

    # --- neurona: nucleo central + dendritas hacia nodos secundarios (IA) ---
    core = (cxn, baseY, S * 0.032)
    sec = [
        (cx + R * 0.47, cy - R * 0.31, S * 0.019),
        (cx + R * 0.58, cy + R * 0.02, S * 0.021),
        (cx + R * 0.45, cy + R * 0.33, S * 0.019),
    ]
    branch_w = int(S * 0.014)
    for (x, y, rr) in sec:
        draw.line([(core[0], core[1]), (x, y)], fill=WHITE, width=branch_w)
    # arista que cierra la red (da sensacion de "grafo")
    draw.line([(sec[0][0], sec[0][1]), (sec[1][0], sec[1][1])], fill=WHITE + (160,), width=int(branch_w * 0.7))
    draw.line([(sec[1][0], sec[1][1]), (sec[2][0], sec[2][1])], fill=WHITE + (160,), width=int(branch_w * 0.7))

    # nodos secundarios (halo cyan + nucleo blanco)
    for (x, y, rr) in sec:
        draw.ellipse([x - rr * 1.9, y - rr * 1.9, x + rr * 1.9, y + rr * 1.9], fill=CYAN_BR + (70,))
        draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=WHITE)
    # nucleo principal con halo
    x, y, rr = core
    draw.ellipse([x - rr * 2.1, y - rr * 2.1, x + rr * 2.1, y + rr * 2.1], fill=CYAN_BR + (95,))
    draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=WHITE)

    return img


# ----------------------- Lockups -----------------------
def build_lockup(dark=False, box_w=1600, box_h=540):
    S = SS
    W, H = box_w * S, box_h * S
    if dark:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    else:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # isotipo a la izquierda
    iso_box = box_h - 40
    iso = build_isotipo(box=iso_box, with_glow=dark, transparent=True)
    iso = iso.resize((iso_box * S, iso_box * S), Image.LANCZOS)
    iso_y = (H - iso_box * S) // 2
    iso_x = int(20 * S)
    img.alpha_composite(iso, (iso_x, iso_y))

    # textos
    tx = iso_x + iso_box * S + int(60 * S)
    word_col = WHITE if dark else INK
    sub_col = CYAN_BR if dark else BLUE
    tag_col = (200, 215, 235) if dark else MUTED

    f_word = font("segoeuib.ttf", int(150 * S))
    f_sub  = font("segoeuisl.ttf", int(40 * S))
    f_tag  = font("segoeui.ttf", int(33 * S))

    # bloque vertical centrado
    tr_word = int(14 * S)
    tr_sub = int(10 * S)
    h_word = 150 * S
    h_sub = 40 * S
    h_tag = 33 * S
    gap1 = int(20 * S)
    gap2 = int(14 * S)
    total_h = h_word + gap1 + h_sub + gap2 + h_tag
    ty = (H - total_h) // 2 - int(18 * S)

    draw_text_tracked(draw, (tx, ty), "ONCONOVA", f_word, word_col, tracking=tr_word)
    y2 = ty + h_word + gap1
    draw_text_tracked(draw, (tx + int(3 * S), y2), "GESTIÓN ONCOLÓGICA INTELIGENTE",
                      f_sub, sub_col, tracking=tr_sub)
    y3 = y2 + h_sub + gap2
    draw.text((tx + int(3 * S), y3), "Hospital Universitario del Valle  ·  Evaristo García E.S.E.",
              font=f_tag, fill=tag_col)

    return img


# ----------------------- App icon (rounded square) -----------------------
def build_app_icon(box=512):
    S = box * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    # fondo navy con gradiente sutil + esquinas redondeadas estilo iOS
    bg = diagonal_gradient((S, S), [(0.0, NAVY_DEEP), (1.0, NAVY)]).convert("RGBA")
    radius = int(S * 0.22)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=radius, fill=255)
    img.paste(bg, (0, 0), mask)

    # patron de circuito tenue
    draw = ImageDraw.Draw(img)
    # isotipo centrado, con glow
    iso = build_isotipo(box=int(box * 0.78), with_glow=True, transparent=True)
    isoS = int(box * 0.78) * SS
    iso = iso.resize((isoS, isoS), Image.LANCZOS)
    off = (S - isoS) // 2
    img.alpha_composite(iso, (off, off))

    # recortar a la mascara redondeada final
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def build_lockup_vertical(dark=False, box=900):
    S = SS
    W, H = box * S, int(box * 0.92) * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    iso_box = int(box * 0.46)
    iso = build_isotipo(box=iso_box, with_glow=dark, transparent=True)
    iso = iso.resize((iso_box * S, iso_box * S), Image.LANCZOS)
    iso_x = (W - iso_box * S) // 2
    iso_y = int(20 * S)
    img.alpha_composite(iso, (iso_x, iso_y))

    word_col = WHITE if dark else INK
    sub_col = CYAN_BR if dark else BLUE
    tag_col = (200, 215, 235) if dark else MUTED

    f_word = font("segoeuib.ttf", int(132 * S))
    f_sub = font("segoeuisl.ttf", int(34 * S))
    f_tag = font("segoeui.ttf", int(28 * S))

    cxw = W / 2
    yw = iso_y + iso_box * S + int(34 * S)
    draw_text_tracked(draw, (cxw, yw), "ONCONOVA", f_word, word_col,
                      tracking=int(12 * S), anchor_center=True)
    ys = yw + int(132 * S) + int(20 * S)
    draw_text_tracked(draw, (cxw, ys), "GESTIÓN ONCOLÓGICA INTELIGENTE", f_sub, sub_col,
                      tracking=int(9 * S), anchor_center=True)
    yt = ys + int(34 * S) + int(12 * S)
    tagw = draw.textlength("Hospital Universitario del Valle  ·  Evaristo García E.S.E.", font=f_tag)
    draw.text((cxw - tagw / 2, yt), "Hospital Universitario del Valle  ·  Evaristo García E.S.E.",
              font=f_tag, fill=tag_col)
    return img


def _hx(c):
    return "#%02X%02X%02X" % c


def generar_svg_isotipo():
    """SVG vectorial exacto del isotipo (viewBox 512). Sin texto -> 100% portable."""
    cx = cy = 256.0
    R = 512 * 0.43
    d = R * 0.16

    def unit(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        return (dx / L, dy / L)

    pts = hexagon_points(cx, cy, R, True)
    n = len(pts)
    segs = []
    for i in range(n):
        V = pts[i]; P = pts[(i - 1) % n]; N = pts[(i + 1) % n]
        uP = unit(V, P); uN = unit(V, N)
        entry = (V[0] + uP[0] * d, V[1] + uP[1] * d)
        ex = (V[0] + uN[0] * d, V[1] + uN[1] * d)
        segs.append((entry, V, ex))
    hexpath = f"M {segs[0][2][0]:.2f},{segs[0][2][1]:.2f} "
    for i in range(1, n + 1):
        e, V, x = segs[i % n]
        hexpath += f"L {e[0]:.2f},{e[1]:.2f} Q {V[0]:.2f},{V[1]:.2f} {x[0]:.2f},{x[1]:.2f} "
    hexpath += "Z"

    amp = R * 0.36
    cxn = cx + R * 0.14
    ecg = [
        (cx - R * 0.72, cy), (cx - R * 0.42, cy),
        (cx - R * 0.32, cy + amp * 0.26), (cx - R * 0.215, cy - amp),
        (cx - R * 0.11, cy + amp * 0.52), (cx - R * 0.02, cy), (cxn, cy),
    ]
    ecg_pts = " ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in ecg)

    core = (cxn, cy, 512 * 0.032)
    sec = [
        (cx + R * 0.47, cy - R * 0.31, 512 * 0.019),
        (cx + R * 0.58, cy + R * 0.02, 512 * 0.021),
        (cx + R * 0.45, cy + R * 0.33, 512 * 0.019),
    ]
    bw = 512 * 0.014
    ew = 512 * 0.026

    branches = "".join(
        f'<line x1="{core[0]:.2f}" y1="{core[1]:.2f}" x2="{s[0]:.2f}" y2="{s[1]:.2f}" '
        f'stroke="#FFFFFF" stroke-width="{bw:.2f}" stroke-linecap="round"/>\n    '
        for s in sec)
    branches += (
        f'<line x1="{sec[0][0]:.2f}" y1="{sec[0][1]:.2f}" x2="{sec[1][0]:.2f}" y2="{sec[1][1]:.2f}" '
        f'stroke="#FFFFFF" stroke-width="{bw*0.7:.2f}" stroke-linecap="round" opacity="0.62"/>\n    '
        f'<line x1="{sec[1][0]:.2f}" y1="{sec[1][1]:.2f}" x2="{sec[2][0]:.2f}" y2="{sec[2][1]:.2f}" '
        f'stroke="#FFFFFF" stroke-width="{bw*0.7:.2f}" stroke-linecap="round" opacity="0.62"/>\n    ')

    nodes = ""
    for s in sec:
        nodes += (f'<circle cx="{s[0]:.2f}" cy="{s[1]:.2f}" r="{s[2]*1.9:.2f}" fill="{_hx(CYAN_BR)}" opacity="0.30"/>\n    '
                  f'<circle cx="{s[0]:.2f}" cy="{s[1]:.2f}" r="{s[2]:.2f}" fill="#FFFFFF"/>\n    ')
    nodes += (f'<circle cx="{core[0]:.2f}" cy="{core[1]:.2f}" r="{core[2]*2.0:.2f}" fill="{_hx(CYAN_BR)}" opacity="0.35"/>\n    '
              f'<circle cx="{core[0]:.2f}" cy="{core[1]:.2f}" r="{core[2]:.2f}" fill="#FFFFFF"/>')

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="hexgrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{_hx(NAVY_DEEP)}"/>
      <stop offset="45%" stop-color="{_hx(BLUE)}"/>
      <stop offset="100%" stop-color="{_hx(CYAN)}"/>
    </linearGradient>
  </defs>
  <g>
    <path d="{hexpath}" fill="url(#hexgrad)" stroke="{_hx(CYAN_BR)}" stroke-width="4" stroke-linejoin="round" opacity="1"/>
    <polyline points="{ecg_pts}" fill="none" stroke="#FFFFFF" stroke-width="{ew:.2f}" stroke-linecap="round" stroke-linejoin="round"/>
    {branches}{nodes}
  </g>
</svg>'''
    path = os.path.join(OUT, "onconova_isotipo.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("OK onconova_isotipo.svg")


def save(img, name, box):
    final = img.resize((box, int(box * img.height / img.width)), Image.LANCZOS)
    path = os.path.join(OUT, name)
    final.save(path)
    print("OK", name, final.size)
    return path


if __name__ == "__main__":
    # Isotipo transparente
    iso = build_isotipo(box=1024, with_glow=False, transparent=True)
    save(iso, "onconova_isotipo.png", 1024)

    # Lockup claro
    lk = build_lockup(dark=False)
    save(lk, "onconova_logo_horizontal.png", 1600)

    # Lockup oscuro
    lkd = build_lockup(dark=True)
    save(lkd, "onconova_logo_horizontal_dark.png", 1600)

    # App icon
    ic = build_app_icon(box=512)
    save(ic, "onconova_icono_app.png", 1024)

    # Lockup vertical
    lv = build_lockup_vertical(dark=False)
    save(lv, "onconova_logo_vertical.png", 900)
    lvd = build_lockup_vertical(dark=True)
    save(lvd, "onconova_logo_vertical_dark.png", 900)

    # ICO multi-resolucion para el ejecutable / ventana de la app
    ico_src = ic.resize((256, 256), Image.LANCZOS)
    ico_path = os.path.join(OUT, "onconova.ico")
    ico_src.save(ico_path, format="ICO",
                 sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("OK onconova.ico")
    # favicons PNG
    save(ic, "onconova_favicon_64.png", 64)
    save(iso, "onconova_isotipo_256.png", 256)

    # SVG vectorial (master escalable)
    generar_svg_isotipo()

    # ---------------- Lamina de marca (brand sheet) ----------------
    W, H = 1700, 1420
    sheet = Image.new("RGB", (W, H), (247, 249, 252))
    sd = ImageDraw.Draw(sheet)
    f_h = font("segoeuib.ttf", 30)
    f_lbl = font("segoeuisl.ttf", 22)
    f_hex = font("segoeui.ttf", 20)

    sd.text((60, 48), "ONCONOVA  ·  Sistema de Identidad Visual", font=f_h, fill=INK)
    sd.line([(60, 96), (W - 60, 96)], fill=(220, 226, 234), width=2)

    # logo horizontal claro
    lk_r = lk.resize((980, int(980 * lk.height / lk.width)), Image.LANCZOS)
    sheet.paste(lk_r, (50, 130), lk_r)
    # isotipo + app icon + favicon a la derecha
    sheet.paste(iso.resize((230, 230), Image.LANCZOS), (1120, 150), iso.resize((230, 230), Image.LANCZOS))
    sd.text((1175, 388), "isotipo", font=f_lbl, fill=MUTED)
    sheet.paste(ic.resize((150, 150), Image.LANCZOS), (1380, 150), ic.resize((150, 150), Image.LANCZOS))
    sheet.paste(ic.resize((72, 72), Image.LANCZOS), (1420, 310), ic.resize((72, 72), Image.LANCZOS))
    sd.text((1400, 388), "app / icono", font=f_lbl, fill=MUTED)

    # banda oscura
    by0 = 470
    band = Image.new("RGB", (W - 120, 360), NAVY_DEEP)
    bmask = Image.new("L", (W - 120, 360), 0)
    ImageDraw.Draw(bmask).rounded_rectangle([0, 0, W - 121, 359], radius=24, fill=255)
    sheet.paste(band, (60, by0), bmask)
    lkd_r = lkd.resize((900, int(900 * lkd.height / lkd.width)), Image.LANCZOS)
    sheet.paste(lkd_r, (120, by0 + 60), lkd_r)
    iso_g = build_isotipo(box=240, with_glow=True).resize((240, 240), Image.LANCZOS)
    sheet.paste(iso_g, (1320, by0 + 60), iso_g)

    # paleta de colores
    py0 = 900
    sd.text((60, py0), "Paleta institucional", font=font("segoeuib.ttf", 26), fill=INK)
    swatches = [
        ("Navy profundo", NAVY_DEEP, "#142642"),
        ("Navy HUV", NAVY, "#2D3E5E"),
        ("Azul HUV", BLUE, "#2B6CB0"),
        ("Azul brillante", BLUE_BR, "#2E86DE"),
        ("Cyan tech", CYAN, "#2EC8EB"),
    ]
    sx = 60
    for nm, col, hx in swatches:
        sw = Image.new("RGB", (290, 150), col)
        swm = Image.new("L", (290, 150), 0)
        ImageDraw.Draw(swm).rounded_rectangle([0, 0, 289, 149], radius=16, fill=255)
        sheet.paste(sw, (sx, py0 + 50), swm)
        tc = WHITE if col != CYAN else INK
        sd.text((sx + 18, py0 + 130), nm, font=f_lbl, fill=tc)
        sd.text((sx + 18, py0 + 162), hx, font=f_hex, fill=tc)
        sx += 312

    sd.text((60, py0 + 230),
            "Significado:  hexágono = célula / biomarcador (patología molecular)   ·   pulso ECG = salud y monitoreo oncológico   ·   red neuronal = IA que analiza los datos",
            font=f_hex, fill=MUTED)
    sheet.save(os.path.join(OUT, "onconova_muestra_marca.png"))
    print("OK muestra de marca")
