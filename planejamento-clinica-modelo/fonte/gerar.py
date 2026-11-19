# Gera a página de planejamento editorial da Clínica de Olhos Modelo
import datetime as dt
import html
from pathlib import Path
AQUI = Path(__file__).resolve().parent
import os
SITE = os.environ.get("MODO", "site") == "site"
import base64
AGE_LOGO = "data:image/png;base64," + open(AQUI / "age_logo.b64.txt").read().strip()
 
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
 
def fd(s):
    if not s:
        return ""
    x = dt.date.fromisoformat(s)
    return f"{DIAS[x.weekday()]} {x.day:02d}/{x.month:02d}"
 
E = html.escape
 
 
import json as _json, re as _re
TRELLO = _json.load(open(AQUI / "trello_desc.json"))
 
def _limpa(t):
    t = t.replace("‌", "")
    t = _re.sub(r'\[([^\[\]]*)\]\((https?://[^)]*)\)', lambda m: "" if _re.sub(r'[\*\s]', '', m.group(1)).lower() in ("foto", "video", "vídeo") or m.group(1).startswith("http") else m.group(1), t)
    t = t.replace("\\*", "").replace("**", "").replace("\\", "")
    t = _re.sub(r'\[\s*\]', '', t)
    t = t.replace("[", "").replace("]", "")
    t = _re.sub(r'(?im)^\s*Imagem\s*(\d+)\s*:?\s*', lambda m: "Tela " + m.group(1) + " · ", t)
    linhas = [l.rstrip() for l in t.split("\n")]
    linhas = [l for l in linhas if "Planyway" not in l and not l.strip().startswith("#")]
    return "\n".join(linhas).strip()
 
def _secoes(desc):
    return [x.strip() for x in _re.split(r'\n-{3,}\s*\n?', desc)]
 
def legenda_de(code):
    desc = TRELLO.get(code, "")
    for sec in _secoes(desc):
        primeira = _re.sub(r'[\*\\#\s‌]', '', sec.split("\n", 1)[0]).lower()
        if primeira.startswith("legenda"):
            corpo = sec.split("\n", 1)[1] if "\n" in sec else ""
            return _limpa(corpo)
    return ""
 
def telas_de(code):
    desc = TRELLO.get(code, "")
    secs = _secoes(desc)
    return _limpa(secs[0]) if secs else ""
 
def texto_html(t):
    out = []
    for bloco in _re.split(r'\n\s*\n', t):
        ls = [l.strip() for l in bloco.split("\n") if l.strip()]
        if not ls:
            continue
        if all(l.startswith("- ") for l in ls):
            out.append("<ul>" + "".join(f"<li>{E(l[2:])}</li>" for l in ls) + "</ul>")
        else:
            out.append("<p>" + "<br>".join(E(l) for l in ls) + "</p>")
    return "".join(out)
 
WA_NUMERO = ""  # número da AGE com DDI, ex.: 5511999999999
 
def wa(texto):
    from urllib.parse import quote
    base = f"https://wa.me/{WA_NUMERO}" if WA_NUMERO else "https://wa.me/"
    return base + "?text=" + quote(texto)
 
def em_producao(it):
    return it["st"] in ("prop", "rev", "prog") and not it.get("video") and it.get("mat") != "A gravar"
 
def drive(i):
    return f"https://drive.google.com/file/d/{i}/view"
 
STATUS = {
    "pub":    ("Publicado", "ok"),
    "late":   ("Publicado com atraso", "warn"),
    "prog":   ("Programado", "info"),
    "rev":    ("Em revisão da Dra.", "info"),
    "reprov": ("Reprovado", "bad"),
    "nexec":  ("Não produzido", "bad"),
    "adiado": ("Adiado", "warn"),
    "noplan": ("Não planejado", "mute"),
    "prop":   ("Proposta", "prop"),
}
 
