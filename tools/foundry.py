#!/usr/bin/env python3
"""Construye la aventura de Foundry desde texto/ (fuente única):
  _data/aventura.json        documento Adventure (actores, objetos, diarios, escenas, tablas, macros, listas de sonido)
  content/direccion-es.json  paquete para MR- Dirección (escenas, música, motivos, efectos por escena, figuras, hitos)
  content/pizarra-es.json    pizarra «Las Listas de Muerte» para MR- Pizarra (formato mr-pizarra-import 1)
Después: node scripts/build.mjs (LevelDB + zip). Uso: python3 tools/foundry.py"""
import hashlib, html, json, sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R / "texto")); sys.path.insert(0, str(R / "tools"))
sys.path.insert(0, "/Volumes/Datos_Dock/FoundryVTT/Trabajo LOGO/marca")
import datos as D  # noqa: E402
import md  # noqa: E402
import marca  # noqa: E402

ID = "mr-kill-mice"
VERSION = json.loads((R / "module.json").read_text())["version"]
A62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
esc = html.escape


def uid(s):
    n = int(hashlib.sha256((ID + s).encode()).hexdigest(), 16); o = ""
    for _ in range(16):
        n, r = divmod(n, 62); o += A62[r]
    return o


def ruta(p):
    return f"modules/{ID}/{p}"


def existe(p):
    return (R / p).exists()


def img(p, defecto="icons/svg/mystery-man.svg"):
    return ruta(p) if existe(p) else defecto


# ------------------------------------------------------------------ carpetas
FOLD = {}


def carpeta(nombre, tipo, orden, color=None):
    f = dict(_id=uid(f"folder:{tipo}:{nombre}"), name=nombre, type=tipo, folder=None, sorting="m", sort=orden, color=color, flags={}, description="")
    FOLD[(tipo, nombre)] = f["_id"]
    return f


folders = [carpeta("Los vengadores", "Actor", 0, "#C8102E"), carpeta("Mares Dorados · Acto I", "Actor", 1, "#F5C518"), carpeta("Escuadrón Víbora · Acto II", "Actor", 2, "#1E40AF"),
           carpeta("Aliados y Masillas", "Actor", 3),
           carpeta("Armas", "Item", 0), carpeta("Equipo", "Item", 1), carpeta("Claves", "Item", 2), carpeta("Condiciones", "Item", 3),
           carpeta("Kill Mice · DJ", "JournalEntry", 0, "#C8102E"), carpeta("Dosieres", "JournalEntry", 1, "#121212"), carpeta("Ayudas de juego", "JournalEntry", 2),
           carpeta("Kill Mice", "Scene", 0, "#F5C518"), carpeta("Kill Mice", "RollTable", 0), carpeta("Kill Mice", "Macro", 0)]

# ------------------------------------------------------------------ objetos
CASILLAS = dict(pata=(-270, -150), torpe=(-270, -20), c1=(-140, -150), c2=(-140, -20), m1=(10, -150), m2=(10, -20))
CLAVES = {"sobre-rojo", "medallon", "moneda-fortuna", "dosier-yan", "botiquin"}


def sheet(x=0, y=0):
    return dict(active=False, currentX=x, currentY=y, initialX=x, initialY=y, xOffset=0, yOffset=0, rotation=0, curWidth=1, curHeight=1, zIndex=1000 + x + y)


def lista_html(p):
    filas = "".join(f'<li data-n="{i + 1}" data-slug="{s}">{esc(t)}</li>' for i, (s, t) in enumerate(zip(p["lista"], D.lista_txt(p))))
    return f'<ol class="mrkm-lista">{filas}</ol><p>Tacha un nombre cuando caiga y hayas participado: Respiro de sangre, Inercia de venganza y, si diste el último golpe a un nombre compartido, una Moneda de Fortuna.</p>'


def item_doc(slug, x=0, y=0, suf="", folder=None, dueno=None):
    if slug in D.COND:
        c = D.COND[slug]
        sysd = dict(description=f"<p>{esc(c['d'])}</p><p><strong>Se quita:</strong> {esc(c['quita'])}</p>", clear=c["quita"], desc=c["d"], color="white")
        tipo, nombre, w, h, fl = "condition", c["n"], 1, 1, {}
    elif slug == "lista":
        sysd = dict(description=lista_html(dueno), color="white", weight=0, cost=0, tag="", placement="body")
        tipo, nombre, w, h, fl = "item", "Mi Lista de Muerte" if dueno["slug"] != "rosa" else "Mi Lista de Muerte nupcial", 1, 1, dict(lista=dueno["lista"])
    else:
        o = D.OBJ[slug]
        tipo, nombre, w, h = o["tipo"], o["n"], o.get("w", 1), o.get("h", 1)
        txt = o["d"] + (f" Daño {o['dmg']}" + (f" ({o['dmg2']} a dos patas)" if o.get("dmg2") else "") + "." if tipo == "weapon" else "")
        sysd = dict(description=f"<p>{esc(txt)}</p>", color="white", weight=0, cost=0, tag="")
        if tipo == "item":
            sysd["placement"] = "hand"
        if tipo == "weapon":
            sysd.update(placement="hand", weapon=dict(dmg1=o["dmg"], dmg2=o.get("dmg2", ""), selected=0, canSwap=bool(o.get("dmg2"))))
        if tipo == "armor":
            sysd["armor"] = dict(value=o["arm"])
        fl = {k: o[k] for k in ("mas", "fuego") if o.get(k)}
    pips = D.OBJ.get(slug, {}).get("pips", 0)
    sysd.update(size=dict(width=w, height=h), sheet=sheet(x, y), pips=dict(value=0, max=pips, html=""))
    icono = f"assets/items/{slug}.webp"
    return dict(_id=uid(f"item:{slug}{suf}"), name=nombre, type=tipo, img=img(icono, "icons/svg/item-bag.svg"), system=sysd,
                effects=[], folder=folder, sort=0, ownership=dict(default=0), flags={ID: dict(slug=slug, **fl)})


