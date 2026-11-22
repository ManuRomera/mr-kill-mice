// MR- Kill Mice · arranque: ajustes, API, importación automática, barra de herramientas, botones de la Turba y las seis casillas.
// Convivencia: no envuelve ninguna función del sistema ni de otros módulos; solo añade hooks propios, tarjetas .mrkm-chat
// y CSS con prefijo. Las tiradas y tarjetas nativas de Mausritter (y lo que hagan con ellas otros módulos) quedan intactas.
import { ID, t, flag, iniciarSocket, vengadores } from "./estado.mjs";
import "./efectos.mjs";
import * as R from "./reglas.mjs";
import { pintarHud } from "./hud.mjs";
import { PanelDJ } from "./panel.mjs";
import { registrarDireccion, abrirPizarra } from "./integraciones.mjs";
import { registrarVentanas } from "./ventanas.mjs";

const PACK = `${ID}.aventura`;

Hooks.once("init", () => {
  const cli = (clave, type, def, extra = {}) => game.settings.register(ID, clave, { name: `MRKM.Ajustes.${clave}.Name`, hint: `MRKM.Ajustes.${clave}.Hint`, scope: "client", config: true, type, default: def, ...extra });
  cli("mostrarHud", Boolean, true, { onChange: () => pintarHud() });
  cli("efectosSonido", Boolean, true);
  cli("volumenEfectos", Number, 0.7, { range: { min: 0, max: 1, step: 0.05 } });
  cli("efectosVisuales", Boolean, true);
  cli("textoGrande", Boolean, false, { onChange: (v) => document.body.classList.toggle("mrkm-texto-grande", v) });
  cli("altoContraste", Boolean, false, { onChange: (v) => document.body.classList.toggle("mrkm-alto-contraste", v) });
  game.settings.register(ID, "estado", { scope: "world", config: false, type: Object, default: {}, onChange: () => pintarHud() });
  game.settings.register(ID, "importada", { scope: "world", config: false, type: Boolean, default: false });
  game.settings.register(ID, "posHud", { scope: "client", config: false, type: Object, default: {} });
  game.settings.register(ID, "ventanas", { scope: "client", config: false, type: Object, default: {} });
  game.settings.registerMenu(ID, "restablecer", { name: "MRKM.Ajustes.restablecer.Name", label: "MRKM.Ajustes.restablecer.Label", hint: "MRKM.Ajustes.restablecer.Hint",
    icon: "fa-solid fa-arrows-to-dot", restricted: false, type: class extends foundry.applications.api.ApplicationV2 {
      async render() { await game.settings.set(ID, "posHud", {}); await game.settings.set(ID, "ventanas", {}); pintarHud(); ui.notifications.info(t("Ajustes.restablecer.Hecho")); return this; }
    } });
  registrarVentanas();
});

/* ---------------- Importación de la aventura ---------------- */
function mundoVacio() {
  const sinContenido = ["actors", "items", "journal", "playlists", "macros", "tables", "cards"].every((c) => !game[c]?.size);
  return sinContenido && game.scenes.contents.every((s) => s.background?.src?.startsWith("nue/") && !s.tokens.size);
}
export async function importarAventura({ confirmar = true } = {}) {
  if (!game.user.isGM) return ui.notifications.warn(t("SoloGM"));
  const pack = game.packs.get(PACK);
  if (!pack) return ui.notifications.error(t("Importar.SinPack"));
  if (confirmar && !mundoVacio()) {
    const ok = await foundry.applications.api.DialogV2.confirm({
      window: { title: t("Importar.Titulo"), icon: "fa-solid fa-file-import" }, content: `<p>${t("Importar.Aviso")}</p>`,
      yes: { label: t("Importar.Si"), icon: "fa-solid fa-file-import" }, no: { label: t("Cancelar") }, rejectClose: false
    });
    if (!ok) return;
  }
  ui.notifications.info(t("Importar.Empieza"));
  const adv = (await pack.getDocuments())[0];
  await adv.import({ dialog: false });
  await game.settings.set(ID, "importada", true);
  await game.scenes.find((s) => s.getFlag(ID, "orden") === 0)?.activate();
  ui.notifications.info(t("Importar.Hecho"));
  game.journal.find((j) => j.getFlag(ID, "guia"))?.sheet.render({ force: true });
}

/* ---------------- API ---------------- */
const API = {
  importarAventura, panel: () => PanelDJ.abrir(), abrirPizarra,
  atacar: R.atacar, turnoTurba: R.turnoTurba, nuevaSecuencia: R.nuevaSecuencia, ataqueBill: R.ataqueBill, bramido: R.bramido,
  desplegarMasillas: R.desplegarMasillas, repartirMasillas: R.repartirMasillas, finPelea: R.finPelea, cambiarActo: R.cambiarActo,
  tachar: R.tachar, preguntarTachon: R.preguntarTachon, sirenaRoja: R.sirenaRoja, gastarMoneda: R.gastarMoneda, reiniciarNoche: R.reiniciarNoche
};

