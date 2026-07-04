#!/usr/bin/env python3
"""
Etapa 2 — RTK + Hooks
Verifica, instala e configura o RTK (token optimizer) para Claude Code.

RTK correto = CLI proxy de economia de tokens, distribuido via Homebrew
(`brew install rtk`, homepage https://www.rtk-ai.app/).
NUNCA usar `cargo install rtk` (crate diferente — "Rust Type Kit").
O hook do Claude Code e instalado pelo proprio RTK via `rtk init`.
"""

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from lib import load_config, mark_checkpoint, save_config

RTK_HOMEPAGE = "https://www.rtk-ai.app/"


def is_rtk_installed():
    return shutil.which("rtk") is not None


def is_real_rtk():
    """Valida empiricamente que o binario `rtk` no PATH e o token optimizer
    (e nao outro pacote homonimo). `rtk gain` imprime a assinatura
    'RTK Token Savings'. Se nao bater, tratamos como RTK errado/ausente."""
    if not is_rtk_installed():
        return False
    try:
        result = subprocess.run(
            ["rtk", "gain"], capture_output=True, text=True, timeout=15
        )
    except Exception:
        return False
    blob = (result.stdout + result.stderr).lower()
    return "token savings" in blob or "rtk" in blob and "savings" in blob


def install_rtk_brew():
    """Instala o RTK via Homebrew (unico caminho correto)."""
    if shutil.which("brew") is None:
        return False, "Homebrew (brew) nao encontrado"
    print("  Instalando RTK via Homebrew (pode demorar alguns minutos)...")
    try:
        result = subprocess.run(
            ["brew", "install", "rtk"],
            capture_output=True, text=True, timeout=600
        )
    except Exception as exc:
        return False, str(exc)
    if result.returncode == 0:
        return True, "instalado via brew"
    return False, (result.stderr or result.stdout)[:200]


def install_hook():
    """Deixa o proprio RTK instalar o hook do Claude Code via `rtk init`.

    `rtk init --global` grava o hook correto em ~/.claude/settings.json
    sozinho — nao montamos o hook na mao (o subcomando `rtk filter` nao
    existe e quebraria todo Bash do Claude Code)."""
    if not is_real_rtk():
        return False, "RTK valido nao detectado — hook nao instalado"
    try:
        result = subprocess.run(
            ["rtk", "init", "--global"],
            capture_output=True, text=True, timeout=60
        )
    except Exception as exc:
        return False, str(exc)
    if result.returncode == 0:
        return True, "Hook instalado via `rtk init` em ~/.claude/settings.json"
    return False, (result.stderr or result.stdout or "rtk init falhou")[:200]


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
    print("[██░░░░░░░] Etapa 2 de 9")
    print()
    print("  O RTK e um otimizador de tokens que reduz em 60-90% o custo")
    print("  das suas sessoes no Claude Code — filtrando saidas de comandos")
    print("  antes de chegarem ao contexto da IA.")
    print()

    # 1. Verificar se ja esta instalado (e se e o RTK correto)
    if is_real_rtk():
        print("  ✅ RTK ja instalado!")
        show_gain()
    else:
        if is_rtk_installed():
            print("  ⚠️  Existe um binario `rtk` no PATH, mas nao e o otimizador")
            print("     de tokens (provavelmente um pacote homonimo).")
            print("     Instale o RTK correto com: brew install rtk")
            print()
        else:
            print("  RTK nao encontrado. Tentando instalar via Homebrew...")
            print()

        ok, detail = install_rtk_brew()
        if ok and is_real_rtk():
            print("  ✅ RTK instalado via Homebrew!")
        else:
            if not ok:
                print(f"  ⚠️  Nao foi possivel instalar automaticamente: {detail}")
            print()
            print("  Para instalar o RTK manualmente:")
            print("    1. Instale o Homebrew (se ainda nao tiver):")
            print('       /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
            print("    2. Instale o RTK:")
            print("       brew install rtk")
            print(f"    Documentacao oficial: {RTK_HOMEPAGE}")
            print("    Depois rode de novo: python3 setup/setup_rtk.py")
            print()
            mark_checkpoint("step_2_rtk", "skipped", "RTK nao instalado — instalacao manual necessaria")
            print("  Etapa pulada — RTK pode ser instalado depois. Seguindo em frente.")
            print()
            return

    # 2. Instalar hook (via rtk init — o proprio RTK grava o hook correto)
    print()
    print("  Configurando hook no Claude Code...")
    ok, msg = install_hook()
    if ok:
        print(f"  ✅ {msg}")
    else:
        print(f"  ⚠️  {msg}")
        print("     Voce pode configurar depois com: rtk init --global")

    mark_checkpoint("step_2_rtk", "done", "RTK instalado + hook configurado")

    print()
    print("  ✅ Etapa 2 concluida!")
    print()
    print("  Proximo passo: Etapa 3 — Skills Profissionais")
    print("  Execute: python3 setup/setup_skills.py")
    print()


if __name__ == "__main__":
    main()
