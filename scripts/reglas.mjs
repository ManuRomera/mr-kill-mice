// Reglas del Sobre Rojo: ataque con dado explosivo y carnicería coreografiada, Turba y Esquiva acrobática, Lista de Muerte
// (tachar, Respiro de sangre, Inercia, Moneda de Fortuna, Golpe de los Cinco Puntos), secuencias, reloj, enemigos y munición.
// Todo va por tarjetas propias (.mrkm-chat): no toca las tarjetas ni las tiradas del sistema, así que convive con
// MR- Mausritter en español y Mausritter Combat Carousel sin que nadie aplique el daño dos veces.
import { ID, t, esc, ruta, flag, estado, guardar, chatGM, chatPublico, registrarAccion, pedir, aTodos, puede, darCondicion, quitarCondicion, condicion,
  enJuego, vengadores, conNombre, porSlug, retrato, pg, armadura, listaDe, tachadosDe } from "./estado.mjs";
import { efecto } from "./efectos.mjs";

const { DialogV2 } = foundry.applications.api;
const tarjeta = (clase, html) => `<div class="mrkm-chat ${clase}">${html}</div>`;
const cab = (img, titulo) => `<header><img src="${esc(img)}" alt=""><h3>${titulo}</h3></header>`;
const habla = (actor) => ChatMessage.getSpeaker({ actor });
const DADOS = ["d4", "d6", "d8", "d10", "d12"];
const caras = (d) => Number(String(d).replace(/\D/g, "")) || 6;
export const sube = (d, n = 1) => DADOS[Math.min(DADOS.length - 1, Math.max(0, DADOS.indexOf(d) + n))];
const ESCALERA = [["d6", 0, 0], ["d8", 0, 0], ["d8", 1, 0], ["d10", 0, 2], ["d12", 0, 0]];   // Bolsa llena de armas: dado, +plano, +Masillas

/** Salvación de Mausritter: d20 igual o por debajo del atributo. ventaja: 2d20 y el menor. */
export async function salvar(actor, stat, { ventaja = false, desventaja = false } = {}) {
  const v = actor.system.stats?.[stat]?.value ?? 10;
  const f = ventaja && !desventaja ? "2d20kl" : desventaja && !ventaja ? "2d20kh" : "1d20";
  const r = await new Roll(f).evaluate();
  return { roll: r, ok: r.total <= v, v };
}

// ---------------------------------------------------------------- Masillas
/** Quita n Masillas: primero los que acosan a ese ratón, luego los libres y luego los de los demás. Devuelve cuántos cayeron. */
async function abatir(actorId, n) {
  let caen = 0;
  await guardar((e) => {
    const m = e.masillas;
    const quita = (k) => { const x = Math.min(n - caen, k === "libres" ? m.libres : m.por[k] ?? 0); if (k === "libres") m.libres -= x; else m.por[k] -= x; caen += x; };
    if (actorId) quita(actorId);
    quita("libres");
    for (const k of Object.keys(m.por)) if (caen < n) quita(k);
    for (const k of Object.keys(m.por)) if (!m.por[k]) delete m.por[k];
  });
  if (caen && canvas.scene) {   // fichas de Masilla en la escena: caen tantas como Masillas
    const fichas = canvas.scene.tokens.filter((tk) => flag(tk.actor, "tipo") === "masilla").slice(0, caen).map((tk) => tk.id);
    if (fichas.length) await canvas.scene.deleteEmbeddedDocuments("Token", fichas);
  }
  return caen;
}
export const totalMasillas = (e = estado()) => e.masillas.libres + Object.values(e.masillas.por).reduce((s, n) => s + n, 0);

export async function desplegarMasillas(n) {
  const e0 = estado();
  n ??= (e0.acto === 1 ? 3 : 2) * enJuego().length;
  await guardar((e) => { e.masillas = { libres: n, por: {} }; });
  await repartirMasillas();
  chatGM(tarjeta("", `<h3>${t("Masillas.Desplegados", { n, tipo: t(`Masillas.Tipo${e0.acto}`) })}</h3>`));
}
/** Reparte los Masillas libres entre los ratones en juego, de uno en uno. */
export async function repartirMasillas() {
  const ids = enJuego().filter((a) => pg(a) > 0).map((a) => a.id);
  if (!ids.length) return;
  await guardar((e) => {
    let i = 0;
    while (e.masillas.libres > 0) { const k = ids[i++ % ids.length]; e.masillas.por[k] = (e.masillas.por[k] ?? 0) + 1; e.masillas.libres--; }
  });
}
export async function moverMasilla(actorId, d) {
  await guardar((e) => {
    const m = e.masillas, ahora = m.por[actorId] ?? 0;
    if (d > 0 && m.libres > 0) { m.libres--; m.por[actorId] = ahora + 1; }
    else if (d > 0) m.por[actorId] = ahora + 1;            // refuerzos
    else if (ahora > 0) { m.por[actorId] = ahora - 1; m.libres++; }
    if (!m.por[actorId]) delete m.por[actorId];
  });
}

