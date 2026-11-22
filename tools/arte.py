#!/usr/bin/env python3
"""Convierte el arte generado (Trabajo KM/raw/*.png) en los archivos del módulo:
figuras de cuerpo entero, fichas redondas, retratos, escenas 16:9 con miniatura, planos con sus zonas, iconos de objeto
(recortados de las hojas de 3×3) y ayudas de juego (las Listas de Muerte escritas a mano y el Sobre Rojo). Todo con la marca MR (regla de la casa).
Uso: python3 tools/arte.py [grupo ...]   grupos: personajes escenas iconos ayudas ui   (sin nada: todos)"""
import random, shutil, sys, textwrap
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

R = Path(__file__).resolve().parent.parent
TR = Path("/Volumes/Datos_Dock/FoundryVTT/Trabajo KM")
RAW, REF, A = TR / "raw", TR / "ref", R / "assets"
FUENTES = A / "fonts"
sys.path.insert(0, "/Volumes/Datos_Dock/FoundryVTT/Trabajo LOGO/marca")
sys.path.insert(0, str(R / "texto"))
import marca  # noqa: E402
import datos as D  # noqa: E402

PAPEL, TINTA, AMARILLO, ROJO = (246, 241, 227), (18, 18, 18), (245, 197, 24), (200, 16, 46)


def guarda(im, ruta, q=86):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    im.save(ruta, "WEBP", quality=q, method=6)
    return ruta


def alfa_bbox(im, umbral=14):
    return im.getchannel("A").point(lambda v: 255 if v > umbral else 0).getbbox()


def recorta_alfa(im, margen=0.03):
    bb = alfa_bbox(im)
    if not bb:
        return im
    im = im.crop(bb)
    m = int(max(im.size) * margen)
    out = Image.new("RGBA", (im.width + 2 * m, im.height + 2 * m), (0, 0, 0, 0))
    out.paste(im, (m, m))
    return out


def encaja(im, w, h, fondo=(0, 0, 0, 0)):
    im = im.copy()
    im.thumbnail((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), fondo)
    out.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    return out


def sin_fondo(im):
    """Codex a veces devuelve fondo opaco aunque se pida alfa: se quita por relleno desde las cuatro esquinas."""
    im = im.convert("RGBA")
    if im.getchannel("A").getextrema()[0] < 250:
        return im
    rgb = im.convert("RGB")
    w, h = rgb.size
    clave = (255, 0, 255)
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(rgb, p, clave, thresh=38)
    r, g, b = rgb.split()
    es_clave = Image.eval(r, lambda v: 255 if v == 255 else 0)
    es_clave = Image.composite(es_clave, Image.new("L", rgb.size, 0), Image.eval(g, lambda v: 255 if v == 0 else 0))
    es_clave = Image.composite(es_clave, Image.new("L", rgb.size, 0), Image.eval(b, lambda v: 255 if v == 255 else 0))
    mascara = ImageOps.invert(es_clave).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
    im.putalpha(mascara)
    print("  (fondo opaco quitado)")
    return im


