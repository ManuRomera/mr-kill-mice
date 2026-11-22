// Panel del DJ: reparto de ratones, la pelea (acto, Masillas, secuencias, Turba, reloj, munición), enemigos con nombre,
// las Listas (tachar a mano), escenas, tablas e integraciones. Recuerda posición, tamaño y secciones abiertas en este navegador.
import { ID, t, esc, flag, estado, vengadores, conNombre, retrato, pg, listaDe, tachadosDe, porSlug, darCondicion } from "./estado.mjs";
import { desplegarMasillas, repartirMasillas, fichasMasillas, nuevaSecuencia, turnoTurba, moverReloj, finPelea, cambiarActo, reiniciarNoche,
  atacarPNJ, ataqueBill, bramido, gatoCopion, tachar, destachar, preguntarTachon, totalMasillas } from "./reglas.mjs";
import { abrirPizarra } from "./integraciones.mjs";

const { ApplicationV2, DialogV2 } = foundry.applications.api;
const dosierDe = (actor) => game.journal.find((j) => flag(j, "dosier") === flag(actor, "slug"));
const jugadores = () => game.users.filter((u) => !u.isGM);

export class PanelDJ extends ApplicationV2 {
  static #instancia;
  static abrir() { (this.#instancia ??= new PanelDJ()).render({ force: true }); }

  static DEFAULT_OPTIONS = {
    id: "mrkm-panel", classes: [ID, "mrkm-panel"], tag: "section",
    window: { title: "MRKM.Panel.Titulo", icon: "fa-solid fa-khanda", resizable: true },
    position: { width: 580, height: 780 }
  };

  constructor(o) {
    super(o);
    const m = game.settings.get(ID, "ventanas")?.panel;
    if (m?.pos) Object.assign(this.options.position, m.pos);
    this.abiertas = new Set(m?.abiertas ?? ["mesa", "pelea"]);
  }

  _onPosition(pos) {
    super._onPosition?.(pos);
    clearTimeout(this._g);
    this._g = setTimeout(() => this.#memoria(), 400);
  }
  #memoria() {
    const v = foundry.utils.deepClone(game.settings.get(ID, "ventanas") ?? {});
    const { left, top, width, height } = this.position;
    v.panel = { pos: { left, top, width, height }, abiertas: [...this.abiertas] };
    game.settings.set(ID, "ventanas", v);
  }

  async _renderHTML() {
    const e = estado();
    const sec = (id, icono, cuerpo) => `<details data-sec="${id}" ${this.abiertas.has(id) ? "open" : ""}><summary><i class="fa-solid ${icono}" aria-hidden="true"></i> ${t(`Panel.${id}`)}</summary><div class="mrkm-sec">${cuerpo}</div></details>`;
    const opcUsuarios = (sel) => `<option value="">${t("Panel.NadieAsignado")}</option>` + jugadores().map((u) => `<option value="${u.id}" ${u.id === sel ? "selected" : ""}>${esc(u.name)}</option>`).join("");
    const pjs = vengadores();
    const dueno = (a) => jugadores().find((u) => a.testUserPermission(u, "OWNER"))?.id ?? "";
    const mesa = pjs.length ? `<p class="mrkm-ayuda">${t("Panel.MesaAyuda")}</p><ul class="mrkm-reparto">${pjs.map((a) => `<li class="${flag(a, "tipo")}">
        <img src="${esc(retrato(a))}" alt=""><span>${esc(a.name)}${flag(a, "tipo") === "reserva" ? ` <em>${t("Panel.Reserva")}</em>` : ""}</span>
        <select data-reparto="${a.id}" aria-label="${t("Panel.Jugador")} ${esc(a.name)}">${opcUsuarios(dueno(a))}</select>
        <button type="button" data-act="dosier" data-id="${a.id}" data-tooltip="${t("Panel.MostrarDosier")}" aria-label="${t("Panel.MostrarDosier")}"><i class="fa-solid fa-envelope-open-text"></i></button></li>`).join("")}</ul>`
      : `<p>${t("Panel.SinAventura")}</p><button type="button" data-act="importar"><i class="fa-solid fa-file-import"></i> ${t("Panel.Importar")}</button>`;
    const pelea = `<div class="mrkm-fila"><span>${t("Panel.Acto")}</span>
        <button type="button" data-acto="1" class="${e.acto === 1 ? "activo" : ""}">${t("Hud.Vol1")}</button><button type="button" data-acto="2" class="${e.acto === 2 ? "activo" : ""}">${t("Hud.Vol2")}</button></div>
      <div class="mrkm-fila"><span>${t("Hud.Masillas", { total: totalMasillas(e), libres: e.masillas.libres })}</span>
        <button type="button" data-act="desplegar"><i class="fa-solid fa-people-group"></i> ${t("Panel.Desplegar")}</button>
        <button type="button" data-act="repartir"><i class="fa-solid fa-shuffle"></i> ${t("Panel.Repartir")}</button>
        <button type="button" data-act="fichas" data-tooltip="${t("Panel.FichasAyuda")}"><i class="fa-solid fa-chess-pawn"></i> ${t("Panel.Fichas")}</button></div>
      <div class="mrkm-fila"><span>${e.secuencia ? t("Hud.Secuencia", { n: e.secuencia }) : t("Hud.SinPelea")}</span>
        <button type="button" data-act="secuencia"><i class="fa-solid fa-forward"></i> ${t("Hud.NuevaSecuencia")}</button>
        <button type="button" data-act="turba"><i class="fa-solid fa-hand-fist"></i> ${t("Hud.Turba")}</button></div>
      <div class="mrkm-fila"><span>${t("Hud.Reloj", { n: e.reloj })}</span><button type="button" data-reloj="-1" aria-label="${t("Hud.Menos")}">−</button><button type="button" data-reloj="1" aria-label="${t("Hud.Mas")}">+</button>
        <small>${esc(t(`Reloj.Gm${e.acto}`))}</small></div>
      <div class="mrkm-fila"><button type="button" data-act="fin"><i class="fa-solid fa-flag-checkered"></i> ${t("Panel.FinPelea")}</button>
        <button type="button" data-act="reiniciar" class="mrkm-discreto"><i class="fa-solid fa-rotate-left"></i> ${t("Panel.Reiniciar")}</button></div>
      <p class="mrkm-ayuda">${t("Hud.MaxGolpe", { n: e.maxGolpe })}</p>`;
    const malos = conNombre().filter((a) => flag(a, "acto") === e.acto || flag(a, "tipo") === "aliado");
    const enemigos = `<ul class="mrkm-enemigos">${malos.map((a) => `<li class="${pg(a) > 0 ? "" : "caido"}"><img src="${esc(retrato(a))}" alt="">
        <span>${esc(a.name)}</span><small>${pg(a)}/${a.system.health?.max ?? 0}</small>
        <button type="button" data-ficha="${a.id}" data-tooltip="${t("Panel.Ficha")}" aria-label="${t("Panel.Ficha")}"><i class="fa-solid fa-id-card"></i></button>
        ${flag(a, "tipo") !== "aliado" ? `<button type="button" data-pnj="${a.id}" data-tooltip="${t("Panel.AtacaPNJ")}" aria-label="${t("Panel.AtacaPNJ")}"><i class="fa-solid fa-crosshairs"></i></button>
        <button type="button" data-tachon="${a.id}" data-tooltip="${t("Panel.TacharCaido")}" aria-label="${t("Panel.TacharCaido")}"><i class="fa-solid fa-marker"></i></button>` : ""}</li>`).join("")}</ul>
      ${e.acto === 2 ? `<div class="mrkm-fila"><button type="button" data-act="bill"><i class="fa-solid fa-dragon"></i> ${t("Panel.Bill")}</button>
        <button type="button" data-act="bramido"><i class="fa-solid fa-volume-high"></i> ${t("Budd.Bramido")}</button>
        <button type="button" data-act="copion" class="${e.copion ? "activo" : ""}"><i class="fa-solid fa-cat"></i> ${t("Panel.Copion")}</button></div>` : ""}`;
    const listas = pjs.map((a) => {
      const tach = tachadosDe(a, e);
      return `<div class="mrkm-lista-dj"><img src="${esc(retrato(a))}" alt=""><b>${esc(a.name)}</b> <small>${t("Panel.Monedas", { n: e.monedas[a.id] ?? 0 })}</small>
        <ol>${listaDe(a).map((s) => `<li><button type="button" data-tachar="${a.id}" data-slug="${s}" class="${tach.includes(s) ? "tachado" : ""}">${esc(porSlug(s)?.name ?? s)}</button></li>`).join("")}</ol>
        <span class="mrkm-conds"><button type="button" data-cond="sirena-roja" data-id="${a.id}">${t("Cond.sirena-roja")}</button><button type="button" data-cond="aturdido" data-id="${a.id}">${t("Cond.aturdido")}</button><button type="button" data-cond="magullado" data-id="${a.id}">${t("Cond.magullado")}</button></span></div>`;
    }).join("");
    const escenas = game.scenes.filter((s) => flag(s, "orden") !== undefined).sort((a, b) => flag(a, "orden") - flag(b, "orden"));
    const esc_ = escenas.length ? `<ul class="mrkm-escenas">${escenas.map((s) => `<li class="${s.active ? "activa" : ""}"><button type="button" data-escena="${s.id}">
        <img src="${esc(s.thumb ?? "")}" alt=""><span>${esc(s.name)}</span></button></li>`).join("")}</ul>` : `<p>${t("Panel.SinEscenas")}</p>`;
    const tablas = game.tables.filter((tb) => flag(tb, "slug")).map((tb) => `<button type="button" data-tabla="${tb.id}"><i class="fa-solid fa-dice"></i> ${esc(tb.name)}</button>`).join("");
    const piz = game.modules.get("mr-pizarra")?.active, dir = game.modules.get("mr-direccion")?.active;
    const otros = ["mr-mausritter-es", "mausritter-combat-carousel"].filter((m) => game.modules.get(m)?.active).map((m) => game.modules.get(m).title);
    const integ = `<p><i class="fa-solid fa-${dir ? "check" : "minus"}"></i> ${t(dir ? "Integ.DireccionSi" : "Integ.DireccionNo")}</p>
      <p><i class="fa-solid fa-${piz ? "check" : "minus"}"></i> ${t(piz ? "Integ.PizarraSi" : "Integ.PizarraNo")}</p>
      ${piz ? `<button type="button" data-act="pizarra"><i class="fa-solid fa-thumbtack"></i> ${t("Integ.AbrirPizarra")}</button>` : ""}
      ${otros.length ? `<p><i class="fa-solid fa-handshake"></i> ${t("Integ.Conviven", { m: esc(otros.join(", ")) })}</p>` : ""}`;
    return `<div class="mrkm-panel-cuerpo">${sec("mesa", "fa-users", mesa)}${sec("pelea", "fa-hand-fist", pelea)}${sec("enemigos", "fa-skull", enemigos)}
      ${sec("listas", "fa-marker", listas)}${sec("escenas", "fa-film", esc_)}${sec("tablas", "fa-table-list", `<div class="mrkm-fila">${tablas}</div>`)}${sec("integ", "fa-plug", integ)}</div>`;
  }

  _replaceHTML(result, content) {
    content.innerHTML = result;
    if (content.dataset.mrkm) return;   // los oyentes van una sola vez sobre el contenedor
    content.dataset.mrkm = "1";
    content.addEventListener("toggle", (ev) => {
      const d = ev.target.closest?.("details[data-sec]");
      if (!d) return;
      d.open ? this.abiertas.add(d.dataset.sec) : this.abiertas.delete(d.dataset.sec);
      this.#memoria();
    }, true);
    content.addEventListener("change", (ev) => { const s = ev.target.closest("select[data-reparto]"); if (s) this.#repartir(s.dataset.reparto, s.value); });
    content.addEventListener("click", (ev) => this.#clic(ev));
  }

  async #clic(ev) {
    const b = ev.target.closest("button");
    if (!b) return;
    const d = b.dataset;
    if (d.reloj) return moverReloj(Number(d.reloj));
    if (d.acto) return cambiarActo(Number(d.acto));
    if (d.escena) return game.scenes.get(d.escena)?.view();
    if (d.tabla) return game.tables.get(d.tabla)?.draw();
    if (d.ficha) return game.actors.get(d.ficha)?.sheet.render({ force: true });
    if (d.pnj) return atacarPNJ(game.actors.get(d.pnj));
    if (d.tachon) return preguntarTachon(game.actors.get(d.tachon));
    if (d.cond) return darCondicion(game.actors.get(d.id), d.cond);
    if (d.tachar) {
      const a = game.actors.get(d.tachar);
      if (b.classList.contains("tachado")) return destachar(a, d.slug);
      const ultimo = await DialogV2.confirm({ window: { title: t("Tachon.Titulo") }, content: `<p>${t("Tachon.UltimoManual", { nombre: esc(a.name) })}</p>`, rejectClose: false });
      return tachar(a, d.slug, Boolean(ultimo));
    }
    switch (d.act) {
      case "importar": return game.modules.get(ID).api.importarAventura();
      case "dosier": { const j = dosierDe(game.actors.get(d.id)); return j?.sheet.render({ force: true }); }
      case "desplegar": {
        const conJugador = vengadores().filter((a) => jugadores().some((u) => a.testUserPermission(u, "OWNER"))).length || 6;
        const n = await DialogV2.prompt({ window: { title: t("Panel.Desplegar") }, content: `<p>${t("Panel.CuantosMasillas")}</p><input type="number" name="n" value="${(estado().acto === 1 ? 3 : 2) * conJugador}" min="0" autofocus>`,
          ok: { label: t("Panel.Desplegar"), callback: (_e, btn) => Number(btn.form.elements.n.value) }, rejectClose: false });
        return Number.isFinite(n) && desplegarMasillas(n);
      }
      case "repartir": return repartirMasillas();
      case "fichas": return fichasMasillas();
      case "secuencia": return nuevaSecuencia();
      case "turba": return turnoTurba();
      case "fin": return finPelea();
      case "bill": return ataqueBill();
      case "bramido": return bramido();
      case "copion": return gatoCopion();
      case "pizarra": return abrirPizarra();
      case "reiniciar": {
        const ok = await DialogV2.confirm({ window: { title: t("Panel.Reiniciar") }, content: `<p>${t("Panel.ReiniciarSeguro")}</p>`, rejectClose: false });
        return ok && reiniciarNoche();
      }
    }
  }

  /** Da el ratón a un jugador: propietario del actor, observador de su dosier y personaje asignado. Lo quita a los demás. */
  async #repartir(actorId, userId) {
    const a = game.actors.get(actorId);
    if (!a) return;
    const j = dosierDe(a);
    const own = { default: 0 };
    for (const u of jugadores()) own[u.id] = 0;
    if (userId) own[userId] = 3;
    await a.update({ ownership: own });
    if (j) await j.update({ ownership: Object.fromEntries(Object.entries(own).map(([k, v]) => [k, v ? 2 : 0])) });
    for (const u of jugadores()) if (u.character?.id === a.id && u.id !== userId) await u.update({ character: null });
    if (userId) {
      await game.users.get(userId).update({ character: a.id });
      if (j) foundry.documents.collections.Journal.show(j, { force: true, users: [userId] });
    }
    this.render();
  }
}

const repinta = () => foundry.applications.instances.get("mrkm-panel")?.render();
Hooks.on("updateSetting", (s) => { if (s.key === `${ID}.estado`) repinta(); });
Hooks.on("updateScene", repinta);
Hooks.on("updateActor", (a) => { if (flag(a, "slug")) repinta(); });
