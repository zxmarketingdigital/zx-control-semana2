#!/usr/bin/env python3
"""
Etapa 3 — Skills Profissionais
Copia as 7 skills de skills/ para ~/.claude/skills/.
"""

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from lib import mark_checkpoint

SKILLS_SRC = ROOT_DIR / "skills"
SKILLS_DEST = Path.home() / ".claude" / "skills"

SKILLS = [
    ("status",      "/status",      "Health check completo de todos os servicos"),
    ("healthcheck", "/healthcheck", "Verificacao rapida de saude do ambiente"),
    ("fix",         "/fix",         "Diagnostico e correcao autonoma de problemas"),
    ("dedup",       "/dedup",       "Deduplicacao de contatos na base"),
    ("preflight",   "/preflight",   "Verifica ambiente antes de sessoes criticas"),
    ("harvest",     "/harvest",     "Captura aprendizados e salva no log da sessao"),
    ("encerrar",    "/encerrar",    "Fechamento completo da sessao"),
]


def install_skill(skill_name):
    src = SKILLS_SRC / skill_name / "SKILL.md"
    dest_dir = SKILLS_DEST / skill_name
    dest = dest_dir / "SKILL.md"

    if not src.exists():
        return False, f"SKILL.md nao encontrado em skills/{skill_name}/"

    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src), str(dest))
    return True, str(dest).replace(str(Path.home()), "~")


def main():
    print()
    print("Etapa 3 — Skills Profissionais")
    print("[███░░░░░░] Etapa 3 de 8")
    print()
    print("  Skills sao comandos que o Claude executa automaticamente —")
    print("  sem voce precisar explicar o que fazer.")
    print()
    print("  Instalando 7 skills em ~/.claude/skills/...")
    print()

    SKILLS_DEST.mkdir(parents=True, exist_ok=True)

    installed = []
    failed = []

    for skill_name, cmd, desc in SKILLS:
        ok, detail = install_skill(skill_name)
        if ok:
            print(f"  ✅ {cmd:15s} — {desc}")
            installed.append(cmd)
        else:
            print(f"  ❌ {cmd:15s} — ERRO: {detail}")
            failed.append(cmd)

    print()
    if installed:
        print(f"  {len(installed)} skill(s) instalada(s) com sucesso.")
    if failed:
        print(f"  {len(failed)} skill(s) com falha: {', '.join(failed)}")

    if failed:
        mark_checkpoint("step_3_skills", "partial", f"Instaladas: {len(installed)}/7")
    else:
        mark_checkpoint("step_3_skills", "done", f"7 skills instaladas em ~/.claude/skills/")

    print()
    print("  ✅ Etapa 3 concluida!")
    print()
    print("  Agora voce pode usar:")
    for _, cmd, _ in SKILLS:
        print(f"    {cmd}")
    print()
    print("  Proximo passo: Etapa 4 — Guardiao + Heartbeat")
    print("  Execute: python3 setup/setup_guardian.py")
    print()


if __name__ == "__main__":
    main()
