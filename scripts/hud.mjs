// HUD «La Lista»: acto, secuencia, reloj de la Sirena Roja y orden de actuación para todos; la Lista de Muerte, las monedas
// y los Masillas encima para cada jugador; el reparto de Masillas para el DJ. Se arrastra con el botón derecho.
import { ID, t, esc, estado, alRecibir, retrato, pg, enJuego, listaDe, tachadosDe, porSlug } from "./estado.mjs";
import { atacar, turnoTurba, nuevaSecuencia, moverMasilla, totalMasillas, gastarMoneda, sirenaRoja, moverReloj } from "./reglas.mjs";

let raiz = null, ultimoAviso = 0;
const pips = (n, max) => Array.from({ length: max }, (_, i) => `<span class="mrkm-pip ${i < n ? "on" : ""}"></span>`).join("");
const miActor = () => game.user.character ?? null;

function listaHtml(a, e) {
  const tach = tachadosDe(a, e);
  return `<ol class="mrkm-hud-lista">${listaDe(a).map((s, i) => {
    const n = s === "bill" ? "BILL «MANDÍBULA» JANG" : porSlug(s)?.name ?? s;
    return `<li class="${tach.includes(s) ? "tachado" : ""}" data-n="${i + 1}"><span>${esc(n)}</span></li>`;
  }).join("")}</ol>`;
}

function html() {
  const e = estado(), gm = game.user.isGM, yo = miActor();
  const cabecera = `<div class="mrkm-hud-cab"><span class="mrkm-hud-vol">${t(`Hud.Vol${e.acto}`)}</span>
    <span class="mrkm-hud-sec" data-tooltip="${esc(t("Hud.SecuenciaAyuda"))}">${e.secuencia ? t("Hud.Secuencia", { n: e.secuencia }) : t("Hud.SinPelea")}</span>
    <span class="mrkm-pips" role="img" aria-label="${esc(t("Hud.Reloj", { n: e.reloj }))}" data-tooltip="${esc(t("Hud.RelojAyuda"))}">${pips(e.reloj, 6)}</span>
    ${gm ? `<span class="mrkm-mm"><button type="button" data-a="reloj-" aria-label="${t("Hud.Menos")}">−</button><button type="button" data-a="reloj+" aria-label="${t("Hud.Mas")}">+</button></span>` : ""}</div>`;
  const ini = e.iniciativa?.length ? `<ol class="mrkm-hud-ini">${e.iniciativa.slice(0, 10).map((o) => `<li class="${o.pj ? "pj" : ""}"><b>${o.v}</b> ${esc(o.n)}</li>`).join("")}</ol>` : "";
  let cuerpo = "";
  if (gm) {
    const filas = enJuego().map((a) => `<li><img src="${esc(retrato(a))}" alt=""><span>${esc(a.name)}</span><small>${pg(a)}/${a.system.health?.max ?? 0}</small>
      <span class="mrkm-mm"><button type="button" data-a="m-" data-id="${a.id}" aria-label="${t("Hud.Menos")}">−</button><b>${e.masillas.por[a.id] ?? 0}</b><button type="button" data-a="m+" data-id="${a.id}" aria-label="${t("Hud.Mas")}">+</button></span></li>`).join("");
    cuerpo = `<p class="mrkm-hud-mas">${t("Hud.Masillas", { total: totalMasillas(e), libres: e.masillas.libres })}</p><ul class="mrkm-hud-pjs">${filas}</ul>
      <div class="mrkm-hud-botones"><button type="button" data-a="secuencia"><i class="fa-solid fa-forward"></i> ${t("Hud.NuevaSecuencia")}</button>
      <button type="button" data-a="turba"><i class="fa-solid fa-people-group"></i> ${t("Hud.Turba")}</button>
      <button type="button" data-a="atacar"><i class="fa-solid fa-khanda"></i> ${t("Hud.Atacar")}</button></div>
      <p class="mrkm-hud-max" data-tooltip="${esc(t("Hud.MaxAyuda"))}">${t("Hud.MaxGolpe", { n: e.maxGolpe })}</p>`;
  } else if (yo) {
    const m = e.masillas.por[yo.id] ?? 0, mon = e.monedas[yo.id] ?? 0;
    cuerpo = `${listaHtml(yo, e)}<p class="mrkm-hud-mas">${t("Hud.Encima", { n: m })}${e.inercia[yo.id] ? ` · <b class="mrkm-inercia">${t("Hud.Inercia")}</b>` : ""}</p>
      <div class="mrkm-hud-botones"><button type="button" data-a="atacar"><i class="fa-solid fa-khanda"></i> ${t("Hud.Atacar")}</button>
      <button type="button" data-a="sirena"><i class="fa-solid fa-bell"></i> ${t("Hud.Sirena")}</button>
      ${mon ? `<button type="button" data-a="moneda"><i class="fa-solid fa-coins"></i> ${t("Hud.Moneda", { n: mon })}</button>` : ""}</div>`;
  }
  return cabecera + ini + cuerpo;
}

