// Conector entre a página de planejamento e o Trello.
// Guarda a chave do Trello em segredo (Cloudflare) para que a página pública nunca a exponha.
//
// Rotas:
//   GET  /card/:id                 -> artes (anexos de imagem) e link de vídeo do Drive de um card
//   GET  /img/:card/:anexo/:arq     -> a imagem do anexo, servida para a página
//   POST /comentario               -> {card?, texto, nome, tipo: "aprovacao"|"comentario", titulo}
//   POST /ideia                    -> {tema, prof, obs, nome}  (comentário no card de ideias)
//   GET  /buscar?q=título          -> procura no quadro o card de um post pelo título

const API = "https://api.trello.com/1";

function cors(env, req) {
  const origem = req.headers.get("Origin") || "";
  const permitido = (env.ALLOWED_ORIGIN || "*").split(",").map(s => s.trim());
  const ok = permitido.includes("*") || permitido.includes(origem);
  return {
    "Access-Control-Allow-Origin": ok ? (origem || "*") : permitido[0],
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
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

function primeiroVideoDrive(desc) {
  const m = /drive\.google\.com\/file\/d\/([A-Za-z0-9_-]{20,})/.exec(desc || "");
  return m ? m[1] : null;
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
  const achado = cards.find(c => c.n === q) || cards.find(c => c.n.includes(q) || (c.n.length >= 12 && q.includes(c.n)));
  return achado ? json({ card: achado.s }, 200, env, req, { "Cache-Control": "public, max-age=300" })
                : json({ card: null }, 404, env, req);
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
      return json({ ok: true, servico: "planejamento-clinica-modelo" }, 200, env, req);
    } catch (e) {
      return json({ erro: "falha inesperada" }, 500, env, req);
    }
  },
};
