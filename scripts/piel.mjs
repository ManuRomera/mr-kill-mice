// Piel Kill Mice para lo nativo de Mausritter: las fichas de actor, las tarjetas de tirada del chat y los diálogos de tirada.
// Solo añade la clase .mrkm-piel (y el CSS hace el resto): no toca el HTML, los datos ni los botones que meten
// MR- Mausritter en español o Combat Carousel. Se apaga con el ajuste «pielTiradas».
import { ID, estado, tachadosDe } from "./estado.mjs";

const DIALOGO = 'select[name="advantage"], select[name="enhanced"], select[name="stat"], input[name="power"]';
const raiz = (x) => x?.[0] ?? x;

export function registrarPiel() {
  game.settings.register(ID, "pielTiradas", { name: "MRKM.Ajustes.pielTiradas.Name", hint: "MRKM.Ajustes.pielTiradas.Hint",
    scope: "client", config: true, type: Boolean, default: true, onChange: (v) => document.body.classList.toggle("mrkm-piel-on", v) });
  Hooks.once("ready", () => document.body.classList.toggle("mrkm-piel-on", game.settings.get(ID, "pielTiradas")));
  Hooks.on("renderChatMessageHTML", (_m, html) => {
    if (html.querySelector?.(".mausritter .rollcontainer")) html.classList.add("mrkm-piel");
  });
  Hooks.on("renderDialog", (app, html) => {
    const el = raiz(app.element) ?? raiz(html);
    if (el?.querySelector?.(DIALOGO)) el.classList.add("mrkm-piel", "mrkm-piel-dialogo");
  });
  Hooks.on("renderActorSheet", (app, html) => {
    const el = raiz(app.element) ?? raiz(html);
    el?.classList.add("mrkm-piel", "mrkm-piel-ficha");
    marcarLista(el, app.actor);
  });
  // la Lista del cuadro de la ficha se tacha en vivo, como el HUD
  Hooks.on("updateSetting", (s) => {
    if (s.key !== `${ID}.estado`) return;
    for (const app of Object.values(ui.windows)) if (app.actor && app.rendered) marcarLista(raiz(app.element), app.actor);
  });
}

function marcarLista(el, actor) {
  const tach = tachadosDe(actor, estado());
  for (const li of el?.querySelectorAll?.(".mrkm-lista li[data-slug]") ?? []) li.classList.toggle("tachado", tach.includes(li.dataset.slug));
}

/** Portada del mundo: si el mundo no tiene imagen de fondo (o descripción), pone las de Kill Mice. Se ven en la pantalla
 *  de entrada y en la tarjeta del mundo. Nunca pisa lo que el DJ haya puesto. */
export async function ponerPortada() {
  if (!game.user.isGM) return;
  const cambios = {};
  if (!game.world.background) cambios.background = `modules/${ID}/assets/portada-mundo.webp`;
  if (!game.world.description?.trim()) cambios.description = game.i18n.localize("MRKM.DescripcionMundo");
  if (!Object.keys(cambios).length) return;
  try {
    const r = await foundry.utils.fetchJsonWithTimeout(foundry.utils.getRoute("setup"), {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "editWorld", id: game.world.id, ...cambios })
    });
    if (r?.error) console.warn(`${ID} | portada del mundo:`, r.error);
  } catch (e) { console.warn(`${ID} | portada del mundo:`, e); }
}
