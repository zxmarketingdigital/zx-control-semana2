# ZX Control — Semana 2: Operação Profissional

> Repositório exclusivo para alunos do ZX Control.
> Pré-requisito: Semana 1 concluída.
> Ao final desta sessão você terá RTK, 7 skills, Guardião 24/7, Supabase na nuvem e Mini-CRM publicado — sem digitar um único comando.

---

## O que você vai ter no final

| O que | Detalhe |
|-------|---------|
| RTK instalado | 60-90% menos tokens no Claude Code — automático |
| 7 Skills profissionais | `/status`, `/healthcheck`, `/fix`, `/dedup`, `/preflight`, `/harvest`, `/encerrar` |
| Guardião + Heartbeat | Monitoramento automático em 3 camadas — avisa no WhatsApp se algo cair |
| Banco Supabase | Seus contatos e disparos guardados na nuvem |
| Mini-CRM | Interface web para gerenciar contatos — publicada no Cloudflare Pages |
| Mission Control | Painel visual da operação no browser |

---

## Como começar

```bash
gh repo clone zxmarketingdigital/zx-control-semana2 ~/zx-control-semana2
cd ~/zx-control-semana2
claude
```

O Claude lê as instruções e conduz você por tudo — sem precisar digitar mais nada.

---

## Pré-requisitos

| Requisito | Versão mínima | Por que |
|-----------|--------------|---------|
| Python | 3.9+ | Scripts de setup |
| Node.js | 18+ | wrangler (deploy CRM) |
| Git | qualquer recente | Clonar o repositório |
| Semana 1 concluída | — | Base da operação (WhatsApp + email) |
| Conta Supabase | gratuita | Banco de dados na nuvem |
| Conta Cloudflare | gratuita | Deploy do CRM |

> **Supabase:** crie em https://app.supabase.com — plano gratuito é suficiente.
> **Cloudflare:** crie em https://cloudflare.com — plano gratuito é suficiente.

---

## As 8 Etapas

| # | Etapa | O que instala |
|---|-------|--------------|
| 0 | Boas-vindas + Base | Estrutura de pastas, verificação Semana 1 |
| 1 | Mission Control | Painel visual HTML no browser |
| 2 | RTK + Hooks | Otimizador de tokens no Claude Code |
| 3 | Skills Profissionais | 7 skills em `~/.claude/skills/` |
| 4 | Guardião + Heartbeat | 3 LaunchAgents de monitoramento |
| 5 | Supabase | Banco de dados na nuvem |
| 6 | Importar Contatos | Migração da Semana 1 ou importação manual |
| 7 | Mini-CRM Cloudflare | Interface web publicada |
| 8 | Finalização | Resumo + Mission Control completo |

---

## Estrutura do repositório

```
zx-control-semana2/
├── CLAUDE.md                  # Instrutor automático — Claude lê e executa
├── README.md                  # Este arquivo
├── setup/
│   ├── setup_base.py          # Etapa 0 — Boas-vindas + Base
│   ├── setup_mission.py       # Etapa 1 — Mission Control
│   ├── setup_rtk.py           # Etapa 2 — RTK + Hooks
│   ├── setup_skills.py        # Etapa 3 — Skills profissionais
│   ├── setup_guardian.py      # Etapa 4 — Guardião + Heartbeat
│   ├── setup_supabase.py      # Etapa 5 — Supabase
│   ├── import_contacts.py     # Etapa 6 — Importar contatos
│   ├── setup_crm.py           # Etapa 7 — Mini-CRM Cloudflare
│   └── setup_final.py         # Etapa 8 — Finalização
├── scripts/
│   ├── lib.py                 # Utilitários compartilhados
│   ├── guardian.py            # Guardião + heartbeat 3 camadas
│   ├── supabase_sync.py       # Client Supabase (apenas stdlib)
│   └── mission_control.py     # Gerador do painel visual
├── skills/
│   ├── status/SKILL.md        # /status
│   ├── healthcheck/SKILL.md   # /healthcheck
│   ├── fix/SKILL.md           # /fix
│   ├── dedup/SKILL.md         # /dedup
│   ├── preflight/SKILL.md     # /preflight
│   ├── harvest/SKILL.md       # /harvest
│   └── encerrar/SKILL.md      # /encerrar
├── crm/
│   ├── index.html             # Login (Supabase Auth)
│   ├── app.html               # App principal (CRUD contatos)
│   ├── app.js                 # Lógica (Supabase JS client)
│   └── style.css              # Estilos compartilhados
├── templates/
│   └── mission-control/
│       └── index.html         # Template do painel (antes do setup)
├── sql/
│   └── 001_init.sql           # Tabelas Supabase
└── docs/
    ├── visao-geral.md         # O que é cada componente
    └── troubleshooting.md     # Problemas comuns e soluções
```

---

## O Guardian — Monitoramento em 3 Camadas

```
Watchdog  (5min)   → verifica diretamente: Evolution API, dispatcher, contacts.db
Heartbeat (10min)  → verifica: watchdog está ativo e recente?
Last Resort(20min) → verifica: heartbeat está ok? Alerta crítico se não
```

Se algo falhar, você recebe um aviso no WhatsApp automaticamente.

---

## Semana 1

Se você ainda não fez a Semana 1:

```bash
gh repo clone zxmarketingdigital/zx-control-semana1 ~/zx-control-semana1
cd ~/zx-control-semana1
claude
```

A Semana 1 configura WhatsApp, Email, Agente IA e Monitor — a fundação que a Semana 2 potencializa.

---

## Precisa de ajuda?

Acesse o grupo do ZX Control ou abra uma issue neste repositório.