// ---------------------------------------------------------------- Daño en Mausritter
/** Aplica daño a la Mausritter: armadura, PG y lo que sobra a FUE con salvación. Devuelve el reparto. */
async function aplicarDano(actor, dano, { arm = armadura(actor), cinco = false } = {}) {
  const tras = Math.max(0, dano - arm);
  const hp0 = pg(actor), fue0 = actor.system.stats?.strength?.value ?? 0;
  const aHp = Math.min(hp0, tras), sobra = tras - aHp;
  const cambios = { "system.health.value": hp0 - aHp };
  let nota = "";
  // Bill: la primera vez que cae, con par se levanta con 3 PG (no contra el Golpe de los Cinco Puntos).
  if (flag(actor, "slug") === "bill" && hp0 - aHp <= 0 && hp0 > 0 && !cinco && !estado().bill.resistencia) {
    const d = await new Roll("1d6").evaluate();
    await guardar((e) => { e.bill.resistencia = true; });
    if (d.total % 2 === 0) { await actor.update({ "system.health.value": 3 }); return { tras, aHp, sobra: 0, nota: t("Bill.Resiste", { n: d.total }), cae: false }; }
    nota = t("Bill.NoResiste", { n: d.total });
  }
  if (sobra > 0 && !cinco) {
    const fue = Math.max(0, fue0 - sobra);
    cambios["system.stats.strength.value"] = fue;
    if (fue > 0) {
      await actor.update(cambios);
      const s = await salvar(actor, "strength", { ventaja: flag(actor, "slug") === "martillo" });
      nota += ` ${t(s.ok ? "Dano.FueAguanta" : "Dano.FueCae", { tirada: s.roll.total, v: fue })}`;
    } else nota += ` ${t("Dano.Muere")}`;
  }
  await actor.update(cambios);
  if (cinco) nota = t("Cinco.Cae");
  return { tras, aHp, sobra, nota, cae: (hp0 > 0 && hp0 - aHp <= 0) || cinco };
}

// ---------------------------------------------------------------- Ataque de Kill Mice
/** Armas del ratón, la de la pata hábil primero (la hoja la coloca arriba a la izquierda), y el kung-fu al final. */
const armasDe = (a) => [...a.items.filter((i) => i.type === "weapon")
    .sort((x, y) => (x.system.sheet?.currentX ?? 0) - (y.system.sheet?.currentX ?? 0) || (x.system.sheet?.currentY ?? 0) - (y.system.sheet?.currentY ?? 0))
    .map((i) => ({ id: i.id, name: i.name, dmg1: i.system.weapon?.dmg1 || "d6", dmg2: i.system.weapon?.dmg2 || "",
      fuego: Boolean(flag(i, "fuego")), mas: Number(flag(i, "mas")) || 0, slug: flag(i, "slug") })),
  { id: "kungfu", name: t("Ataque.Kungfu"), dmg1: "d6", dmg2: "", fuego: false, mas: 0 }];

/** Enemigos con Nombre a los que se puede atacar: los marcados con la diana primero; si no, los del acto en curso que siguen en pie. */
function objetivosPosibles() {
  const e = estado();
  const diana = [...game.user.targets].map((tk) => tk.actor).filter((a) => flag(a, "nombre"));
  const resto = conNombre().filter((a) => pg(a) > 0 && flag(a, "tipo") !== "aliado" && (flag(a, "acto") === e.acto || canvas.scene?.tokens.some((tk) => tk.actor?.id === a.id)));
  return [...new Map([...diana, ...resto].map((a) => [a.id, a])).values()];
}