def bloqueo(suf):
    return dict(_id=uid(f"item:sin-sitio{suf}"), name="Sin sitio (seis casillas)", type="item", img=ruta("assets/ui/sin-sitio.webp"),
                system=dict(description="<p>En Kill Mice solo hay seis casillas: dos de patas, dos de cuerpo y dos de mochila. Esta parte de la mochila no existe. Solo el DJ puede quitarla.</p>",
                            weight=0, cost=0, tag="", placement="hand", color="white", size=dict(width=2, height=2), sheet=sheet(205, -85), pips=dict(value=0, max=0, html="")),
                effects=[], folder=None, sort=0, ownership=dict(default=0), flags={ID: dict(slug="sin-sitio", bloqueo=True)})


def carpeta_obj(slug):
    if slug in D.COND:
        return "Condiciones"
    if slug in CLAVES:
        return "Claves"
    return "Armas" if D.OBJ[slug]["tipo"] == "weapon" or slug == "petardos" else "Equipo"


items = [item_doc(s, folder=FOLD[("Item", carpeta_obj(s))]) for s in list(D.OBJ) + list(D.COND) if s != "kungfu"]

# ------------------------------------------------------------------ actores
def stats(f, d, v):
    return {k: dict(value=x, max=x, label=l) for k, x, l in zip(("strength", "dexterity", "will"), (f, d, v), ("Strength", "Dexterity", "Will"))}


def token(slug, nombre, disp, tam=1, link=False, vision=False):
    return dict(name=nombre, displayName=30, actorLink=link, disposition=disp, width=tam, height=tam, lockRotation=True,
                texture=dict(src=img(f"assets/actors/figures/{slug}.webp"), scaleX=1, scaleY=1, fit="contain", anchorX=0.5, anchorY=0.5),
                bar1=dict(attribute="health"), displayBars=20, sight=dict(enabled=vision, range=30), ring=dict(enabled=False))


def ficha_pj(p, tipo="pj"):
    inv = [item_doc(s, *CASILLAS[k], suf=":" + p["slug"], dueno=p) for k, s in p["inv"].items()]
    # los objetos de dos casillas van centrados entre las dos (la hoja de Mausritter coloca por el centro)
    for it in inv:
        if it["system"]["size"]["height"] == 2:
            sh = it["system"]["sheet"]; sh["currentY"] = sh["initialY"] = -85
    inv += [bloqueo(":" + p["slug"])]
    tec = "".join(f"<li><strong>{esc(n)}.</strong> {esc(t)}</li>" for n, t in p["tec"])
    bio = (f"<p><em>{esc(p['arq'])} · {esc(p['lema'])}</em></p><p>{esc(p['aspecto'])}</p><h3>Técnicas</h3><ul>{tec}</ul>"
           + f"<h3>Mi Lista de Muerte</h3>{lista_html(p)}")
    return dict(_id=uid("actor:" + p["slug"]), name=p["n"], type="character", img=img(f"assets/actors/portraits/{p['slug']}.webp"),
                system=dict(health=dict(value=p["pg"], min=0, max=p["pg"]), hits=dict(value=2, max=2), armor=0, biography=bio, notes="",
                            description=dict(background=p["arq"], birthsign="", coat="", look=p["aspecto"]), level=dict(value=1, xp=0), pips=dict(value=p["pepitas"]),
                            grit=dict(value=0, ignored=""), stats=stats(p["fue"], p["des"], p["vol"]), other=dict(grit=dict(value=0))),
                prototypeToken=token(p["slug"], p["n"], 1, 1, True, True), items=inv, effects=[], folder=FOLD[("Actor", "Los vengadores")], sort=D.TODOS.index(p),
                ownership=dict(default=0), flags={ID: dict(slug=p["slug"], tipo=tipo, lista=p["lista"], op=p["op"], color=p["color"])})


def arma_pnj(slug, i, a, d):
    return dict(_id=uid(f"atq:{slug}:{i}"), name=a, type="weapon", img="icons/svg/sword.svg",
                system=dict(description="", weight=0, cost=0, tag="", placement="hand", color="white", weapon=dict(dmg1=d if d != "esp" else "d10", dmg2="", selected=0, canSwap=False),
                            size=dict(width=1, height=1), sheet=sheet(), pips=dict(value=0, max=0, html="")), effects=[], folder=None, sort=0, ownership=dict(default=0), flags={})


def carpeta_pnj(n):
    if n["tipo"] == "aliado":
        return "Aliados y Masillas"
    return "Mares Dorados · Acto I" if n["acto"] == 1 else "Escuadrón Víbora · Acto II"


