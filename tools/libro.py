#!/usr/bin/env python3
"""Maqueta el libro de Kill Mice (HTML → Chrome headless → PDF A4) desde la misma fuente que el módulo:
texto/aventura.md, texto/datos.py y el arte de assets/. Portada a sangre, créditos e índice con páginas, capítulos a dos
columnas justificadas con guionado español, dosieres (hoja de venganza + ficha de seis casillas) de los seis ratones y Rosa,
apéndice con las Listas de Muerte recortables, el Sobre Rojo, tarjetas de estado y los dos planos, y contraportada.
Salida: docs/pdf/Kill-Mice.pdf. Uso: python3 tools/libro.py"""
import html, json, re, subprocess, sys
from pathlib import Path
import fitz
import pyphen

R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R / "texto")); sys.path.insert(0, str(R / "tools"))
import datos as D  # noqa: E402
import md  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SAL = R / "docs" / "pdf"; TMP = Path("/Volumes/Datos_Dock/FoundryVTT/Trabajo KM/tmp")
A = R / "assets"
PAPEL = (0.965, 0.945, 0.89)   # #F6F1E3
esc = html.escape
VERSION = json.loads((R / "module.json").read_text())["version"]
GUION = pyphen.Pyphen(lang="es", left=3, right=3)

NUEVA = {"personajes", "escenario1", "acto1", "enemigos1", "interludio", "escenario2", "acto2", "enemigos2", "reemplazos", "finales"}  # página nueva
ANCHOS = re.compile(r'<div class="tabla">.*?</table></div>|<div class="(?:ancho|tabla ancho)">.*?</table>.*?</div>|<div class="mrkm-rejilla">.*?</div>'
                    r'|<figure class="fig-ancha".*?</figure>|<table>.*?</table>', re.S)


def trozo(h):
    return f'<div class="cols{" corto" if len(re.sub("<[^>]+>", "", h)) < 500 else ""}">{h}</div>'


def columnas(h):
    """Los bloques a todo el ancho van FUERA del texto a dos columnas: con column-span, Chrome deja páginas medio vacías al imprimir."""
    out, i = [], 0
    for m in ANCHOS.finditer(h):
        b = m.group(0)
        if b.startswith('<div class="tabla">') or (b.startswith("<table>") and b.count("<th") < 3):
            continue
        out += [trozo(h[i:m.start()]), b]; i = m.end()
    out.append(trozo(h[i:]))
    return "".join(x for x in out if re.sub("<[^>]+>", "", x).strip() or "<img" in x or "<figure" in x)


def u(p):
    """Chrome incrusta los WebP descomprimidos: se pasan a JPEG, o a PNG reducido si tienen transparencia."""
    src = A / p
    if not src.exists():
        return ""
    if src.suffix != ".webp":
        return src.as_uri()
    from PIL import Image
    out = TMP / "img" / p.replace("/", "_")
    im = Image.open(src)
    alfa = im.mode in ("RGBA", "LA") and im.getchannel("A").getextrema()[0] < 250
    out = out.with_suffix(".png" if alfa else ".jpg")
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        out.parent.mkdir(parents=True, exist_ok=True)
        im.thumbnail((1400, 1400) if alfa else (2200, 2200), Image.LANCZOS)
        im.save(out, optimize=True) if alfa else im.convert("RGB").save(out, quality=85, optimize=True)
    return out.as_uri()


def girado(p):
    """Los planos son apaisados: girados llenan la página A4."""
    from PIL import Image
    src = A / p
    if not src.exists():
        return ""
    out = TMP / f"girado-{src.stem}.jpg"
    Image.open(src).convert("RGB").rotate(90, expand=True).save(out, quality=88)
    return out.as_uri()


def figura_justa(slug):
    from PIL import Image
    src = A / "actors" / "figures" / f"{slug}.webp"
    if not src.exists():
        return ""
    im = Image.open(src)
    out = TMP / f"fig-{slug}.png"
    im.crop(im.getchannel("A").getbbox()).save(out)
    return out.as_uri()


def guiona(h):
    def palabra(m):
        w = m.group(0)
        return GUION.inserted(w, hyphen="­") if len(w) >= 7 and w.islower() else w
    return re.sub(r">([^<]+)<", lambda m: ">" + re.sub(r"[a-záéíóúñü]+", palabra, m.group(1)) + "<", h)