/** Abre el diálogo de ataque del ratón (el del jugador, o el elegido en la escena) y lo resuelve. */
export async function atacar(actor = game.user.character ?? canvas.tokens?.controlled[0]?.actor) {
  if (!actor) return ui.notifications.warn(t("Ataque.SinActor"));
  if (flag(actor, "nombre")) return atacarPNJ(actor);
  if (!actor.isOwner) return ui.notifications.warn(t("Ataque.NoTuyo"));
  const e = estado();
  const armas = armasDe(actor), objs = objetivosPosibles(), op = flag(actor, "op") ?? [];
  const lista = listaDe(actor), tach = tachadosDe(actor, e), m = e.masillas.por[actor.id] ?? 0, total = totalMasillas(e);
  const cincoOk = [0, 1, 2, 3].every((i) => tach.includes(lista[i])) && !e.usos[actor.id]?.cinco;
  const sirena = Boolean(condicion(actor, "sirena-roja")), inercia = Boolean(e.inercia[actor.id]);
  const opHtml = op.map((o) => `<label class="mrkm-chip"><input type="checkbox" name="op" value="${o.id}" ${o.auto ? "checked" : ""}> ${esc(o.n)}</label>`).join("");
  const porDefecto = m > 0 || !objs.length ? "masillas" : objs[0].id;
  const content = `<div class="mrkm-ataque">
    <label>${t("Ataque.Arma")} <select name="arma">${armas.map((a) => `<option value="${a.id}">${esc(a.name)} · ${a.dmg1}${a.dmg2 ? `/${a.dmg2}` : ""}</option>`).join("")}</select></label>
    <label class="mrkm-chip"><input type="checkbox" name="dos"> ${t("Ataque.DosPatas")}</label>
    <fieldset class="mrkm-objetivos"><legend>${t("Ataque.Objetivo")}</legend>
      <label class="mrkm-chip"><input type="radio" name="obj" value="masillas" ${porDefecto === "masillas" ? "checked" : ""}> ${t("Ataque.Masillas", { m, total })}</label>
      ${objs.map((a) => `<label class="mrkm-chip"><input type="radio" name="obj" value="${a.id}" ${porDefecto === a.id ? "checked" : ""}><img src="${esc(retrato(a))}" alt=""> ${esc(a.name)}
        ${lista.includes(flag(a, "slug")) ? `<b class="mrkm-en-lista">${t("Ataque.EnLista", { n: lista.indexOf(flag(a, "slug")) + 1 })}</b>` : ""}</label>`).join("")}</fieldset>
    <fieldset><legend>${t("Ataque.Tecnicas")}</legend>${opHtml}
      <label class="mrkm-chip"><input type="checkbox" name="inercia" ${inercia ? "checked" : ""}> ${t("Ataque.Inercia")}</label>
      <label class="mrkm-chip"><input type="checkbox" name="mejorado"> ${t("Ataque.Mejorado")}</label>
      <label class="mrkm-chip"><input type="checkbox" name="ventaja"> ${t("Ataque.Ventaja")}</label>
      <label class="mrkm-chip">${t("Ataque.Plano")} <input type="number" name="plano" value="0" step="1"></label>
      ${cincoOk ? `<label class="mrkm-chip mrkm-cinco"><input type="checkbox" name="cinco"> ${t("Ataque.Cinco")}</label>` : ""}</fieldset>
    ${sirena ? `<p class="mrkm-ayuda"><i class="fa-solid fa-bell"></i> ${t("Ataque.SirenaAyuda")}</p>` : ""}
    ${e.siluetas ? `<p class="mrkm-ayuda"><i class="fa-solid fa-lightbulb"></i> ${t("Ataque.SiluetasAyuda")}</p>` : ""}</div>`;
  const datos = await DialogV2.wait({
    window: { title: t("Ataque.Titulo", { nombre: actor.name }), icon: "fa-solid fa-khanda" }, classes: [ID, "mrkm-dlg-ataque"], position: { width: 660 }, content, rejectClose: false,
    buttons: [{ action: "ok", label: t("Ataque.Tirar"), icon: "fa-solid fa-dice", default: true,
      callback: (_ev, btn) => { const f = btn.form.elements; return { arma: f.arma.value, dos: f.dos.checked, obj: btn.form.querySelector("input[name=obj]:checked")?.value ?? "masillas",
        op: [...btn.form.querySelectorAll("input[name=op]:checked")].map((i) => i.value), inercia: f.inercia.checked, mejorado: f.mejorado.checked,
        ventaja: f.ventaja.checked, plano: Number(f.plano.value) || 0, cinco: Boolean(f.cinco?.checked) }; } },
      { action: "no", label: t("Cancelar") }]
  });
  if (!datos || datos === "no") return;
  return resolverAtaque(actor, datos);
}

async function resolverAtaque(actor, d) {
  const e = estado();
  const arma = armasDe(actor).find((a) => a.id === d.arma) ?? armasDe(actor)[0];
  const ops = (flag(actor, "op") ?? []).filter((o) => d.op.includes(o.id));
  const obj = d.obj === "masillas" ? null : game.actors.get(d.obj);
  const lista = listaDe(actor), slugObj = flag(obj, "slug");
  let dado = d.dos && arma.dmg2 ? arma.dmg2 : arma.dmg1, plano = d.plano, mas = arma.mas, pasos = 0, ignora = 0, ventaja = d.ventaja, suma = false, explotaMenos = e.siluetas ? 1 : 0;
  const notas = [];
  const escalera = ops.some((o) => o.escalera) && arma.slug === "hierro-turno";
  if (escalera) {
    const k = Math.min(ESCALERA.length - 1, e.usos[actor.id]?.escalera ?? 0);
    [dado] = ESCALERA[k]; plano += ESCALERA[k][1]; mas += ESCALERA[k][2];
    notas.push(t("Ataque.Escalera", { n: k + 1 }));
  }
  for (const o of ops) {
    if (o.fija) dado = o.fija;
    if (o.minimo && DADOS.indexOf(dado) < DADOS.indexOf(o.minimo)) dado = o.minimo;
    if (o.paso) pasos += o.paso;
    if (o.plano) plano += o.plano;
    if (o.mas && !obj) mas += o.mas;
    if (o.ignora && obj) ignora += o.ignora;
    if (o.ventaja) ventaja = true;
    if (o.suma) suma = true;
    if (o.explota) explotaMenos = Math.max(explotaMenos, o.explota);
  }
  if (d.inercia) { pasos++; notas.push(t("Ataque.InerciaUsada")); }
  if (d.mejorado) pasos++;
  if (obj && condicion(actor, "sirena-roja") && lista.includes(slugObj)) { pasos++; notas.push(t("Ataque.SirenaUsada")); }
  dado = sube(dado, pasos);
  const N = caras(dado);
  const x = explotaMenos ? `x>=${N - explotaMenos}` : "x";
  let formula = d.cinco ? `${N} + 1d${N}${x}` : suma ? `2d${N}${x}` : ventaja ? `{1d${N}${x}, 1d${N}${x}}kh` : `1d${N}${x}`;
  if (plano) formula += plano > 0 ? ` + ${plano}` : ` - ${-plano}`;
  const roll = await new Roll(formula).evaluate();
  const total = Math.max(1, roll.total);
  const explosiones = roll.dice.flatMap((dd) => dd.results).filter((r) => r.exploded).length;
  efecto(arma.fuego ? (mas >= 2 ? "rafaga" : "disparo") : "katana");
  // estado: mayor golpe de la noche (daño de Bill), inercia gastada, escalera, arma de fuego usada, atacantes de Bill
  await pedir("anota", { actor: actor.id, total, inercia: d.inercia, escalera: escalera && Boolean(obj), fuego: arma.fuego ? arma.id : null, cinco: d.cinco, bill: slugObj === "bill" });
  const linea = `<p class="mrkm-tirada"><strong>${total}</strong> · ${esc(arma.name)} (${dado}${plano ? ` ${plano > 0 ? "+" : "−"} ${Math.abs(plano)}` : ""})${explosiones ? ` · <b class="mrkm-explota">${t("Ataque.Explota", { n: explosiones })}</b>` : ""}</p>`
    + (notas.length ? `<p class="mrkm-notas">${notas.map(esc).join(" · ")}</p>` : "");
  if (!obj) {
    await chatPublico(tarjeta("mrkm-carniceria", cab(retrato(actor), t("Ataque.Carniceria")) + linea + `<p>${t("Ataque.Abatiendo", { n: total + mas })}</p>`), habla(actor), [roll]);
    await pedir("carniceria", { actor: actor.id, n: total + mas });
  } else {
    await chatPublico(tarjeta("mrkm-golpe", cab(retrato(actor), t("Ataque.Contra", { nombre: esc(obj.name) })) + linea), habla(actor), [roll]);
    await pedir("dano", { actor: actor.id, obj: obj.id, dano: total, ignora, armDoble: suma, cinco: d.cinco });
  }
  if (explosiones) await pedir("tabla", {});
}