def ficha_pnj(n):
    atq = [arma_pnj(n["slug"], i, a, d) for i, (a, d) in enumerate(n["atq"])]
    esp = "".join(f"<li><strong>{esc(a)}.</strong> {esc(b)}</li>" for a, b in n["esp"])
    en = [p["n"] for p in D.TODOS if n["slug"] in p["lista"]]
    bio = (f"<p><em>{esc(n['apodo'])}</em></p><p>{esc(n['d'])}</p><ul>{esp}</ul><p><strong>Voz:</strong> {esc(n['voz'])} <em>{esc(n['frase'])}</em></p>"
           + (f"<p><strong>En la Lista de:</strong> {esc(', '.join(en))}.</p>" if en else ""))
    return dict(_id=uid("actor:" + n["slug"]), name=n["n"], type="creature", img=img(f"assets/actors/portraits/{n['slug']}.webp"),
                system=dict(health=dict(value=n["pg"], min=0, max=n["pg"]), hits=dict(value=2, max=2), armor=n["arm"], biography=bio, notes="",
                            description=dict(disposition=""), stats=stats(n["fue"], n["des"], n["vol"])),
                prototypeToken=token(n["slug"], n["n"], 0 if n["tipo"] == "aliado" else -1, n.get("tam", 1)), items=atq, effects=[],
                folder=FOLD[("Actor", carpeta_pnj(n))], sort=0, ownership=dict(default=0),
                flags={ID: dict(slug=n["slug"], tipo=n["tipo"], acto=n["acto"], nombre=True, arm=n["arm"])})


def ficha_masilla(m):
    return dict(_id=uid("actor:" + m["slug"]), name=m["n"], type="creature", img=img(f"assets/actors/figures/{m['slug']}.webp"),
                system=dict(health=dict(value=1, min=0, max=1), hits=dict(value=0, max=0), armor=0, biography=f"<p>{esc(m['d'])}</p>", notes="",
                            description=dict(disposition=""), stats=stats(8, 8, 6)),
                prototypeToken=token(m["slug"], m["n"], -1), items=[], effects=[], folder=FOLD[("Actor", "Aliados y Masillas")], sort=0,
                ownership=dict(default=0), flags={ID: dict(slug=m["slug"], tipo="masilla", acto=m["acto"])})


actors = [ficha_pj(p) for p in D.PJ] + [ficha_pj(D.ROSA, "reserva")] + [ficha_pnj(n) for n in D.PNJ] + [ficha_masilla(m) for m in D.MASILLAS]
for a in actors:   # las masillas no llevan barra
    if a["flags"][ID]["tipo"] == "masilla":
        a["prototypeToken"].update(displayBars=0, displayName=0)

# ------------------------------------------------------------------ tablas
def tabla(clave):
    t = D.TABLAS[clave]
    res = [dict(_id=uid(f"res:{clave}:{i}"), type="text", name=f[0] if len(f) > 1 else str(i + 1), description=f"<p>{esc(f[-1])}</p>", img="icons/svg/d20-black.svg",
                range=[i + 1, i + 1], weight=1, drawn=False, flags={}) for i, f in enumerate(t["filas"])]
    return dict(_id=uid("tabla:" + clave), name=t["n"], img=img("assets/items/explota.webp", "icons/svg/d20-black.svg"), description="", formula=t["dado"], replacement=True, displayRoll=True,
                results=res, folder=FOLD[("RollTable", "Kill Mice")], sort=0, ownership=dict(default=0), flags={ID: dict(slug=clave)})


tablas = [tabla(k) for k in D.TABLAS]
TABLA_ID = {k: uid("tabla:" + k) for k in D.TABLAS}

# ------------------------------------------------------------------ diarios
FIG = {"mapa-jardin": "assets/scenes/mapa-jardin.webp", "mapa-casa": "assets/scenes/mapa-casa.webp"}


def fig_ruta(i):
    if i in FIG:
        return FIG[i]
    if i.startswith("esc-"):
        return f"assets/scenes/{i[4:]}.webp"
    if i.startswith("por-"):
        return f"assets/actors/portraits/{i[4:]}.webp"
    return f"assets/{i}.webp"


def fig_html(i, pos, cap):
    clase = ' class="derecha"' if pos in ("right", "left") else ""
    return f'<figure{clase}><img src="{img(fig_ruta(i), "")}" alt="">' + (f"<figcaption>{esc(cap)}</figcaption>" if cap else "") + "</figure>"


def tabla_html(clave, enlace=True):
    t = D.TABLAS[clave]
    cab = "".join(f"<th>{esc(c)}</th>" for c in (t["dado"],) + t["cols"])
    filas = "".join("<tr><td>%d</td>%s</tr>" % (i + 1, "".join(f"<td>{esc(x)}</td>" for x in f)) for i, f in enumerate(t["filas"]))
    link = f"<p>@UUID[RollTable.{TABLA_ID[clave]}]{{Tirar: {esc(t['n'])}}}</p>" if enlace else ""
    return f"<h3>{esc(t['n'])} · {t['dado']}</h3><table><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody></table>{link}"


def portador(slug):
    return ", ".join(p["n"] for p in D.TODOS if slug in p["inv"].values()) or "Todos"


def arsenal_html():
    filas = []
    for s in D.ARSENAL:
        o = D.OBJ[s]
        dano = o.get("dmg", "d10 / 1d6 + 2 Masillas") + (f" ({o['dmg2']} a dos patas)" if o.get("dmg2") else "") + (f" · +{o['mas']} Masillas" if o.get("mas") else "")
        filas.append(f"<tr><td><strong>{esc(o['n'])}</strong></td><td>{esc(o['d'])}</td><td>{esc(dano)}</td><td>{esc(portador(s))}</td></tr>")
    return "<h3>Arsenal reciclado</h3><table><thead><tr><th>Arma</th><th>A escala ratón</th><th>Daño</th><th>Quién la lleva</th></tr></thead><tbody>" + "".join(filas) + "</tbody></table>"