# ---------------------------------------------------------------- dados
MESES = [
 {
  "id": "outubro", "nome": "Outubro 2026", "tipo": "Realizado",
  "intro": "Objetivo do mês: retomar a constância com temas semanais conectados, aproveitando o Dia das Crianças.",
  "resumo": "7 conteúdos de feed no calendário · 6 publicados · 1 reprovado",
  "aviso": None,
  "semanas": [
   {"datas": "12 a 18/10", "tema": "Saúde ocular infantil · Semana das Crianças",
    "porque": ["Dia das Crianças (12/10): prevenção e acompanhamento da visão desde a infância."],
    "itens": [
      {"fmt": "Reels", "titulo": "Dia das Crianças: oftalmopediatria, mitos e verdades", "video": "1Wo29Q8zqo0kYrwbsHoWZDWtU5LnnQ-Gm", "trello": "HIi778DU", "quem": "Dra. Adriana + Dra. Renata", "plan": "2026-10-12", "feito": "2026-10-12", "st": "pub", "aprov": "Aprovado"},
      {"fmt": "Carrossel", "titulo": "Exames oftalmológicos em crianças", "trello": "s4JAG0Y1", "plan": "2026-10-14", "feito": "2026-10-14", "st": "pub"},
      {"fmt": "Reels", "titulo": "Por que realizar exame nas crianças?", "video": "13-1ZkDjG2jC6Nr2SFahy_gdQQVViSb5m", "capa": "1H5AjjenkWLY7bZlJhsz8lsNDNgsAS3zv", "trello": "LbuoIEzW", "quem": "Dra. Adriana + Dra. Natalia", "plan": "2026-10-16", "feito": "2026-10-16", "st": "pub", "aprov": "Aprovado"},
    ],
    "stories": "Caixinha publicada em 13/10. As respostas previstas para 14/10 não foram publicadas. Extra: stories do Dia do Médico em 18/10."},
   {"datas": "19 a 25/10", "tema": "A visão vai além do grau · função visual e tecnologia",
    "porque": ["Mostrar que avaliar a visão envolve alinhamento, coordenação dos olhos, função visual e exames de imagem."],
    "itens": [
      {"fmt": "Reels", "titulo": "Avaliação ortóptica", "video": "17G8C0wJ0bGzewt0wdNT7pvDUsWnylXYk", "capa": "1WqSNlF1vHtnzxgIK4EW2yC-G50Hx1hpn", "trello": "I2by9qcr", "quem": "Dra. Adriana + Carmem Silvia (técnica em ortóptica)", "plan": "2026-10-19", "feito": "2026-10-19", "st": "pub", "aprov": "Aprovado"},
      {"fmt": "Carrossel", "titulo": "Exercícios ortópticos: quando podem ser indicados?", "plan": "2026-10-21", "st": "reprov", "aprov": "Reprovado", "nota": "Arquivado em 26/10."},
    ]},
   {"datas": "26 a 31/10", "tema": "Sem tema único no calendário",
    "porque": ["A semana concluiu a função visual e abriu o histórico familiar, que seguiu em novembro com genética ocular."],
    "itens": [
      {"fmt": "Carrossel", "titulo": "Como avaliamos a visão e a função visual?", "trello": "2dD2Cz6e", "plan": "2026-10-21", "feito": "2026-10-27", "st": "pub", "aprov": "Aprovado", "nota": "Previsto para a semana anterior."},
      {"fmt": "Carrossel", "titulo": "Histórico familiar: quais doenças oculares merecem mais atenção?", "trello": "a8n4jUGM", "plan": "2026-10-30", "feito": "2026-10-29", "st": "pub", "nota": "Antecipado em um dia: a data foi ajustada para 29/10 no Trello em 27/10."},
    ]},
  ],
  "remanejado": "Semana “Olho seco e pálpebras”: prevista no Trello para o fim de outubro, com caixinha em 27 e 28/10, o Reels “A pálpebra participa ativamente da saúde ocular” e o carrossel “Exames para avaliação do olho seco”. Remanejada para novembro em 20/10. A pálpebra volta na semana de 23/11.",
 },
 {
  "id": "novembro", "nome": "Novembro 2026", "tipo": "Realizado + proposta",
  "intro": "Objetivo do mês: manter os temas semanais e usar o Dia Mundial do Ceratocone (10/11) e o Dia Mundial do Diabetes (14/11) como gancho. O tema de genética foi definido pela Dra. na reunião de alinhamento.",
  "resumo": "12 conteúdos de feed no calendário · 3 publicados até 18/11 · 1 programado para 19/11",
  "aviso": None,
  "semanas": [
   {"datas": "02 a 08/11", "tema": "Genética ocular e histórico familiar",
    "porque": ["Primeiro tema da sequência definida pela Dra.: genética ocular, depois refrativa, depois pálpebra."],
    "itens": [
      {"fmt": "Reels", "titulo": "Genética ocular", "video": "1r1mSCqV1tHBFwn3tMAoR6zrJ_gkqD9P_", "capa": "1ECymXMwdFhm7lFqiY7bgUE6bvew8avIm", "trello": "dTE2c5oO", "quem": "Dra. Adriana + Dr. Daniel", "plan": "2026-11-03", "feito": "2026-11-04", "st": "pub"},
      {"fmt": "Reels", "titulo": "“Dr., meu problema de visão pode ser genético?”", "trello": "SlttrK0X", "plan": "2026-11-06", "feito": "2026-11-12", "st": "pub", "nota": "Data remarcada para 9, 11 e 12/11."},
    ]},
   {"datas": "09 a 15/11", "tema": "Córnea e ceratocone + Dia Mundial do Diabetes",
    "porque": ["Dia Mundial do Ceratocone (10/11) e Dia Mundial do Diabetes (14/11).", "O carrossel de exames da córnea, previsto para 09/11, foi publicado na semana seguinte, em 18/11."],
    "itens": [
      {"fmt": "Reels", "titulo": "Dia Mundial do Ceratocone: sinais, diagnóstico e acompanhamento", "plan": "2026-11-10", "st": "nexec", "nota": "Dependia de gravação."},
      {"fmt": "Carrossel", "titulo": "Dia Mundial do Diabetes: o diabetes também pode afetar a visão", "trello": "ABvfaX44", "plan": "2026-11-14", "st": "adiado", "nota": "Enviado para aprovação do Dr. Alisson, que não aprovou a tempo da data. O conteúdo foi adiado e volta, sem a referência ao Dia Mundial do Diabetes, na semana de retina e diabetes."},
    ],
    "stories": "Caixinha prevista para 11 e 12/11: sem registro de publicação no Trello."},
   {"datas": "16 a 22/11", "tema": "Da córnea à pálpebra · semana de transição",
    "porque": ["Fecha o tema de córnea, com o carrossel de exames, e abre o tema de pálpebra pedido pela Dra., que segue na semana de 23/11.",
               "Retina e diabetes, previsto para esta semana, passou para janeiro (25 a 31/01), quando os vídeos já estarão gravados e o material pronto pode sair em sequência."],
    "itens": [
      {"fmt": "Carrossel", "titulo": "Exames para avaliação da córnea", "trello": "UXOkYvvP", "plan": "2026-11-09", "feito": "2026-11-18", "st": "pub"},
      {"fmt": "Reels", "titulo": "A pálpebra participa ativamente da saúde ocular", "video": "16_yqotxcOoSM3vn02EKRMWEgSs39VLAr", "capa": "1WUuyIJGjBUdoLMm1qSYON3JtWVjPBN4u", "trello": "YQYhsZY6", "quem": "Dra. Adriana + Dr. João Victor", "plan": "2026-11-19", "feito": "2026-11-19", "st": "prog", "mat": "Gravado", "nota": "Abre o tema de pálpebra. Stories: enquete “Quantas vezes piscamos por dia?” e a resposta."},
    ],
    "reman": "Retina e diabetes foi para janeiro: o carrossel de exames da retina, que está pronto, ficou no banco de vídeos e posts, e os Reels entram na próxima gravação.",
    },
   {"datas": "23 a 29/11", "tema": "Pálpebra · função e estética", "nova": "Nova proposta. Antes: glaucoma.",
    "porque": ["É o próximo tema da sequência definida pela Dra.: genética ocular, refrativa e pálpebra.",
               "Atende ao pedido de falar de estética sem reduzir a pálpebra à aparência: ela protege o olho e espalha a lágrima a cada piscada.",
               "Continua o que o Reels de 19/11 abriu, com o vídeo de cirurgia já gravado com o Dr. João Victor.",
               "O tema está previsto desde outubro. O glaucoma, com vídeos prontos, fica para março, na Semana Mundial do Glaucoma."],
    "itens": [
      {"fmt": "Reels", "titulo": "Cirurgia de pálpebra", "video": "1nnv2a7y7bz9TIJGvFQyRV1-d7yFkQ7Zk", "quem": "Dra. Adriana + Dr. João Victor", "plan": "2026-11-23", "st": "prop", "mat": "Gravado"},
      {"fmt": "Carrossel", "titulo": "Blefaroplastia: estética, função ou os dois?", "plan": "2026-11-25", "st": "prop", "mat": "Texto a produzir", "nota": "A pálpebra protege e espalha a lágrima · o excesso de pele pode pesar no olhar e, em alguns casos, reduzir o campo de visão · por isso a indicação pode ser funcional, estética ou as duas · quem define é a avaliação. Convite: “Saiba quando procurar avaliação”."},
      {"fmt": "Carrossel", "titulo": "Exames para avaliação do olho seco", "trello": "Dtf2A6R0", "plan": "2026-11-27", "st": "prop", "mat": "Pronto (revisar)", "nota": "Liga a pálpebra à lágrima: a cada piscada, a pálpebra espalha a lágrima pela superfície do olho."},
    ],
    "stories": "Caixinha “Dúvidas sobre pálpebras e blefaroplastia” em 25/11, respostas em 26/11. As perguntas abastecem a semana seguinte."},
  ],
 },
 {
  "id": "dezembro", "nome": "Dezembro 2026", "tipo": "Proposta",
  "intro": "Objetivo: mais uma semana de estética com função, leveza com curiosidades sobre os olhos, cuidados nas férias e o fechamento do ano com agradecimento. Os vídeos saem da gravação do fim de novembro.",
  "resumo": "13 conteúdos de feed · 7 vídeos a gravar · 1 vídeo em edição · caixinha em 09/12",
  "aviso": None,
  "semanas": [
   {"datas": "30/11 a 06/12", "tema": "Blefaroplastia · da avaliação à recuperação",
    "porque": ["A Dra. sugeriu temas de até 15 dias. A estética ganha uma segunda semana com outro ângulo: o caminho de quem considera a cirurgia.",
               "Responde às dúvidas da caixinha de 25/11.",
               "Dezembro é quando muita gente planeja procedimentos para as férias. O conteúdo explica o planejamento sem prometer resultado nem prazo de recuperação."],
    "itens": [
      {"fmt": "Reels", "titulo": "Caso de blefaroplastia que não deu certo", "quem": "Dra. Adriana + Dr. João Victor", "plan": "2026-11-30", "st": "prop", "mat": "Em edição", "nota": "Já gravado. Falta a foto do paciente, que a Dra. Adriana vai enviar. Para publicar, é preciso a autorização por escrito do paciente para uso da imagem."},
      {"fmt": "Carrossel", "titulo": "Antes da blefaroplastia: o que é avaliado", "plan": "2026-12-02", "st": "prop", "mat": "Texto a produzir", "nota": "Pálpebra e campo visual, saúde da superfície do olho (olho seco), expectativas, e o pós-operatório, que varia caso a caso. Validar com o Dr. João Victor."},
      {"fmt": "Reels", "titulo": "Respostas da caixinha: dúvidas sobre blefaroplastia", "quem": "Dr. João Victor", "plan": "2026-12-04", "st": "prop", "mat": "A gravar", "nota": "Perguntas reais da caixinha. Se a gravação for antes, usar dúvidas frequentes do consultório."},
    ]},
   {"datas": "07 a 13/12", "tema": "Curiosidades sobre os olhos",
    "porque": ["Tema proposto pela AGE e aceito pela Dra.",
               "Conteúdo leve e fácil de compartilhar, bom para alcançar quem ainda não segue a clínica.",
               "Conversa com a semana de pálpebra: não percebemos a maior parte das piscadas."],
    "itens": [
      {"fmt": "Reels", "titulo": "Você tem um ponto cego em cada olho", "quem": "Dra. Adriana + colega a definir", "plan": "2026-12-07", "st": "prop", "mat": "A gravar", "nota": "Story com o teste do ponto cego para fazer em casa."},
      {"fmt": "Carrossel", "titulo": "4 curiosidades sobre os seus olhos", "plan": "2026-12-09", "st": "prop", "mat": "Texto a produzir", "nota": "Cada olho tem um ponto cego · a imagem chega invertida à retina e o cérebro a corrige · a córnea não tem vasos sanguíneos · você não percebe a maior parte das piscadas. Convite: “Leve sua curiosidade para a próxima consulta”."},
      {"fmt": "Reels", "titulo": "Verdade ou mito? Curiosidades em dupla", "quem": "Dra. Adriana + colega", "plan": "2026-12-11", "st": "prop", "mat": "A gravar"},
    ],
    "stories": "Caixinha “O que você sempre quis saber sobre os olhos?” em 09/12, respostas em 10/12."},
   {"datas": "14 a 20/12", "tema": "Olhos nas férias · sol, água e telas",
    "porque": ["Começo das férias escolares e das viagens.",
               "Retoma assuntos que foram bem em 2026 (protetor solar perto dos olhos, lente de contato na água, telas na infância) com conteúdo novo."],
    "itens": [
      {"fmt": "Reels", "titulo": "Sol, piscina e mar: o que muda para os olhos nas férias", "quem": "Dra. Adriana + colega", "plan": "2026-12-14", "st": "prop", "mat": "A gravar"},
      {"fmt": "Carrossel", "titulo": "Checklist dos olhos para as férias", "plan": "2026-12-16", "st": "prop", "mat": "Texto a produzir", "nota": "Óculos de sol com proteção UV · lente de contato longe da piscina e do mar · protetor solar sem irritar os olhos · colírios de uso contínuo na mala · consulta antes de viajar para quem faz acompanhamento."},
      {"fmt": "Reels", "titulo": "Férias das crianças: as telas não precisam ser vilãs", "quem": "Dra. Renata ou Dra. Natalia", "plan": "2026-12-18", "st": "prop", "mat": "A gravar", "nota": "Mais tempo ao ar livre, olhando para longe."},
    ]},
   {"datas": "21 a 27/12", "tema": "Natal · agradecimento", "nota_sem": "Semana de festa: 2 conteúdos de feed.",
    "porque": ["Tema previsto para a gravação do fim de novembro.",
               "Fortalece a marca e a equipe: o cuidado da Clínica Modelo não depende de uma pessoa só."],
    "itens": [
      {"fmt": "Carrossel", "titulo": "2026 na Clínica Modelo", "plan": "2026-12-21", "st": "prop", "mat": "Texto a produzir", "nota": "Retrospectiva com os temas do ano, a equipe e os 30 anos de carreira da Dra. Adriana. Sem números que não possam ser confirmados."},
      {"fmt": "Reels", "titulo": "Agradecimento de Natal da equipe", "quem": "Equipe Clínica Modelo", "plan": "2026-12-23", "st": "prop", "mat": "A gravar", "nota": "Cada profissional diz uma frase curta; o vídeo fecha com a marca."},
    ],
    "stories": "Funcionamento de fim de ano, depois de confirmar os horários."},
   {"datas": "28/12 a 03/01", "tema": "Réveillon com segurança para os olhos", "nota_sem": "Semana de Ano Novo: 2 conteúdos de feed.",
    "porque": ["Orientação útil para a virada: rolhas de espumante e fogos de artifício podem machucar os olhos."],
    "itens": [
      {"fmt": "Carrossel", "titulo": "Réveillon: 3 cuidados com os olhos", "plan": "2026-12-28", "st": "prop", "mat": "Texto a produzir", "nota": "Rolha de espumante apontada para longe das pessoas · distância dos fogos, principalmente para as crianças · não dormir de lente de contato depois da festa."},
      {"fmt": "Reels", "titulo": "Feliz 2027 da Clínica Modelo", "quem": "Dra. Adriana + equipe", "plan": "2026-12-30", "st": "prop", "mat": "A gravar", "nota": "Na mesma gravação do Natal."},
    ]},
  ],
 },
 {
  "id": "janeiro", "nome": "Janeiro 2027", "tipo": "Proposta",
  "intro": "Objetivo: retomar a sequência pedida pela Dra. com duas semanas de refrativa, cuidar do verão e publicar o material de retina e diabetes que ficou pendente em novembro.",
  "resumo": "12 conteúdos de feed · 7 vídeos a gravar · 1 vídeo e 2 carrosséis já prontos · caixinhas em 06/01 e 20/01",
  "aviso": None,
  "semanas": [
   {"datas": "04 a 10/01", "tema": "Refrativa (1) · as formas de corrigir o grau",
    "porque": ["Tema pedido pela Dra. na reunião de alinhamento, por duas semanas, e que ainda não foi abordado.",
               "No começo do ano muita gente troca óculos e lentes e retoma as consultas."],
    "itens": [
      {"fmt": "Reels", "titulo": "Óculos, lentes de contato ou cirurgia: quem define?", "quem": "Dra. Adriana + Dr. Alisson", "plan": "2027-01-04", "st": "prop", "mat": "A gravar"},
      {"fmt": "Carrossel", "titulo": "Miopia, hipermetropia, astigmatismo e presbiopia", "plan": "2027-01-06", "st": "prop", "mat": "Texto a produzir", "nota": "Uma tela por condição, com palavras do dia a dia."},
      {"fmt": "Reels", "titulo": "Lentes de contato: adaptação e cuidados", "quem": "Dra. Adriana + colega", "plan": "2027-01-08", "st": "prop", "mat": "A gravar"},
    ],
    "stories": "Caixinha sobre grau e correção em 06/01, respostas em 07/01."},
   {"datas": "11 a 17/01", "tema": "Refrativa (2) · cirurgia refrativa",
    "porque": ["Segunda semana do tema, como a Dra. pediu.",
               "Fala de indicação e segurança, sem promessa de deixar os óculos."],
    "itens": [
      {"fmt": "Reels", "titulo": "Cirurgia refrativa: a avaliação vem antes", "quem": "Dr. Alisson", "plan": "2027-01-11", "st": "prop", "mat": "A gravar"},
      {"fmt": "Carrossel", "titulo": "Exames antes da cirurgia refrativa", "plan": "2027-01-13", "st": "prop", "mat": "Texto a produzir", "nota": "Topografia e tomografia de córnea, paquimetria e refração. Confirmar o equipamento antes de citar o Pentacam."},
      {"fmt": "Reels", "titulo": "Depois da cirurgia refrativa: o que esperar", "quem": "Dr. Alisson + Dra. Adriana", "plan": "2027-01-15", "st": "prop", "mat": "A gravar", "nota": "A recuperação varia caso a caso."},
    ]},
   {"datas": "18 a 24/01", "tema": "Verão · olho vermelho e conjuntivite",
    "porque": ["Auge do verão e de ambientes cheios.",
               "Usa um carrossel que já está pronto desde abril."],
    "itens": [
      {"fmt": "Carrossel", "titulo": "3 lugares onde você pode pegar conjuntivite", "trello": "XHndrHyh", "plan": "2027-01-18", "st": "prop", "mat": "Pronto (revisar)"},
      {"fmt": "Reels", "titulo": "Olho vermelho: alergia, conjuntivite ou olho seco?", "quem": "Dra. Adriana + colega", "plan": "2027-01-20", "st": "prop", "mat": "A gravar"},
      {"fmt": "Reels", "titulo": "Conjuntivite: quando procurar o oftalmologista", "quem": "Dra. Adriana + colega", "plan": "2027-01-22", "st": "prop", "mat": "A gravar"},
    ],
    "stories": "Caixinha sobre olho vermelho em 20/01, respostas em 21/01."},
   {"datas": "25 a 31/01", "tema": "Retina e diabetes · acompanhar mesmo sem sintomas",
    "porque": ["Retoma o tema de novembro que ficou sem gravação.",
               "Usa material pronto: o vídeo do OCT e o carrossel do diabetes, sem a referência à data."],
    "itens": [
      {"fmt": "Reels", "titulo": "Sobre o exame OCT", "video": "1ywulJYyxVUfS_tgOL6MyeWsUULjNdakV", "capa": "1RxjECQgFfS0yHeEyi3RP3eddfyNX7Ji-", "trello": "G9Hf3hsL", "quem": "Danilo Freire, técnico em oftalmologia", "plan": "2027-01-25", "st": "prop", "mat": "Gravado", "nota": "O roteiro fala da retina, por isso entra nesta semana. O Danilo aparece como técnico."},
      {"fmt": "Carrossel", "titulo": "O diabetes também pode afetar a visão", "trello": "ABvfaX44", "plan": "2027-01-27", "st": "prop", "mat": "Pronto (ajustar)", "nota": "Tirar a referência ao Dia Mundial do Diabetes."},
      {"fmt": "Reels", "titulo": "Retinopatia diabética: por que acompanhar mesmo sem sintomas?", "quem": "Dra. Adriana + Dra. Jane", "plan": "2027-01-29", "st": "prop", "mat": "A gravar"},
    ]},
  ],
 },
]
 