registrarAccion("anota", async ({ actor, total, inercia, escalera, fuego, cinco, bill }, userId) => {
  if (!puede(game.actors.get(actor), userId)) return;
  await guardar((e) => {
    e.maxGolpe = Math.max(e.maxGolpe, total);
    if (inercia) delete e.inercia[actor];
    const u = (e.usos[actor] ??= {});
    if (escalera) u.escalera = (u.escalera ?? 0) + 1;
    if (fuego) u.fuego = [...new Set([...(u.fuego ?? []), fuego])];
    if (cinco) u.cinco = true;
    if (bill && !e.bill.atacantes.includes(actor)) e.bill.atacantes.push(actor);
  });
});
registrarAccion("carniceria", async ({ actor, n }, userId) => {
  if (!puede(game.actors.get(actor), userId)) return;
  const caen = await abatir(actor, n);
  chatPublico(tarjeta("mrkm-carniceria", `<p>${t("Ataque.Caen", { n: caen, quedan: totalMasillas() })}</p>`));
});
registrarAccion("tabla", async () => {
  const tb = game.tables.find((x) => flag(x, "slug") === `pelea${estado().acto}`);
  if (tb) await tb.draw();
});

/** El GM resuelve el daño contra un Enemigo con Nombre (con Lacayo ablativo, Gato copión, Tajo continuo y la Lista). */
registrarAccion("dano", async ({ actor, obj, dano, ignora = 0, armDoble = false, cinco = false }, userId) => {
  const a = game.actors.get(actor), o = game.actors.get(obj), e = estado();
  if (!puede(a, userId) || !o) return;
  const slug = flag(o, "slug");
  if (slug === "sheng" && totalMasillas(e) > 0 && !e.lacayo && !cinco) {
    const usar = await DialogV2.confirm({ window: { title: t("Sheng.Titulo"), icon: "fa-solid fa-user-shield" }, content: `<p>${t("Sheng.Pregunta", { dano })}</p>`, rejectClose: false });
    if (usar) {
      await guardar((x) => { x.lacayo = true; });
      await abatir(null, 1);
      return chatPublico(tarjeta("mrkm-golpe", `<p>${t("Sheng.Escudo")}</p>`));
    }
  }
  let arm = cinco ? 0 : Math.max(0, armadura(o) + (slug === "oren" && e.copion ? 1 : 0) - ignora);
  if (armDoble) arm *= 2;
  const r = await aplicarDano(o, dano, { arm, cinco });
  let extra = "";
  if (r.cae && r.sobra > 0 && totalMasillas() > 0) extra = ` ${t("Ataque.TajoContinuo", { n: await abatir(actor, r.sobra) })}`;
  if (r.cae && cinco) await o.update({ "system.health.value": 0 });
  await chatPublico(tarjeta(r.cae ? "mrkm-alerta" : "mrkm-golpe", `<p>${t("Dano.Resumen", { nombre: esc(o.name), arm, hp: r.aHp, quedan: pg(o) })}${r.nota ? ` ${esc(r.nota)}` : ""}${extra}</p>`));
  if (r.cae) {
    if (slug === "sheng") chatPublico(tarjeta("mrkm-alerta", `<p>${t("Sheng.Lealtad")}</p>`));
    if (slug === "pei") chatPublico(tarjeta("", `<p>${t("Pei.Herencia")}</p>`));
    await preguntarTachon(o, a);
  }
});