def listas_html():
    cab = "<tr><th>Ratón</th>" + "".join(f"<th>N.º {i}</th>" for i in range(1, 6)) + "</tr>"
    filas = "".join(f"<tr><td><strong>{esc(p['n'])}</strong></td>" + "".join(f"<td>{esc(t)}</td>" for t in D.lista_txt(p)) + "</tr>" for p in D.PJ)
    return f"<h3>Las seis Listas de Muerte</h3><table><thead>{cab}</thead><tbody>{filas}</tbody></table>"


def pnj_caja(n):
    atq = ", ".join(f"{a} {d if d != 'esp' else '(daño escalable)'}" for a, d in n["atq"]) or "sin armas"
    esp = "".join(f"<li><strong>{esc(a)}.</strong> {esc(b)}</li>" for a, b in n["esp"])
    en = ", ".join(p["n"] for p in D.TODOS if n["slug"] in p["lista"])
    return (f'<div class="mrkm-caja"><h4>@UUID[Actor.{uid("actor:" + n["slug"])}]{{{esc(n["n"])}}} · <em>{esc(n["apodo"])}</em></h4><p><strong>FUE {n["fue"]} · DES {n["des"]} · VOL {n["vol"]} · PG {n["pg"]}'
            f'{" · Armadura " + str(n["arm"]) if n["arm"] else ""}</strong> · {esc(atq)}</p><p>{esc(n["d"])}</p><ul>{esp}</ul>'
            + (f"<p><strong>En la Lista de:</strong> {esc(en)}</p>" if en else "") + f'<p><em>{esc(n["voz"])}</em> {esc(n["frase"])}</p></div>')


def pnj_html(args):
    acto = 1 if "1" in args else 2
    return "".join(pnj_caja(n) for n in D.PNJ if n["acto"] == acto and n["tipo"] != "aliado") + ("" if acto == 2 else pnj_caja(D.PNJ_POR["leon"]))


def masillas_html(args):
    m = D.MASILLAS[int(args) - 1]
    return f'<div class="mrkm-regla"><h4>{esc(m["n"])} · Masillas</h4><p>{esc(m["d"])} Despliega {m["por_pj"]} por jugador. Atacan como Turba: 1d6 a cada PJ acosado, 1d8 si son seis o más.</p></div>'


def secuencias_html(args):
    n = int(args)
    filas = "".join(f"<tr><td><strong>{esc(nom)}</strong></td>" + "".join(f"<td>{v}</td>" for v in vals) + "</tr>" for _, nom, vals in D.SECUENCIAS[n])
    return (f"<h3>Secuencias de la Pelea {'I' if n == 1 else 'II'}</h3><table><thead><tr><th>Personaje o grupo</th><th>Sec. 1</th><th>Sec. 2</th><th>Sec. 3</th><th>Sec. 4</th></tr></thead>"
            f"<tbody>{filas}<tr><td><strong>Cada PJ</strong></td><td colspan=\"4\">1d6 + mitad de DES al empezar cada secuencia</td></tr></tbody></table>")


def pj_caja(p):
    tec = "".join(f"<li><strong>{esc(a)}.</strong> {esc(b)}</li>" for a, b in p["tec"])
    return (f'<div class="mrkm-caja mrkm-pj" style="--pj: {p["color"]}"><h4>@UUID[Actor.{uid("actor:" + p["slug"])}]{{{esc(p["n"])}}} · <em>{esc(p["arq"])}</em></h4>'
            f'<p><strong>FUE {p["fue"]} · DES {p["des"]} · VOL {p["vol"]} · PG {p["pg"]} · {p["pepitas"]} pepitas</strong></p><p>{esc(p["aspecto"])}</p><ul>{tec}</ul>'
            f'<p><strong>Lista:</strong> {esc(" · ".join(D.lista_txt(p)))}</p></div>')


def especial(nombre, args):
    f = {"arsenal": lambda: arsenal_html(), "listas": lambda: listas_html(), "pnj": lambda: pnj_html(args), "masillas": lambda: masillas_html(args),
         "secuencias": lambda: secuencias_html(args), "pjs": lambda: "".join(pj_caja(p) for p in D.PJ), "rosa": lambda: pj_caja(D.ROSA)}
    return f.get(nombre, lambda: tabla_html(args))()


caps = md.capitulos(fig_html, especial)


def pagina(nombre, contenido, orden, tipo="text", src=None, titulo=True):
    p = dict(_id=uid(f"pag:{nombre}:{orden}"), name=nombre, type=tipo, sort=orden * 1000, title=dict(show=titulo, level=1), ownership=dict(default=-1), flags={})
    if tipo == "image":
        p.update(src=src, image=dict(caption=contenido))
    else:
        p.update(text=dict(content=contenido, format=1))
    return p