BANCO = [
 ("Reels", "5 exames importantes para o glaucoma", "Dra. Adriana + Dr. Alisson", "Gravado", "Março de 2027, na Semana Mundial do Glaucoma", "", "1zdZ9M3ZuLjuLMu6HuPU0e24uT4_PA6Vo"),
 ("Carrossel", "Exames para diagnóstico e acompanhamento do glaucoma", "", "Em produção", "Março de 2027", "", ""),
 ("Carrossel", "Exames para avaliação da retina", "", "Pronto", "Uma semana de retina ou de exames, a definir", "Adiado em novembro.", ""),
 ("Vídeos", "Apresentação da equipe (10 vídeos)", "Médicos e técnicos", "Gravados", "A combinar", "Sugestão: série nos stories e no destaque da equipe.", ""),
 ("Vídeo", "Vídeo para a TV da clínica", "", "Pronto", "Recepção", "", "1SHtd3n6uLSlE2DRdljDGSw7my3iJBXwj"),
 ("Reels", "Medir a pressão intraocular", "Dra. Adriana + Dr. Alisson", "Reprovado", "Só com novo roteiro e nova aprovação", "", "1tinEHqcm2GnwnA7h_ScE60w9EOXg9EtD"),
]
 
GRAVACAO = [
 ("Dezembro", [
   ("Respostas sobre blefaroplastia", "Dr. João Victor"),
   ("Você tem um ponto cego em cada olho", "Dra. Adriana + colega"),
   ("Verdade ou mito? Curiosidades", "Dra. Adriana + colega"),
   ("Sol, piscina e mar nas férias", "Dra. Adriana + colega"),
   ("Férias das crianças e telas", "Dra. Renata ou Dra. Natalia"),
   ("Agradecimento de Natal", "Equipe"),
   ("Feliz 2027", "Dra. Adriana + equipe"),
 ]),
 ("Janeiro", [
   ("Óculos, lentes ou cirurgia: quem define?", "Dra. Adriana + Dr. Alisson"),
   ("Lentes de contato: adaptação e cuidados", "A definir"),
   ("Cirurgia refrativa: a avaliação vem antes", "Dr. Alisson"),
   ("Depois da cirurgia refrativa", "Dr. Alisson + Dra. Adriana"),
   ("Olho vermelho: alergia, conjuntivite ou olho seco?", "A definir"),
   ("Conjuntivite: quando procurar o oftalmologista", "A definir"),
   ("Retinopatia diabética sem sintomas", "Dra. Adriana + Dra. Jane"),
 ]),
]
 