# ------------------------------------------------------------------ bloques especiales
def fig(i, pos, cap):
    p = (f"scenes/{i}.webp" if i.startswith("mapa-") else f"scenes/{i[4:]}.webp" if i.startswith("esc-")
         else f"actors/portraits/{i[4:]}.webp" if i.startswith("por-") else f"{i}.webp")
    if not (A / p).exists():
        return ""
    clase = "fig-dcha" if pos in ("right", "left") else "fig-ancha"
    return f'<figure class="{clase}"><img src="{u(p)}" alt="">' + (f"<figcaption>{esc(cap)}</figcaption>" if cap else "") + "</figure>"


def portador(slug):
    return ", ".join(p["n"] for p in D.TODOS if slug in p["inv"].values()) or "Todos"


def arsenal():
    filas = []
    for s in D.ARSENAL:
        o = D.OBJ[s]
        dano = o.get("dmg", "d10 · 1d6 + 2 M.") + (f" · {o['dmg2']} a dos patas" if o.get("dmg2") else "") + (f" · +{o['mas']} M." if o.get("mas") else "")
        icono = f'<img src="{u(f"items/{s}.webp")}" alt="">' if (A / f"items/{s}.webp").exists() else ""
        filas.append(f"<tr><td class='ic'>{icono}</td><td><strong>{esc(o['n'])}</strong><br>{esc(o['d'])}</td><td class='dano'>{esc(dano)}</td><td>{esc(portador(s))}</td></tr>")
    return ('<div class="ancho"><h3>Arsenal reciclado</h3><table class="arsenal"><thead><tr><th></th><th>Arma</th><th>Daño</th><th>Quién la lleva</th></tr></thead><tbody>'
            + "".join(filas) + "</tbody></table><p><small>M. = Masillas abatidos de más contra la Turba.</small></p></div>")


def tabla(clave):
    t = D.TABLAS[clave]
    cab = "".join(f"<th>{esc(c)}</th>" for c in (t["dado"],) + t["cols"])
    filas = "".join("<tr><td class='n'>%d</td>%s</tr>" % (i + 1, "".join(f"<td>{esc(x)}</td>" for x in f)) for i, f in enumerate(t["filas"]))
    ancho = " ancho" if len(t["cols"]) > 1 else ""
    return f'<div class="tabla{ancho}"><h3>{esc(t["n"])} · {t["dado"]}</h3><table><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody></table></div>'


def listas():
    cab = "<tr><th>Ratón</th>" + "".join(f"<th>N.º {i}</th>" for i in range(1, 6)) + "</tr>"
    filas = "".join(f"<tr><td>{esc(p['n'])}</td>" + "".join(f"<td>{esc(t)}</td>" for t in D.lista_txt(p)) + "</tr>" for p in D.PJ)
    return f'<div class="ancho"><h3>Las seis Listas de Muerte</h3><table class="matriz"><thead>{cab}</thead><tbody>{filas}</tbody></table></div>'


def secuencias(n):
    n = int(n)
    filas = "".join(f"<tr><td><strong>{esc(nom)}</strong></td>" + "".join(f"<td>{v}</td>" for v in vals) + "</tr>" for _, nom, vals in D.SECUENCIAS[n])
    return (f'<div class="ancho"><h3>Secuencias de la Pelea {"I" if n == 1 else "II"}</h3><table class="secs"><thead><tr><th>Personaje o grupo</th><th>Sec. 1</th><th>Sec. 2</th><th>Sec. 3</th><th>Sec. 4</th></tr></thead>'
            f"<tbody>{filas}<tr><td><strong>Cada PJ</strong></td><td colspan='4'>1d6 + mitad de DES al empezar cada secuencia</td></tr></tbody></table></div>")


def pnj_bloque(n):
    atq = ", ".join(f"{a} {d if d != 'esp' else '(daño escalable)'}" for a, d in n["atq"]) or "sin armas"
    esp = "".join(f"<li><strong>{esc(a)}.</strong> {esc(b)}</li>" for a, b in n["esp"])
    en = ", ".join(p["n"] for p in D.TODOS if n["slug"] in p["lista"])
    return (f'<div class="pnj"><img src="{u("actors/portraits/" + n["slug"] + ".webp")}" alt=""><div><h4>{esc(n["n"])}</h4>'
            f'<p class="st">{esc(n["apodo"].upper())} · FUE {n["fue"]} · DES {n["des"]} · VOL {n["vol"]} · PG {n["pg"]}{" · Arm. " + str(n["arm"]) if n["arm"] else ""} · {esc(atq)}</p>'
            f'<p>{esc(n["d"])}</p><ul class="esp">{esp}</ul>' + (f'<p class="lista">En la Lista de {esc(en)}</p>' if en else "")
            + f'<p class="voz"><em>{esc(n["voz"])}</em> {esc(n["frase"])}</p></div></div>')


