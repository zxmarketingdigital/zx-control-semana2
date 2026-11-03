#!/usr/bin/env python3
"""
Etapa 0 — Boas-vindas + Base
Cria ~/.operacao-ia/ e um config.json minimo se nao existirem.
Nao exige nenhum setup anterior: se ja houver uma instalacao, aproveita o que for valido.
Mostra o plano das 8 etapas.

Uso: python3 setup/setup_base.py [--nome "Nome do aluno"] [--negocio "Nome do negocio"]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from lib import ensure_config, save_config  # noqa: E402

BASE_DIR = Path.home() / ".operacao-ia"
CONFIG_PATH = BASE_DIR / "config" / "config.json"
CHECKPOINT_PATH = BASE_DIR / "config" / "week2_checkpoint.json"

SUBDIRS = ["config", "scripts", "data", "logs", "mission-control", "logs/heartbeat"]

ETAPAS = [
    (0, "Boas-vindas + Base",        "Cria a estrutura de pastas e a configuracao base"),
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


def detect_instalacao_anterior():
    """Informativo: devolve (True, nome) se ja existe um config.json com dados de aluno."""
    if not CONFIG_PATH.exists():
        return False, "config.json ainda nao existe"
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if config.get("student_name"):
            return True, config.get("student_name")
        return False, "config.json sem nome do aluno"
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
    parser = argparse.ArgumentParser(description="Etapa 0 — Boas-vindas + Base")
    parser.add_argument("--nome", default="", help="Nome do aluno (opcional)")
    parser.add_argument("--negocio", default="", help="Nome do negocio (opcional)")
    args = parser.parse_args()

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

    # 2. Config base: cria o minimo se nao existir; aproveita o que ja existe
    existed = CONFIG_PATH.exists()
    config = ensure_config()
    changed = False
    if args.nome and not config.get("student_name"):
        config["student_name"] = args.nome.strip()
        changed = True
    if args.negocio and not config.get("business_name"):
        config["business_name"] = args.negocio.strip()
        changed = True
    if changed or not existed:
        save_config(config)
    if existed:
        print("  ✅ config.json pronto — dados existentes preservados")
    else:
        print("  ✅ config.json base criado")

    ja_tem, info = detect_instalacao_anterior()
    if ja_tem:
        print(f"  ✅ Dados do aluno encontrados — {info}")
    else:
        print("  ℹ️  Nome do aluno ainda nao registrado.")
        print("      Pergunte o nome e o negocio ao aluno e rode de novo:")
        print('      python3 setup/setup_base.py --nome "<nome>" --negocio "<negocio>"')
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
    mark_done("step_0_base", "Estrutura e config base criados")

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