# ---------------------------------------------------------------- render
def chip(st):
    lab, cls = STATUS[st]
    return f'<span class="chip c-{cls}">{E(lab)}</span>'
 
def item_html(it, mes_id, wi, ii):
    st = it["st"]
    extra = ""
    if it.get("mat"):
        mcls = "m-ready" if it["mat"].startswith(("Gravado", "Pronto")) else "m-todo"
        extra = f'<span class="chip {mcls}">{E(it["mat"])}</span>'
    linhas = []
    if it.get("quem"):
        linhas.append(f'<p class="quem">{E(it["quem"])}</p>')
    datas = []
    if it.get("plan"):
        datas.append(f'<span><b>{"Previsto" if st in ("prop","rev") else "Planejado"}</b> {fd(it["plan"])}</span>')
    if it.get("feito"):
        datas.append(f'<span><b>{"Publica" if st=="prog" else "Publicado"}</b> {fd(it["feito"])}</span>')
    if datas:
        linhas.append('<p class="datas">' + "".join(datas) + "</p>")
    if it.get("aprov"):
        linhas.append(f'<p class="aprov"><b>Aprovação</b> {E(it["aprov"])}</p>')
    if it.get("nota"):
        linhas.append(f'<p class="nota">{E(it["nota"])}</p>')
    acoes = []
    extras = ""
    if it.get("trello"):
        lg = legenda_de(it["trello"])
        if lg:
            extras += f'<details class="txt"><summary>Ver legenda</summary><div>{texto_html(lg)}</div></details>'
    pendente = st in ("prop", "rev", "prog")
    if SITE:
        midia = ""
        tem_card = bool(it.get("trello"))
        if it.get("video"):
            acoes.append(f'<button type="button" class="btn-ver js-video" data-video="{it["video"]}">▶ Ver vídeo</button>')
        else:
            acoes.append('<button type="button" class="btn-ver js-video" data-video="" hidden>▶ Ver vídeo</button>')
        if it["fmt"] == "Carrossel":
            midia = '<div class="galeria" hidden></div>'
        if em_producao(it):
            acoes.append('<span class="btn-prod">Conteúdo em produção</span>')
        if pendente:
            esconder = " hidden" if (em_producao(it) or not tem_card) else ""
            acoes.append(f'<button type="button" class="btn-aprovar js-aprovar"{esconder}>✓ Aprovar conteúdo</button>')
        acoes.append(f'<button type="button" class="btn-sec js-comentar"{"" if tem_card else " hidden"}>💬 Comentar</button>')
        linhas.append(midia)
        linhas.append('<div class="acoes-card">' + "".join(acoes) + '</div>')
        linhas.append('<form class="form-cmt" hidden><label>Comentário<textarea rows="3" maxlength="2000"></textarea></label><div class="acoes-card"><button type="submit" class="btn-ver">Enviar ao Trello</button><button type="button" class="btn-sec js-cancelar">Cancelar</button></div></form><p class="retorno" role="status"></p>')
        if extras:
            linhas.append(extras)
    else:
        if it.get("video"):
            acoes.append(f'<a class="btn-ver" href="{drive(it["video"])}" target="_blank" rel="noopener">▶ Ver vídeo</a>')
        if em_producao(it):
            acoes.append('<span class="btn-prod">Conteúdo em produção</span>')
        elif pendente:
            quando = f" (previsto para {fd(it['plan'])})" if it.get("plan") else ""
            msg = f"Aprovo o conteúdo: [{it['fmt']}] {it['titulo']}{quando}."
            acoes.append(f'<a class="btn-aprovar" href="{wa(msg)}" target="_blank" rel="noopener">✓ Aprovar conteúdo</a>')
        if acoes:
            linhas.append('<div class="acoes-card">' + "".join(acoes) + '</div>')
        if extras:
            linhas.append(extras)
    cid = f"{mes_id}-s{wi+1}-c{ii+1}"
    dados = f' data-card="{it.get("trello","")}" data-titulo="{E(it["fmt"] + ": " + it["titulo"])}" data-pendente="{1 if st in ("prop","rev","prog") else 0}"' if SITE else ""
    return f'''<article class="card st-{st}" id="{cid}" data-comment-target{dados}>
  <div class="card-top"><span class="fmt">{E(it["fmt"])}</span><span class="chips">{chip(st)}{extra}</span></div>
  <h4>{E(it["titulo"])}</h4>
  {"".join(linhas)}
  <button class="cmt" type="button" hidden>Comentar</button>
</article>'''
 
