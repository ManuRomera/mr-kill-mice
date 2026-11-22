#!/usr/bin/env python3
"""Banda sonora sintética de Kill Mice: funk de los setenta, koto, taiko y gong (escalas «in» e «hirajoshi»),
con bajo, batería y metales; ambientes del jardín, el neón y la Casa, y efectos. Bucles sin costura (la cola se suma al principio), −26 LUFS, Ogg Opus.
Es música de sustitución: cualquier pista se puede reemplazar por otra con el mismo nombre.
Uso: python3 tools/audio.py [clave ...]   (claves: music/tema, moods/paranoia, sfx/disparo…; sin nada, todo)"""
import subprocess, sys, tempfile, wave
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parent.parent
OUT = R / "assets" / "audio"
SR = 44100
rng = np.random.default_rng(1)
ESC = {"men": [0, 2, 3, 5, 7, 8, 10], "dor": [0, 2, 3, 5, 7, 9, 10], "blu": [0, 3, 5, 6, 7, 10], "fri": [0, 1, 3, 5, 7, 8, 10], "may": [0, 2, 4, 5, 7, 9, 11], "in": [0, 1, 5, 7, 8], "hira": [0, 2, 3, 7, 8]}


def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR


def env(n, a=0.005, r=0.05, dec=None):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:min(na, n)] = np.linspace(0, 1, min(na, n))
    if dec:
        e *= np.exp(-np.arange(n) / SR / dec)
    e[max(0, n - nr):] *= np.linspace(1, 0, min(nr, n))
    return e


def lp(x, fc):
    """Paso bajo de un polo por FFT cuando el corte es fijo; por muestras cuando varía (wah)."""
    if np.ndim(fc) == 0:
        X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
        return np.fft.irfft(X / (1 + 1j * f / fc), len(x))
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y


def saw(f, t): return 2 * ((f * t) % 1) - 1
def ruido(d): return rng.standard_normal(int(d * SR))


# ---- instrumentos
def kick(d=0.4):
    t = tt(d); f = 45 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def snare(d=0.25):
    t = tt(d); n = rng.standard_normal(len(t))
    return (0.7 * n * np.exp(-t * 22) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)) * 0.8


def hat(d=0.06, abierto=False):
    t = tt(0.3 if abierto else d); n = rng.standard_normal(len(t))
    n = n - lp(n, 6000)
    return n * np.exp(-t * (9 if abierto else 60)) * 0.35


def bajo(m, d):
    t = tt(d); f = hz(m)
    return lp(saw(f, t) * 0.6 + np.sin(2 * np.pi * f * t), 900) * env(len(t), 0.004, 0.04, 0.5) * 0.9


def epiano(m, d):
    t = tt(d); f = hz(m)
    x = np.sin(2 * np.pi * f * t + 1.2 * np.sin(2 * np.pi * f * t) * np.exp(-t * 6)) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
    return x * env(len(t), 0.003, 0.15, 1.6) * (1 + 0.15 * np.sin(2 * np.pi * 5 * t)) * 0.35


def wah(m, d, vel=4.0):
    t = tt(d); f = hz(m)
    fc = 500 + 1800 * (0.5 + 0.5 * np.sin(2 * np.pi * vel * t - np.pi / 2))
    return lp(lp(saw(f, t), fc), fc) * env(len(t), 0.002, 0.03, 0.25) * 0.5


def organo(m, d):
    t = tt(d); f = hz(m)
    x = sum(a * np.sin(2 * np.pi * f * k * t) for k, a in ((0.5, .5), (1, 1), (2, .5), (3, .3), (4, .2)))
    return x * env(len(t), 0.02, 0.2) * (1 + 0.2 * np.sin(2 * np.pi * 6 * t)) * 0.12


def cuerdas(m, d):
    t = tt(d); f = hz(m)
    return lp(sum(saw(f * (1 + dt), t) for dt in (-0.004, 0, 0.005)), 1600) * env(len(t), 0.5, 0.6) * 0.08


