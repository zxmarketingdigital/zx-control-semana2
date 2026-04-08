#!/usr/bin/env python3
"""
Gera/atualiza ~/.operacao-ia/mission-control/index.html.
Le config.json e week2_checkpoint.json para montar o painel.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib import (
    MISSION_CONTROL_DIR, ensure_structure,
    latest_heartbeat_snapshot, load_checkpoint, load_config, now_iso,
)

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "mission-control" / "index.html"


def status_badge(ok):
    if ok is True:
        return '<span class="badge ok">✅ OK</span>'
    elif ok is False:
        return '<span class="badge err">❌ Pendente</span>'
    return '<span class="badge warn">⏳ Aguardando</span>'


def step_row(number, name, step_key, checkpoint_steps):
    step_data = checkpoint_steps.get(step_key, {})
    status = step_data.get("status", "pending")
    detail = step_data.get("detail", "")
    updated = step_data.get("updated_at", "")
    ok = status == "done"
    badge = status_badge(ok)
    detail_html = f'<small class="detail">{detail}</small>' if detail else ""
    updated_html = f'<small class="ts">{updated}</small>' if updated else ""
    return f"""
        <tr>
          <td class="step-num">{number}</td>
          <td>{name}{detail_html}</td>
          <td>{badge}</td>
          <td>{updated_html}</td>
        </tr>"""


def generate_html(config, checkpoint):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    student_name = config.get("student_name", "Aluno")
    business_name = config.get("business_name", "")
    crm_url = config.get("crm_url", "")
    supabase_url = config.get("supabase_url", "")
    week2_completed = config.get("week2", {}).get("completed", False)

    steps = checkpoint.get("steps", {})
    heartbeat = latest_heartbeat_snapshot()
    watchdog = heartbeat.get("watchdog") or {}
    hb_status = watchdog.get("status", "sem dados")
    hb_updated = watchdog.get("updated_at", "")

    steps_def = [
        (0, "Boas-vindas + Base", "step_0_base"),
        (1, "Mission Control", "step_1_mission"),
        (2, "RTK + Hooks", "step_2_rtk"),
        (3, "Skills Profissionais", "step_3_skills"),
        (4, "Guardiao + Heartbeat", "step_4_guardian"),
        (5, "Supabase", "step_5_supabase"),
        (6, "Importar Contatos", "step_6_contacts"),
        (7, "Mini-CRM Cloudflare", "step_7_crm"),
        (8, "Finalizacao", "step_8_final"),
    ]

    rows_html = "\n".join(step_row(n, name, key, steps) for n, name, key in steps_def)

    crm_link = f'<a href="{crm_url}" target="_blank" class="link-btn">Abrir CRM</a>' if crm_url else '<span class="muted">Nao configurado</span>'
    supabase_link = f'<a href="{supabase_url}" target="_blank" class="link-btn">Abrir Supabase</a>' if supabase_url else '<span class="muted">Nao configurado</span>'
    week2_badge = status_badge(week2_completed)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Mission Control — {student_name}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #0a0a0f;
      color: #e2e8f0;
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      padding: 2rem 1rem;
    }}
    .container {{ max-width: 860px; margin: 0 auto; }}
    header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 2.5rem;
      flex-wrap: wrap;
      gap: 1rem;
    }}
    header h1 {{ font-size: 1.5rem; font-weight: 700; color: #8b5cf6; }}
    header .meta {{ font-size: 0.8rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; }}
    .card {{
      background: #111118;
      border: 1px solid #1e1e2e;
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
    }}
    .card h2 {{ font-size: 1rem; font-weight: 600; color: #8b5cf6; margin-bottom: 1rem; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 0.6rem 0.75rem; text-align: left; font-size: 0.875rem; }}
    th {{ color: #94a3b8; font-weight: 500; border-bottom: 1px solid #1e1e2e; }}
    tr:not(:last-child) td {{ border-bottom: 1px solid #0f0f1a; }}
    .step-num {{ color: #8b5cf6; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; width: 2rem; }}
    .badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 6px; font-size: 0.75rem; font-weight: 500; }}
    .badge.ok {{ background: #052e16; color: #4ade80; }}
    .badge.err {{ background: #2d1515; color: #f87171; }}
    .badge.warn {{ background: #1c1a05; color: #facc15; }}
    .detail {{ display: block; color: #64748b; margin-top: 0.15rem; }}
    .ts {{ color: #475569; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; }}
    .muted {{ color: #475569; font-size: 0.8rem; }}
    .link-btn {{
      display: inline-block;
      background: #8b5cf6;
      color: #fff;
      text-decoration: none;
      padding: 0.3rem 0.8rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 500;
    }}
    .link-btn:hover {{ background: #7c3aed; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
    .stat {{ padding: 0.75rem; background: #0d0d16; border-radius: 8px; }}
    .stat-label {{ font-size: 0.75rem; color: #64748b; margin-bottom: 0.25rem; }}
    .stat-value {{ font-size: 0.95rem; font-weight: 600; color: #e2e8f0; }}
    footer {{ margin-top: 3rem; text-align: center; color: #475569; font-size: 0.75rem; }}
    @media (max-width: 600px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>Mission Control</h1>
        <div class="meta">{student_name} &nbsp;·&nbsp; {business_name}</div>
      </div>
      <div class="meta">Atualizado: {now}</div>
    </header>

    <div class="card">
      <h2>Status da Semana 2</h2>
      <div class="grid" style="margin-bottom:1.25rem">
        <div class="stat">
          <div class="stat-label">Semana 2 completa</div>
          <div class="stat-value">{week2_badge}</div>
        </div>
        <div class="stat">
          <div class="stat-label">Guardian (watchdog)</div>
          <div class="stat-value">
            <span class="badge {'ok' if hb_status == 'ok' else 'err'}">{hb_status}</span>
            <small class="ts" style="display:block;margin-top:0.2rem">{hb_updated}</small>
          </div>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Modulo</th>
            <th>Status</th>
            <th>Atualizado</th>
          </tr>
        </thead>
        <tbody>
{rows_html}
        </tbody>
      </table>
    </div>

    <div class="card">
      <h2>Links Rapidos</h2>
      <div class="grid">
        <div class="stat">
          <div class="stat-label">Mini-CRM</div>
          <div class="stat-value" style="margin-top:0.4rem">{crm_link}</div>
        </div>
        <div class="stat">
          <div class="stat-label">Supabase Dashboard</div>
          <div class="stat-value" style="margin-top:0.4rem">{supabase_link}</div>
        </div>
      </div>
    </div>

    <footer>ZX LAB &nbsp;·&nbsp; <a href="https://zxlab.com.br" style="color:#8b5cf6">zxlab.com.br</a></footer>
  </div>
</body>
</html>"""


def update_mission_control(open_browser=False):
    ensure_structure()
    try:
        config = load_config()
    except FileNotFoundError:
        config = {}
    checkpoint = load_checkpoint()
    html = generate_html(config, checkpoint)
    out_path = MISSION_CONTROL_DIR / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  Mission Control atualizado: {out_path}")

    if open_browser:
        import subprocess
        subprocess.run(["open", str(out_path)], check=False)

    return out_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Atualiza Mission Control")
    parser.add_argument("--open", action="store_true", help="Abre no browser apos gerar")
    args = parser.parse_args()
    update_mission_control(open_browser=args.open)