PLURAL = {"pub": ("publicado", "publicados"), "reprov": ("reprovado", "reprovados"),
          "nexec": ("não produzido", "não produzidos"), "adiado": ("adiado", "adiados"),
          "rev": ("em revisão", "em revisão"), "prog": ("programado", "programados"),
          "prop": ("proposto", "propostos")}
 
def fim_iso(datas, mes_id):
    dd, mm = datas.split(" a ")[-1].strip().split("/")
    ano = 2027 if (mes_id == "janeiro" or mm == "01") else 2026
    return f"{ano}-{mm}-{dd}"
 
def semana_html(s, mes_id, wi):
    itens = "".join(item_html(it, mes_id, wi, i) for i, it in enumerate(s["itens"]))
    porque = "".join(f"<li>{E(p)}</li>" for p in s["porque"])
    nova = f'<span class="badge-nova">{E(s["nova"])}</span>' if s.get("nova") else ""
    notasem = f'<p class="notasem">{E(s["nota_sem"])}</p>' if s.get("nota_sem") else ""
    stories = f'<p class="stories"><b>Stories</b> {E(s["stories"])}</p>' if s.get("stories") else ""
    if s.get("reman"):
        stories = f'<p class="stories"><b>Remanejado</b> {E(s["reman"])}</p>' + stories
    pend = [it for it in s["itens"] if it["st"] in ("prop", "rev", "prog") and not em_producao(it)]
    aprovar_semana = ""
    if pend:
        corpo = "\n".join(f"{n}) [{it['fmt']}] {it['titulo']}" + (f" ({fd(it['plan'])})" if it.get("plan") else "") for n, it in enumerate(pend, 1))
        msg = f"Aprovo a semana {s['datas']}: {s['tema']}.\n{corpo}"
        aprovar_semana = (f'<div class="aprov-semana"><button type="button" class="btn-aprovar js-aprovar-semana">✓ Aprovar a semana inteira</button><span class="retorno" role="status"></span></div>' if SITE else f'<div class="aprov-semana"><a class="btn-aprovar" href="{wa(msg)}" target="_blank" rel="noopener">✓ Aprovar a semana inteira</a></div>')
    cont = {}
    for it in s["itens"]:
        cont[it["st"]] = cont.get(it["st"], 0) + 1
    resumo = "".join(f'<span class="chip c-{STATUS[k][1]}">{v} {PLURAL[k][0 if v == 1 else 1]}</span>' for k, v in cont.items())
    return f'''<details class="semana" id="{mes_id}-s{wi+1}" data-fim="{fim_iso(s["datas"], mes_id)}" data-comment-target open>
  <summary class="sem-head">
    <span class="sem-datas">{E(s["datas"])}</span>
    <span class="sem-tit"><h3>{E(s["tema"])}</h3>{nova}</span>
    <span class="sem-resumo">{resumo}</span>
    <span class="seta" aria-hidden="true"></span>
  </summary>
  <div class="sem-corpo">
    <div class="porque"><span class="lbl">Por que este tema</span><ul>{porque}</ul>{notasem}</div>
    <div class="grid">{itens}</div>
    {stories}
    {aprovar_semana}
    <button class="cmt" type="button" hidden>Comentar a semana</button>
  </div>
</details>'''
 
def seguir_html(m):
    i = next(k for k, x in enumerate(MESES) if x["id"] == m["id"])
    ant = MESES[i - 1] if i > 0 else None
    prox = MESES[i + 1] if i + 1 < len(MESES) else None
    nome = lambda x: E(x["nome"].split()[0])
    a = f'<a class="seg ant" href="#{ant["id"]}">← {nome(ant)}</a>' if ant else '<span></span>'
    b = f'<a class="seg prox" href="#{prox["id"]}">{nome(prox)} →</a>' if prox else '<span></span>'
    return f'<nav class="seguir" aria-label="Outros meses">{a}{b}</nav>'
 
def mes_html(m):
    sem = "".join(semana_html(s, m["id"], i) for i, s in enumerate(m["semanas"]))
    aviso = f'<p class="aviso">{E(m["aviso"])}</p>' if m.get("aviso") else ""
    reman = f'<div class="reman"><span class="lbl">Remanejado</span><p>{E(m["remanejado"])}</p></div>' if m.get("remanejado") else ""
    return f'''<section class="mes" id="{m["id"]}">
  <div class="mes-head">
    <span class="tipo">{E(m["tipo"])}</span>
    <h2>{E(m["nome"])}</h2>
    <p class="intro">{E(m["intro"])}</p>
    <p class="resumo">{E(m["resumo"])}</p>
    {aviso}
  </div>
  {sem}
  {reman}
  {seguir_html(m)}
</section>'''
 
def banco_html():
    cards = ""
    for f, t, q, sit, quando, n, v in BANCO:
        if sit.startswith(("Gravad", "Pronto")):
            ch = f'<span class="chip m-ready">{E(sit)}</span>'
        elif sit.startswith("Reprovad"):
            ch = chip("reprov")
        else:
            ch = f'<span class="chip m-todo">{E(sit)}</span>'
        linhas = []
        if q:
            linhas.append(f'<p class="quem">{E(q)}</p>')
        linhas.append(f'<p class="datas"><span><b>Quando entra</b> {E(quando)}</span></p>')
        if n:
            linhas.append(f'<p class="nota">{E(n)}</p>')
        if v:
            if SITE:
                btn = f'<button type="button" class="btn-ver js-video" data-video="{v}" data-titulo="{E(f + ": " + t)}">▶ Ver vídeo</button>'
            else:
                btn = f'<a class="btn-ver" href="{drive(v)}" target="_blank" rel="noopener">▶ Ver vídeo</a>'
            linhas.append(f'<div class="acoes-card">{btn}</div>')
        cards += f'''<article class="card" data-comment-target>
  <div class="card-top"><span class="fmt">{E(f)}</span><span class="chips">{ch}</span></div>
  <h4>{E(t)}</h4>
  {"".join(linhas)}
  <button class="cmt" type="button" hidden>Comentar</button>
</article>'''
    return f'''<section class="mes fixa" id="banco">
  <div class="mes-head"><span class="tipo">Material pronto ou em andamento</span><h2>Banco de vídeos e posts</h2>
  <p class="intro">O que está gravado ou produzido e ainda não tem semana, com a sugestão de quando entra.</p></div>
  <div class="grid">{cards}</div>
</section>'''
 
def grav_html():
    blocos = ""
    n = 0
    for mes, lst in GRAVACAO:
        lis = ""
        for t, q in lst:
            n += 1
            lis += f'<li data-comment-target><span class="num">{n:02d}</span><span class="gt">{E(t)}</span><span class="quem">{E(q)}</span></li>'
        blocos += f'<div class="gbloco"><h3>Para {E(mes.lower())}</h3><ol>{lis}</ol></div>'
    linha = lambda k: f'''<fieldset class="linha" data-n="{k}"><legend>Ideia {k}</legend>
<label for="ideia-{k}-tema">Tema</label><input id="ideia-{k}-tema" name="tema" type="text" maxlength="200" placeholder="Ex.: o que é ceratocone">
<label for="ideia-{k}-prof">Profissionais envolvidos</label><input id="ideia-{k}-prof" name="prof" type="text" maxlength="200" placeholder="Ex.: Dra. Adriana + Dr. Alisson">
<label for="ideia-{k}-obs">Observação (opcional)</label><textarea id="ideia-{k}-obs" name="obs" rows="2" maxlength="1000"></textarea>
</fieldset>'''
    form = f'''<div class="ideias" id="ideias-dra">
  <h3>Ideias da Dra. Adriana</h3>
  <p class="intro">Escreva aqui os temas que a senhora quer gravar e quem participa. Dá para adicionar quantas ideias quiser e enviar todas de uma vez. A AGE recebe e encaixa nas semanas.</p>
  <form id="form-ideias" novalidate>
    <div id="linhas">{linha(1)}{linha(2)}{linha(3)}</div>
    <div class="acoes"><button type="button" id="add-linha" class="sec">+ Adicionar outra ideia</button><button type="submit" id="enviar" class="pri">Enviar ideias</button></div>
    <p id="msg-ideias" class="msg" role="status"></p>
  </form>
  {'<p class="nota">As ideias enviadas entram como comentário no card “Ideias de vídeos — Dra. Adriana”, no Trello da AGE.</p>' if SITE else '<div class="enviadas"><h4>Ideias enviadas</h4><ul id="lista-ideias"><li class="vazio">Carregando…</li></ul></div>'}
</div>'''
    return f'''<section class="mes fixa" id="gravacao">
  <div class="mes-head"><span class="tipo">Fim de novembro · data a confirmar</span><h2>Próxima gravação</h2>
  <p class="intro">{n} vídeos para dezembro e janeiro, definidos antes da gravação para que cada um já tenha semana e sequência. Se o dia não comportar todos, a prioridade é dezembro; parte de janeiro pode sair em formato mais simples.</p></div>
  <p class="lbl sug">Sugestões da equipe AGE</p>
  <div class="gwrap">{blocos}</div>
  {form}
</section>'''
 