USO_FOUNDRY = """<p class="mrkm-kicker">00 · Cómo se juega en Foundry</p>
<p>Todo está en el grupo <strong>Kill Mice</strong> de la barra de herramientas de la izquierda (icono de katana) y en el <strong>Panel del DJ</strong>:</p>
<ul><li><strong>Los vengadores.</strong> Elige qué jugador lleva cada ratón: recibe la ficha y su dosier se le abre en pantalla. Rosa Muk es la reserva.</li>
<li><strong>La pelea.</strong> Despliega los Masillas del acto (3 o 2 por jugador), repártelos entre los ratones y avanza las cuatro secuencias. La Tigresa y El Sapo se curan solos al empezar cada una.</li>
<li><strong>Atacar.</strong> Cada jugador tiene el botón <em>Atacar (Kill Mice)</em>: elige arma y objetivo (Masillas o un Enemigo con Nombre marcado con la diana), marca sus técnicas y tira. El dado explota solo, los Masillas caen solos y el daño se aplica con su armadura.</li>
<li><strong>La Turba.</strong> En su hueco, pulsa <em>Turno de la Turba</em>: cada ratón acosado recibe su tarjeta con <em>Esquiva acrobática</em> o <em>Encajar el golpe</em>.</li>
<li><strong>La Lista.</strong> Se ve en el HUD de cada jugador. Al tachar un nombre, el módulo aplica el Respiro de sangre, la Inercia y, a quien dio el último golpe, la Moneda de Fortuna.</li></ul>
<p><strong>Compatibilidad.</strong> El ataque de Kill Mice escribe su propia tarjeta en el chat, así que no se mezcla con la automatización de daño de <em>MR- Mausritter en español</em> ni con <em>Mausritter Combat Carousel</em>: las tiradas normales de la hoja siguen funcionando igual con esos módulos. Si los tienes activos, usa la tirada normal para las salvaciones y el ataque de Kill Mice para el daño.</p>
<p><strong>Integraciones.</strong> Con <em>MR- Dirección</em> activo, sus escenas, música, motivos, efectos y figuras aparecen en su barra. Con <em>MR- Pizarra</em>, el botón <em>Pizarra de las Listas</em> monta el tablero de quién va a por quién.</p>"""

guia_paginas = [pagina("Kill Mice", "La Lista del Sobre Rojo.", 0, "image", ruta("assets/cover.webp")), pagina("Cómo se juega en Foundry", f'<div class="mrkm-diario">{USO_FOUNDRY}</div>', 1)]
for k, c in enumerate(caps):
    guia_paginas.append(pagina(c["titulo"], f'<div class="mrkm-diario"><p class="mrkm-kicker">{esc(c["kicker"])}</p>{c["html"]}</div>', k + 2))
diarios = [dict(_id=uid("diario:guia"), name="Kill Mice · Guía del DJ", pages=guia_paginas, folder=FOLD[("JournalEntry", "Kill Mice · DJ")], sort=0,
                ownership=dict(default=0), flags={ID: dict(guia=True)}, categories=[])]
RANURAS = (("pata", "Pata hábil"), ("torpe", "Pata torpe"), ("c1", "Cuerpo 1"), ("c2", "Cuerpo 2"), ("m1", "Mochila 1"), ("m2", "Mochila 2"))


def nombre_obj(s):
    return "Mi Lista de Muerte" if s == "lista" else D.OBJ[s]["n"]


def dosier_html(p):
    inv = "".join(f"<dt>{lbl}</dt><dd>{esc(nombre_obj(p['inv'][k])) if k in p['inv'] else '—'}</dd>" for k, lbl in RANURAS)
    op = "".join(f"<dt>{esc(D.NOMBRE[k])}</dt><dd>{esc(v)}</dd>" for k, v in p["opina"].items())
    tec = "".join(f"<dt>{esc(a)}</dt><dd>{esc(b)}</dd>" for a, b in p["tec"])
    foto = img(f"assets/actors/portraits/{p['slug']}.webp", "")
    return (f'<div class="mrkm-dosier" style="--pj: {p["color"]}"><span class="mrkm-sello">VENGANZA</span><img class="mrkm-foto" src="{foto}" alt="">'
            f'<h1>{esc(p["n"])}</h1><p><em>{esc(p["arq"])} · {esc(p["lema"])}</em></p>'
            f'<div class="mrkm-stats"><span>FUE {p["fue"]}</span><span>DES {p["des"]}</span><span>VOL {p["vol"]}</span><span>PG {p["pg"]}</span><span>{p["pepitas"]} pepitas</span></div>'
            + (f'<p><strong>Cuándo entra:</strong> {esc(p["cuando"])}</p>' if p.get("cuando") else "")
            + f'<h3>Tu vínculo con la boda</h3><p>{esc(p["vinculo"])}</p><h3>Mi Lista de Muerte</h3>{lista_html(p)}<h3>Técnicas</h3><dl>{tec}</dl>'
            + (f"<h3>Qué opinas de los demás</h3><dl>{op}</dl>" if op else "")
            + f"<h3>Lo que llevas (seis casillas)</h3><dl>{inv}</dl></div>")


for p in D.TODOS:
    paginas = [pagina("Dosier", dosier_html(p), 0, titulo=False)]
    if existe(f"assets/handouts/lista-{p['slug']}.webp"):
        paginas.append(pagina("Mi Lista de Muerte", "Cinco nombres que deben morir hoy.", 1, "image", ruta(f"assets/handouts/lista-{p['slug']}.webp")))
    diarios.append(dict(_id=uid("diario:dosier:" + p["slug"]), name=f"Dosier · {p['n']}", pages=paginas, folder=FOLD[("JournalEntry", "Dosieres")],
                        sort=D.TODOS.index(p), ownership=dict(default=0), flags={ID: dict(dosier=p["slug"])}, categories=[]))

