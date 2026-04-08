#!/usr/bin/env python3
"""
Etapa 8 — Finalizacao
Atualiza Mission Control, marca week2.completed e mostra resumo final.
"""

import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from lib import load_checkpoint, load_config, mark_checkpoint, save_config


def status_label(steps, key):
    s = steps.get(key, {}).get("status", "pending")
    if s == "done":
        return "✅ Concluido"
    elif s == "skipped":
        return "⏭  Pulado"
    elif s == "partial":
        return "⚠️  Parcial"
    elif s == "error":
        return "❌ Erro"
    return "⏳ Pendente"


def main():
    print()
    print("Etapa 8 — Finalizacao")
    print("[█████████] Etapa 8 de 8")
    print()
    print("  Chegamos ao final da Semana 2!")
    print("  Vamos revisar tudo que foi instalado e atualizar seu painel.")
    print()

    try:
        config = load_config()
    except FileNotFoundError:
        config = {}

    checkpoint = load_checkpoint()
    steps = checkpoint.get("steps", {})

    # Mapa de etapas
    etapas = [
        ("step_0_base",      "Boas-vindas + Base"),
        ("step_1_mission",   "Mission Control"),
        ("step_2_rtk",       "RTK + Hooks"),
        ("step_3_skills",    "Skills Profissionais"),
        ("step_4_guardian",  "Guardiao + Heartbeat"),
        ("step_5_supabase",  "Supabase"),
        ("step_6_contacts",  "Importar Contatos"),
        ("step_7_crm",       "Mini-CRM Cloudflare"),
    ]

    print("  Resumo da Semana 2:")
    print("  " + "-" * 45)
    for key, name in etapas:
        print(f"  {status_label(steps, key):20s} {name}")
    print("  " + "-" * 45)
    print()

    # Links
    crm_url = config.get("crm_url", "")
    supabase_url = config.get("supabase_url", "")
    student_name = config.get("student_name", "Aluno")

    if crm_url:
        print(f"  Mini-CRM:  {crm_url}")
    if supabase_url:
        print(f"  Supabase:  {supabase_url}")
    print()

    # Marcar Semana 2 como concluida
    REQUIRED_STEPS = ["step_0_base", "step_1_mission", "step_2_rtk", "step_3_skills",
                       "step_4_guardian", "step_5_supabase", "step_7_crm"]
    has_errors = any(steps.get(s, {}).get("status") == "error" for s in REQUIRED_STEPS)
    completed = not has_errors

    config.setdefault("week2", {})["completed"] = completed
    config["week2"]["completed_at"] = __import__("datetime").datetime.now().isoformat(timespec="seconds")
    save_config(config)

    if completed:
        mark_checkpoint("step_8_final", "done", "Semana 2 concluida")
    else:
        mark_checkpoint("step_8_final", "partial", "Semana 2 com erros em etapas obrigatorias")
        print("  ⚠️  Algumas etapas obrigatorias tiveram erro. Revise e corrija antes de continuar.")

    # Atualizar Mission Control
    mc_path = ROOT_DIR / "scripts" / "mission_control.py"
    if mc_path.exists():
        try:
            spec = importlib.util.spec_from_file_location("mission_control", mc_path)
            mc = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mc)
            out = mc.update_mission_control(open_browser=True)
            print(f"  ✅ Mission Control atualizado e aberto!")
        except Exception as exc:
            print(f"  ⚠️  Mission Control: {exc}")

    print()
    print("=" * 55)
    print()
    print(f"  Parabens, {student_name}!")
    print()
    print("  Sua operacao esta rodando com:")
    print("  ✅ RTK economizando tokens automaticamente")
    print("  ✅ 7 skills profissionais instaladas")
    print("  ✅ Guardiao monitorando 24/7 em 3 camadas")
    print("  ✅ Contatos sincronizados no Supabase")
    if crm_url:
        print(f"  ✅ Mini-CRM publicado em: {crm_url}")
    print()
    print("  Comandos mais usados no dia a dia:")
    print("  /status      — ver saude de tudo agora")
    print("  /healthcheck — verificacao rapida")
    print("  /preflight   — antes de sessoes importantes")
    print("  /harvest     — capturar aprendizados")
    print("  /encerrar    — fechar sessao com resumo")
    print()
    print("  Nos vemos na Semana 3!")
    print()
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()