def pnj(args):
    acto = 1 if "1" in args else 2
    out = [pnj_bloque(n) for n in D.PNJ if n["acto"] == acto and n["tipo"] != "aliado"]
    if acto == 1:
        out.append(pnj_bloque(D.PNJ_POR["leon"]))
    return "".join(out)


def masillas(args):
    m = D.MASILLAS[int(args) - 1]
    return f'<div class="mrkm-regla"><h4>{esc(m["n"])} · Masillas</h4><p>{esc(m["d"])} Despliega {m["por_pj"]} por jugador. Atacan como Turba: 1d6 a cada PJ acosado, 1d8 si son seis o más.</p></div>'


def pj_caja(p):
    tec = "".join(f"<li><strong>{esc(a)}.</strong> {esc(b)}</li>" for a, b in p["tec"])
    return (f'<div class="pjcaja" style="--pj: {p["color"]}"><img src="{u("actors/portraits/" + p["slug"] + ".webp")}" alt=""><div><h4>{esc(p["n"])}</h4>'
            f'<p class="st">{esc(p["arq"].upper())} · FUE {p["fue"]} · DES {p["des"]} · VOL {p["vol"]} · PG {p["pg"]}</p><p>{esc(p["aspecto"])}</p><ul>{tec}</ul></div></div>')


def especial(nombre, args):
    f = {"arsenal": arsenal, "listas": listas, "pnj": lambda: pnj(args), "masillas": lambda: masillas(args), "secuencias": lambda: secuencias(args),
         "pjs": lambda: "".join(pj_caja(p) for p in D.PJ), "rosa": lambda: pj_caja(D.ROSA)}
    return f.get(nombre, lambda: tabla(args))()


# ------------------------------------------------------------------ dosieres
RANURAS = (("pata", "Pata hábil"), ("torpe", "Pata torpe"), ("c1", "Cuerpo"), ("c2", "Cuerpo"), ("m1", "Mochila"), ("m2", "Mochila"))


def casilla(p, k, lbl):
    s = p["inv"].get(k)
    if not s:
        return f'<div class="cas vacia"><span class="lbl">{lbl}</span><span class="libre">Libre</span></div>'
    if s == "lista":
        return (f'<div class="cas"><span class="lbl">{lbl}</span><img src="{u("items/lista.webp")}" alt=""><strong>Mi Lista de Muerte</strong>'
                f'<small>Cinco nombres. Tacha cada uno al caer: Respiro de sangre e Inercia de venganza.</small></div>')
    o = D.OBJ[s]
    if o.get("h") == 2:
        lbl = "Mochila · dos casillas"
    dano = (f" · {o['dmg']}" + (f"/{o['dmg2']}" if o.get("dmg2") else "")) if o["tipo"] == "weapon" else (f" · Arm. {o['arm']}" if o["tipo"] == "armor" else "")
    return (f'<div class="cas"><span class="lbl">{lbl}</span><img src="{u(f"items/{s}.webp")}" alt=""><strong>{esc(o["n"])}{dano}</strong>'
            f'<small>{esc(o["d"])}</small></div>')


def dosier(p):
    op = "".join(f"<dt>{esc(D.NOMBRE[k])}</dt><dd>{esc(v)}</dd>" for k, v in p["opina"].items())
    tec = "".join(f"<dt>{esc(a)}</dt><dd>{esc(b)}</dd>" for a, b in p["tec"])
    cuaderno = "".join(f"<li>{esc(t)}</li>" for t in D.lista_txt(p))
    franja = p["color"]
    secreta = (f'<section class="pag dosier" style="--franja: {franja}"><img class="polaroid" src="{u("actors/portraits/" + p["slug"] + ".webp")}" alt="">'
               f'<p class="kick">Hoja de venganza · solo para quien lleve a este ratón</p><h1>{esc(p["n"])}</h1><p class="lema">{esc(p["lema"])}</p>'
               + (f'<p><strong>Cuándo entra:</strong> {esc(p["cuando"])}</p>' if p.get("cuando") else "")
               + f'<h3>Tu vínculo con la boda</h3><p>{esc(p["vinculo"])}</p><h3>Mi Lista de Muerte</h3><ol class="cuaderno">{cuaderno}</ol>'
               + f'<h3>Técnicas</h3><dl class="tec">{tec}</dl>' + (f"<h3>Qué opinas de los demás</h3><dl>{op}</dl>" if op else "") + "</section>")
    stats = "".join(f'<div><span>{k}</span><b>{v}</b></div>' for k, v in (("FUE", p["fue"]), ("DES", p["des"]), ("VOL", p["vol"]), ("PG", p["pg"]), ("Pepitas", p["pepitas"])))
    ranuras = [(k, l) for k, l in RANURAS if not (k == "m2" and D.OBJ.get(p["inv"].get("m1"), {}).get("h") == 2)]
    ficha = (f'<section class="pag ficha" style="--franja: {franja}"><img class="cuerpo" src="{figura_justa(p["slug"])}" alt="">'
             f'<div class="cab"><p class="kick">Ficha · Mausritter</p><h1>{esc(p["n"])}</h1><p class="sub">{esc(p["arq"])}</p></div>'
             f'<div class="stats">{stats}</div><p class="aspecto"><strong>Aspecto.</strong> {esc(p["aspecto"])}</p><h3>Seis casillas</h3><div class="inv">'
             + "".join(casilla(p, k, l) for k, l in ranuras) + '</div><p class="nota">Las condiciones ocupan casillas. Si no queda sitio, suelta algo.</p></section>')
    return secreta + ficha