// ---------------------------------------------------------------- La Lista de Muerte
/** Cuando cae un nombre, el GM marca quién participó (el atacante ya viene marcado) y quién dio el último golpe. */
export async function preguntarTachon(obj, ultimo = null) {
  const slug = flag(obj, "slug");
  const quien = vengadores().filter((a) => listaDe(a).includes(slug) && !tachadosDe(a).includes(slug));
  if (!quien.length) return;
  const content = `<p>${t("Tachon.Pregunta", { nombre: esc(obj.name) })}</p><div class="mrkm-chips">${quien.map((a) => `<label class="mrkm-chip">
      <input type="checkbox" name="p" value="${a.id}" ${a.id === ultimo?.id || quien.length === 1 ? "checked" : ""}><img src="${esc(retrato(a))}" alt=""> ${esc(a.name)}</label>`).join("")}</div>
    <label>${t("Tachon.Ultimo")} <select name="u"><option value="">—</option>${quien.map((a) => `<option value="${a.id}" ${a.id === ultimo?.id ? "selected" : ""}>${esc(a.name)}</option>`).join("")}</select></label>`;
  const r = await DialogV2.wait({ window: { title: t("Tachon.Titulo"), icon: "fa-solid fa-marker" }, classes: [ID], content, rejectClose: false,
    buttons: [{ action: "ok", label: t("Tachon.Tachar"), icon: "fa-solid fa-marker", default: true,
      callback: (_e, b) => ({ ids: [...b.form.querySelectorAll("input[name=p]:checked")].map((i) => i.value), u: b.form.elements.u.value }) }, { action: "no", label: t("Cancelar") }] });
  if (!r || r === "no") return;
  for (const id of r.ids) await tachar(game.actors.get(id), slug, id === r.u);
}

/** Tacha un nombre: Respiro de sangre, Inercia, quita Sirena Roja y Aturdido, y Moneda de Fortuna al del último golpe en un nombre compartido. */
export async function tachar(actor, slug, ultimo = false) {
  if (!actor || !game.user.isGM) return;
  const lista = listaDe(actor);
  if (!lista.includes(slug) || tachadosDe(actor).includes(slug)) return;
  const compartido = vengadores().filter((a) => listaDe(a).includes(slug)).length > 1;
  const moneda = ultimo && compartido;
  const cura = await new Roll("1d4").evaluate();
  const max = actor.system.health?.max ?? 0, ahora = pg(actor);
  let respiro;
  if (ahora < max) { await actor.update({ "system.health.value": Math.min(max, ahora + cura.total) }); respiro = t("Tachon.Cura", { n: Math.min(max - ahora, cura.total) }); }
  else if (await quitarCondicion(actor, "magullado")) respiro = t("Tachon.QuitaMagullado");
  else respiro = t("Tachon.SinHeridas");
  const quitadas = [];
  for (const c of ["sirena-roja", "aturdido"]) if (await quitarCondicion(actor, c)) quitadas.push(t(`Cond.${c}`));
  const e = await guardar((x) => {
    (x.tachados[actor.id] ??= []).push(slug);
    x.inercia[actor.id] = true;
    x.tachadoEnSec = true;
    if (moneda) x.monedas[actor.id] = (x.monedas[actor.id] ?? 0) + 1;
  });
  const hechos = e.tachados[actor.id];
  const frase = (await game.tables.find((x) => flag(x, "slug") === "sentencias")?.roll({}))?.results?.[0];
  const n = lista.indexOf(slug) + 1, nombre = porSlug(slug)?.name ?? slug;
  efecto("tachon");
  aTodos("tachon", { actor: actor.id, slug, n });
  const cinco = [0, 1, 2, 3].every((i) => hechos.includes(lista[i])) && !hechos.includes("bill");
  const completa = lista.every((s) => hechos.includes(s));
  const textoFrase = frase ? (frase.description || frase.text || frase.name || "").replace(/<[^>]+>/g, "") : "";
  await chatPublico(tarjeta("mrkm-tachon", `${cab(retrato(actor), t("Tachon.Cabecera", { n }))}<p class="mrkm-tachado">${esc(nombre)}</p>
    ${textoFrase ? `<p class="mrkm-cita">${esc(textoFrase)}</p>` : ""}
    <ul><li>${t("Tachon.Respiro")}: ${esc(respiro)}</li><li>${t("Tachon.InerciaLista")}</li>${quitadas.length ? `<li>${t("Tachon.Quita", { c: esc(quitadas.join(", ")) })}</li>` : ""}
    ${moneda ? `<li><strong>${t("Tachon.Moneda")}</strong></li>` : ""}</ul>
    ${cinco ? `<p class="mrkm-cinco">${t("Cinco.Desbloqueado")}</p>` : ""}${completa ? `<p class="mrkm-cinco">${t("Tachon.Completa")}</p>` : ""}`), habla(actor), [cura]);
}
/** Deshace un tachón (error del DJ): solo quita la marca, no devuelve PG ni monedas. */
export const destachar = (actor, slug) => guardar((e) => { e.tachados[actor.id] = (e.tachados[actor.id] ?? []).filter((s) => s !== slug); });