Hooks.once("ready", async () => {
  game.modules.get(ID).api = API;
  iniciarSocket();
  document.body.classList.toggle("mrkm-texto-grande", game.settings.get(ID, "textoGrande"));
  document.body.classList.toggle("mrkm-alto-contraste", game.settings.get(ID, "altoContraste"));
  registrarDireccion();
  pintarHud();
  if (game.user.isGM) {
    // las macros del compendio llevan un autor ficticio: pasan al GM que las importa
    for (const m of game.macros.filter((m) => m.getFlag(ID, "macro") && !game.users.has(m.author?.id))) await m.update({ author: game.user.id });
    if (game.user === game.users.activeGM && !game.settings.get(ID, "importada") && mundoVacio()) await importarAventura({ confirmar: false });
  }
});
Hooks.on("updateActor", (a) => { if (flag(a, "slug")) pintarHud(); });
Hooks.on("updateUser", () => pintarHud());

/* ---------------- Barra de herramientas ---------------- */
// Lo que usan los jugadores va aquí y no en macros (no pueden ejecutar macros de script).
Hooks.on("getSceneControlButtons", (controls) => {
  const gm = game.user.isGM;
  const herr = (name, title, icon, fn, soloGM = false) => ({ name, title, icon, button: true, visible: gm || !soloGM, onChange: () => fn() });
  const tools = [
    herr("panel", "MRKM.Barra.Panel", "fa-solid fa-user-ninja", API.panel, true),
    herr("atacar", "MRKM.Barra.Atacar", "fa-solid fa-khanda", () => R.atacar()),
    herr("turba", "MRKM.Barra.Turba", "fa-solid fa-people-group", R.turnoTurba, true),
    herr("secuencia", "MRKM.Barra.Secuencia", "fa-solid fa-forward", R.nuevaSecuencia, true),
    herr("hud", "MRKM.Barra.Hud", "fa-solid fa-list-ol", () => game.settings.set(ID, "mostrarHud", !game.settings.get(ID, "mostrarHud"))),
    herr("pizarra", "MRKM.Barra.Pizarra", "fa-solid fa-thumbtack", abrirPizarra, true)
  ];
  controls.mrkm = { name: "mrkm", title: "MRKM.Barra.Titulo", icon: "fa-solid fa-khanda", order: 91, visible: true, activeTool: "",
    tools: Object.fromEntries(tools.map((x, i) => [x.name, { ...x, order: i }])) };
});

/* ---------------- Botones de la Turba en el chat ---------------- */
Hooks.on("renderChatMessageHTML", (_msg, html) => {
  const caja = html.querySelector?.(".mrkm-botones[data-turba]");
  if (!caja) return;
  const a = game.actors.get(caja.dataset.turba);
  const mio = game.user.isGM || a?.isOwner;
  for (const b of caja.querySelectorAll("button")) {
    b.disabled = !mio;
    b.addEventListener("click", () => { caja.querySelectorAll("button").forEach((x) => { x.disabled = true; }); R.responderTurba(caja.dataset.turba, b.dataset.modo); });
  }
});

/* ---------------- Seis casillas ---------------- */
// La hoja de Mausritter es un lienzo libre. En los vengadores, las cuatro casillas de mochila de la derecha están tapadas
// por «Sin sitio»: ni se mueve ni se borra salvo el GM, y nada se coloca encima. Solo afecta a estos actores.
const BLOQUEADAS = new Set([[140, -150], [270, -150], [140, -20], [270, -20]].map((p) => p.join(",")));
const esVengador = (actor) => vengadores().includes(actor);
Hooks.on("preUpdateItem", (item, cambios, _o, userId) => {
  if (!item.parent || !esVengador(item.parent) || game.users.get(userId)?.isGM) return;
  if (flag(item, "bloqueo")) return false;
  const x = foundry.utils.getProperty(cambios, "system.sheet.currentX");
  if (x === undefined) return;
  const y = foundry.utils.getProperty(cambios, "system.sheet.currentY") ?? item.system.sheet.currentY;
  const w = item.system.size?.width ?? 1, h = item.system.size?.height ?? 1;
  for (let dx = 0; dx < w; dx++) for (let dy = 0; dy < h; dy++) {
    if (BLOQUEADAS.has(`${x - 65 * (w - 1) + 130 * dx},${y - 65 * (h - 1) + 130 * dy}`)) { ui.notifications.warn(t("Casillas.Aviso")); return false; }
  }
});
Hooks.on("preDeleteItem", (item, _o, userId) => {
  if (flag(item, "bloqueo") && !game.users.get(userId)?.isGM) { ui.notifications.warn(t("Casillas.NoSeQuita")); return false; }
});
