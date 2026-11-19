# Planejamento editorial · Clínica de Olhos Modelo

Página de planejamento da AGE Criação para a Clínica de Olhos Modelo, publicada no GitHub Pages e ligada ao Trello.

- `site/`: o endereço do conector (`config.js`). A página (`index.html`) é gerada automaticamente a cada publicação.
- `worker/`: o conector do Trello (Cloudflare Worker). Mostra as artes anexadas aos cards e transforma aprovações, comentários e ideias da página em comentários no Trello.
- `fonte/`: o gerador da página (`gerar.py`), com os dados de cada mês.
- `.github/workflows/publicar.yml`: publica a página e o conector a cada atualização.

## Configuração (uma vez)

### 1. Ativar o GitHub Pages
No repositório: **Settings → Pages → Source: GitHub Actions**.

### 2. Chave do Trello
1. Entre em https://trello.com/power-ups/admin com a conta da AGE.
2. Crie uma integração (New) com o nome "Planejamento Clínica Modelo", no workspace da AGE.
3. Em **API key**, gere a chave e copie.
4. Ao lado da chave, clique em **Token** (gerar token manualmente), autorize e copie o token.

### 3. Conta gratuita no Cloudflare
1. Crie a conta em https://dash.cloudflare.com/sign-up.
2. Copie o **Account ID** (aparece em Workers & Pages, na lateral).
3. Em **My Profile → API Tokens → Create Token**, use o modelo **Edit Cloudflare Workers** e copie o token.

### 4. Guardar os segredos no GitHub
No repositório: **Settings → Secrets and variables → Actions → New repository secret**. Crie quatro:

| Nome | Valor |
|---|---|
| `TRELLO_KEY` | chave do Trello |
| `TRELLO_TOKEN` | token do Trello |
| `CLOUDFLARE_API_TOKEN` | token do Cloudflare |
| `CLOUDFLARE_ACCOUNT_ID` | Account ID do Cloudflare |

Esses valores ficam guardados no GitHub e no Cloudflare. Eles nunca aparecem na página.

### 5. Publicar
Em **Actions → Publicar página e conector → Run workflow**. Ao terminar, a página fica em `https://<usuário>.github.io/<repositório>/` e o conector em `https://planejamento-clinica-modelo.<subdomínio>.workers.dev`. O endereço do conector vai em `site/config.js`.

## Como funciona com o Trello
- **Artes:** cada carrossel mostra as imagens anexadas ao card correspondente no Trello, na ordem dos anexos. Ao anexar a arte no card, ela aparece na página.
- **Vídeos:** tocam dentro da página pelo player do Google Drive (arquivos com acesso "qualquer pessoa com o link").
- **Aprovar e comentar:** viram comentários dentro do card do próprio post no Trello, com o nome de quem enviou. Nenhum card novo é criado. Quando o post ainda não tem card informado, a página procura no quadro um card com o mesmo título; enquanto não existir, os botões de aprovar e comentar ficam escondidos.
- **Ideias para a gravação:** entram como comentário no card definido em `CARD_IDEIAS` (`worker/wrangler.toml`).

Quem tem o link da página consegue ver, aprovar e comentar. Não há dados de pacientes na página.