tarjetas = "".join(f'<div class="mrkm-regla"><h4>{esc(c["n"])}</h4><p>{esc(c["d"])}</p><p><strong>Se quita:</strong> {esc(c["quita"])}</p></div>' for c in D.COND.values())
ayudas_pag = [pagina("El Sobre Rojo y el Medallón", "Medio Medallón Llave Fénix-Dragón.", 0, "image", ruta("assets/handouts/sobre-rojo.webp")),
              pagina("Plano · El Jardín del Banquete Koi", "J1 Pabellón · J2 Mesas · J3 Estanque · J4 Estatuas · J5 Setos", 1, "image", ruta("assets/scenes/mapa-jardin.webp")),
              pagina("Plano · La Casa de las Hojas Azules", "H1 Tatami · H2 Jaula · H3 Columna · H4 Pasarela · H5 Pila de 9 V", 2, "image", ruta("assets/scenes/mapa-casa.webp")),
              pagina("Tarjetas de estado", f'<div class="mrkm-diario">{tarjetas}</div>', 3)]
diarios.append(dict(_id=uid("diario:ayudas"), name="Ayudas de juego", pages=ayudas_pag, folder=FOLD[("JournalEntry", "Ayudas de juego")], sort=0,
                    ownership=dict(default=0), flags={ID: dict(ayudas=True)}, categories=[]))
PAG_CAP = {c["id"]: uid(f"pag:{c['titulo']}:{k + 2}") for k, c in enumerate(caps)}

# ------------------------------------------------------------------ sonido
MUSICA = [("tema", "Kill Mice (tema)"), ("banquete", "El banquete"), ("pelea1", "Pelea I"), ("huida", "Huida del altar"), ("casa", "La Casa de las Hojas Azules"),
          ("pelea2", "Pelea II"), ("siluetas", "Siluetas"), ("epilogo", "El último tachón")]
MOTIVOS = [("tension", "Tensión", "hourglass-half"), ("venganza", "Venganza", "skull"), ("ralenti", "Cámara lenta", "feather"),
           ("triunfo", "Triunfo", "trophy"), ("derrota", "Derrota", "heart-crack"), ("calma", "Calma", "leaf")]
AMBIENTES = [("jardin", "Jardín y estanque"), ("neon", "Neón y lluvia"), ("casa", "Santuario y canal")]
EFECTOS = [("disparo", "Disparo", "gun"), ("katana", "Katana", "khanda"), ("rafaga", "Ráfaga", "burst"), ("kachink", "¡KA-CHINK!", "hand-fist"),
           ("petardo", "Petardo", "bomb"), ("gong", "Gong", "drum"), ("sirena", "Sirena Roja", "bell"), ("tachon", "Tachón", "marker"),
           ("bramido", "Bramido", "volume-high"), ("cristal", "Cristal", "glass-water"), ("cadena", "Cadena", "link"), ("apagon", "Apagón azul", "lightbulb"),
           ("sirenas-guardia", "Sirenas de la Guardia", "tower-broadcast"), ("discurso", "Brindis", "champagne-glasses")]


def sonido(carpeta, slug, nombre, canal, repetir, vol):
    return dict(_id=uid(f"sonido:{carpeta}:{slug}"), name=nombre, description="", path=ruta(f"assets/audio/{carpeta}/{slug}.ogg"), channel=canal, playing=False, pausedTime=None,
                repeat=repetir, volume=vol, fade=2000 if repetir else None, sort=0, flags={ID: dict(slug=f"{carpeta}-{slug}")})


def lista(nombre, carpeta, elems, canal, repetir, vol, orden):
    return dict(_id=uid("lista:" + carpeta), name=nombre, description="", mode=0, channel=canal, sounds=[sonido(carpeta, e[0], e[1], canal, repetir, vol) for e in elems],
                playing=False, folder=None, sorting="m", sort=orden, seed=None, fade=None, ownership=dict(default=0), flags={ID: dict(lista=carpeta)})


playlists = [lista("Kill Mice · Música", "music", MUSICA, "music", True, 0.5, 0), lista("Kill Mice · Motivos", "moods", MOTIVOS, "music", True, 0.5, 1),
             lista("Kill Mice · Ambiente", "ambient", AMBIENTES, "environment", True, 0.4, 2), lista("Kill Mice · Efectos", "sfx", EFECTOS, "interface", False, 0.8, 3)]

# ------------------------------------------------------------------ escenas
# (orden, slug, nombre, música, capítulo de la guía, reparto de figuras, ambiente)
VENG = [p["slug"] for p in D.PJ]
ESC = [(0, "jardin", "El Jardín del Estanque Koi", "banquete", "acto1", VENG + ["rosa", "leon"], "jardin"),
       (1, "masacre", "Pelea I · Algo prestado", "pelea1", "acto1", ["sheng", "tonyma", "alas", "leung", "rosa"], "jardin"),
       (2, "mapa-jardin", "Plano · El Jardín del Banquete", "pelea1", "escenario1", [], "jardin"),
       (3, "wanchai", "Interludio · Wan Chai", "huida", "interludio", [], "neon"),
       (4, "callejon", "Interludio · El maletero", "huida", "interludio", ["sofie", "lau"], "neon"),
       (5, "casa", "La Casa de las Hojas Azules", "casa", "escenario2", ["elle", "pei"], "neon"),
       (6, "santuario", "Pelea II · El santuario", "pelea2", "acto2", ["bill", "oren", "budd"], "casa"),
       (7, "mapa-casa", "Plano · El santuario", "pelea2", "escenario2", [], "casa"),
       (8, "siluetas", "Siluetas sobre fondo azul", "siluetas", "acto2", [], "casa"),
       (9, "columna", "La Columna del Fénix y el Dragón", "epilogo", "finales", ["bill"], "casa"),
       (10, "tejados", "Fuga por los tejados", "huida", "acto2", [], "neon"),
       (11, "boda", "Epílogo · La foto de boda", "epilogo", "finales", ["rosa", "leon"], "jardin"),
       (12, "tren", "Postcréditos · El tren del norte", "epilogo", "finales", [], None)]
