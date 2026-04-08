# Troubleshooting — ZX Control Semana 2

## Problemas mais comuns

---

### RTK nao instalado apos Etapa 2

**Sintoma:** `which rtk` retorna vazio.

**Causa:** cargo nao estava disponivel e o download do binario falhou.

**Fix:**
```bash
# Opcao 1: instalar via cargo
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
cargo install rtk

# Opcao 2: instalar Homebrew (se nao tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install rtk
```

---

### Guardian nao aparece no launchctl list

**Sintoma:** `launchctl list | grep guardian` retorna vazio.

**Causa:** plist nao foi carregado ou foi removido.

**Fix:**
```bash
# Recarregar
launchctl load ~/Library/LaunchAgents/br.zxlab.operacao-ia.guardian.watchdog.plist
launchctl load ~/Library/LaunchAgents/br.zxlab.operacao-ia.guardian.heartbeat.plist
launchctl load ~/Library/LaunchAgents/br.zxlab.operacao-ia.guardian.last_resort.plist

# Verificar
launchctl list | grep guardian
```

Se os plist nao existirem:
```bash
cd ~/zx-control-semana2 && python3 setup/setup_guardian.py
```

---

### Supabase retorna 401 (Unauthorized)

**Sintoma:** requests falham com HTTP 401.

**Causa:** chave errada (anon_key vs service_role_key) ou URL incorreta.

**Fix:**
1. Acesse https://app.supabase.com → seu projeto → Settings → API
2. Copie novamente a URL do projeto (deve terminar em `.supabase.co`)
3. Use a `anon` key para leitura publica, `service_role` para escrita com RLS

Atualize o config.json:
```bash
python3 setup/setup_supabase.py
```

---

### CRM mostra tela branca apos login

**Sintoma:** `app.html` abre mas nao carrega dados.

**Causa:** `window.SUPABASE_CONFIG` nao foi injetado (deploy feito sem o setup_crm.py).

**Fix:**
1. Edite `crm/app.js` e adicione no topo:
```javascript
window.SUPABASE_CONFIG = {
  url: "https://SEU-PROJETO.supabase.co",
  anonKey: "SUA-ANON-KEY"
};
```
2. Refaca o deploy: `python3 setup/setup_crm.py`

---

### Heartbeat desatualizado (> 15 min)

**Sintoma:** `watchdog.json` tem timestamp antigo.

**Causa:** LaunchAgent parou ou nao foi carregado.

**Fix:**
```bash
# Rodar manualmente para testar
python3 ~/.operacao-ia/scripts/guardian.py --layer watchdog

# Se funcionar: recarregar LaunchAgent
launchctl unload ~/Library/LaunchAgents/br.zxlab.operacao-ia.guardian.watchdog.plist
launchctl load ~/Library/LaunchAgents/br.zxlab.operacao-ia.guardian.watchdog.plist
```

---

### Contacts.db nao encontrado

**Sintoma:** `/dedup` ou `/status` reporta que contacts.db nao existe.

**Causa:** Etapa 6 foi pulada ou nao criou o banco local.

**Fix:**
```bash
python3 setup/import_contacts.py
```

---

### wrangler nao encontrado (Etapa 7)

**Sintoma:** `setup_crm.py` reporta que wrangler nao esta disponivel.

**Fix:**
```bash
npm install -g wrangler
wrangler --version

# Depois reexecutar
python3 setup/setup_crm.py
```

---

### Mission Control nao abre no browser

**Sintoma:** `mission_control.py --open` nao abre o browser.

**Fix:**
```bash
# Abrir manualmente
open ~/.operacao-ia/mission-control/index.html

# Ou ver o caminho
python3 -c "from pathlib import Path; print(Path.home()/'.operacao-ia/mission-control/index.html')"
```

---

## Comandos uteis de diagnostico

```bash
# Ver config completo (sem expor chaves)
python3 -c "
import json
from pathlib import Path
c = json.loads((Path.home()/'.operacao-ia/config/config.json').read_text())
for k, v in c.items():
    val = str(v)
    if len(val) > 20 and k not in ('student_name','business_name','supabase_url','crm_url'):
        val = val[:8] + '...'
    print(f'{k}: {val}')
"

# Ver checkpoint da Semana 2
cat ~/.operacao-ia/config/week2_checkpoint.json | python3 -m json.tool

# Ver ultimo heartbeat
cat ~/.operacao-ia/logs/heartbeat/watchdog.json | python3 -m json.tool

# Listar LaunchAgents instalados
ls ~/Library/LaunchAgents/ | grep zxlab

# Reexecutar etapa especifica
python3 setup/setup_base.py        # Etapa 0
python3 setup/setup_mission.py     # Etapa 1
python3 setup/setup_rtk.py         # Etapa 2
python3 setup/setup_skills.py      # Etapa 3
python3 setup/setup_guardian.py    # Etapa 4
python3 setup/setup_supabase.py    # Etapa 5
python3 setup/import_contacts.py   # Etapa 6
python3 setup/setup_crm.py         # Etapa 7
python3 setup/setup_final.py       # Etapa 8
```