# ------------------------------------------------------------------ apéndice recortable
def recortables():
    tarj = []
    for s, c in D.COND.items():
        tarj.append(f'<div class="tarjeta"><img src="{u(f"items/{s}.webp")}" alt=""><h4>{esc(c["n"])}</h4><p>{esc(c["d"])}</p><p class="q"><strong>Se quita:</strong> {esc(c["quita"])}</p><span>1 casilla</span></div>')
    for s in ("moneda-fortuna", "sobre-rojo", "medallon"):
        o = D.OBJ[s]
        tarj.append(f'<div class="tarjeta clave"><img src="{u(f"items/{s}.webp")}" alt=""><h4>{esc(o["n"])}</h4><p>{esc(o["d"])}</p><span>Objeto clave</span></div>')
    hojas = [p for p in D.TODOS if (A / f"handouts/lista-{p['slug']}.webp").exists()]
    pags = "".join(f'<section class="pag apendice"><p class="kick">Apéndice · Recortables</p><h1>Las Listas de Muerte</h1><div class="recorte">'
                   + "".join(f'<img src="{u("handouts/lista-" + p["slug"] + ".webp")}" alt="">' for p in hojas[i:i + 4]) + "</div></section>" for i in range(0, len(hojas), 4))
    sobre = f'<img class="ayuda" src="{u("handouts/sobre-rojo.webp")}" alt="">' if (A / "handouts/sobre-rojo.webp").exists() else ""
    laminas = "".join(f'<section class="lamina mapa"><img src="{girado(f"scenes/{m}.webp")}" alt=""><p>{t}</p></section>'
                      for m, t in (("mapa-jardin", "El Jardín del Banquete Koi · J1 Pabellón · J2 Mesas · J3 Estanque · J4 Estatuas · J5 Setos"),
                                   ("mapa-casa", "La Casa de las Hojas Azules · H1 Tatami · H2 Jaula · H3 Columna · H4 Pasarela · H5 Pila de 9 V")) if (A / f"scenes/{m}.webp").exists())
    return (pags + f'<section class="pag apendice"><p class="kick">Apéndice · Ayudas de juego</p><h1>El Sobre Rojo y el Medallón Fénix-Dragón</h1>{sobre}'
            f'<h1>Tarjetas de estado y objetos clave</h1><div class="tarjetas">{"".join(tarj)}</div></section>' + laminas)


