// Conector entre a página de planejamento e o Trello.
// Guarda a chave do Trello em segredo (Cloudflare) para que a página pública nunca a exponha.
//
// Rotas:
//   GET  /card/:id                 -> artes (anexos de imagem) e link de vídeo do Drive de um card
//   GET  /img/:card/:anexo/:arq     -> a imagem do anexo, servida para a página
//   POST /comentario               -> {card?, texto, nome, tipo: "aprovacao"|"comentario", titulo}
//   POST /ideia                    -> {tema, prof, obs, nome}  (comentário no card de ideias)
//   GET  /buscar?q=título          -> procura no quadro o card de um post pelo título
//   GET  /painel                   -> todos os cards das listas de produção, com data, etapa, vídeo e legenda
//   GET  /video/:idDrive           -> o vídeo do Drive para o player do celular (só links que estão em cards do quadro)
 
const API = "https://api.trello.com/1";
 
function cors(env, req) {
  const origem = req.headers.get("Origin") || "";
  const permitido = (env.ALLOWED_ORIGIN || "*").split(",").map(s => s.trim());
  const ok = permitido.includes("*") || permitido.includes(origem);
  return {
    "Access-Control-Allow-Origin": ok ? (origem || "*") : permitido[0],
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Range",
    "Access-Control-Expose-Headers": "Content-Length, Content-Range, Accept-Ranges",
    "Vary": "Origin",
  };
}
 
function json(dados, status, env, req, extra = {}) {
  return new Response(JSON.stringify(dados), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...cors(env, req), ...extra },
  });
}
 
function auth(env) {
  return `key=${encodeURIComponent(env.TRELLO_KEY)}&token=${encodeURIComponent(env.TRELLO_TOKEN)}`;
}
 
async function cardDoQuadro(env, id) {
  if (!/^[A-Za-z0-9]{6,32}$/.test(id)) return null;
  const r = await fetch(`${API}/cards/${id}?fields=id,idBoard,name,desc,shortLink&attachments=true&attachment_fields=id,name,mimeType,url,bytes,isUpload&${auth(env)}`);
  if (!r.ok) return null;
  const c = await r.json();
  return c.idBoard === env.BOARD_ID ? c : null;
}
 
function ordemAnexo(nome) {
  const m = /\((\d+)\)\s*\.[a-z0-9]+$/i.exec(nome);
  return m ? parseInt(m[1], 10) : 1;
}
 
// Link do vídeo no Drive: ignora capa, foto e imagem; prefere a linha que diz "Vídeo"
function primeiroVideoDrive(desc) {
  const t = String(desc || "");
  const re = /drive\.google\.com\/file\/d\/([A-Za-z0-9_-]{20,})/g;
  const achados = [];
  let m;
  while ((m = re.exec(t))) {
    const linha = t.slice(t.lastIndexOf("\n", m.index) + 1, m.index).toLowerCase();
    if (/capa|foto|imagem|thumb/.test(linha)) continue;
    achados.push({ id: m[1], video: /v[ií]deo/.test(linha) });
  }
  const a = achados.find(x => x.video) || achados[0];
  return a ? a.id : null;
}
 
