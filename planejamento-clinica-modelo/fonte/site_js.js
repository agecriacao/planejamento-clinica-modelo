(() => {
  const API = (window.PLANEJAMENTO_API || "").replace(/\/$/, "");
  const nomeEl = document.getElementById("meu-nome");
  try { const n = localStorage.getItem("planejamento-nome"); if (n) nomeEl.value = n; } catch (e) {}
  nomeEl.addEventListener("change", () => { try { localStorage.setItem("planejamento-nome", nomeEl.value.trim()); } catch (e) {} });
  const nome = () => nomeEl.value.trim() || "Dra. Adriana";
 
  const avisar = (el, texto, erro) => { if (!el) return; el.textContent = texto; el.classList.toggle("erro", !!erro); };
 
  async function enviar(rota, corpo) {
    if (!API) throw new Error("A página ainda não está ligada ao Trello.");
    const r = await fetch(API + rota, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.erro || "Não foi possível enviar agora.");
    return j;
  }
 
  // Vídeo em janela centralizada (player do Google Drive)
  const modal = document.getElementById("video-modal");
  const vmPlayer = modal && modal.querySelector(".vm-player");
  const vmTitulo = modal && modal.querySelector(".vm-titulo");
  function fecharVideo() { if (modal.open) modal.close(); }
  function abrirVideo(id, titulo) {
    vmPlayer.innerHTML = "";
    const f = document.createElement("iframe");
    f.src = "https://drive.google.com/file/d/" + encodeURIComponent(id) + "/preview";
    f.allow = "autoplay; fullscreen";
    f.allowFullscreen = true;
    f.title = "Vídeo: " + titulo;
    vmPlayer.appendChild(f);
    vmTitulo.textContent = titulo.replace(/^[^:]+:\s*/, "");
    modal.showModal();
    modal.querySelector(".vm-fechar").focus();
  }
  if (modal) {
    modal.querySelector(".vm-fechar").addEventListener("click", fecharVideo);
    // Clique fora do vídeo fecha
    modal.addEventListener("click", e => { if (!e.target.closest(".vm-top, .vm-player")) fecharVideo(); });
    // Ao fechar, para o vídeo
    modal.addEventListener("close", () => { vmPlayer.innerHTML = ""; });
  }
  document.querySelectorAll(".js-video").forEach(b => b.addEventListener("click", () => {
    if (!b.dataset.video || !modal) return;
    const alvo = b.closest("[data-titulo]");
    abrirVideo(b.dataset.video, b.dataset.titulo || (alvo && alvo.dataset.titulo) || "");
  }));
 
  // Galeria do carrossel a partir dos anexos do card no Trello
  function montarGaleria(card, imagens) {
    const g = card.querySelector(".galeria");
    if (!g || !imagens.length) return;
    imagens.forEach((im, i) => {
      const img = document.createElement("img");
      img.src = API + im.src;
      img.alt = "Tela " + (i + 1) + " de " + imagens.length + ": " + card.dataset.titulo;
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
    // Arte encontrada: o conteúdo deixa de estar "em produção"
    const prod = card.querySelector(".btn-prod");
    if (prod) prod.remove();
    const apr = card.querySelector(".js-aprovar");
    if (apr) apr.hidden = false;
  }
 
  function carregarCard(card) {
    const id = card.dataset.card;
    return fetch(API + "/card/" + encodeURIComponent(id)).then(r => r.ok ? r.json() : null).then(d => {
      if (!d) return;
      if (card.querySelector(".galeria")) montarGaleria(card, d.imagens || []);
      const bv = card.querySelector(".js-video");
      // O link do vídeo no Trello é o que vale: substitui o que estiver na página
      if (bv && d.video && (card.dataset.titulo || "").startsWith("Reels")) { bv.dataset.video = d.video; bv.hidden = false; }
    }).catch(() => {});
  }
 
  function ligarCard(card, id) {
    card.dataset.card = id;
    const c = card.querySelector(".js-comentar");
    if (c) c.hidden = false;
    const a = card.querySelector(".js-aprovar");
    if (a && !card.querySelector(".btn-prod")) a.hidden = false;
    return carregarCard(card);
  }
 
  if (API) {
    document.querySelectorAll("article.card").forEach(card => {
      if (card.dataset.card) { carregarCard(card); return; }
      // Sem card informado: procura no Trello um card com o mesmo título
      const titulo = (card.dataset.titulo || "").replace(/^[^:]+:\s*/, "");
      fetch(API + "/buscar?q=" + encodeURIComponent(titulo)).then(r => r.ok ? r.json() : null).then(d => {
        if (d && d.card) ligarCard(card, d.card);
        else if (card.dataset.pendente === "1") {
          const ret = card.querySelector(".retorno");
          if (ret) { ret.textContent = "Aguardando o card no Trello para receber aprovação e comentários."; ret.classList.add("aguarda"); }
        }
      }).catch(() => {});
    });
  }
 
  // Aprovar um conteúdo
  document.querySelectorAll(".js-aprovar").forEach(b => b.addEventListener("click", async () => {
    const card = b.closest("article.card");
    const ret = card.querySelector(".retorno");
    b.disabled = true; avisar(ret, "Enviando aprovação…");
    try {
      await enviar("/comentario", { card: card.dataset.card, titulo: card.dataset.titulo, tipo: "aprovacao", nome: nome() });
      b.textContent = "✓ Aprovado"; avisar(ret, "Aprovação registrada no Trello.");
    } catch (e) { b.disabled = false; avisar(ret, e.message, true); }
  }));
 
  // Comentar um conteúdo
  document.querySelectorAll(".js-comentar").forEach(b => b.addEventListener("click", () => {
    const card = b.closest("article.card");
    const f = card.querySelector(".form-cmt");
    f.hidden = !f.hidden;
    if (!f.hidden) f.querySelector("textarea").focus();
  }));
  document.querySelectorAll(".form-cmt").forEach(f => {
    f.querySelector(".js-cancelar").addEventListener("click", () => { f.hidden = true; });
    f.addEventListener("submit", async e => {
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
  });
 
  // Aprovar a semana inteira
  document.querySelectorAll(".js-aprovar-semana").forEach(b => b.addEventListener("click", async () => {
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
      } catch (e) { erro = e.message; }
    }
    if (erro) { b.disabled = false; avisar(ret, ok + " aprovado(s). " + erro, true); }
    else { b.textContent = "✓ Semana aprovada"; avisar(ret, "Aprovações registradas no Trello."); }
  }));
 
  // Ideias para a gravação
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
 