def metal(m, d):
    t = tt(d); f = hz(m)
    x = saw(f, t) + 0.5 * saw(f * 1.003, t)
    fc = 300 + 3500 * np.exp(-t * 8)
    return lp(x, fc) * env(len(t), 0.01, 0.08) * 0.25


def vibra(m, d):
    t = tt(d); f = hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 8)
    return x * env(len(t), 0.002, 0.2, 1.2) * (1 + 0.35 * np.sin(2 * np.pi * 5.5 * t)) * 0.3


def koto(m, d):
    """Cuerda pulsada: Karplus-Strong."""
    f = hz(m); n = int(d * SR); p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p); out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return out * env(n, 0.001, 0.05) * 0.5


def taiko(d=0.8):
    t = tt(d); f = 70 + 60 * np.exp(-t * 18)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) + lp(ruido(d), 600) * np.exp(-t * 25) * .4) * 1.1


def gong(d=6):
    t = tt(d)
    return sum(a * np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * .7 * t)) * np.exp(-t * dc) for f, a, dc in ((92, 1, .5), (147, .6, .7), (233, .4, 1), (377, .25, 1.6), (611, .15, 2))) * env(len(t), 0.005, 1) * .5


def silbido(m, d):
    t = tt(d); f = hz(m) * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * t))
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) + lp(ruido(d), 3000) * .05) * env(len(t), 0.06, 0.2) * 0.35


def poner(pista, x, s, g=1.0):
    i = int(s * SR)
    if i >= len(pista):
        return
    n = min(len(x), len(pista) - i)
    pista[i:i + n] += x[:n] * g


# ---- compositor: patrones de funk/noir sobre una progresión de grados
def tema(cfg):
    bpm, compases = cfg["bpm"], cfg.get("compases", 16)
    neg = 60 / bpm; comp = 4 * neg; dur = compases * comp
    pista = np.zeros(int((dur + 5) * SR))
    raiz, esc, prog = cfg["raiz"], ESC[cfg.get("escala", "men")], cfg["prog"]
    g = lambda grado, octv=0: raiz + esc[grado % len(esc)] + 12 * (grado // len(esc) + octv)
    swing = cfg.get("swing", 0.0)
    for c in range(compases):
        t0, gr = c * comp, prog[c % len(prog)]
        if cfg.get("bateria", True):
            for b in range(4):
                if b == 0 or (cfg.get("bombo2") and b == 2):
                    poner(pista, kick(), t0 + b * neg, 0.9)
                if b in (1, 3):
                    poner(pista, snare(), t0 + b * neg, cfg.get("caja", 0.5))
                for s in range(2):
                    poner(pista, hat(abierto=(s == 1 and b == 3)), t0 + b * neg + s * neg / 2 + (swing * neg / 2 if s else 0), 0.6)
            if cfg.get("fantasma"):
                poner(pista, snare(0.08), t0 + 2.75 * neg, 0.15)
        elif cfg.get("pulso"):
            for b in range(4):
                poner(pista, kick(0.3), t0 + b * neg, 0.35)
        for (b, inter, d) in cfg.get("bajo", [(0, 0, .5), (1.5, 0, .25), (2, 4, .5), (3, 7, .25), (3.5, 6, .25)]):
            poner(pista, bajo(g(gr, -2) + inter - (12 if cfg.get("bajo_grave") else 0), d * neg), t0 + b * neg)
        inst = cfg.get("acorde", "epiano")
        fn = {"epiano": epiano, "organo": organo, "cuerdas": cuerdas, "vibra": vibra}[inst]
        for b in cfg.get("golpes", [0.5, 2.5]) if inst not in ("organo", "cuerdas") else [0]:
            for k in (0, 2, 4, 6):
                poner(pista, fn(g(gr + k), comp * 1.02 if inst in ("organo", "cuerdas") else neg * 1.5), t0 + b * neg)
        if cfg.get("wah"):
            for s in range(8):
                if (c * 8 + s) % 3 != 2:
                    poner(pista, wah(g(gr + (s % 3) * 2), neg / 2.2, cfg["wah"]), t0 + s * neg / 2, 0.5)
        if cfg.get("melodia") and c % 4 in (1, 3):
            voz = {"metal": metal, "vibra": vibra, "epiano": epiano, "koto": koto, "silbido": silbido}[cfg.get("voz", "metal")]
            for (b, gm, d) in cfg["melodia"]:
                poner(pista, voz(g(gr + gm, 1), d * neg), t0 + b * neg, 0.7)
        if cfg.get("taiko"):
            for b in cfg["taiko"]:
                poner(pista, taiko(), t0 + b * neg, 0.8)
        if cfg.get("koto"):
            for s8 in range(8):
                if (c + s8) % 3 != 1:
                    poner(pista, koto(g(gr + (s8 * 2) % 5, 1), neg * 1.2), t0 + s8 * neg / 2, 0.5)
        if cfg.get("gong") and c % 8 == 0:
            poner(pista, gong(), t0, 0.6)
        if cfg.get("pad"):
            for k in (0, 2, 4):
                poner(pista, cuerdas(g(gr + k), comp * 1.02), t0, 0.7)
    return pista, dur


def cerrar_bucle(pista, dur):
    n = int(dur * SR)
    out = pista[:n].copy()
    cola = pista[n:]
    out[:min(len(cola), n)] += cola[:n]
    return out


# ---- ambientes y efectos


def jardin(d=60):
    out = lp(ruido(d), 500) * 0.35   # agua del estanque
    for _ in range(18):   # pájaros
        tg = tt(0.25); f = 2600 + 900 * np.sin(np.pi * tg / 0.25 * 3)
        poner(out, 0.06 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tg), 0.02, 0.1), rng.uniform(0, d - 1))
    for _ in range(10):   # murmullo de invitados
        poner(out, (lp(ruido(2), 900) - lp(ruido(2), 200)) * env(int(2 * SR), 0.5, 0.8) * .5, rng.uniform(0, d - 3))
    return out