export const gastarMoneda = (actor) => pedir("moneda", { actor: actor?.id });
registrarAccion("moneda", async ({ actor }, userId) => {
  const a = game.actors.get(actor);
  if (!puede(a, userId) || !(estado().monedas[actor] > 0)) return;
  await guardar((e) => { e.monedas[actor]--; });
  efecto("gong");
  chatPublico(tarjeta("mrkm-moneda", `${cab(ruta("assets/items/moneda-fortuna.webp"), t("Moneda.Titulo"))}<p>${t("Moneda.Gasta", { nombre: esc(a.name) })}</p>`), habla(a));
});

export const sirenaRoja = (actor) => pedir("sirena", { actor: actor?.id });
registrarAccion("sirena", async ({ actor }, userId) => {
  const a = game.actors.get(actor);
  if (!puede(a, userId)) return;
  if (!(await darCondicion(a, "sirena-roja"))) return;
  efecto("sirena");
  chatPublico(tarjeta("mrkm-alerta", `${cab(ruta("assets/items/sirena-roja.webp"), t("Cond.sirena-roja"))}<p>${t("Sirena.Acepta", { nombre: esc(a.name) })}</p>`), habla(a));
});

// ---------------------------------------------------------------- La Turba
/** El GM lanza el turno de la Turba: cada ratón acosado recibe su tarjeta para esquivar o encajar. */
export async function turnoTurba() {
  if (!game.user.isGM) return;
  const e = estado();
  const acosados = Object.entries(e.masillas.por).filter(([, n]) => n > 0).map(([id, n]) => [game.actors.get(id), n]).filter(([a]) => a);
  if (!acosados.length) return ui.notifications.info(t("Turba.Nadie"));
  efecto("rafaga");
  const tony = e.acto === 1 && pg(porSlug("tonyma")) > 0;
  await guardar((x) => { x.turba = Object.fromEntries(acosados.map(([a]) => [a.id, true])); });
  for (const [a, n] of acosados) {
    await chatPublico(tarjeta("mrkm-turba", `${cab(retrato(a), t("Turba.Titulo"))}<p>${t("Turba.Encima", { nombre: esc(a.name), n, dado: n >= 6 ? "1d8" : "1d6" })}${tony ? ` ${t("Turba.Tony")}` : ""}</p>
      <div class="mrkm-botones" data-turba="${a.id}"><button type="button" data-modo="esquiva"><i class="fa-solid fa-person-running"></i> ${t("Turba.Esquiva")}</button>
      <button type="button" data-modo="encaja"><i class="fa-solid fa-shield-halved"></i> ${t("Turba.Encaja")}</button></div>`));
  }
}
registrarAccion("turba", async ({ actor, modo }, userId) => {
  const a = game.actors.get(actor), e = estado();
  if (!puede(a, userId) || !e.turba?.[actor]) return;
  await guardar((x) => { delete x.turba[actor]; });
  const n = e.masillas.por[actor] ?? 0;
  if (modo === "esquiva") {
    const s = await salvar(a, "dexterity", { desventaja: Boolean(condicion(a, "aturdido")) });
    if (s.ok) {
      const d4 = await new Roll("1d4").evaluate();
      const caen = await abatir(actor, d4.total);
      efecto("cristal");
      return chatPublico(tarjeta("mrkm-turba", `${cab(retrato(a), t("Turba.EsquivaOk"))}<p>${t("Turba.EsquivaDetalle", { tirada: s.roll.total, v: s.v, caen })}</p>`), habla(a), [s.roll, d4]);
    }
    await chatPublico(tarjeta("mrkm-alerta", `<p>${t("Turba.EsquivaFalla", { nombre: esc(a.name), tirada: s.roll.total, v: s.v })}</p>`), habla(a), [s.roll]);
  }
  const tony = e.acto === 1 && pg(porSlug("tonyma")) > 0;
  const r = await new Roll(`${n >= 6 ? "1d8" : "1d6"}${tony ? " + 2" : ""}`).evaluate();
  const res = await aplicarDano(a, r.total);
  efecto("disparo");
  chatPublico(tarjeta("mrkm-alerta", `${cab(retrato(a), t("Turba.Golpe"))}<p class="mrkm-tirada"><strong>${r.total}</strong></p><p>${t("Dano.Resumen", { nombre: esc(a.name), arm: armadura(a), hp: res.aHp, quedan: pg(a) })}${res.nota ? ` ${esc(res.nota)}` : ""}</p>`), habla(a), [r]);
});
export const responderTurba = (actorId, modo) => pedir("turba", { actor: actorId, modo });

