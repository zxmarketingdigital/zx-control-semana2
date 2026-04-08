#!/usr/bin/env python3
"""
Etapa 2 — RTK + Hooks
Verifica, instala e configura o RTK (token optimizer) para Claude Code.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from lib import load_config, mark_checkpoint, save_config

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
RTK_HOOK_CMD = "rtk"


def is_rtk_installed():
    return shutil.which("rtk") is not None


def install_rtk_cargo():
    """Tenta instalar via cargo."""
    print("  Instalando RTK via cargo (pode demorar alguns minutos)...")
    result = subprocess.run(
        ["cargo", "install", "rtk"],
        capture_output=True, text=True, timeout=300
    )
    return result.returncode == 0, result.stderr


def install_rtk_binary():
    """Tenta baixar binario pre-compilado do GitHub releases."""
    import platform
    import urllib.request

    system = platform.system().lower()
    arch = platform.machine().lower()

    # Mapeia para nomes de release
    if system == "darwin":
        target = "aarch64-apple-darwin" if "arm" in arch or "aarch" in arch else "x86_64-apple-darwin"
    elif system == "linux":
        target = "x86_64-unknown-linux-musl"
    else:
        return False, f"Sistema {system} nao suportado para download automatico"

    url = f"https://github.com/rcastrodigital/rtk/releases/latest/download/rtk-{target}"
    dest = Path.home() / ".local" / "bin" / "rtk"
    dest.parent.mkdir(parents=True, exist_ok=True)

    print(f"  Baixando binario RTK para {target}...")
    try:
        urllib.request.urlretrieve(url, str(dest))
        dest.chmod(0o755)
        return True, str(dest)
    except Exception as exc:
        return False, str(exc)


def install_hook():
    """Instala o hook RTK no settings.json do Claude Code."""
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    if SETTINGS_PATH.exists():
        try:
            settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            settings = {}
    else:
        settings = {}

    hooks = settings.setdefault("hooks", {})
    pre_tool = hooks.setdefault("PreToolUse", [])

    # Verifica se hook ja existe
    for hook in pre_tool:
        if isinstance(hook, dict) and "rtk" in str(hook.get("command", "")):
            return True, "Hook RTK ja instalado"

    pre_tool.append({
        "matcher": "Bash",
        "hooks": [{
            "type": "command",
            "command": "rtk filter"
        }]
    })

    SETTINGS_PATH.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
    return True, "Hook instalado em ~/.claude/settings.json"


def show_gain():
    """Mostra rtk gain se disponivel."""
    if not is_rtk_installed():
        return
    try:
        result = subprocess.run(["rtk", "gain"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            print()
            print("  RTK Savings:")
            for line in result.stdout.strip().split("\n"):
                print(f"    {line}")
    except Exception:
        pass


def main():
    print()
    print("Etapa 2 — RTK + Hooks")
    print("[██░░░░░░░] Etapa 2 de 8")
    print()
    print("  O RTK e um otimizador de tokens que reduz em 60-90% o custo")
    print("  das suas sessoes no Claude Code — filtrando saidas de comandos")
    print("  antes de chegarem ao contexto da IA.")
    print()

    # 1. Verificar se ja esta instalado
    if is_rtk_installed():
        print("  ✅ RTK ja instalado!")
        show_gain()
    else:
        print("  RTK nao encontrado. Tentando instalar...")
        print()

        # Tenta cargo primeiro
        cargo_ok = shutil.which("cargo") is not None
        installed = False

        if cargo_ok:
            ok, detail = install_rtk_cargo()
            if ok:
                print("  ✅ RTK instalado via cargo!")
                installed = True
            else:
                print(f"  ⚠️  cargo falhou: {detail[:100]}")

        if not installed:
            ok, detail = install_rtk_binary()
            if ok:
                print(f"  ✅ RTK instalado em {detail}")
                installed = True
            else:
                print(f"  ⚠️  Download falhou: {detail}")
                print()
                print("  Instale manualmente: https://github.com/rcastrodigital/rtk")
                print("  Depois rode: python3 setup/setup_rtk.py")

        if not installed:
            mark_checkpoint("step_2_rtk", "skipped", "RTK nao instalado — instalacao manual necessaria")
            print()
            print("  Etapa pulada — RTK pode ser instalado depois.")
            print()
            return

    # 2. Instalar hook
    print()
    print("  Configurando hook no Claude Code...")
    ok, msg = install_hook()
    if ok:
        print(f"  ✅ {msg}")
    else:
        print(f"  ⚠️  {msg}")

    mark_checkpoint("step_2_rtk", "done", "RTK instalado + hook configurado")

    print()
    print("  ✅ Etapa 2 concluida!")
    print()
    print("  Proximo passo: Etapa 3 — Skills Profissionais")
    print("  Execute: python3 setup/setup_skills.py")
    print()


if __name__ == "__main__":
    main()