def neon(d=50):
    t = tt(d)
    x = lp(ruido(d), 2500) * 0.5 + sum(a * np.sin(2 * np.pi * 60 * k * t) for k, a in ((1, .15), (2, .1), (3, .06)))
    for _ in range(6):   # coches lejanos
        tc = tt(4); poner(x, lp(ruido(4), 300) * np.sin(np.pi * tc / 4) * .6, rng.uniform(0, d - 5))
    return x


def casa(d=50):
    t = tt(d)
    x = lp(ruido(d), 250) * 0.8 + 0.25 * np.sin(2 * np.pi * 41 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * .1 * t))
    for _ in range(8):   # gotas en el canal
        poner(x, np.sin(2 * np.pi * 900 * tt(.15)) * np.exp(-tt(.15) * 30) * .3, rng.uniform(0, d - 1))
    return x


def sfx(nombre):
    if nombre == "disparo":
        t = tt(1.2); return lp(ruido(1.2) * np.exp(-t * 9) + kick(1.2) * 1.5, 3000)
    if nombre == "rafaga":
        x = np.zeros(int(1.6 * SR)); t = tt(.3)
        for k in range(9):
            poner(x, lp(ruido(.3) * np.exp(-t * 18) + kick(.3), 3500), k * 0.11)
        return x
    if nombre == "katana":
        t = tt(1.4); f = 3200 + 2000 * np.exp(-t * 3)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.5) * .4 + (ruido(1.4) - lp(ruido(1.4), 4000)) * np.exp(-t * 14) * .6)
    if nombre == "kachink":
        x = np.zeros(int(0.7 * SR)); poner(x, hat(0.04) * 5, 0); poner(x, lp(kick(0.1), 2000) * 2 + hat(0.05) * 5, 0.22); return x
    if nombre == "petardo":
        t = tt(2); x = lp(ruido(2) * np.exp(-t * 4), 1800) + kick(2) * 2
        for _ in range(12):
            poner(x, hat(0.03) * 2, rng.uniform(0.2, 1.6))
        return x
    if nombre == "gong":
        return gong(7)
    if nombre == "sirena":   # el silbido de alarma de la venganza
        t = tt(4); f = 900 + 500 * (np.sin(2 * np.pi * 1.2 * t) > 0)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.05, 0.6) * .5 + taiko(4) * .3
    if nombre == "sirenas-guardia":
        t = tt(5); f = 650 + 250 * np.sin(2 * np.pi * 0.5 * t)
        return lp(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.5, 1), 2500) * .5
    if nombre == "tachon":
        t = tt(0.9); n = ruido(0.9)
        x = (n - lp(n, 1500)) * env(len(t), 0.02, 0.2) * (0.5 + 0.5 * np.sin(np.pi * t / 0.9)) * .5
        poner(x, taiko(0.6) * .8, 0.6)
        return x
    if nombre == "bramido":
        t = tt(2.5); f = 70 + 15 * np.sin(2 * np.pi * 3 * t)
        return lp(saw(f, t) + ruido(2.5) * .3, 900) * env(len(t), 0.1, 0.6) * .8
    if nombre == "cristal":
        x = np.zeros(int(2 * SR))
        for _ in range(26):
            tc = tt(.4); poner(x, np.sin(2 * np.pi * rng.uniform(2500, 7000) * tc) * np.exp(-tc * rng.uniform(8, 20)) * .2, rng.uniform(0, 1.2))
        poner(x, lp(ruido(.3), 5000) * np.exp(-tt(.3) * 10), 0)
        return x
    if nombre == "cadena":
        x = np.zeros(int(1.5 * SR))
        for k in range(10):
            poner(x, hat(0.05) * 3 + np.sin(2 * np.pi * 2200 * tt(.05)) * np.exp(-tt(.05) * 60) * .3, k * 0.09 + rng.uniform(0, .03))
        return x
    if nombre == "apagon":
        t = tt(3); x = np.zeros(int(3 * SR)); poner(x, ruido(.08) * 1.5, 0)
        return x + lp(saw(55 * (1 - 0.3 * t / 3), t), 400) * env(len(t), 0.01, 1.5) * .6
    if nombre == "discurso":   # brindis: copas y murmullo
        x = np.zeros(int(3 * SR))
        for k in range(5):
            tc = tt(.8); poner(x, sum(np.sin(2 * np.pi * f * tc) for f in (2100, 3300)) * np.exp(-tc * 6) * .2, 0.3 + k * 0.25)
        poner(x, (lp(ruido(3), 900) - lp(ruido(3), 200)) * .3, 0)
        return x
    raise KeyError(nombre)