# ------------------------------------------------------------------ documento
def documento(pags=None):
    pags = pags or {}
    css = (R / "tools" / "libro.css").read_text().replace("ASSETS/", A.as_uri() + "/")
    caps = md.capitulos(fig, especial)
    indice = "".join(f'<li><span>{esc(c["kicker"].split(" · ")[0])}</span><b>{esc(c["titulo"])}</b><i>{pags.get(c["titulo"], "")}</i></li>' for c in caps)
    indice += (f'<li><span>19</span><b>Los dosieres</b><i>{pags.get("Los dosieres", "")}</i></li>'
               f'<li><span>20</span><b>Apéndice · Recortables</b><i>{pags.get("Las Listas de Muerte", "")}</i></li>')
    cuerpo = "".join(f'<section class="cap{" nueva" if c["id"] in NUEVA else ""}" id="{c["id"]}"><header><p class="kick">{esc(c["kicker"])}</p><h1>{esc(c["titulo"])}</h1></header>{columnas(guiona(c["html"]))}</section>'
                     for c in caps)
    logo = u("brand/MR_11_Formal_Marfil_Transparente.png")
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Kill Mice · La Lista del Sobre Rojo</title><style>{css}</style></head><body>
<section class="portada"><img src="{u("cover.webp")}" alt=""><div class="titulo"><h1>Kill Mice</h1><br><p>La Lista del Sobre Rojo</p><span class="vol">Volumen 1 &amp; 2</span></div>
<div class="pie"><span>Una aventura para <b>Mausritter</b> · 3–6 jugadores · una sesión explosiva</span><img src="{logo}" alt="MR"></div></section>
<section class="pag creditos"><div class="gancho"><p class="kick">Os dejaron por muertos</p><p class="grande">Afilasteis el acero. Escribisteis cinco nombres en un papel. Y hoy, en la boda del año, entre carpas koi y sobres rojos, el primero de esos nombres acaba de asomar el hocico entre los bonsáis.</p></div>
<h2>Índice</h2><ol class="indice">{indice}</ol>
<div class="cred"><p><b>Adaptación, texto, arte, maquetación y módulo de Foundry:</b> Manu Romera (MR-). Edición {VERSION}.</p>
<p><b>Basada en la estructura de</b> <i>Red Packet Rumble</i>, escenario para <i>Feng Shui 2</i> (Atlas Games), y en el cine de venganza de los setenta y de Hong Kong. Parte de la colección de aventuras de Mausritter de Manu Romera, con <i>Reservoir Mice</i>, <i>The Ratefoul Eight</i> y <i>Malditos Maustardos</i>.</p>
<p><i>Kill Mice</i> es una producción independiente de Manu Romera y no está afiliada a Losing Games ni a Atlas Games. Se publica bajo la licencia de terceros de Mausritter. <i>Mausritter</i> es © Losing Games.</p>
<p>Texto e ilustraciones bajo licencia CC BY-NC-SA 4.0. Se permite imprimir y fotocopiar para uso personal.</p></div></section>
{cuerpo}
<section class="lamina parte" id="dosieres"><img src="{u("scenes/masacre.webp")}" alt=""><div><p class="kick">Para los jugadores</p><h1>Los dosieres</h1><p>Seis vengadores y una novia de reserva. Cada jugador ve solo el suyo: hoja de venganza y ficha lista para jugar.</p></div></section>
{"".join(dosier(p) for p in D.TODOS)}
{recortables()}
<section class="contra"><img src="{u("scenes/siluetas.webp")}" alt=""><div><h2>Cinco nombres. Un rotulador rojo.</h2><p>Os dejaron por muertos hace un año. Hoy, en la boda de Rosa Muk y León Yan, los asesinos del Escuadrón Víbora del Loto Negro vuelven a por el Sobre Rojo… y vosotros ya tenéis sus nombres escritos.</p>
<p>Venganza ratonil de una sesión para <b>Mausritter</b>: seis personajes listos para jugar con su Lista de Muerte, reglas de Masillas, Turba y dados explosivos, dos peleas coreografiadas y un villano que pega tan fuerte como vuestro mejor golpe.</p>
<img class="logo" src="{logo}" alt="MR"></div></section>
</body></html>"""


def imprime(h, nombre):
    TMP.mkdir(parents=True, exist_ok=True); SAL.mkdir(parents=True, exist_ok=True)
    f = TMP / f"{nombre}.html"; f.write_text(h, encoding="utf-8")
    pdf = SAL / f"{nombre}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files", "--virtual-time-budget=30000",
                    f"--print-to-pdf={pdf}", f.as_uri()], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    d = fitz.open(pdf)
    for p in d:   # papel a sangre por debajo (Chrome deja los márgenes en blanco)
        p.draw_rect(p.rect, color=None, fill=PAPEL, overlay=False)
    tmp = pdf.with_suffix(".tmp.pdf"); d.save(tmp, garbage=3, deflate=True); d.close(); tmp.replace(pdf)
    return pdf


def paginas(pdf, titulos):
    d = fitz.open(pdf); res = {}
    for i, p in enumerate(d):
        for b in p.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                if not ln["spans"] or max(sp["size"] for sp in ln["spans"]) < 20:
                    continue
                txt = " ".join("".join(sp["text"] for sp in ln["spans"]).replace("­", "").split()).lower()
                for t in titulos:
                    if len(txt) > 5 and t.lower().startswith(txt):
                        res.setdefault(t, i + 1)
    return res


if __name__ == "__main__":
    nombre = "Kill-Mice"
    pdf = imprime(documento(), nombre)
    titulos = [c["titulo"] for c in md.capitulos(fig, especial)] + ["Los dosieres", "Las Listas de Muerte"]
    pdf = imprime(documento(paginas(pdf, titulos)), nombre)
    print(pdf, fitz.open(pdf).page_count, "páginas")
