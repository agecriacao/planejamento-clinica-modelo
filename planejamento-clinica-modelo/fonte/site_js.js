(() => {
  const API = (window.PLANEJAMENTO_API || "").replace(/\/$/, "");
  const ST = window.PLAN_STATUS || {};
  const nomeEl = document.getElementById("meu-nome");
  try { const n = localStorage.getItem("planejamento-nome"); if (n) nomeEl.value = n; } catch (e) {}
  nomeEl.addEventListener("change", () => { try { localStorage.setItem("planejamento-nome", nomeEl.value.trim()); } catch (e) {} });
  const nome = () => nomeEl.value.trim() || "Dra. Adriana";
 
  const avisar = (el, texto, erro) => { if (!el) return; el.textContent = texto; el.classList.toggle("erro", !!erro); };
  const esc = t => String(t || "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const norm = t => String(t || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
    .replace(/\[[^\]]*\]/g, " ").replace(/[^a-z0-9]+/g, " ").trim();
  const DIAS = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"];
  const fd = iso => { const [y, m, d] = iso.split("-").map(Number); const x = new Date(Date.UTC(y, m - 1, d)); return DIAS[x.getUTCDay()] + " " + String(d).padStart(2, "0") + "/" + String(m).padStart(2, "0"); };
  const semPrefixo = n => String(n || "").replace(/^\s*\[[^\]]*\]\s*/, "");
  const fmtDe = n => { const m = /^\s*\[([^\]]+)\]/.exec(n || ""); return m ? m[1].trim() : ""; };
  const tituloDe = art => (art.dataset.titulo || "").replace(/^[^:]+:\s*/, "");
  const K = { pub: "ok", late: "ok", prog: "info", rev: "info", prop: "prop" };
 
  async function enviar(rota, corpo) {
    if (!API) throw new Error("A página ainda não está ligada ao Trello.");
    const r = await fetch(API + rota, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.erro || "Não foi possível enviar agora.");
    return j;
  }
 
  // ------------------------------------------------ vídeo em janela centralizada
  const modal = document.getElementById("video-modal");
  const vmPlayer = modal && modal.querySelector(".vm-player");
  const vmTitulo = modal && modal.querySelector(".vm-titulo");
  function abrirVideo(id, titulo) {
    vmPlayer.innerHTML = "";
    const f = document.createElement("iframe");
    f.src = "https://drive.google.com/file/d/" + encodeURIComponent(id) + "/preview";
    f.allow = "autoplay; fullscreen";
    f.allowFullscreen = true;
    f.title = "Vídeo: " + titulo;
    vmPlayer.appendChild(f);
    vmTitulo.textContent = titulo.replace(/^[^:]+:\s*/, "");
    document.documentElement.classList.add("video-aberto");
    modal.showModal();
    modal.querySelector(".vm-fechar").focus();
  }
  if (modal) {
    modal.querySelector(".vm-fechar").addEventListener("click", () => modal.close());
    modal.addEventListener("click", e => { if (!e.target.closest(".vm-top, .vm-player")) modal.close(); });
    modal.addEventListener("close", () => { vmPlayer.innerHTML = ""; document.documentElement.classList.remove("video-aberto"); });
  }
 
  // ------------------------------------------------ ações (delegadas: valem também para cards criados pelo Trello)
  document.addEventListener("click", async e => {
    const v = e.target.closest(".js-video");
    if (v) {
      if (!v.dataset.video || !modal) return;
      const alvo = v.closest("[data-titulo]");
      abrirVideo(v.dataset.video, v.dataset.titulo || (alvo && alvo.dataset.titulo) || "");
      return;
    }
    const ap = e.target.closest(".js-aprovar");
    if (ap) {
      const card = ap.closest("article.card");
      const ret = card.querySelector(".retorno");
      ap.disabled = true; avisar(ret, "Enviando aprovação…");
      try {
        await enviar("/comentario", { card: card.dataset.card, titulo: card.dataset.titulo, tipo: "aprovacao", nome: nome() });
        ap.textContent = "✓ Aprovado"; avisar(ret, "Aprovação registrada no Trello.");
      } catch (err) { ap.disabled = false; avisar(ret, err.message, true); }
      return;
    }
    const cm = e.target.closest(".js-comentar");
    if (cm) {
      const f = cm.closest("article.card").querySelector(".form-cmt");
      f.hidden = !f.hidden;
      if (!f.hidden) f.querySelector("textarea").focus();
      return;
    }
    const cn = e.target.closest(".js-cancelar");
    if (cn) { cn.closest(".form-cmt").hidden = true; return; }
    const sem = e.target.closest(".js-aprovar-semana");
    if (sem) aprovarSemana(sem);
  });
 
  document.addEventListener("submit", async e => {
    const f = e.target.closest(".form-cmt");
    if (!f) return;
    e.preventDefault();
    const card = f.closest("article.card");
    const ret = card.querySelector(".retorno");
    const ta = f.querySelector("textarea");
    const texto = ta.value.trim();
    if (!texto) { avisar(ret, "Escreva o comentário antes de enviar.", true); return; }
    const btn = f.querySelector('button[type="submit"]');
    btn.disabled = true; avisar(ret, "Enviando…");
    try {
      await enviar("/comentario", { card: card.dataset.card, titulo: card.dataset.titulo, tipo: "comentario", texto, nome: nome() });
      ta.value = ""; f.hidden = true; avisar(ret, "Comentário enviado ao Trello.");
    } catch (err) { avisar(ret, err.message, true); }
    btn.disabled = false;
  });
 
  async function aprovarSemana(b) {
    const semana = b.closest("details.semana");
    const ret = b.parentElement.querySelector(".retorno");
    const cards = [...semana.querySelectorAll('article.card[data-pendente="1"]')].filter(c => {
      const a = c.querySelector(".js-aprovar"); return a && !a.hidden && !a.disabled;
    });
    if (!cards.length) { avisar(ret, "Nada pendente de aprovação nesta semana."); return; }
    b.disabled = true; avisar(ret, "Enviando aprovações…");
    let ok = 0, erro = "";
    for (const c of cards) {
      try {
        await enviar("/comentario", { card: c.dataset.card, titulo: c.dataset.titulo, tipo: "aprovacao", nome: nome() });
        ok += 1; const a = c.querySelector(".js-aprovar"); a.textContent = "✓ Aprovado"; a.disabled = true;
      } catch (err) { erro = err.message; }
    }
    if (erro) { b.disabled = false; avisar(ret, ok + " aprovado(s). " + erro, true); }
    else { b.textContent = "✓ Semana aprovada"; avisar(ret, "Aprovações registradas no Trello."); }
  }
 
  // ------------------------------------------------ mídia do card (vídeo e artes)
  function liberarAprovacao(art) {
    const prod = art.querySelector(".btn-prod");
    if (prod) prod.remove();
    const apr = art.querySelector(".js-aprovar");
    if (apr && art.dataset.pendente === "1") apr.hidden = false;
  }
 
  function montarGaleria(art, imagens) {
    const g = art.querySelector(".galeria");
    if (!g || !imagens.length || g.childElementCount) return;
    imagens.forEach((im, i) => {
      const img = document.createElement("img");
      img.src = API + im.src;
      img.alt = "Tela " + (i + 1) + " de " + imagens.length + ": " + tituloDe(art);
      img.loading = "lazy";
      g.appendChild(img);
    });
    g.hidden = false;
    if (imagens.length > 1) {
      const nav = document.createElement("div");
      nav.className = "galeria-nav";
      const ant = document.createElement("button"); ant.type = "button"; ant.textContent = "‹"; ant.setAttribute("aria-label", "Tela anterior");
      const prox = document.createElement("button"); prox.type = "button"; prox.textContent = "›"; prox.setAttribute("aria-label", "Próxima tela");
      const cont = document.createElement("span");
      const atual = () => Math.round(g.scrollLeft / g.clientWidth);
      const upd = () => { cont.textContent = "Tela " + (atual() + 1) + " de " + imagens.length; };
      ant.addEventListener("click", () => g.scrollTo({ left: (atual() - 1) * g.clientWidth, behavior: "smooth" }));
      prox.addEventListener("click", () => g.scrollTo({ left: (atual() + 1) * g.clientWidth, behavior: "smooth" }));
      g.addEventListener("scroll", () => requestAnimationFrame(upd));
      upd();
      nav.append(ant, cont, prox);
      g.after(nav);
    }
    liberarAprovacao(art);
  }
 
  function aplicarVideo(art, video) {
    const bv = art.querySelector(".js-video");
    if (!bv || !video || (art.dataset.fmt || "") !== "Reels") return;
    bv.dataset.video = video;   // o link do Trello é o que vale
    bv.hidden = false;
    liberarAprovacao(art);
  }
 
  function carregarArtes(art) {
    if (!art.querySelector(".galeria") || !art.dataset.card) return;
    fetch(API + "/card/" + encodeURIComponent(art.dataset.card)).then(r => r.ok ? r.json() : null)
      .then(d => { if (d) { montarGaleria(art, d.imagens || []); aplicarVideo(art, d.video); } }).catch(() => {});
  }
 
  function ligar(art, id) {
    art.dataset.card = id;
    const c = art.querySelector(".js-comentar");
    if (c) c.hidden = false;
    const a = art.querySelector(".js-aprovar");
    if (a && art.dataset.pendente === "1" && !art.querySelector(".btn-prod")) a.hidden = false;
  }
 
  function semCard(art) {
    if (art.dataset.pendente !== "1") return;
    const ret = art.querySelector(".retorno");
    if (ret) { ret.textContent = "Aguardando o card no Trello para receber aprovação e comentários."; ret.classList.add("aguarda"); }
  }
 
  // ------------------------------------------------ dados do Trello aplicados ao post
  function legendaHtml(t) {
    return t.split(/\n\s*\n/).map(b => {
      const ls = b.split("\n").map(l => l.trim()).filter(Boolean);
      if (!ls.length) return "";
      if (ls.every(l => l.startsWith("- "))) return "<ul>" + ls.map(l => "<li>" + esc(l.slice(2)) + "</li>").join("") + "</ul>";
      return "<p>" + ls.map(esc).join("<br>") + "</p>";
    }).join("");
  }
 
  function aplicarLegenda(art, legenda) {
    if (!legenda) return;
    let det = art.querySelector("details.txt");
    if (!det) {
      det = document.createElement("details");
      det.className = "txt";
      det.innerHTML = "<summary>Ver legenda</summary><div></div>";
      art.querySelector(".cmt") ? art.insertBefore(det, art.querySelector(".cmt")) : art.appendChild(det);
    }
    det.querySelector("div").innerHTML = legendaHtml(legenda);
  }
 
  function aplicarSituacao(art, st) {
    if (!ST[st]) return;
    art.dataset.st = st;
    art.className = art.className.replace(/\bst-\S+/, "st-" + st);
    const chip = art.querySelector(".card-top .chips .chip");
    if (chip) { chip.className = "chip c-" + ST[st][1]; chip.textContent = ST[st][0]; }
    if (st === "pub") {
      art.dataset.pendente = "0";
      art.querySelectorAll(".js-aprovar, .btn-prod").forEach(x => x.remove());
    }
  }
 
  function aplicarData(art, dia, st) {
    if (!dia) return;
    art.dataset.dia = dia;
    const p = art.querySelector(".datas");
    if (!p) return;
    const rot = st === "pub" ? "Publicado" : st === "prog" ? "Programado para" : "Previsto";
    p.innerHTML = "<span><b>" + rot + "</b> " + fd(dia) + "</span>";
  }
 
  function semanaDe(dia, semanas) {
    return semanas.find(s => s.dataset.inicio <= dia && dia <= s.dataset.fim) || null;
  }
 
  function etapaParaSituacao(c) {
    if (c.etapa === "fim" || c.concluido) return "pub";
    if (c.etapa === "agend") return "prog";
    if (c.etapa === "aprov") return "rev";
    return "prop";
  }
 
  function aplicar(art, c, semanas) {
    const fmt = art.dataset.fmt || fmtDe(c.nome);
    const titulo = semPrefixo(c.nome);
    const h = art.querySelector(".tit");
    if (h && titulo) h.textContent = titulo;
    art.dataset.titulo = fmt + ": " + titulo;
    const st = etapaParaSituacao(c);
    aplicarSituacao(art, st);
    aplicarData(art, c.dia, st);
    if (c.gravado) {
      const m = [...art.querySelectorAll(".chip.m-todo")].find(x => /gravar/i.test(x.textContent));
      if (m) { m.className = "chip m-ready"; m.textContent = "Gravado"; }
    }
    // mudou de data para outra semana: o post muda de semana
    const sem = c.dia && semanaDe(c.dia, semanas);
    if (sem && !sem.contains(art)) sem.querySelector(".grid").appendChild(art);
  }
 
  function novoCard(c, fmt) {
    const titulo = semPrefixo(c.nome);
    const art = document.createElement("article");
    art.className = "card st-prop";
    art.id = "trello-" + c.s;
    art.setAttribute("data-comment-target", "");
    Object.assign(art.dataset, { card: c.s, titulo: fmt + ": " + titulo, pendente: "1", dia: "", fmt, st: "prop", sync: "1" });
    art.innerHTML =
      '<div class="card-top"><span class="fmt">' + esc(fmt) + '</span><span class="chips"><span class="chip c-prop">Proposta</span></span></div>' +
      '<h4 class="tit">' + esc(titulo) + '</h4>' +
      '<p class="nota">Incluído no Trello.</p>' +
      '<p class="datas"></p>' +
      (fmt === "Carrossel" ? '<div class="galeria" hidden></div>' : "") +
      '<div class="acoes-card"><button type="button" class="btn-ver js-video" data-video="" hidden>▶ Ver vídeo</button>' +
      '<span class="btn-prod">Conteúdo em produção</span>' +
      '<button type="button" class="btn-aprovar js-aprovar" hidden>✓ Aprovar conteúdo</button>' +
      '<button type="button" class="btn-sec js-comentar">💬 Comentar</button></div>' +
      '<form class="form-cmt" hidden><label>Comentário<textarea rows="3" maxlength="2000"></textarea></label>' +
      '<div class="acoes-card"><button type="submit" class="btn-ver">Enviar ao Trello</button><button type="button" class="btn-sec js-cancelar">Cancelar</button></div></form>' +
      '<p class="retorno" role="status"></p>';
    return art;
  }
 
  function cardBanco(c, fmt) {
    const titulo = semPrefixo(c.nome);
    const art = document.createElement("article");
    art.className = "card banco-item";
    art.dataset.ids = c.id;
    art.dataset.titulo = fmt + ": " + titulo;
    art.innerHTML =
      '<div class="card-top"><span class="fmt">' + esc(fmt) + '</span><span class="chips">' +
      (c.gravado ? '<span class="chip m-ready">Gravado</span>' : '<span class="chip m-todo">Na Gaveta</span>') + '</span></div>' +
      '<h4>' + esc(titulo) + '</h4>' +
      '<p class="datas"><span><b>Quando entra</b> A definir</span></p>' +
      (c.video ? '<div class="acoes-card"><button type="button" class="btn-ver js-video" data-video="' + esc(c.video) + '">▶ Ver vídeo</button></div>' : "");
    return art;
  }
 
  // ------------------------------------------------ calendário e resumos refeitos a partir dos posts
  function refazerCalendario() {
    document.querySelectorAll(".cal-grid .cal-p:not(.k-conf)").forEach(b => b.remove());
    document.querySelectorAll("section.mes:not(#banco) article.card[data-dia]").forEach(art => {
      const dia = art.dataset.dia;
      if (!dia) return;
      const cel = document.querySelector('.cal-d[data-dia="' + dia + '"]');
      if (!cel) return;
      const st = art.dataset.st;
      const fmt = art.dataset.fmt || "";
      const tit = (art.querySelector(".tit") || art.querySelector("h4")).textContent;
      const lab = ST[st] ? ST[st][0] : "";
      const b = document.createElement("button");
      b.type = "button";
      b.className = "cal-p k-" + (K[st] || "off") + (art.dataset.dra ? " p-dra" : "");
      b.dataset.alvo = art.id;
      b.title = fmt + ": " + tit + " · " + lab;
      b.setAttribute("aria-label", fmt + ": " + tit + " (" + lab + ")");
      b.innerHTML = '<span class="cal-f">' + (fmt === "Reels" ? "R" : fmt === "Carrossel" ? "C" : esc(fmt.slice(0, 1))) + '</span><span class="cal-t">' + esc(tit) + "</span>";
      cel.insertBefore(b, cel.querySelector(".k-conf"));
    });
  }
 
  function refazerResumos(semanas) {
    semanas.forEach(s => {
      const cont = {};
      s.querySelectorAll(".grid article.card").forEach(a => { cont[a.dataset.st] = (cont[a.dataset.st] || 0) + 1; });
      const alvo = s.querySelector(".sem-resumo");
      if (!alvo) return;
      alvo.innerHTML = Object.entries(cont).filter(([k]) => ST[k]).map(([k, v]) =>
        '<span class="chip c-' + ST[k][1] + '">' + v + " " + ST[k][2][v === 1 ? 0 : 1] + "</span>").join("");
    });
  }
 
  function ordenar(semanas) {
    semanas.forEach(s => {
      const g = s.querySelector(".grid");
      [...g.children].sort((a, b) => (a.dataset.dia || "").localeCompare(b.dataset.dia || "")).forEach(x => g.appendChild(x));
    });
  }
 
  // ------------------------------------------------ sincronização com o Trello
  async function sincronizar() {
    const r = await fetch(API + "/painel");
    if (!r.ok) throw new Error("painel");
    const { cards = [] } = await r.json();
    const porId = new Map();
    cards.forEach(c => { porId.set(c.id, c); porId.set(c.s, c); });
    const usados = new Set();
    const semanas = [...document.querySelectorAll("details.semana[data-inicio]")];
    const banco = document.getElementById("banco-grid");
    document.querySelectorAll("#banco-grid .banco-item[data-ids]").forEach(b => b.dataset.ids.split(" ").filter(Boolean).forEach(i => usados.add(i)));
    const artigos = [...document.querySelectorAll("section.mes:not(#banco) article.card[data-titulo]")];
 
    // 1) posts que já têm card definido; 2) os demais pelo título
    const achar = art => {
      if (art.dataset.card) return porId.get(art.dataset.card) || null;
      const t = norm(tituloDe(art));
      return cards.find(x => !usados.has(x.id) && x.n === t) ||
        (t.length >= 12 ? cards.find(x => !usados.has(x.id) && x.n.includes(t)) : null);
    };
    const ordem = [...artigos.filter(a => a.dataset.card), ...artigos.filter(a => !a.dataset.card)];
    for (const art of ordem) {
      const c = achar(art);
      if (!c) {
        if (art.dataset.card) { carregarArtes(art); ligar(art, art.dataset.card); } else semCard(art);
        continue;
      }
      usados.add(c.id);
      ligar(art, c.s);
      if (art.dataset.sync === "1") {
        if (c.etapa === "gaveta") {   // foi para a Gaveta: sai da semana e vai para o Banco
          art.remove();
          banco.appendChild(cardBanco(c, art.dataset.fmt || fmtDe(c.nome)));
          continue;
        }
        aplicar(art, c, semanas);
        aplicarLegenda(art, c.legenda);
      }
      aplicarVideo(art, c.video);
      carregarArtes(art);
    }
 
    // Cards novos no Trello que ainda não estão na página
    const ini = semanas.length ? semanas[0].dataset.inicio : "";
    const fim = semanas.length ? semanas[semanas.length - 1].dataset.fim : "";
    for (const c of cards) {
      if (usados.has(c.id)) continue;
      const fmt = fmtDe(c.nome);
      if (fmt !== "Reels" && fmt !== "Carrossel") continue;
      usados.add(c.id);
      if (c.etapa === "gaveta") { banco.appendChild(cardBanco(c, fmt)); continue; }
      if (c.etapa === "fim" || !c.dia || c.dia < ini || c.dia > fim) continue;
      const sem = semanaDe(c.dia, semanas);
      if (!sem) continue;
      const art = novoCard(c, fmt);
      sem.querySelector(".grid").appendChild(art);
      aplicar(art, c, semanas);
      aplicarLegenda(art, c.legenda);
      aplicarVideo(art, c.video);
      carregarArtes(art);
    }
 
    ordenar(semanas);
    refazerResumos(semanas);
    refazerCalendario();
  }
 
  // Sem o painel (conector antigo ou fora do ar): só liga os cards e busca vídeo e artes
  function modoSimples() {
    document.querySelectorAll("section.mes:not(#banco) article.card[data-titulo]").forEach(art => {
      if (art.dataset.card) {
        ligar(art, art.dataset.card);
        fetch(API + "/card/" + encodeURIComponent(art.dataset.card)).then(r => r.ok ? r.json() : null)
          .then(d => { if (d) { montarGaleria(art, d.imagens || []); aplicarVideo(art, d.video); } }).catch(() => {});
        return;
      }
      fetch(API + "/buscar?q=" + encodeURIComponent(tituloDe(art))).then(r => r.ok ? r.json() : null).then(d => {
        if (d && d.card) {
          ligar(art, d.card);
          fetch(API + "/card/" + encodeURIComponent(d.card)).then(r => r.ok ? r.json() : null)
            .then(x => { if (x) { montarGaleria(art, x.imagens || []); aplicarVideo(art, x.video); } }).catch(() => {});
        } else semCard(art);
      }).catch(() => {});
    });
  }
 
  if (API) sincronizar().catch(modoSimples);
 
  // ------------------------------------------------ ideias para a gravação
  const form = document.getElementById("form-ideias");
  const linhas = document.getElementById("linhas");
  const msg = document.getElementById("msg-ideias");
  let n = linhas.querySelectorAll(".linha").length;
  document.getElementById("add-linha").addEventListener("click", () => {
    n += 1;
    const f = linhas.querySelector(".linha").cloneNode(true);
    f.querySelector("legend").textContent = "Ideia " + n;
    f.querySelectorAll("input, textarea").forEach(el => { el.value = ""; el.id = "ideia-" + n + "-" + el.name; });
    f.querySelectorAll("label").forEach(l => { const c = l.getAttribute("for").split("-").pop(); l.setAttribute("for", "ideia-" + n + "-" + c); });
    linhas.appendChild(f);
    f.querySelector("input").focus();
  });
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const itens = [...linhas.querySelectorAll(".linha")].map(f => ({
      tema: f.querySelector('[name="tema"]').value.trim(),
      prof: f.querySelector('[name="prof"]').value.trim(),
      obs: f.querySelector('[name="obs"]').value.trim(),
    })).filter(i => i.tema || i.prof || i.obs);
    if (!itens.length) { avisar(msg, "Preencha pelo menos um tema antes de enviar.", true); return; }
    if (itens.some(i => !i.tema)) { avisar(msg, "Cada ideia precisa de um tema.", true); return; }
    const btn = document.getElementById("enviar");
    btn.disabled = true; avisar(msg, "Enviando…");
    let ok = 0;
    for (const i of itens) {
      try { await enviar("/ideia", { ...i, nome: nome() }); ok += 1; }
      catch (err) { avisar(msg, (ok ? ok + " ideia(s) enviada(s). " : "") + err.message, true); btn.disabled = false; return; }
    }
    linhas.querySelectorAll("input, textarea").forEach(el => el.value = "");
    btn.disabled = false;
    avisar(msg, ok === 1 ? "Ideia enviada ao Trello. Obrigada!" : ok + " ideias enviadas ao Trello. Obrigada!");
  });
})();
 