export function pintarHud() {
  const ver = game.settings.get(ID, "mostrarHud") && game.ready;
  if (!ver) { raiz?.remove(); raiz = null; return; }
  if (!raiz) {
    raiz = document.createElement("section");
    raiz.id = "mrkm-hud";
    raiz.className = `${ID} mrkm-hud`;
    raiz.setAttribute("aria-label", t("Hud.Titulo"));
    document.body.append(raiz);
    raiz.addEventListener("click", alPulsar);
    arrastrable(raiz);
  }
  raiz.classList.toggle("es-gm", game.user.isGM);
  raiz.classList.toggle("siluetas", estado().siluetas);
  raiz.innerHTML = html();
  colocar();
  avisar();
}

function colocar() {
  const p = game.settings.get(ID, "posHud") ?? {};
  if (Number.isFinite(p.x)) Object.assign(raiz.style, { left: `${Math.max(0, Math.min(innerWidth - 80, p.x))}px`, top: `${Math.max(0, Math.min(innerHeight - 60, p.y))}px` });
  else Object.assign(raiz.style, { left: "", top: "", bottom: "" });
}

async function alPulsar(ev) {
  const b = ev.target.closest("button");
  if (!b) return;
  const a = b.dataset.a;
  if (a === "m+" || a === "m-") return moverMasilla(b.dataset.id, a === "m+" ? 1 : -1);
  if (a === "reloj+" || a === "reloj-") return moverReloj(a === "reloj+" ? 1 : -1);
  if (a === "secuencia") return nuevaSecuencia();
  if (a === "turba") return turnoTurba();
  if (a === "atacar") return atacar();
  if (a === "sirena") return sirenaRoja(miActor());
  if (a === "moneda") return gastarMoneda(miActor());
}

/** Botón derecho + arrastrar mueve el HUD; la posición se guarda en este navegador. */
function arrastrable(el) {
  el.addEventListener("contextmenu", (e) => e.preventDefault());
  el.addEventListener("pointerdown", (e) => {
    if (e.button !== 2) return;
    const r = el.getBoundingClientRect(), dx = e.clientX - r.left, dy = e.clientY - r.top;
    let pos = { x: r.left, y: r.top };
    try { el.setPointerCapture(e.pointerId); } catch { /* sin captura también funciona */ }
    const mover = (m) => { pos = { x: m.clientX - dx, y: m.clientY - dy }; Object.assign(el.style, { left: `${pos.x}px`, top: `${pos.y}px`, bottom: "auto" }); };
    const soltar = () => { el.removeEventListener("pointermove", mover); game.settings.set(ID, "posHud", pos); };
    el.addEventListener("pointermove", mover);
    el.addEventListener("pointerup", soltar, { once: true });
  });
}

/** Cuando el reloj de la Sirena Roja avanza, todos ven un rótulo grande. */
function avisar() {
  const av = estado().aviso;
  if (!av || av.t <= ultimoAviso) return;
  const primera = ultimoAviso === 0;
  ultimoAviso = av.t;
  if (primera && Date.now() - av.t > 10000) return;   // al recargar no se repite un aviso viejo
  rotulo(av.n >= 6 ? t(`Reloj.Lleno${estado().acto}`) : t("Reloj.Sube", { n: av.n }), t(`Reloj.Pub${Math.min(6, av.n)}`), "reloj");
}
function rotulo(titulo, sub, clase) {
  const el = document.createElement("div");
  el.className = `mrkm-rotulo mrkm-rotulo-${clase}`;
  el.setAttribute("role", "status");
  el.innerHTML = `<strong>${esc(titulo)}</strong><span>${esc(sub)}</span>`;
  document.body.append(el);
  setTimeout(() => el.classList.add("fuera"), 3800);
  setTimeout(() => el.remove(), 4800);
}
/** El tachón se ve en todas las pantallas: el nombre en grande y una línea roja que lo cruza. */
alRecibir("tachon", ({ actor, slug, n }) => {
  if (!game.settings.get(ID, "efectosVisuales")) return;
  const a = game.actors.get(actor), o = porSlug(slug);
  rotulo(slug === "bill" ? "BILL «MANDÍBULA» JANG" : o?.name ?? slug, t("Tachon.Rotulo", { nombre: a?.name ?? "", n }), "tachon");
});
