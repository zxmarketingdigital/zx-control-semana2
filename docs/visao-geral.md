# Visao Geral — ZX Control Semana 2

## O que e a Semana 2

A Semana 2 transforma a fundacao criada na Semana 1 em uma **operacao profissional**:
econômica em tokens, monitorada 24/7 e com dados na nuvem.

## O que voce tem apos a Semana 2

| Componente | O que faz | Onde fica |
|------------|-----------|-----------|
| RTK | Reduz 60-90% o custo de tokens do Claude Code | `~/.claude/settings.json` (hook) |
| 7 Skills | Comandos prontos para o dia a dia | `~/.claude/skills/` |
| Guardian | Monitoramento automatico em 3 camadas | `~/.operacao-ia/scripts/guardian.py` |
| Supabase | Banco de dados na nuvem | app.supabase.com |
| Mini-CRM | Interface web para gerenciar contatos | Cloudflare Pages |
| Mission Control | Painel visual da operacao | `~/.operacao-ia/mission-control/index.html` |

## Estrutura de pastas

```
~/.operacao-ia/
├── config/
│   ├── config.json              # Configuracoes de tudo
│   └── week2_checkpoint.json    # Progresso do setup
├── scripts/
│   ├── guardian.py              # Guardian + heartbeat
│   ├── lib.py                   # Utilitarios compartilhados
│   └── mission_control.py       # Gerador do painel
├── data/
│   └── contacts.db              # Banco local de contatos (backup)
├── logs/
│   ├── heartbeat/               # Snapshots do guardian
│   │   ├── watchdog.json
│   │   ├── heartbeat.json
│   │   └── last_resort.json
│   └── harvest/                 # Aprendizados das sessoes
│       └── YYYY-MM-DD.md
└── mission-control/
    └── index.html               # Painel visual
```

## Skills instaladas

| Comando | O que faz | Quando usar |
|---------|-----------|-------------|
| `/status` | Health check completo | Todo dia ao abrir Claude |
| `/healthcheck` | Verificacao rapida | Quando quiser checar algo rapido |
| `/fix` | Corrige problemas autonomamente | Quando algo nao esta funcionando |
| `/dedup` | Remove contatos duplicados | Apos importacoes |
| `/preflight` | Pre-voo antes de operacoes criticas | Antes de disparos em massa |
| `/harvest` | Captura aprendizados da sessao | Ao final de cada sessao |
| `/encerrar` | Fecha a sessao com resumo | Sempre ao terminar o trabalho |

## Guardian — As 3 Camadas

```
Watchdog  (5min)   → verifica: Evolution API, dispatcher, contacts.db
Heartbeat (10min)  → verifica: watchdog esta rodando e recente?
Last Resort(20min) → verifica: heartbeat esta ok? Se nao: alerta critico
```

Cada camada salva um snapshot em `~/.operacao-ia/logs/heartbeat/`.
Se algo falhar, o alerta vai para o WhatsApp do aluno.

## config.json — Campos da Semana 2

Campos adicionados apos o setup:

```json
{
  "supabase_url": "https://xxx.supabase.co",
  "supabase_anon_key": "...",
  "supabase_service_role_key": "...",
  "cloudflare_account_id": "...",
  "crm_project_name": "meu-nome-crm",
  "crm_url": "https://meu-nome-crm.pages.dev",
  "week2": {
    "completed": true,
    "completed_at": "2026-04-08T14:30:00"
  }
}
```