async function rotaCard(req, env, id) {
  const c = await cardDoQuadro(env, id);
  if (!c) return json({ erro: "card não encontrado" }, 404, env, req);
  const imagens = (c.attachments || [])
    .filter(a => a.isUpload && /^image\//.test(a.mimeType || ""))
    .sort((a, b) => ordemAnexo(a.name) - ordemAnexo(b.name) || a.name.localeCompare(b.name))
    .map(a => {
      const arq = a.url.split("/").pop();
      return { nome: a.name, src: `/img/${c.id}/${a.id}/${arq}` };
    });
  return json({ id: c.id, nome: c.name, imagens, video: primeiroVideoDrive(c.desc) }, 200, env, req,
    { "Cache-Control": "public, max-age=300" });
}
 
async function rotaImagem(req, env, ctx, card, anexo, arq) {
  const cache = caches.default;
  const chave = new Request(new URL(req.url).toString());
  const salvo = await cache.match(chave);
  if (salvo) return salvo;
  const c = await cardDoQuadro(env, card);
  if (!c || !(c.attachments || []).some(a => a.id === anexo)) return new Response("não encontrado", { status: 404 });
  const r = await fetch(`${API}/cards/${card}/attachments/${anexo}/download/${arq}`, {
    headers: { Authorization: `OAuth oauth_consumer_key="${env.TRELLO_KEY}", oauth_token="${env.TRELLO_TOKEN}"` },
  });
  if (!r.ok) return new Response("erro ao buscar a imagem", { status: 502 });
  const resp = new Response(r.body, {
    headers: {
      "Content-Type": r.headers.get("Content-Type") || "image/jpeg",
      "Cache-Control": "public, max-age=86400",
      ...cors(env, req),
    },
  });
  ctx.waitUntil(cache.put(chave, resp.clone()));
  return resp;
}
 
function limpa(t, max) {
  return String(t || "").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").trim().slice(0, max);
}
 
async function rotaComentario(req, env) {
  let b;
  try { b = await req.json(); } catch { return json({ erro: "pedido inválido" }, 400, env, req); }
  const nome = limpa(b.nome, 80) || "Dra. Adriana";
  const titulo = limpa(b.titulo, 200);
  const texto = limpa(b.texto, 2000);
  const tipo = b.tipo === "aprovacao" ? "aprovacao" : "comentario";
  if (tipo === "comentario" && !texto) return json({ erro: "escreva o comentário" }, 400, env, req);
  const alvo = limpa(b.card, 32);
  if (!alvo) return json({ erro: "este conteúdo ainda não tem card no Trello" }, 400, env, req);
  const c = await cardDoQuadro(env, alvo);
  if (!c) return json({ erro: "card não encontrado no Trello" }, 404, env, req);
  const sobre = "";
  const msg = tipo === "aprovacao"
    ? `✅ Aprovado por ${nome}${sobre} pela página de planejamento.${texto ? "\n\n" + texto : ""}`
    : `💬 Comentário de ${nome}${sobre} pela página de planejamento:\n\n${texto}`;
  const r = await fetch(`${API}/cards/${c.id}/actions/comments?text=${encodeURIComponent(msg)}&${auth(env)}`, { method: "POST" });
  if (!r.ok) return json({ erro: "o Trello não aceitou o comentário" }, 502, env, req);
  return json({ ok: true }, 200, env, req);
}
 
async function rotaIdeia(req, env) {
  let b;
  try { b = await req.json(); } catch { return json({ erro: "pedido inválido" }, 400, env, req); }
  const tema = limpa(b.tema, 200);
  if (!tema) return json({ erro: "a ideia precisa de um tema" }, 400, env, req);
  if (!env.CARD_IDEIAS) return json({ erro: "o card de ideias ainda não foi definido" }, 400, env, req);
  const c = await cardDoQuadro(env, env.CARD_IDEIAS);
  if (!c) return json({ erro: "card de ideias não encontrado no Trello" }, 404, env, req);
  const nome = limpa(b.nome, 80) || "Dra. Adriana";
  const msg = [
    `💡 Ideia de ${nome} para a gravação, enviada pela página de planejamento:`,
    `**Tema:** ${tema}`,
    b.prof ? `**Profissionais envolvidos:** ${limpa(b.prof, 300)}` : "",
    b.obs ? `**Observação:** ${limpa(b.obs, 1500)}` : "",
  ].filter(Boolean).join("\n");
  const r = await fetch(`${API}/cards/${c.id}/actions/comments?text=${encodeURIComponent(msg)}&${auth(env)}`, { method: "POST" });
  if (!r.ok) return json({ erro: "o Trello não aceitou a ideia" }, 502, env, req);
  return json({ ok: true }, 200, env, req);
}
 
function normaliza(t) {
  return String(t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
    .replace(/\[[^\]]*\]/g, " ").replace(/[^a-z0-9]+/g, " ").trim();
}
 
async function rotaBuscar(req, env, ctx) {
  const q = normaliza(new URL(req.url).searchParams.get("q"));
  if (q.length < 6) return json({ erro: "busca curta" }, 400, env, req);
  const cache = caches.default;
  const chave = new Request(`https://cache.local/cards/${env.BOARD_ID}`);
  let lista = await cache.match(chave);
  let cards;
  if (lista) cards = await lista.json();
  else {
    const r = await fetch(`${API}/boards/${env.BOARD_ID}/cards/open?fields=name,shortLink&${auth(env)}`);
    if (!r.ok) return json({ erro: "falha ao ler o Trello" }, 502, env, req);
    cards = (await r.json()).map(c => ({ n: normaliza(c.name), s: c.shortLink }));
    ctx.waitUntil(cache.put(chave, new Response(JSON.stringify(cards), { headers: { "Cache-Control": "max-age=300" } })));
  }
  const achado = cards.find(c => c.n === q) || cards.find(c => q.length >= 12 && c.n.includes(q));
  return achado ? json({ card: achado.s }, 200, env, req, { "Cache-Control": "public, max-age=300" })
                : json({ card: null }, 404, env, req);
}
 
// ---------------------------------------------------------------- painel
// Etapa do card pelo nome da lista
function etapa(nomeLista) {
  const n = normaliza(nomeLista);
  if (n.includes("calendario")) return "cal";
  if (n.includes("em producao")) return "prod";
  if (n.includes("aprovacao")) return "aprov";
  if (n.includes("agendamento")) return "agend";
  if (n.includes("finalizado")) return "fim";
  if (n.includes("gaveta")) return "gaveta";
  return null;
}
 
function limpaTexto(t) {
  t = String(t || "").replace(/‌/g, "");
  t = t.replace(/\[([^\[\]]*)\]\((https?:\/\/[^)]*)\)/g, (m, txt) => {
    const k = txt.replace(/[\*\s]/g, "").toLowerCase();
    return (k === "foto" || k === "video" || k === "vídeo" || txt.startsWith("http")) ? "" : txt;
  });
  t = t.replace(/\\\*/g, "").replace(/\*\*/g, "").replace(/\\/g, "");
  t = t.replace(/\[\s*\]/g, "").replace(/[\[\]]/g, "");
  return t.split("\n").map(l => l.replace(/\s+$/, ""))
    .filter(l => !l.includes("Planyway") && !l.trim().startsWith("#")).join("\n").trim();
}
 
