#!/usr/bin/env python3
"""
Etapa 0 — Boas-vindas + Base
Cria ~/.operacao-ia/ minimo se nao existir.
Detecta se a Semana 1 foi concluida.
Mostra o plano das 8 etapas.
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path.home() / ".operacao-ia"
CONFIG_PATH = BASE_DIR / "config" / "config.json"
CHECKPOINT_PATH = BASE_DIR / "config" / "week2_checkpoint.json"

SUBDIRS = ["config", "scripts", "data", "logs", "mission-control", "logs/heartbeat"]

ETAPAS = [
    (0, "Boas-vindas + Base",        "Cria a estrutura de pastas e verifica a Semana 1"),
    (1, "Mission Control",           "Painel visual da sua operacao no browser"),
    (2, "RTK + Hooks",               "60-90% menos tokens no Claude Code"),
    (3, "Skills Profissionais",      "7 comandos /skill para o dia a dia"),
    (4, "Guardiao + Heartbeat",      "Monitoramento automatico em 3 camadas"),
    (5, "Supabase",                  "Banco de dados na nuvem para seus contatos"),
    (6, "Importar Contatos",         "Migra ou importa sua lista de contatos"),
    (7, "Mini-CRM Cloudflare",       "Interface web para gerenciar contatos"),
    (8, "Finalizacao",               "Resumo completo e Mission Control atualizado"),
]


def ensure_base_structure():
    created = []
    for subdir in SUBDIRS:
        path = BASE_DIR / subdir
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(str(path).replace(str(Path.home()), "~"))
    return created


def detect_semana1():
    if not CONFIG_PATH.exists():
        return False, "config.json nao encontrado"
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if config.get("phase_completed", 0) >= 1:
            return True, config.get("student_name", "Aluno")
        return False, "phase_completed < 1 no config.json"
    except Exception as exc:
        return False, str(exc)


def load_checkpoint():
    if not CHECKPOINT_PATH.exists():
        return {"steps": {}}
    try:
        return json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"steps": {}}


def save_checkpoint(checkpoint):
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    checkpoint["updated_at"] = datetime.now().isoformat(timespec="seconds")
    CHECKPOINT_PATH.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")


def mark_done(step_key, detail=""):
    from datetime import datetime
    cp = load_checkpoint()
    cp.setdefault("steps", {})[step_key] = {
        "status": "done",
        "detail": detail,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    save_checkpoint(cp)


def main():
    print()
    print("ZX Control Semana 2 — Setup Operacao Profissional")
    print("=" * 55)
    print()

    # 1. Estrutura base
    print("  Verificando estrutura de pastas...")
    created = ensure_base_structure()
    if created:
        for p in created:
            print(f"  ✅ Criada: {p}")
    else:
        print("  ✅ Estrutura ~/.operacao-ia/ ja existe")
    print()

    # 2. Detectar Semana 1
    sem1_ok, sem1_info = detect_semana1()
    if sem1_ok:
        print(f"  ✅ Semana 1 detectada — aluno: {sem1_info}")
    else:
        print(f"  ⚠️  Semana 1 nao detectada ({sem1_info})")
        print()
        print("  Voce pode continuar mesmo assim — algumas etapas serao")
        print("  adaptadas para o seu caso.")
    print()

    # 3. Mostrar plano
    print("  Plano da Semana 2 — 8 etapas:")
    print()
    cp = load_checkpoint()
    steps_done = cp.get("steps", {})

    for n, nome, desc in ETAPAS:
        key = f"step_{n}_{'base' if n == 0 else ['mission','rtk','skills','guardian','supabase','contacts','crm','final'][n-1]}"
        done = steps_done.get(key, {}).get("status") == "done"
        marker = "✅" if done else "  "
        print(f"  {marker} Etapa {n}: {nome}")
        print(f"        → {desc}")
    print()
    print("=" * 55)

    # 4. Marcar etapa 0 como concluida
    mark_done("step_0_base", "Estrutura criada e Semana 1 verificada")

    # Atualizar mission control
    try:
        import importlib.util
        mc_path = Path(__file__).resolve().parent.parent / "scripts" / "mission_control.py"
        spec = importlib.util.spec_from_file_location("mission_control", mc_path)
        mc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mc)
        mc.update_mission_control()
    except Exception:
        pass

    print()
    print("  ✅ Etapa 0 concluida!")
    print()
    print("  Proximo passo: Etapa 1 — Mission Control")
    print("  Execute: python3 setup/setup_mission.py")
    print()


if __name__ == "__main__":
    main()
