#!/usr/bin/env python3
"""
Etapa 4 — Guardiao + Heartbeat
Instala o guardian.py em ~/.operacao-ia/scripts/ e configura 3 LaunchAgents.
"""

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from lib import SCRIPTS_DIR, ensure_structure, mark_checkpoint

GUARDIAN_SRC = ROOT_DIR / "scripts" / "guardian.py"
GUARDIAN_DEST = SCRIPTS_DIR / "guardian.py"
LIB_SRC = ROOT_DIR / "scripts" / "lib.py"
LIB_DEST = SCRIPTS_DIR / "lib.py"

LAUNCHAGENTS_DIR = Path.home() / "Library" / "LaunchAgents"

LAYERS = [
    {
        "label": "br.zxlab.operacao-ia.guardian.watchdog",
        "interval": 300,   # 5 minutos
        "layer": "watchdog",
        "desc": "Watchdog (5min)",
    },
    {
        "label": "br.zxlab.operacao-ia.guardian.heartbeat",
        "interval": 600,   # 10 minutos
        "layer": "heartbeat",
        "desc": "Heartbeat (10min)",
    },
    {
        "label": "br.zxlab.operacao-ia.guardian.last_resort",
        "interval": 1200,  # 20 minutos
        "layer": "last_resort",
        "desc": "Last Resort (20min)",
    },
]


def plist_content(label, interval, layer, python_bin, guardian_path, log_dir):
    log_out = log_dir / f"{layer}.out.log"
    log_err = log_dir / f"{layer}.err.log"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{label}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{python_bin}</string>
    <string>{guardian_path}</string>
    <string>--layer</string>
    <string>{layer}</string>
  </array>
  <key>StartInterval</key>
  <integer>{interval}</integer>
  <key>RunAtLoad</key>
  <false/>
  <key>StandardOutPath</key>
  <string>{log_out}</string>
  <key>StandardErrorPath</key>
  <string>{log_err}</string>
</dict>
</plist>
"""


def install_launchagent(label, interval, layer, python_bin, guardian_path, log_dir):
    plist_path = LAUNCHAGENTS_DIR / f"{label}.plist"
    content = plist_content(label, interval, layer, python_bin, guardian_path, log_dir)
    plist_path.write_text(content, encoding="utf-8")

    # Descarregar se ja existir
    subprocess.run(["launchctl", "unload", str(plist_path)],
                   capture_output=True)
    # Carregar
    result = subprocess.run(["launchctl", "load", str(plist_path)],
                            capture_output=True, text=True)
    if result.returncode == 0:
        return True, f"LaunchAgent {label} carregado"
    return False, f"Erro ao carregar: {result.stderr.strip()}"


def main():
    print()
    print("Etapa 4 — Guardiao + Heartbeat")
    print("[████░░░░░] Etapa 4 de 8")
    print()
    print("  O Guardiao monitora sua operacao automaticamente em 3 camadas:")
    print("  - Watchdog (5min): verifica Evolution API, dispatcher, contatos")
    print("  - Heartbeat (10min): confirma que o watchdog esta rodando")
    print("  - Last Resort (20min): alerta critico se tudo falhar")
    print()

    ensure_structure()
    LAUNCHAGENTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copiar scripts
    print("  Copiando guardian.py para ~/.operacao-ia/scripts/...")
    shutil.copy2(str(GUARDIAN_SRC), str(GUARDIAN_DEST))
    print("  ✅ guardian.py copiado")

    shutil.copy2(str(LIB_SRC), str(LIB_DEST))
    print("  ✅ lib.py copiado")
    print()

    # 2. Detectar Python
    python_bin = sys.executable
    log_dir = Path.home() / ".operacao-ia" / "logs"

    # 3. Instalar LaunchAgents
    print("  Instalando LaunchAgents (requer permissao do macOS)...")
    all_ok = True
    for layer_cfg in LAYERS:
        ok, msg = install_launchagent(
            label=layer_cfg["label"],
            interval=layer_cfg["interval"],
            layer=layer_cfg["layer"],
            python_bin=str(python_bin),
            guardian_path=str(GUARDIAN_DEST),
            log_dir=log_dir,
        )
        marker = "✅" if ok else "⚠️ "
        print(f"  {marker} {layer_cfg['desc']}: {msg}")
        if not ok:
            all_ok = False

    print()

    if all_ok:
        mark_checkpoint("step_4_guardian", "done", "Guardian + 3 LaunchAgents instalados")
        print("  ✅ Guardiao ativo em 3 camadas!")
    else:
        mark_checkpoint("step_4_guardian", "partial", "Instalacao parcial — verificar LaunchAgents")
        print("  ⚠️  Algumas camadas precisam de atencao — verifique os erros acima.")

    print()
    print("  ✅ Etapa 4 concluida!")
    print()
    print("  Proximo passo: Etapa 5 — Supabase")
    print("  Execute: python3 setup/setup_supabase.py")
    print()


if __name__ == "__main__":
    main()