MUSICA = {  # pistas de escena
 "tema": dict(bpm=100, raiz=50, escala="in", prog=[0, 0, 3, 3, 0, 0, 4, 1], wah=4, taiko=[0, 2.5], gong=True, melodia=[(0, 4, 1.5), (1.5, 3, .5), (2, 0, 2)], voz="silbido", swing=.1),
 "banquete": dict(bpm=84, raiz=55, escala="hira", prog=[0, 2, 3, 0], acorde="epiano", golpes=[0, 2], koto=True, bateria=False, pulso=True, bajo=[(0, 0, 1), (2, 3, 1)]),
 "pelea1": dict(bpm=138, raiz=52, escala="in", prog=[0, 0, 1, 3], wah=7, bombo2=True, caja=.8, taiko=[0, 1, 2, 3], melodia=[(0, 0, .5), (.5, 1, .5), (1, 3, .5), (1.5, 4, 1)]),
 "huida": dict(bpm=124, raiz=50, escala="blu", prog=[0, 0, 2, 3], wah=6, bombo2=True, caja=.7, melodia=[(0, 0, .5), (.5, 2, .5), (1, 3, .5), (1.5, 4, 1)]),
 "casa": dict(bpm=70, raiz=45, escala="in", prog=[0, 1, 0, 3], acorde="cuerdas", bateria=False, pulso=True, koto=True, gong=True, bajo=[(0, 0, 2), (2, 1, 2)]),
 "pelea2": dict(bpm=146, raiz=48, escala="in", prog=[0, 1, 0, 4], wah=8, bombo2=True, caja=.9, taiko=[0, .5, 2, 2.5], gong=True, melodia=[(0, 4, .5), (.5, 3, .5), (1, 1, 1)], voz="metal"),
 "siluetas": dict(bpm=92, raiz=47, escala="in", prog=[0, 0, 1, 1], acorde="organo", taiko=[0, 2], melodia=[(0, 4, 3)], voz="silbido", caja=.4),
 "epilogo": dict(bpm=78, raiz=51, escala="hira", prog=[0, 3, 2, 0], acorde="epiano", koto=True, bateria=False, pad=True, melodia=[(0, 4, 2), (2, 2, 2)], voz="silbido"),
}
MOTIVOS = {
 "tension": dict(bpm=80, raiz=45, escala="in", prog=[0, 0, 0, 1], acorde="cuerdas", bateria=False, pulso=True, taiko=[0], bajo=[(0, 0, .5), (1, 0, .5), (2, 0, .5), (3, 0, .5)]),
 "venganza": dict(bpm=96, raiz=46, escala="in", prog=[0, 1, 0, 1], wah=5, taiko=[0, 2], melodia=[(0, 4, 2), (2, 3, 2)], voz="silbido"),
 "ralenti": dict(bpm=56, raiz=45, escala="hira", prog=[0, 2], acorde="cuerdas", bateria=False, koto=True, bajo=[(0, 0, 4)]),
 "triunfo": dict(bpm=108, raiz=53, escala="may", prog=[0, 3, 4, 0], acorde="organo", wah=4, gong=True, melodia=[(0, 4, .5), (.5, 5, .5), (1, 7, 2)]),
 "derrota": dict(bpm=62, raiz=45, escala="men", prog=[0, 5, 3, 4], acorde="cuerdas", bateria=False, bajo=[(0, 0, 4)], melodia=[(0, 4, 2), (2, 2, 2)], voz="koto"),
 "calma": dict(bpm=72, raiz=50, escala="hira", prog=[0, 3, 0, 2], acorde="epiano", koto=True, bateria=False, pad=True),
}
EFECTOS = ["disparo", "katana", "rafaga", "kachink", "petardo", "gong", "sirena", "tachon", "bramido", "cristal", "cadena", "apagon", "sirenas-guardia", "discurso"]