nav = "".join(f'<a href="#{m["id"]}">{E(m["nome"].split()[0])}</a>' for m in MESES)
legenda = "".join(chip(k) for k in ["pub","prog","rev","adiado","reprov","nexec","prop"]) + '<span class="chip m-ready">Gravado / pronto</span><span class="chip m-todo">A gravar / a produzir</span>'
 
CLAUDE_JS = ""  # a versão do Claude (artifact) não é gerada neste repositório
SCRIPT_FINAL = open(AQUI / 'site_js.js').read() if SITE else CLAUDE_JS
 
page = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<script>document.documentElement.classList.add("js");</script>{'<script src="config.js"></script>' if SITE else ''}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Planejamento editorial Clínica Modelo</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Noto+Serif:ital,wdth,wght@0,62.5..100,400..700;1,62.5..100,400..700&display=swap" rel="stylesheet">
<style>
:root {{
  /* Paleta "Clareza" do kit Clínica Modelo + tinta escura para leitura */
  --fundo: #E6E4DD;     /* off-white */
  --papel: #FFFFFF;
  --areia: #EDDABE;
  --bege: #C3B29F;
  --marrom: #6D473B;
  --tinta: #3E312B;
  --cinza: #666666;
  --ok: #4C6B48; --warn: #94651C; --bad: #9A3E2F; --info: #4A6276;
  --display: "Noto Serif", Georgia, "Times New Roman", serif;
  --texto: "Barlow", "DIN Alternate", "Helvetica Neue", Arial, sans-serif;
  /* Layout: coluna única por mês; semana = faixa com justificativa + grade de 3 cards */
  color-scheme: light;
}}
* {{ box-sizing: border-box; }}
[hidden] {{ display: none !important; }}
html {{ scroll-behavior: smooth; }}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
body {{ margin: 0; background: var(--fundo); color: var(--tinta); font: 16px/1.5 var(--texto); }}
.wrap {{ max-width: 1120px; margin: 0 auto; padding: 0 20px 64px; }}
h1, h2, h3 {{ font-family: var(--display); font-stretch: 62.5%; color: var(--marrom); text-wrap: balance; margin: 0; font-weight: 600; }}
h1 {{ font-size: clamp(2.4rem, 6vw, 3.6rem); line-height: 1; }}
h1 em, h2 em {{ font-weight: 400; }}
h2 {{ font-size: 2.4rem; line-height: 1.05; }}
h3 {{ font-size: 1.6rem; line-height: 1.1; }}
h4 {{ font: 600 1.05rem/1.3 var(--texto); margin: 6px 0 4px; color: var(--tinta); }}
.topo {{ padding: 40px 0 20px; display: grid; gap: 12px; }}
.marca {{ font-family: var(--display); font-stretch: 62.5%; font-size: 1.15rem; color: var(--marrom); letter-spacing: .02em; }}
.sub {{ color: var(--cinza); margin: 0; }}
.marcas {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; padding-bottom: 14px; border-bottom: 1px solid var(--bege); margin-bottom: 8px; }}
.assin {{ display: inline-flex; align-items: center; gap: 10px; font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; color: var(--cinza); font-weight: 600; }}
.logo-age {{ display: block; height: auto; }}
.assin-rodape {{ display: flex; align-items: center; gap: 12px; color: var(--tinta); }}
.lead {{ max-width: 68ch; margin: 4px 0 0; }}
.regras {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }}
.regras span {{ background: var(--areia); color: var(--marrom); border-radius: 999px; padding: 4px 12px; font-size: .88rem; font-weight: 500; }}
nav.meses {{ position: sticky; top: 0; z-index: 5; background: var(--fundo); border-bottom: 1px solid var(--bege); display: flex; gap: 4px; overflow-x: auto; padding: 10px 0; }}
nav.meses a {{ color: var(--marrom); text-decoration: none; padding: 6px 14px; border-radius: 999px; font-weight: 600; white-space: nowrap; }}
nav.meses a:hover, nav.meses a:focus-visible {{ background: var(--areia); outline: none; }}
nav.meses a[aria-current="page"] {{ background: var(--marrom); color: #fff; }}
.js .mes {{ display: none; }}
.js .mes.ativo, .js .mes.fixa {{ display: block; }}
.seguir {{ display: flex; justify-content: space-between; gap: 12px; margin: 20px 0 4px; }}
.seguir .seg {{ font: 600 .95rem var(--texto); color: var(--marrom); text-decoration: none; background: var(--areia); border-radius: 999px; padding: 10px 18px; }}
.seguir .seg.prox {{ background: var(--marrom); color: #fff; margin-left: auto; }}
.seguir .seg:focus-visible {{ outline: 2px solid var(--marrom); outline-offset: 2px; }}
.mes.fixa {{ margin-top: 48px; }}
.js .legenda.oculta {{ display: none; }}
.legenda {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 16px 0 8px; align-items: center; font-size: .85rem; }}
.legenda > b {{ margin-right: 4px; color: var(--cinza); font-weight: 500; }}
.mes {{ padding-top: 40px; scroll-margin-top: 56px; }}
.mes-head {{ display: grid; gap: 6px; border-top: 2px solid var(--marrom); padding-top: 16px; margin-bottom: 18px; }}
.tipo {{ font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; color: var(--cinza); font-weight: 600; }}
.intro {{ margin: 0; max-width: 72ch; }}
.resumo {{ margin: 0; font-weight: 600; color: var(--marrom); font-variant-numeric: tabular-nums; }}
.aviso {{ margin: 0; color: var(--bad); font-size: .92rem; }}
.semana {{ background: var(--papel); border-radius: 10px; padding: 16px 18px; margin: 12px 0; scroll-margin-top: 60px; display: block; }}
.sem-head {{ display: grid; grid-template-columns: auto 1fr auto auto; gap: 4px 16px; align-items: center; cursor: pointer; list-style: none; }}
.sem-head::-webkit-details-marker {{ display: none; }}
.sem-head:focus-visible {{ outline: 2px solid var(--marrom); outline-offset: 4px; border-radius: 4px; }}
.sem-resumo {{ display: flex; gap: 4px; flex-wrap: wrap; justify-content: flex-end; }}
.seta {{ width: 10px; height: 10px; border-right: 2px solid var(--marrom); border-bottom: 2px solid var(--marrom); transform: rotate(45deg); transition: transform .15s; margin: 0 4px 4px; }}
details[open] > .sem-head .seta {{ transform: rotate(-135deg); margin-top: 6px; margin-bottom: 0; }}
@media (prefers-reduced-motion: reduce) {{ .seta {{ transition: none; }} }}
.sem-corpo {{ display: grid; gap: 12px; margin-top: 12px; }}
details.semana:not([open]) {{ background: #F7F5F1; }}
.sem-datas {{ font-variant-numeric: tabular-nums; font-weight: 600; color: var(--cinza); white-space: nowrap; }}
.sem-tit {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: baseline; }}
.badge-nova {{ font-size: .8rem; background: var(--marrom); color: #fff; border-radius: 4px; padding: 2px 8px; font-weight: 600; }}
.porque {{ background: #F6F3EE; border-left: 3px solid var(--bege); padding: 10px 14px; border-radius: 0 6px 6px 0; }}
.porque ul {{ margin: 4px 0 0; padding-left: 18px; }}
.porque li {{ margin: 2px 0; max-width: 90ch; }}
.lbl {{ font-size: .78rem; text-transform: uppercase; letter-spacing: .07em; color: var(--marrom); font-weight: 600; }}
.notasem {{ margin: 6px 0 0; color: var(--cinza); font-size: .92rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; }}
.card {{ border: 1px solid #E3DDD3; border-top: 4px solid var(--bege); border-radius: 8px; padding: 12px 14px; display: flex; flex-direction: column; gap: 4px; background: var(--papel); }}
.card.st-pub {{ border-top-color: var(--ok); }}
.card.st-late {{ border-top-color: var(--warn); }}
.card.st-adiado {{ border-top-color: var(--warn); }}
.card.st-prog, .card.st-rev {{ border-top-color: var(--info); }}
.card.st-reprov, .card.st-nexec {{ border-top-color: var(--bad); }}
.card.st-noplan {{ border-top-color: #D9D4CB; background: #FAF8F5; }}
.card.st-prop {{ border-top-color: var(--marrom); }}
.card p {{ margin: 0; font-size: .92rem; }}
.card-top {{ display: flex; justify-content: space-between; gap: 8px; align-items: flex-start; flex-wrap: wrap; }}
.fmt {{ font-size: .75rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 600; color: var(--cinza); }}
.chips {{ display: flex; gap: 4px; flex-wrap: wrap; justify-content: flex-end; }}
.chip {{ font-size: .74rem; font-weight: 600; border-radius: 999px; padding: 2px 9px; white-space: nowrap; border: 1px solid transparent; }}
.c-ok {{ background: #E5EDE2; color: var(--ok); }}
.c-warn {{ background: #F5EAD6; color: var(--warn); }}
.c-bad {{ background: #F4E1DC; color: var(--bad); }}
.c-info {{ background: #E2E9EF; color: var(--info); }}
.c-mute {{ background: #EEEBE6; color: var(--cinza); }}
.c-prop {{ background: var(--marrom); color: #fff; }}
.m-ready {{ background: #fff; border-color: var(--ok); color: var(--ok); }}
.m-todo {{ background: var(--areia); color: var(--marrom); }}
.quem {{ color: var(--marrom); font-weight: 500; }}
.datas {{ display: flex; flex-wrap: wrap; gap: 4px 14px; font-variant-numeric: tabular-nums; color: var(--cinza); }}
.datas b, .aprov b {{ font-weight: 600; color: var(--tinta); }}
.nota {{ color: var(--cinza); }}
.stories {{ margin: 0; font-size: .92rem; color: var(--cinza); }}
.stories b {{ color: var(--tinta); }}
.quem-sou {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-size: .88rem; color: var(--cinza); margin: 4px 0 10px; }}
.quem-sou input {{ font: 600 .9rem var(--texto); color: var(--marrom); border: 1px solid var(--bege); border-radius: 6px; padding: 4px 8px; background: #fff; }}
button.btn-ver, button.btn-sec, button.btn-aprovar {{ border: 0; cursor: pointer; }}
button.btn-sec {{ border: 1px solid var(--marrom); }}
.video-modal {{ border: 0; padding: 0; background: transparent; max-width: none; max-height: none; width: 100%; height: 100%; }}
.video-modal::backdrop {{ background: rgba(30, 22, 18, .82); }}
.vm-box {{ position: fixed; inset: 0; margin: auto; width: min(92vw, calc((100dvh - 96px) * 9 / 16)); height: fit-content; display: flex; flex-direction: column; gap: 10px; }}
.vm-top {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; color: #fff; }}
.vm-titulo {{ margin: 0; font-weight: 600; font-size: .95rem; line-height: 1.3; }}
.vm-fechar {{ flex: none; font: 600 .86rem var(--texto); background: #fff; color: var(--marrom); border: 0; border-radius: 999px; padding: 8px 14px; cursor: pointer; }}
.vm-fechar:focus-visible {{ outline: 2px solid #fff; outline-offset: 2px; }}
.vm-player {{ position: relative; width: 100%; aspect-ratio: 9 / 16; background: #000; border-radius: 10px; overflow: hidden; }}
.vm-player iframe {{ position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }}
.galeria {{ margin-top: 8px; display: flex; gap: 8px; overflow-x: auto; scroll-snap-type: x mandatory; border-radius: 8px; }}
.galeria img {{ flex: 0 0 100%; width: 100%; aspect-ratio: 4 / 5; object-fit: cover; scroll-snap-align: start; border-radius: 8px; background: #F1ECE4; }}
.galeria-nav {{ display: flex; justify-content: space-between; align-items: center; font-size: .8rem; color: var(--cinza); margin-top: 4px; }}
.galeria-nav button {{ font: 600 .9rem var(--texto); background: #fff; border: 1px solid var(--bege); color: var(--marrom); border-radius: 999px; width: 30px; height: 30px; cursor: pointer; }}
.form-cmt {{ display: grid; gap: 6px; margin-top: 8px; }}
.form-cmt label {{ display: grid; gap: 4px; font-size: .82rem; font-weight: 600; color: var(--cinza); }}
.form-cmt textarea {{ font: inherit; font-size: .92rem; border: 1px solid var(--bege); border-radius: 6px; padding: 7px 9px; resize: vertical; }}
.retorno {{ margin: 4px 0 0; font-size: .85rem; color: var(--ok); font-weight: 600; min-height: 0; }}
.retorno.erro {{ color: var(--bad); }}
.retorno.aguarda {{ color: var(--cinza); font-weight: 500; }}
.aprov-semana {{ align-items: center; gap: 10px; }}
.acoes-card {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
.btn-ver, .btn-sec {{ font: 600 .86rem var(--texto); text-decoration: none; border-radius: 999px; padding: 6px 14px; display: inline-flex; align-items: center; gap: 6px; }}
.btn-ver {{ background: var(--marrom); color: #fff; }}
.btn-ver:hover {{ background: #5A3A30; }}
.btn-sec {{ border: 1px solid var(--marrom); color: var(--marrom); background: #fff; }}
.btn-sec:hover {{ background: var(--areia); }}
.btn-ver:focus-visible, .btn-sec:focus-visible, details.txt summary:focus-visible {{ outline: 2px solid var(--marrom); outline-offset: 2px; }}
.btn-prod {{ font: 600 .82rem var(--texto); border-radius: 999px; padding: 6px 12px; background: #F1ECE4; color: var(--cinza); border: 1px dashed var(--bege); }}
.btn-aprovar {{ font: 600 .86rem var(--texto); text-decoration: none; border-radius: 999px; padding: 6px 14px; background: var(--ok); color: #fff; display: inline-flex; align-items: center; gap: 6px; }}
.btn-aprovar:hover {{ background: #3E5A3B; }}
.btn-aprovar:focus-visible {{ outline: 2px solid var(--ok); outline-offset: 2px; }}
.aprov-semana {{ display: flex; justify-content: flex-end; }}
details.txt {{ margin-top: 6px; border-top: 1px solid #EEE8DF; padding-top: 6px; }}
details.txt summary {{ cursor: pointer; font-weight: 600; font-size: .86rem; color: var(--marrom); list-style: none; }}
details.txt summary::-webkit-details-marker {{ display: none; }}
details.txt summary::before {{ content: "+ "; }}
details.txt[open] summary::before {{ content: "− "; }}
details.txt div {{ font-size: .88rem; color: var(--tinta); margin-top: 6px; display: grid; gap: 6px; }}
details.txt div p, details.txt div ul {{ margin: 0; }}
details.txt div ul {{ padding-left: 18px; }}
.reman {{ background: var(--areia); border-radius: 10px; padding: 14px 18px; }}
.reman p {{ margin: 4px 0 0; max-width: 90ch; }}
button.cmt {{ align-self: flex-start; margin-top: auto; font: 600 .82rem var(--texto); color: var(--marrom); background: transparent; border: 1px solid var(--bege); border-radius: 6px; padding: 4px 10px; cursor: pointer; }}
.card button.cmt {{ margin-top: 8px; }}
button.cmt:hover {{ background: var(--areia); }}
button.cmt:focus-visible, nav.meses a:focus-visible {{ outline: 2px solid var(--marrom); outline-offset: 2px; }}
.tbl {{ overflow-x: auto; background: var(--papel); border-radius: 10px; }}
table {{ border-collapse: collapse; width: 100%; min-width: 760px; font-size: .92rem; }}
th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #ECE7DF; vertical-align: top; }}
th {{ font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; color: var(--cinza); font-weight: 600; }}
.gwrap {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px; }}
.gbloco {{ background: var(--papel); border-radius: 10px; padding: 16px 18px; }}
.gbloco ol {{ list-style: none; margin: 10px 0 0; padding: 0; display: grid; gap: 2px; }}
.gbloco li {{ display: grid; grid-template-columns: 2.2em 1fr; gap: 0 8px; padding: 6px 0; border-bottom: 1px solid #F0ECE5; }}
.gbloco .num {{ font-variant-numeric: tabular-nums; color: var(--bege); font-weight: 600; grid-row: span 2; }}
.gbloco .quem {{ grid-column: 2; font-size: .88rem; }}
.sug {{ margin: 0 0 10px; }}
.ideias {{ background: var(--papel); border-radius: 10px; padding: 18px; margin-top: 18px; display: grid; gap: 12px; border-top: 4px solid var(--marrom); }}
#linhas {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }}
.linha {{ border: 1px solid #E3DDD3; border-radius: 8px; padding: 10px 14px 14px; margin: 0; display: grid; gap: 4px; }}
.linha legend {{ font-family: var(--display); font-stretch: 62.5%; color: var(--marrom); font-size: 1.2rem; padding: 0 4px; }}
.linha label {{ font-size: .82rem; font-weight: 600; color: var(--cinza); margin-top: 4px; }}
.linha input, .linha textarea {{ font: inherit; font-size: .95rem; color: var(--tinta); border: 1px solid var(--bege); border-radius: 6px; padding: 7px 9px; background: #FCFBF9; width: 100%; resize: vertical; }}
.linha input:focus-visible, .linha textarea:focus-visible {{ outline: 2px solid var(--marrom); outline-offset: 1px; }}
.acoes {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.acoes button {{ font: 600 .92rem var(--texto); border-radius: 6px; padding: 8px 16px; cursor: pointer; }}
.acoes .pri {{ background: var(--marrom); color: #fff; border: 1px solid var(--marrom); }}
.acoes .sec {{ background: transparent; color: var(--marrom); border: 1px solid var(--bege); }}
.acoes button:disabled {{ opacity: .5; cursor: not-allowed; }}
.acoes button:focus-visible {{ outline: 2px solid var(--marrom); outline-offset: 2px; }}
.msg {{ margin: 0; font-size: .92rem; color: var(--marrom); min-height: 1.4em; }}
.msg.erro {{ color: var(--bad); }}
.enviadas h4 {{ margin: 0 0 6px; }}
#lista-ideias {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }}
#lista-ideias li {{ background: #F6F3EE; border-radius: 8px; padding: 10px 14px; display: grid; gap: 2px; }}
#lista-ideias li.vazio {{ background: transparent; padding: 0; color: var(--cinza); }}
#lista-ideias .it-tema {{ font-weight: 600; }}
#lista-ideias .it-meta {{ font-size: .82rem; color: var(--cinza); display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }}
#lista-ideias .rem {{ font: 600 .8rem var(--texto); color: var(--bad); background: none; border: none; padding: 0; cursor: pointer; text-decoration: underline; }}
footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--bege); color: var(--cinza); font-size: .88rem; display: grid; gap: 6px; }}
footer .ass {{ color: var(--tinta); }}
@media (max-width: 640px) {{
  .sem-head {{ grid-template-columns: 1fr auto; }}
  .sem-datas, .sem-tit, .sem-resumo {{ grid-column: 1; }}
  .seta {{ grid-column: 2; grid-row: 1; }}
  .sem-resumo {{ justify-content: flex-start; }}
  .semana {{ padding: 14px; }}
  h2 {{ font-size: 2rem; }}
}}
</style>
</head>
<body>
<div class="wrap">
  <header class="topo">
    <div class="marcas">
      <span class="marca">Clínica de Olhos Modelo</span>
      <span class="assin"><span>Planejamento por</span><img class="logo-age" src="{AGE_LOGO}" alt="AGE Criação" width="72" height="35"></span>
    </div>
    <h1>Planejamento <em>editorial</em></h1>
    <p class="sub">Instagram @clinica_modelo · outubro de 2026 a janeiro de 2027 · atualizado em 18/11/2026</p>
    <p class="lead">O que foi planejado e o que foi publicado em outubro e novembro, e a proposta para dezembro e janeiro. Cada semana tem um tema, três conteúdos em formatos que se completam e o motivo da escolha. Para pedir ajuste ou aprovar, use “Comentar” no conteúdo ou na semana.</p>
    <div class="regras"><span>1 tema por semana</span><span>3 conteúdos de feed: 2 Reels + 1 carrossel</span><span>Caixinha a cada 15 dias, respostas no dia seguinte</span><span>Aprovação da Dra. antes de publicar</span></div>
  </header>
  {'<div class="quem-sou"><label for="meu-nome">Comentários e aprovações enviados em nome de</label><input id="meu-nome" type="text" maxlength="80" value="Dra. Adriana"></div>' if SITE else ''}
  <nav class="meses" aria-label="Meses">{nav}</nav>
  <div class="legenda"><b>Legenda</b>{legenda}</div>
  {"".join(mes_html(m) for m in MESES)}
  {banco_html()}
  {grav_html()}
  {'<dialog id="video-modal" class="video-modal" aria-label="Vídeo"><div class="vm-box"><div class="vm-top"><p class="vm-titulo"></p><button type="button" class="vm-fechar">✕ Fechar</button></div><div class="vm-player"></div></div></dialog>' if SITE else ''}
  <footer>
    <p class="ass">Todas as peças levam a identificação: Clínica de Olhos Modelo · Responsável técnica: Dra. Adriana Rodrigues Corpa | CRM-SP 87235 | RQE 56606</p>
    <p class="assin-rodape"><img class="logo-age" src="{AGE_LOGO}" alt="AGE Criação" width="62" height="30"><span>Planejamento editorial desenvolvido pela AGE Criação para a Clínica de Olhos Modelo.</span></p>
    <p>Fontes: calendário editorial e métricas da AGE Criação, quadro de produção no Trello e documento de alinhamento com a Dra. Adriana.</p>
  </footer>
</div>
<script>
(() => {{
  const vistas = [...document.querySelectorAll("section.mes:not(.fixa)")].map(s => s.id);
  const inicial = "novembro";
  const legenda = document.querySelector(".legenda");
  function mostrar(rolar) {{
    const h = location.hash.slice(1);
    const id = vistas.includes(h) ? h : inicial;
    document.querySelectorAll("section.mes:not(.fixa)").forEach(s => s.classList.toggle("ativo", s.id === id));
    document.querySelectorAll("nav.meses a").forEach(a => {{
      if (a.getAttribute("href") === "#" + id) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    }});
    if (rolar) document.querySelector("nav.meses").scrollIntoView({{ block: "start" }});
  }}
  document.querySelectorAll("nav.meses a, nav.seguir a").forEach(a => a.addEventListener("click", e => {{
    e.preventDefault();
    const alvo = a.getAttribute("href");
    if (location.hash !== alvo) location.hash = alvo; else mostrar(true);
  }}));
  window.addEventListener("hashchange", () => mostrar(true));
  const t = new Date();
  const hoje = t.getFullYear() + "-" + String(t.getMonth() + 1).padStart(2, "0") + "-" + String(t.getDate()).padStart(2, "0");
  document.querySelectorAll("details.semana[data-fim]").forEach(d => {{ if (d.dataset.fim < hoje) d.open = false; }});
  mostrar(false);
}})();
{SCRIPT_FINAL}</script>
</body>
</html>
'''
 
open(AQUI.parent / "site" / "index.html" if SITE else AQUI / "planejamento-claude.html", "w", encoding="utf-8").write(page)
print("ok", len(page))
 