MAPAS = {"mapa-jardin", "mapa-casa"}


def escena(orden, slug, nombre, musica, cap, _reparto, _amb):
    mapa = slug in MAPAS
    w, h = (2304, 1536) if mapa else (1920, 1080)
    mx, my, mw, mh = marca.caja_animada(w, h)
    tiles = [dict(_id=uid(f"tile:{slug}:marca"), texture=dict(src=ruta("assets/brand/mr-marca.webm"), scaleX=1, scaleY=1, tint="#ffffff", alphaThreshold=0, fit="fill", anchorX=0.5, anchorY=0.5),
                  x=mx, y=my, width=mw, height=mh, elevation=0, sort=0, rotation=0, alpha=1, hidden=False, locked=True, restrictions=dict(light=False, weather=False),
                  occlusion=dict(mode=0, alpha=0), video=dict(loop=True, autoplay=True, volume=0), flags={})]
    return dict(_id=uid("escena:" + slug), name=nombre, active=False, navigation=orden < 11, navOrder=orden, navName=nombre,
                background=dict(src=ruta(f"assets/scenes/{slug}.webp")), width=w, height=h, padding=0, backgroundColor="#121212",
                grid=dict(type=1 if mapa else 0, size=96 if mapa else 100, style="solidLines", thickness=1, color="#000000", alpha=0.15 if mapa else 0, distance=1, units="m"),
                initial=None, tokenVision=False, fog=dict(exploration=False), environment=dict(darknessLevel=0, globalLight=dict(enabled=True)),
                thumb=img(f"assets/scenes/thumbs/{slug}.webp", None), tiles=tiles, tokens=[], drawings=[], lights=[], notes=[], sounds=[], templates=[], walls=[], regions=[],
                journal=diarios[0]["_id"], journalEntryPage=PAG_CAP.get(cap), playlist=playlists[0]["_id"], playlistSound=uid(f"sonido:music:{musica}"),
                folder=FOLD[("Scene", "Kill Mice")], sort=orden * 1000, ownership=dict(default=0), flags={ID: dict(slug=slug, orden=orden, mapa=mapa, acto=2 if orden >= 5 else 1)})


escenas = [escena(*e) for e in ESC]

# ------------------------------------------------------------------ macros
MAC = [("Panel del DJ", "panel()", "assets/actors/portraits/bill.webp"), ("Atacar (Kill Mice)", "atacar()", "assets/items/katana.webp"),
       ("Turno de la Turba", "turnoTurba()", "assets/items/masilla.webp"), ("Nueva secuencia", "nuevaSecuencia()", "assets/items/inercia.webp"),
       ("Ataque de Bill", "ataqueBill()", "assets/actors/portraits/bill.webp"), ("Pizarra de las Listas", "abrirPizarra()", "assets/items/lista.webp"),
       ("Importar la aventura", "importarAventura()", "assets/cover.webp")]
macros = [dict(_id=uid("macro:" + n), name=n, type="script", img=img(i, "icons/svg/dice-target.svg"), scope="global", command=f'game.modules.get("{ID}").api.{c};',
               author=uid("autor"), folder=FOLD[("Macro", "Kill Mice")], sort=k * 1000, ownership=dict(default=0), flags={ID: dict(macro=True)}) for k, (n, c, i) in enumerate(MAC)]

adv = dict(_id=uid("adventure"), name="MR- Kill Mice", img=ruta("assets/cover.webp"),
           caption="<p>La Lista del Sobre Rojo. Venganza ratonil para Mausritter.</p>",
           description="<p>Seis ratones, cinco nombres cada uno y una boda que salta por los aires. Incluye la guía del DJ, los dosieres, las Listas de Muerte, las reglas de Masillas, Turba y dados explosivos, escenas, música y herramientas de mesa.</p>",
           actors=actors, combats=[], items=items, journal=diarios, scenes=escenas, tables=tablas, macros=macros, cards=[], playlists=playlists, folders=folders,
           folder=None, sort=0, flags={ID: dict(version=VERSION)})