def escribe(x, destino, bucle):
    destino.parent.mkdir(parents=True, exist_ok=True)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        with wave.open(f.name, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((x * 32767).astype(np.int16).tobytes())
        filtro = "loudnorm=I=-26:TP=-2:LRA=11" if bucle else "loudnorm=I=-20:TP=-1.5"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f.name, "-af", filtro, "-ar", "48000", "-c:a", "libopus", "-b:a", "96k", str(destino)], check=True)


def construir(clave):
    carpeta, nombre = clave.split("/")
    if carpeta in ("music", "moods"):
        pista, dur = tema((MUSICA if carpeta == "music" else MOTIVOS)[nombre])
        x = cerrar_bucle(pista, dur)
        if dur < 45:   # bucles cortos: se repiten hasta ~1 min
            x = np.tile(x, int(np.ceil(60 / dur)))
        escribe(x, OUT / carpeta / f"{nombre}.ogg", True)
    elif carpeta == "ambient":
        d = 50
        escribe(cerrar_bucle({"jardin": jardin, "neon": neon, "casa": casa}[nombre](d + 3), d), OUT / carpeta / f"{nombre}.ogg", True)
    else:
        escribe(sfx(nombre), OUT / "sfx" / f"{nombre}.ogg", False)
    print("hecho", clave, flush=True)


TODO = [f"music/{k}" for k in MUSICA] + [f"moods/{k}" for k in MOTIVOS] + ["ambient/jardin", "ambient/neon", "ambient/casa"] + [f"sfx/{k}" for k in EFECTOS]
if __name__ == "__main__":
    for c in sys.argv[1:] or TODO:
        construir(c)
