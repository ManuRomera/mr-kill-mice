// Estado compartido de la pelea (acto, secuencia, Masillas, Listas tachadas, monedas, reloj), peticiones de jugadores al GM e inventario.
export const ID = "mr-kill-mice";
export const t = (k, d) => (d ? game.i18n.format(`MRKM.${k}`, d) : game.i18n.localize(`MRKM.${k}`));
export const esc = (s) => foundry.utils.escapeHTML(String(s ?? ""));
export const ruta = (p) => `modules/${ID}/${p}`;
export const flag = (d, k) => d?.flags?.[ID]?.[k];

const BASE = {
  acto: 1, secuencia: 0, ronda: 1, iniciativa: [],
  masillas: { libres: 0, por: {} },                // libres: sin asignar · por: {actorId: n} encima de cada ratón
  tachados: {}, monedas: {}, inercia: {},            // por actorId
  maxGolpe: 0, reloj: 0, tachadoEnSec: false, siluetas: false,
  usos: {},                                          // {actorId: {escalera, establecimiento…}} se borra al acabar la pelea
  bill: { atacantes: [], resistencia: false }, lacayo: false, aviso: null
};

export function estado() {
  return foundry.utils.mergeObject(foundry.utils.deepClone(BASE), game.settings.get(ID, "estado") ?? {}, { inplace: false });
}
/** Solo el GM escribe: aplica fn a una copia y guarda (los jugadores piden con `pedir`). */
export async function guardar(fn) {
  const e = estado();
  await fn(e);
  await game.settings.set(ID, "estado", e);
  return e;
}

export const gms = () => game.users.filter((u) => u.isGM).map((u) => u.id);
export const chatGM = (content) => ChatMessage.create({ content, whisper: gms() });
export const chatPublico = (content, speaker, rolls) => ChatMessage.create({ content, speaker, rolls });

// ---- Peticiones de jugadores al GM, de una en una (dos a la vez leerían el mismo estado y una pisaría a la otra).
const ACC = {};
export const registrarAccion = (nombre, fn) => { ACC[nombre] = fn; };
let cola = Promise.resolve();
const enSerie = (fn) => { const p = cola.then(fn); cola = p.catch((e) => console.error(ID, e)); return p; };
export function pedir(nombre, datos = {}) {
  if (game.user.isGM) return enSerie(() => ACC[nombre]?.(datos, game.user.id));
  if (!game.users.activeGM) return ui.notifications.warn(t("SinGM"));
  game.socket.emit(`module.${ID}`, { nombre, datos, de: game.user.id });
}
const OYENTES = {};
/** Mensajes que el GM manda a todos (efectos, ventanas que se abren en cada cliente). */
export const alRecibir = (tipo, fn) => { OYENTES[tipo] = fn; };
export function aTodos(tipo, datos = {}) {
  game.socket.emit(`module.${ID}`, { tipo, datos });
  OYENTES[tipo]?.(datos);
}
export function iniciarSocket() {
  game.socket.on(`module.${ID}`, (m) => {
    if (m.tipo) return OYENTES[m.tipo]?.(m.datos);
    if (!game.user.isActiveGM) return;
    enSerie(() => ACC[m.nombre]?.(m.datos, m.de));
  });
}
/** ¿Puede este usuario actuar por este actor? (lo comprueba el GM al recibir una petición) */
export const puede = (actor, userId) => Boolean(actor && (game.users.get(userId)?.isGM || actor.testUserPermission(game.users.get(userId), "OWNER")));

// ---- Inventario: seis casillas (2 patas, 2 cuerpo, 2 mochila) en las coordenadas de la hoja de Mausritter.
export const CASILLAS = { pata: [-270, -150], torpe: [-270, -20], c1: [-140, -150], c2: [-140, -20], m1: [10, -150], m2: [10, -20] };
const ORDEN = ["m1", "m2", "c1", "c2", "torpe", "pata"];   // dónde busca hueco una condición
function ocupadas(actor) {
  const s = new Set();
  for (const i of actor.items) {
    const x = i.system.sheet?.currentX ?? 0, y = i.system.sheet?.currentY ?? 0;
    const w = i.system.size?.width ?? 1, h = i.system.size?.height ?? 1;
    for (let dx = 0; dx < w; dx++) for (let dy = 0; dy < h; dy++) s.add(`${x - 65 * (w - 1) + 130 * dx},${y - 65 * (h - 1) + 130 * dy}`);   // la hoja coloca por el centro
  }
  return s;
}
export function huecoLibre(actor) {
  const o = ocupadas(actor);
  const k = ORDEN.find((c) => !o.has(CASILLAS[c].join(",")));
  return k ? CASILLAS[k] : null;
}
export const condicion = (actor, slug) => actor.items.find((i) => flag(i, "slug") === slug);

/** Añade una condición (objeto del mundo con flag slug) en una casilla libre; si no hay, avisa de que hay que soltar algo. */
export async function darCondicion(actor, slug) {
  if (condicion(actor, slug)) return null;
  const base = game.items.find((i) => flag(i, "slug") === slug) ?? (await plantilla(slug));
  if (!base) { ui.notifications.warn(t("FaltaCondicion", { slug })); return null; }
  const datos = base.toObject();
  delete datos._id; delete datos.folder;
  const hueco = huecoLibre(actor);
  if (hueco) Object.assign(datos.system.sheet, { currentX: hueco[0], currentY: hueco[1], initialX: hueco[0], initialY: hueco[1] });
  const [creada] = await actor.createEmbeddedDocuments("Item", [datos]);
  if (!hueco) chatPublico(`<div class="mrkm-chat mrkm-alerta"><p>${t("SinHueco", { nombre: esc(actor.name), cond: esc(base.name) })}</p></div>`);
  return creada;
}
export async function quitarCondicion(actor, slug) {
  const i = condicion(actor, slug);
  if (i) await i.delete();
  return Boolean(i);
}
/** Si el mundo no tiene el objeto (aventura sin importar), se saca del compendio. */
async function plantilla(slug) {
  const adv = (await game.packs.get(`${ID}.aventura`)?.getDocuments())?.[0];
  const d = adv?.items.find((i) => i.flags?.[ID]?.slug === slug);
  return d ? new Item.implementation(d) : null;
}

// ---- Quién es quién
export const vengadores = () => game.actors.filter((a) => ["pj", "reserva"].includes(flag(a, "tipo")));
/** Los ratones que están en juego: los que tienen jugador; si nadie tiene jugador (pruebas del DJ), los seis titulares. */
export function enJuego() {
  const todos = vengadores();
  const con = todos.filter((a) => game.users.some((u) => !u.isGM && a.testUserPermission(u, "OWNER")));
  return con.length ? con : todos.filter((a) => flag(a, "tipo") === "pj");
}
export const conNombre = () => game.actors.filter((a) => flag(a, "nombre"));
export const porSlug = (slug) => game.actors.find((a) => flag(a, "slug") === slug);
export const retrato = (a) => a?.img ?? "icons/svg/mystery-man.svg";
export const pg = (a) => a?.system.health?.value ?? 0;
export const armadura = (a) => {
  const items = a.items.filter((i) => i.type === "armor").reduce((s, i) => s + (Number(i.system.armor?.value) || 0), 0);
  return Math.max(items, Number(a.system.armor) || 0);
};
export const listaDe = (a) => flag(a, "lista") ?? [];
export const tachadosDe = (a, e = estado()) => e.tachados[a.id] ?? [];
