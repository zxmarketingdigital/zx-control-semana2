#!/usr/bin/env python3
"""
Etapa 1 — Mission Control
Gera ~/.operacao-ia/mission-control/index.html e abre no browser.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from lib import mark_checkpoint, MISSION_CONTROL_DIR


def load_mission_control():
    mc_path = ROOT_DIR / "scripts" / "mission_control.py"
    spec = importlib.util.spec_from_file_location("mission_control", mc_path)
    mc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mc)
    return mc


def main():
    print()
    print("Etapa 1 — Mission Control")
    print("[█░░░░░░░░] Etapa 1 de 8")
    print()
    print("  O Mission Control e um painel visual que mostra o status")
    print("  de toda a sua operacao — em tempo real, no browser.")
    print()
    print("  Gerando painel em ~/.operacao-ia/mission-control/...")

    try:
        mc = load_mission_control()
        out_path = mc.update_mission_control(open_browser=False)
        print(f"  ✅ Painel gerado: {out_path}")
    except Exception as exc:
        # Fallback: copiar template
        template = ROOT_DIR / "templates" / "mission-control" / "index.html"
        dest = MISSION_CONTROL_DIR / "index.html"
        MISSION_CONTROL_DIR.mkdir(parents=True, exist_ok=True)
        if template.exists():
            dest.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  ✅ Template copiado: {dest}")
        else:
            print(f"  ⚠️  Nao foi possivel gerar o painel: {exc}")

    # Abre no browser
    html_path = MISSION_CONTROL_DIR / "index.html"
    if html_path.exists():
        try:
            subprocess.run(["open", str(html_path)], check=False)
            print("  ✅ Abrindo no browser...")
        except Exception:
            print(f"  Abra manualmente: {html_path}")

        mark_checkpoint("step_1_mission", "done", "Mission Control gerado e aberto")

        print()
        print("  ✅ Etapa 1 concluida!")
        print()
        print("  Proximo passo: Etapa 2 — RTK + Hooks")
        print("  Execute: python3 setup/setup_rtk.py")
        print()
    else:
        mark_checkpoint("step_1_mission", "error", "Falha ao gerar Mission Control")
        print("  ❌ Nao foi possivel gerar o Mission Control.")
        print("  Tente rodar novamente: python3 setup/setup_mission.py")


if __name__ == "__main__":
    main()