(R / "_data").mkdir(exist_ok=True)
json.dump([adv], open(R / "_data" / "aventura.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ paquete de MR- Dirección
def fl(slug):
    return {"flag": [ID, "slug", slug]}


# Solo lo que puede pasar en cualquier momento va en la barra global; el resto, en la escena donde ocurre.
GLOBALES = {"disparo", "katana"}
EFECTOS_ESCENA = {
    "jardin": ["discurso", "gong"],
    "masacre": ["rafaga", "kachink", "cristal", "sirena", "tachon"],
    "mapa-jardin": ["rafaga", "kachink", "cristal", "sirena", "tachon", "sirenas-guardia"],
    "wanchai": ["sirenas-guardia"],
    "callejon": ["tachon", "sirena"],
    "casa": ["petardo", "cadena"],
    "santuario": ["gong", "cadena", "bramido", "cristal", "petardo", "tachon"],
    "mapa-casa": ["cadena", "bramido", "cristal", "petardo", "apagon", "tachon"],
    "siluetas": ["apagon", "cadena", "tachon"],
    "columna": ["gong", "tachon"],
    "tejados": ["sirenas-guardia", "petardo"],
    "boda": ["discurso"],
}
_EF = {i: (l, ic) for i, l, ic in EFECTOS}
assert all(e in _EF for v in EFECTOS_ESCENA.values() for e in v), "efecto de escena desconocido"
cues = lambda slug: [dict(label=_EF[e][0], icon=_EF[e][1], sound=fl(f"sfx-{e}")) for e in EFECTOS_ESCENA.get(slug, [])]
dir_escenas = []
for e, s in zip(ESC, escenas):
    orden, slug, nombre, musica, cap, reparto, amb = e
    dir_escenas.append(dict(ref=fl(slug), order=orden, name=nombre, reading={"uuid": f"JournalEntry.{diarios[0]['_id']}.JournalEntryPage.{PAG_CAP[cap]}"},
                            music=fl(f"music-{musica}"), motifs=None, cues=cues(slug), ambient=fl(f"ambient-{amb}") if amb else None,
                            figures=[dict(ref=fl(a), label="") for a in reparto], handouts=[], notes="", thumb=s["thumb"] or "",
                            stage=dict(eye=0.5, anchors=[[0.2, 0.9], [0.35, 0.92], [0.5, 0.93], [0.65, 0.92], [0.8, 0.9]])))
direccion = dict(schema=1, id=ID, title="MR- Kill Mice", version=VERSION, author="Manu Romera", license="CC BY-NC-SA 4.0",
                 settings=dict(fade=3, motifs=[dict(id=i, label=l, icon=ic, music=fl(f"moods-{i}")) for i, l, ic in MOTIVOS],
                               effects=[dict(id=i, label=l, icon=ic, sound=fl(f"sfx-{i}")) for i, l, ic in EFECTOS if i in GLOBALES],
                               markers=dict(milestones=[dict(id="estallido", label="Estalla la boda"), dict(id="secuestro", label="Los novios han desaparecido"),
                                                        dict(id="pista", label="Rumbo a Wan Chai"), dict(id="jaula", label="La jaula, abierta"),
                                                        dict(id="bill", label="BILL, tachado"), dict(id="medallon", label="El medallón tiene dueño")],
                                            clocks=[])),
                 scenes=dir_escenas)
(R / "content").mkdir(exist_ok=True)
json.dump(direccion, open(R / "content" / "direccion-es.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
json.dump({str(k): [list(f) for f in v] for k, v in D.SECUENCIAS.items()}, open(R / "content" / "secuencias.json", "w", encoding="utf8"), ensure_ascii=False)

# ------------------------------------------------------------------ pizarra «Las Listas de Muerte» para MR- Pizarra
P = []
for k, p in enumerate(D.PJ):
    P.append(dict(ref=p["slug"], type="entity", name=p["n"], kind="Actor", frame="polaroid", showToAll=True, layer="vengadores", x=300 + k * 420, y=240, w=220, rot=[-4, 3, -2, 4, -3, 2][k]))
FILA = {"teniente": 760, "propio": 1120, "campeon": 1480, "jefe": 1480}
xs = {}
for n in D.PNJ:
    if n["tipo"] == "aliado":
        continue
    y = FILA[n["tipo"]]
    x = xs.get(y, 260)
    P.append(dict(ref=n["slug"], type="entity", name=n["n"], kind="Actor", frame="foto-instantanea-80", layer="acto1" if n["acto"] == 1 else "acto2", x=x, y=y, w=170, rot=(len(P) % 5) - 2))
    xs[y] = x + 400
P.append(dict(ref="sello", type="stamp", layer="acto2", kind="marco-circular-rojo", text="CINCO NOMBRES", x=2350, y=1560, w=260, rot=-8))
COL = ["rojo", "ambar", "ambar", "violeta", "negro"]
L = [{"from": p["slug"], "to": s, "color": COL[i], "style": "solido" if i == 0 else "punteado", "label": "n.º 1" if i == 0 else ""}
     for p in D.PJ for i, s in enumerate(p["lista"])]
pizarra = {"format": "mr-pizarra-import", "version": 1, "mode": "board", "title": "Kill Mice · Las Listas de Muerte", "background": "corcho-claro",
           "pinPreset": {"pin": "auto", "color": "", "layout": "auto"},
           "layers": [{"ref": "vengadores", "name": "Los vengadores", "revealed": True}, {"ref": "acto1", "name": "Mares Dorados", "revealed": True},
                      {"ref": "acto2", "name": "Escuadrón Víbora", "revealed": False}],
           "items": P, "links": L}
json.dump(pizarra, open(R / "content" / "pizarra-es.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)

faltan = sorted({p for p in (x.rstrip("\\") for x in json.dumps(adv).split('"')) if p.startswith(f"modules/{ID}/assets/") and not p.endswith(".ogg") and not existe(p[len(f'modules/{ID}/'):])})
print(f"{len(actors)} actores · {len(items)} objetos · {len(diarios)} diarios · {len(escenas)} escenas · {len(tablas)} tablas · {len(macros)} macros · {sum(len(p['sounds']) for p in playlists)} sonidos")
print("imágenes que faltan:", len(faltan), *faltan[:80], sep="\n  ")