// ---------------------------------------------------------------- Enemigos con Nombre
const CAMPEONES = new Set(["bill", "oren", "budd"]);
/** Daño que un Enemigo con Nombre hace a un ratón (con Desesperación del perdedor y Derramamiento de sangre heroico). */
async function golpearPJ(pnj, pj, roll, titulo) {
  const e = estado();
  let arm = armadura(pj);
  if (flag(pj, "slug") === "placa" && pg(pj) < pg(pnj)) arm = Math.max(arm, 2);
  let total = roll.total, nota = "";
  if (flag(pj, "slug") === "vibora" && e.acto === 2 && CAMPEONES.has(flag(pnj, "slug")) && total - arm >= 3) { total += 1; nota = t("Vibora.Sangre"); }
  const r = await aplicarDano(pj, total, { arm });
  efecto(flag(pnj, "slug") === "bill" ? "katana" : "disparo");
  await chatPublico(tarjeta("mrkm-alerta", `${cab(retrato(pnj), titulo)}<p class="mrkm-tirada"><strong>${total}</strong> → ${esc(pj.name)}</p>
    <p>${t("Dano.Resumen", { nombre: esc(pj.name), arm, hp: r.aHp, quedan: pg(pj) })}${r.nota ? ` ${esc(r.nota)}` : ""} ${esc(nota)}</p>`), habla(pnj), [roll]);
}
const objetivoPJ = () => [...game.user.targets].map((tk) => tk.actor).find((a) => ["pj", "reserva"].includes(flag(a, "tipo")));
async function elegirPJ(titulo) {
  const pj = objetivoPJ();
  if (pj) return pj;
  const op = enJuego().filter((a) => pg(a) > 0);
  if (!op.length) return null;
  const r = await DialogV2.wait({ window: { title: titulo, icon: "fa-solid fa-crosshairs" }, classes: [ID], rejectClose: false, content: `<p>${t("Enemigo.Elige")}</p>`,
    buttons: op.map((a) => ({ action: a.id, label: a.name })) });
  return game.actors.get(r);
}
/** Ataque normal de un Enemigo con Nombre (lo lanza el GM): el dado de su arma contra el ratón marcado con la diana. */
export async function atacarPNJ(pnj) {
  if (!game.user.isGM || !pnj) return;
  if (flag(pnj, "slug") === "bill") return ataqueBill();
  const pj = await elegirPJ(t("Enemigo.Ataca", { nombre: pnj.name }));
  if (!pj) return;
  const arma = pnj.items.find((i) => i.type === "weapon");
  const roll = await new Roll(`1${arma?.system.weapon?.dmg1 || "d6"}`).evaluate();
  return golpearPJ(pnj, pj, roll, t("Enemigo.Ataca", { nombre: esc(pnj.name) }));
}
/** Bill «Mandíbula» Jang: el mayor golpe de la noche + 1 (o 1d10 + 2 si nadie ha pasado de 8, el mayor de los dos). */
export async function ataqueBill() {
  if (!game.user.isGM) return;
  const bill = porSlug("bill"), e = estado();
  if (!bill) return;
  const pj = await elegirPJ(t("Bill.Ataca"));
  if (!pj) return;
  const base = e.maxGolpe + 1;
  let roll = await new Roll(`${base}`).evaluate();
  if (e.maxGolpe <= 8) {
    const alt = await new Roll("1d10 + 2").evaluate();
    if (alt.total > base) roll = alt;
  }
  await golpearPJ(bill, pj, roll, t("Bill.Golpe", { base }));
  if (e.bill.atacantes.length >= 2) chatGM(tarjeta("", `<p>${t("Bill.Pared", { n: e.bill.atacantes.length })}</p>`));
}
/** Bramido de Budd: salvación de VOL; si falla, Aturdido y 1d4. */
export async function bramido() {
  if (!game.user.isGM) return;
  const budd = porSlug("budd"), pj = await elegirPJ(t("Budd.Bramido"));
  if (!budd || !pj) return;
  efecto("bramido");
  const s = await salvar(pj, "will");
  if (s.ok) return chatPublico(tarjeta("mrkm-golpe", `${cab(retrato(budd), t("Budd.Bramido"))}<p>${t("Budd.Aguanta", { nombre: esc(pj.name), tirada: s.roll.total, v: s.v })}</p>`), habla(budd), [s.roll]);
  await darCondicion(pj, "aturdido");
  await golpearPJ(budd, pj, await new Roll("1d4").evaluate(), t("Budd.Aturde", { nombre: esc(pj.name), tirada: s.roll.total, v: s.v }));
}
export const gatoCopion = () => guardar((e) => { e.copion = !e.copion; });

