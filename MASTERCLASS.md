# MasterClass — Setup 2: Operação Profissional

> Roteiro da aula. Os `BUNNY_GUID_*` são preenchidos depois de gravar e cortar
> a aula — não preencha valores reais aqui.

## Promessa da aula

Sair de uma operação básica (Semana 1) para uma **operação profissional**: mais
barata de rodar, monitorada sozinha e com os dados na nuvem, acessíveis de
qualquer lugar.

Ao final o aluno tem: RTK economizando tokens, 7 skills de rotina, Guardião
vigiando 24/7, banco na nuvem e o próprio Mini-CRM publicado.

## Estrutura geral (duração estimada: 50min)

| # | Bloco | Tempo | Vídeo |
|---|-------|-------|-------|
| 1 | Hook + o que muda da Semana 1 pra 2 | 00:00 — 00:04 | `BUNNY_GUID_S2_1` |
| 2 | Mission Control + RTK (o painel e a economia) | 00:04 — 00:16 | `BUNNY_GUID_S2_2` |
| 3 | Skills + Guardião (a operação que se cuida sozinha) | 00:16 — 00:30 | `BUNNY_GUID_S2_3` |
| 4 | Supabase + contatos + Mini-CRM no ar | 00:30 — 00:46 | `BUNNY_GUID_S2_4` |
| 5 | Fechamento + o que vem na Semana 3 | 00:46 — final | `BUNNY_GUID_S2_5` |

## Roteiro

### 1. Abertura (hook)

Abrir pela dor concreta: a operação da Semana 1 funciona, mas ela é **cara de
rodar, cega e local**. Cara porque cada sessão queima token à toa. Cega porque
quando algo cai, ninguém avisa — o aluno descobre pelo cliente. Local porque os
contatos estão presos numa máquina só.

Prometer o destino: no fim desta aula os três problemas estão resolvidos, e
nenhum comando foi digitado pelo aluno.

### 2. Mission Control + RTK

**Mission Control (Etapa 1)** — mostrar o painel abrindo no browser, ainda
vazio, e explicar que ele vai se preenchendo sozinho a cada etapa. É a tela do
"está tudo de pé?" que o aluno vai abrir todo dia.

**RTK (Etapa 2)** — o ponto que mais gera pergunta. Explicar em uma frase: ele
filtra o retorno dos comandos antes de chegar no Claude, cortando o que é
repetido. Mostrar o `rtk gain` com número real na tela — a economia precisa ser
vista, não prometida. Deixar claro que depois de instalado o aluno não faz nada:
funciona sozinho, sem perder funcionalidade.

### 3. Skills + Guardião

**Skills (Etapa 3)** — o pulo do gato é o aluno entender que skill não é
"comando técnico", é rotina embalada. Demonstrar ao vivo pelo menos duas:
`/status` (abrir o dia) e `/encerrar` (fechar o dia com resumo). Citar as outras
cinco pelo uso, não pelo nome: corrigir problema, limpar contato duplicado,
conferir antes de um disparo, guardar aprendizado.

**Guardião (Etapa 4)** — mostrar as 3 camadas e, principalmente, o alerta
chegando no WhatsApp. É o bloco que vende sozinho: a partir daqui a operação
avisa antes do cliente reclamar. Mencionar que roda em segundo plano e que o
aluno só interage quando recebe alerta.

### 4. Supabase + contatos + Mini-CRM

Bloco mais longo e o mais delicado — envolve criar conta em dois serviços.

**Supabase (Etapa 5)** — enquadrar como "uma planilha na nuvem, só que rápida e
segura". Mostrar onde pegar as credenciais e rodar o SQL de criação das tabelas.

**Contatos (Etapa 6)** — mostrar a migração do que já existe da Semana 1. Se o
aluno não tiver lista, mostrar o caminho de importar depois — ninguém trava aqui.

**Mini-CRM (Etapa 7)** — o clímax da aula: a URL publicada abrindo no browser,
com os contatos do aluno dentro. Terminar o bloco com o aluno logando no próprio
CRM.

Avisar o ponto onde mais gente empaca: o token do Cloudflare precisa de permissão
de Pages, e o `wrangler` precisa estar instalado antes.

### 5. Encerramento

Recapitular o antes/depois nos três eixos (custo, monitoramento, nuvem) e mostrar
o Mission Control já preenchido — o mesmo painel vazio do começo da aula, agora
completo. Fechar com os comandos do dia a dia e um gancho curto para a Semana 3.

CTA único → https://zxlab.com.br/mission-control

## Erros comuns a mostrar na aula

Vale gravar cada um acontecendo — o aluno reconhece o próprio erro e não abre
chamado:

- **RTK "instalado" mas sem economia** — o hook não entrou; conferir com `rtk gain`.
- **Guardião sem alertar** — os agendamentos não subiram; a etapa mostra como recarregar.
- **CRM publica mas abre em branco** — credenciais do banco não foram injetadas no build.
- **Contatos duplicados depois da importação** — é esperado; existe rotina pronta pra limpar.