# ------------------------------------------------------------------ personajes
def figura(im, lado=1024, visible=0.97, pie=0.01):
    """Cuerpo entero en un lienzo cuadrado, pies abajo (MR- Dirección mide el alfa real de cada figura)."""
    im = recorta_alfa(im, 0)
    alto = round(lado * visible)
    ancho = round(im.width * alto / im.height)
    if ancho > lado:
        ancho, alto = lado, round(im.height * lado / im.width)
    im = im.resize((ancho, alto), Image.LANCZOS)
    out = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    out.alpha_composite(im, ((lado - ancho) // 2, round(lado * (1 - pie)) - alto))
    return out


def redondo(im, lado=400):
    """Ficha redonda opcional: cabeza y hombros de la figura sobre papel crema, con aro de tinta y cuña amarilla."""
    im = recorta_alfa(im, 0)
    cab = im.crop((0, 0, im.width, min(im.height, int(im.width * 0.95))))
    cab = encaja(cab, lado - 40, lado - 40)
    base = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    d.ellipse((4, 4, lado - 5, lado - 5), fill=PAPEL + (255,))
    d.pieslice((4, 4, lado - 5, lado - 5), 200, 340, fill=AMARILLO + (255,))
    mask = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mask).ellipse((14, 14, lado - 15, lado - 15), fill=255)
    capa = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    capa.alpha_composite(cab, (20, 24))
    base.paste(capa, (0, 0), Image.composite(capa.getchannel("A"), Image.new("L", (lado, lado), 0), mask))
    ImageDraw.Draw(base).ellipse((6, 6, lado - 7, lado - 7), outline=TINTA + (255,), width=10)
    return marca.discreta(base, 300, 330, 18)


def _rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
COLOR = {k: _rgb(v) for k, v in D.COLORES.items() if k != "mamba"}   # La Mamba conserva el amarillo de la serie

def panel(im, slug):
    """Cambia el panel amarillo de la serie al color del ratón, conservando la textura de tinta y los bordes."""
    if slug not in COLOR: return im
    rgba = np.array(im.convert("RGBA")); rgb = rgba[..., :3].astype(np.float32)
    hsv = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2HSV).astype(np.float32)  # H 0-180
    h, s, v = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
    tono = np.clip(1 - (np.abs(h - 21) - 6) / 6, 0, 1)       # amarillo-naranja de la serie (H≈21 en OpenCV)
    w = tono * np.clip((s - .32) / .28, 0, 1)
    # El panel es amarillo puro (H 19-25, muy saturado y claro); pelajes, corbatas y cadenas de oro no llegan.
    nucleo = (h >= 19) & (h <= 25) & (s > .7) & (v > .82)
    n, lab, st, _ = cv2.connectedComponentsWithStats(nucleo.astype(np.uint8), 8)
    zona = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 120]).astype(np.uint8)
    zona = cv2.dilate(zona, np.ones((7, 7), np.uint8))       # incluye el antialias del borde
    w = w * zona
    vref = np.median(v[(zona > 0) & (w > .8)])
    nuevo = np.array(COLOR[slug], np.float32)[None, None, :] * np.clip(v / vref, 0, 1.25)[..., None]
    rgba[..., :3] = np.clip(rgb * (1 - w[..., None]) + nuevo * w[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(rgba)


def retrato_compuesto(fig, w=1024, h=1365):
    """PNJ genéricos sin retrato propio: su figura sobre papel crema con el panel amarillo de la serie."""
    out = Image.new("RGBA", (w, h), PAPEL + (255,))
    ImageDraw.Draw(out).polygon([(w * .14, h * .1), (w * .9, h * .07), (w * .93, h * .86), (w * .1, h * .9)], fill=AMARILLO + (255,))
    f = recorta_alfa(fig, 0)
    f = f.crop((0, 0, f.width, min(f.height, int(f.width * 1.35))))
    f = encaja(f, int(w * .92), int(h * .95))
    out.alpha_composite(f, ((w - f.width) // 2, h - f.height))
    return out


def personajes():
    for s in [p["slug"] for p in D.TODOS] + [n["slug"] for n in D.PNJ] + [m["slug"] for m in D.MASILLAS]:
        src = RAW / f"fig-{s}.png"
        if not src.exists():
            print("  falta", src.name); continue
        fig = sin_fondo(Image.open(src))
        guarda(redondo(fig), A / "actors" / "tokens" / f"{s}.webp")
        guarda(marca.hombro(figura(fig)), A / "actors" / "figures" / f"{s}.webp", 88)
        por = RAW / f"por-{s}.png"
        p = panel(Image.open(por).convert("RGBA"), s) if por.exists() else retrato_compuesto(fig)
        p = ImageOps.fit(p, (768, 1024), Image.LANCZOS, centering=(0.5, 0.3))
        guarda(marca.esquina(p), A / "actors" / "portraits" / f"{s}.webp")
        print("hecho", s)


# ------------------------------------------------------------------ escenas
ESCENAS = ["jardin", "masacre", "wanchai", "callejon", "casa", "santuario", "siluetas", "columna", "tejados", "boda", "tren"]
# zonas de los planos: (etiqueta, x, y) en proporción del plano; se miden sobre la imagen generada
ZONAS = {"mapa-jardin": [("J1", 0.5, 0.27), ("J2", 0.2, 0.5), ("J3", 0.83, 0.43), ("J4", 0.5, 0.12), ("J5", 0.12, 0.9)],
         "mapa-casa": [("H1", 0.36, 0.33), ("H2", 0.5, 0.53), ("H3", 0.5, 0.12), ("H4", 0.86, 0.5), ("H5", 0.11, 0.69)]}


def etiquetas(im, zonas):
    d = ImageDraw.Draw(im)
    f = fuente("Anton-Regular.ttf", 54)
    for txt, fx, fy in zonas:
        x, y = fx * im.width, fy * im.height
        caja = d.textbbox((x, y), txt, font=f, anchor="mm")
        d.rectangle((caja[0] - 14, caja[1] - 8, caja[2] + 14, caja[3] + 8), fill=TINTA, outline=AMARILLO, width=5)
        d.text((x, y), txt, font=f, fill=AMARILLO, anchor="mm")
    return im


def escenas():
    for s in ESCENAS:
        src = RAW / f"esc-{s}.png"
        if not src.exists():
            print("  falta", src.name); continue
        im = ImageOps.fit(Image.open(src).convert("RGB"), (1920, 1080), Image.LANCZOS)
        guarda(marca.esquina(im), A / "scenes" / f"{s}.webp", 85)
        guarda(im.resize((400, 225), Image.LANCZOS), A / "scenes" / "thumbs" / f"{s}.webp", 80)
        print("hecho", s)
    for m in ZONAS:
        src = RAW / f"{m}.png"
        if src.exists():
            im = ImageOps.fit(Image.open(src).convert("RGB"), (2304, 1536), Image.LANCZOS)
            guarda(marca.esquina(etiquetas(im, ZONAS[m])), A / "scenes" / f"{m}.webp", 88)
            guarda(im.resize((400, 267), Image.LANCZOS), A / "scenes" / "thumbs" / f"{m}.webp", 80)
            print("hecho", m)
    if (RAW / "cover.png").exists():
        guarda(marca.esquina(Image.open(RAW / "cover.png").convert("RGB")), A / "cover.webp", 88)


# ------------------------------------------------------------------ iconos (hojas de 3×3)
def celdas(hoja):
    im = sin_fondo(Image.open(hoja))
    w, h = im.size
    out = []
    for f in range(3):
        for c in range(3):
            cel = im.crop((c * w // 3, f * h // 3, (c + 1) * w // 3, (f + 1) * h // 3))
            # restos del icono vecino pegados al borde de la celda: fuera
            a = cel.getchannel("A"); b = int(cel.width * .035)
            m = Image.new("L", cel.size, 0); ImageDraw.Draw(m).rectangle((b, b, cel.width - b - 1, cel.height - b - 1), fill=255)
            cel.putalpha(Image.composite(a, m, m))
            out.append(encaja(recorta_alfa(cel, .06), 256, 256))
    return out


def iconos():
    hojas = {}
    for slug, o in {**D.OBJ, **D.COND}.items():
        if not o.get("ic"):
            continue
        h, n = o["ic"]
        if h not in hojas:
            src = RAW / f"hoja-{h}.png"
            hojas[h] = celdas(src) if src.exists() else None
            if not hojas[h]:
                print("  falta", src.name)
        if hojas[h]:
            ic = hojas[h][n - 1]
            if slug.endswith("-izq"):  # la pareja del gemelo, en espejo
                ic = ImageOps.mirror(ic)
            guarda(marca.discreta(ic, 200, 226, 22), A / "items" / f"{slug}.webp")
    # iconos que no son objetos del inventario: la Lista, las reglas y los Masillas
    for slug, (h, n) in EXTRA.items():
        if hojas.get(h) is None and (RAW / f"hoja-{h}.png").exists():
            hojas[h] = celdas(RAW / f"hoja-{h}.png")
        if hojas.get(h):
            guarda(marca.discreta(hojas[h][n - 1], 200, 226, 22), A / "items" / f"{slug}.webp")
    print("iconos:", len(list((A / "items").glob("*.webp"))))


EXTRA = {"lista": ("equipo", 1), "tachon": ("condiciones", 4), "respiro": ("condiciones", 5), "inercia": ("condiciones", 6),
         "cinco": ("condiciones", 7), "masilla": ("condiciones", 8), "explota": ("condiciones", 9)}


# ------------------------------------------------------------------ ayudas de juego
def fuente(nombre, tam):
    return ImageFont.truetype(str(FUENTES / nombre), tam)


def listas(caja=(0.17, 0.13, 0.82, 0.88)):
    """Las Listas de Muerte escritas a rotulador sobre la hoja de cuaderno (bg-lista). caja = zona útil de la hoja, en proporción."""
    src = RAW / "bg-lista.png"
    if not src.exists():
        print("  falta bg-lista"); return
    for p in D.TODOS:
        bg = ImageOps.fit(Image.open(src).convert("RGB"), (1536, 1024), Image.LANCZOS)
        d = ImageDraw.Draw(bg)
        x0, y0, x1, y1 = (int(caja[0] * 1536), int(caja[1] * 1024), int(caja[2] * 1536), int(caja[3] * 1024))
        titulo = "LISTA DE MUERTE" if p["slug"] != "rosa" else "LISTA NUPCIAL"
        d.text((x0, y0), titulo, font=fuente("Caveat-Bold.ttf", 78), fill=TINTA)
        d.text((x1, y0 + 30), p["n"].split(",")[0], font=fuente("Caveat-Regular.ttf", 40), fill=(60, 60, 70), anchor="ra")
        paso = (y1 - y0 - 140) / 5
        for i, nombre in enumerate(D.lista_txt(p)):
            y = y0 + 140 + i * paso
            tam = 74 if i < 4 else 82
            f = fuente("Caveat-Bold.ttf", tam)
            while d.textlength(nombre, font=f) > x1 - x0 - 90 and tam > 40:
                tam -= 4; f = fuente("Caveat-Bold.ttf", tam)
            d.text((x0, y), f"{i + 1}.", font=fuente("Caveat-Bold.ttf", 80), fill=ROJO)
            d.text((x0 + 80, y), nombre, font=f, fill=TINTA)
            if i == 4:   # BILL, subrayado dos veces
                w = d.textlength(nombre, font=f)
                for k in (0, 14):
                    d.line((x0 + 80, y + tam + 8 + k, x0 + 80 + w, y + tam + 2 + k), fill=TINTA, width=6)
        guarda(marca.esquina(bg), A / "handouts" / f"lista-{p['slug']}.webp", 88)


def sobre():
    src = RAW / "bg-sobre.png"
    if src.exists():
        guarda(marca.esquina(ImageOps.fit(Image.open(src).convert("RGB"), (1536, 1024), Image.LANCZOS)), A / "handouts" / "sobre-rojo.webp", 88)


def ayudas():
    listas(); sobre()
    print("ayudas hechas")


def ui():
    """«Sin sitio»: el objeto que tapa las cuatro casillas de mochila que no existen en Kill Mice."""
    lado = 512
    base = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    ImageDraw.Draw(base).rectangle((8, 8, lado - 9, lado - 9), fill=(40, 36, 32, 255), outline=TINTA + (255,), width=12)
    rayas = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(rayas)
    for k in range(-lado, lado, 46):
        d.line((k, lado, k + lado, 0), fill=AMARILLO + (200,), width=14)
    m = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(m).rectangle((22, 22, lado - 23, lado - 23), fill=255)
    base.paste(rayas, (0, 0), Image.composite(rayas.getchannel("A"), Image.new("L", (lado, lado), 0), m))
    guarda(base, A / "ui" / "sin-sitio.webp")
    (A / "brand").mkdir(parents=True, exist_ok=True)
    shutil.copy("/Volumes/Datos_Dock/FoundryVTT/Trabajo LOGO/marca/mr-marca.webm", A / "brand" / "mr-marca.webm")


GRUPOS = dict(personajes=personajes, escenas=escenas, iconos=iconos, ayudas=ayudas, ui=ui)
if __name__ == "__main__":
    for g in sys.argv[1:] or GRUPOS:
        print("==", g)
        GRUPOS[g]()