// ---------------------------------------------------------------- Secuencias y reloj
let FIJAS = null;
async function fijas(acto) {
  FIJAS ??= await (await fetch(ruta("content/secuencias.json"))).json();
  return FIJAS[acto] ?? [];
}
/** Empieza la siguiente secuencia: reloj de la Sirena Roja, curación de los campeones, iniciativas y orden de actuación. */
export async function nuevaSecuencia() {
  if (!game.user.isGM) return;
  const e0 = estado();
  const avanza = e0.secuencia > 0 && !e0.tachadoEnSec;
  const reloj = Math.min(6, e0.reloj + (avanza ? 1 : 0));
  const sec = e0.secuencia % 4 + 1, ronda = e0.secuencia === 4 ? e0.ronda + 1 : e0.ronda;
  if (e0.acto === 2) for (const s of ["oren", "budd"]) {
    const a = porSlug(s);
    if (a && pg(a) > 0 && pg(a) < a.system.health.max) await a.update({ "system.health.value": Math.min(a.system.health.max, pg(a) + 2) });
  }
  const rolls = [], orden = [];
  for (const a of enJuego().filter((x) => pg(x) > 0)) {
    const r = await new Roll(`1d6 + ${Math.floor((a.system.stats?.dexterity?.value ?? 10) / 2)}`).evaluate();
    rolls.push(r); orden.push({ id: a.id, n: a.name, v: r.total, pj: true });
  }
  const rosaPJ = enJuego().some((a) => flag(a, "slug") === "rosa");
  for (const [slug, n, vals] of await fijas(e0.acto)) if (!(slug === "rosa" && rosaPJ)) orden.push({ slug, n, v: vals[sec - 1], pj: false });
  orden.sort((x, y) => y.v - x.v || Number(y.pj) - Number(x.pj));
  await guardar((e) => {
    Object.assign(e, { secuencia: sec, ronda, reloj, tachadoEnSec: false, lacayo: false, copion: false, iniciativa: orden });
    e.bill.atacantes = [];
    if (reloj > e0.reloj) e.aviso = { clave: "reloj", n: reloj, t: Date.now() };
    if (reloj >= 6 && e0.acto === 2) e.siluetas = true;
  });
  await chatPublico(tarjeta("mrkm-secuencia", `<h3>${t("Secuencia.Titulo", { n: sec, ronda })}</h3><ol>${orden.map((o) => `<li class="${o.pj ? "pj" : ""}"><b>${o.v}</b> ${esc(o.n)}</li>`).join("")}</ol>
    ${e0.acto === 2 ? `<p class="mrkm-ayuda">${t("Secuencia.Curan")}</p>` : ""}`), undefined, rolls);
  if (reloj > e0.reloj) {
    efecto(reloj >= 6 ? (e0.acto === 2 ? "apagon" : "sirenas-guardia") : "sirena");
    if (reloj >= 6) chatPublico(tarjeta("mrkm-alerta", `<h3>${t(`Reloj.Lleno${e0.acto}`)}</h3>`));
  }
}
export async function moverReloj(d) {
  if (!game.user.isGM) return;
  await guardar((e) => {
    e.reloj = Math.max(0, Math.min(6, e.reloj + d));
    if (d > 0) e.aviso = { clave: "reloj", n: e.reloj, t: Date.now() };
    e.siluetas = e.acto === 2 && e.reloj >= 6;
  });
  if (d > 0) efecto("sirena");
}
export async function cambiarActo(acto) {
  if (!game.user.isGM) return;
  await guardar((e) => { Object.assign(e, { acto, secuencia: 0, ronda: 1, reloj: 0, siluetas: false, iniciativa: [], tachadoEnSec: false }); e.masillas = { libres: 0, por: {} }; });
}

/** Al acabar cada gran pelea: dado de munición por arma de fuego usada (4–6 marca un uso), y se olvidan los usos por pelea. */
export async function finPelea() {
  if (!game.user.isGM) return;
  const e = estado(), lineas = [], rolls = [];
  for (const [id, u] of Object.entries(e.usos)) {
    const a = game.actors.get(id);
    if (!a || flag(a, "slug") === "mecha") continue;
    for (const itemId of u.fuego ?? []) {
      const it = a.items.get(itemId);
      if (!it) continue;
      const r = await new Roll("1d6").evaluate(); rolls.push(r);
      if (r.total >= 4) {
        const max = it.system.pips?.max || 3, v = Math.min(max, (it.system.pips?.value ?? 0) + 1);
        await it.update({ "system.pips.value": v });
        lineas.push(`<li>${esc(a.name)} · ${esc(it.name)}: <b>${r.total}</b> → ${t("Municion.Marca", { v, max })}${v >= max ? ` <b>${t("Municion.Encasquilla")}</b>` : ""}</li>`);
      } else lineas.push(`<li>${esc(a.name)} · ${esc(it.name)}: <b>${r.total}</b> → ${t("Municion.Bien")}</li>`);
    }
  }
  await guardar((x) => { Object.assign(x, { usos: {}, secuencia: 0, ronda: 1, reloj: 0, iniciativa: [], lacayo: false, copion: false, siluetas: false, turba: {} }); x.masillas = { libres: 0, por: {} }; x.bill.atacantes = []; });
  if (canvas.scene) {
    const fichas = canvas.scene.tokens.filter((tk) => flag(tk.actor, "tipo") === "masilla").map((tk) => tk.id);
    if (fichas.length) await canvas.scene.deleteEmbeddedDocuments("Token", fichas);
  }
  await chatPublico(tarjeta("", `<h3>${t("Municion.Titulo")}</h3>${lineas.length ? `<ul>${lineas.join("")}</ul>` : `<p>${t("Municion.Nada")}</p>`}`), undefined, rolls);
}
export const reiniciarNoche = () => game.settings.set(ID, "estado", {});

/** Pone fichas de Masilla en la escena (opcional): tantas como Masillas, en filas junto al borde. */
export async function fichasMasillas() {
  if (!game.user.isGM || !canvas.scene) return;
  const e = estado(), m = porSlug(e.acto === 1 ? "farolillo" : "maniaco"), n = totalMasillas(e);
  if (!m || !n) return;
  const g = canvas.scene.grid.size;
  const docs = await Promise.all(Array.from({ length: n }, async (_, i) => (await m.getTokenDocument({ x: g * (1 + (i % 12)), y: g * (1 + Math.floor(i / 12)), actorLink: false })).toObject()));
  await canvas.scene.createEmbeddedDocuments("Token", docs);
}