function legendaDe(desc) {
  for (const sec of String(desc || "").split(/\n-{3,}\s*\n?/)) {
    const s = sec.trim();
    const [primeira, ...resto] = s.split("\n");
    if (primeira.replace(/[\*\\#\s‌]/g, "").toLowerCase().startsWith("legenda")) return limpaTexto(resto.join("\n"));
  }
  return "";
}
 
function diaSP(iso) {
  if (!iso) return null;
  const d = new Date(new Date(iso).getTime() - 3 * 3600 * 1000);
  return d.toISOString().slice(0, 10);
}
 
async function rotaPainel(req, env, ctx) {
  const cache = caches.default;
  const chave = new Request(`https://cache.local/painel/${env.BOARD_ID}`);
  const salvo = await cache.match(chave);
  if (salvo) return json(await salvo.json(), 200, env, req, { "Cache-Control": "public, max-age=60" });
  const [rl, rc] = await Promise.all([
    fetch(`${API}/boards/${env.BOARD_ID}/lists?fields=id,name&${auth(env)}`),
    fetch(`${API}/boards/${env.BOARD_ID}/cards/open?fields=id,shortLink,name,due,dueComplete,idList,labels,desc&${auth(env)}`),
  ]);
  if (!rl.ok || !rc.ok) return json({ erro: "falha ao ler o Trello" }, 502, env, req);
  const listas = Object.fromEntries((await rl.json()).map(l => [l.id, etapa(l.name)]));
  const limite = Date.now() - 120 * 86400 * 1000;
  const cards = [];
  for (const c of await rc.json()) {
    const e = listas[c.idList];
    if (!e) continue;
    // Finalizados antigos não interessam à página
    if (e === "fim" && (!c.due || new Date(c.due).getTime() < limite)) continue;
    const etiquetas = (c.labels || []).map(l => normaliza(l.name));
    cards.push({
      id: c.id, s: c.shortLink, nome: c.name, n: normaliza(c.name),
      dia: diaSP(c.due), concluido: !!c.dueComplete, etapa: e,
      gravado: etiquetas.includes("gravado"), gravar: etiquetas.includes("gravar"),
      video: primeiroVideoDrive(c.desc), legenda: legendaDe(c.desc),
    });
  }
  const dados = { atualizado: new Date().toISOString(), cards };
  ctx.waitUntil(cache.put(chave, new Response(JSON.stringify(dados), { headers: { "Cache-Control": "max-age=120" } })));
  return json(dados, 200, env, req, { "Cache-Control": "public, max-age=60" });
}
 
// ---------------------------------------------------------------- vídeo
async function idsDeVideo(env, ctx) {
  const cache = caches.default;
  const chave = new Request(`https://cache.local/videos/${env.BOARD_ID}`);
  const salvo = await cache.match(chave);
  if (salvo) return new Set(await salvo.json());
  const r = await fetch(`${API}/boards/${env.BOARD_ID}/cards/open?fields=desc&${auth(env)}`);
  if (!r.ok) return new Set();
  const ids = new Set();
  for (const c of await r.json()) {
    for (const m of String(c.desc || "").matchAll(/drive\.google\.com\/file\/d\/([A-Za-z0-9_-]{20,})/g)) ids.add(m[1]);
  }
  ctx.waitUntil(cache.put(chave, new Response(JSON.stringify([...ids]), { headers: { "Cache-Control": "max-age=600" } })));
  return ids;
}
 
async function rotaVideo(req, env, ctx, id) {
  const base = cors(env, req);
  if (!/^[A-Za-z0-9_-]{20,}$/.test(id)) return new Response("link inválido", { status: 400, headers: base });
  if (!(await idsDeVideo(env, ctx)).has(id)) return new Response("vídeo não está em nenhum card do quadro", { status: 404, headers: base });
  const pedido = {};
  const faixa = req.headers.get("Range");
  if (faixa) pedido.Range = faixa;
  const r = await fetch(`https://drive.usercontent.google.com/download?id=${encodeURIComponent(id)}&export=download&confirm=t`, { headers: pedido, redirect: "follow" });
  const tipo = r.headers.get("Content-Type") || "";
  if (!r.ok || tipo.startsWith("text/html")) return new Response("vídeo indisponível", { status: 502, headers: base });
  const cab = new Headers(base);
  cab.set("Content-Type", tipo.startsWith("video/") ? tipo : "video/mp4");
  cab.set("Accept-Ranges", "bytes");
  cab.set("Cache-Control", "public, max-age=3600");
  for (const k of ["Content-Length", "Content-Range"]) { const v = r.headers.get(k); if (v) cab.set(k, v); }
  return new Response(r.body, { status: r.status, headers: cab });
}
 
export default {
  async fetch(req, env, ctx) {
    if (req.method === "OPTIONS") return new Response(null, { headers: cors(env, req) });
    const p = new URL(req.url).pathname.split("/").filter(Boolean);
    try {
      if (req.method === "GET" && p[0] === "card" && p[1]) return await rotaCard(req, env, p[1]);
      if (req.method === "GET" && p[0] === "img" && p.length === 4) return await rotaImagem(req, env, ctx, p[1], p[2], p[3]);
      if (req.method === "POST" && p[0] === "comentario") return await rotaComentario(req, env);
      if (req.method === "POST" && p[0] === "ideia") return await rotaIdeia(req, env);
      if (req.method === "GET" && p[0] === "buscar") return await rotaBuscar(req, env, ctx);
      if (req.method === "GET" && p[0] === "painel") return await rotaPainel(req, env, ctx);
      if (req.method === "GET" && p[0] === "video" && p[1]) return await rotaVideo(req, env, ctx, p[1]);
      return json({ ok: true, servico: "planejamento-clinica-modelo" }, 200, env, req);
    } catch (e) {
      return json({ erro: "falha inesperada" }, 500, env, req);
    }
  },
};
 
