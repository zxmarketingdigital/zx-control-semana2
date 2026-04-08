#!/usr/bin/env python3
"""
Etapa 7 — Mini-CRM Cloudflare Pages
Injeta credenciais Supabase no app.js e faz deploy via wrangler.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from lib import load_config, mark_checkpoint, save_config

CRM_DIR = ROOT_DIR / "crm"


def ask(prompt, default=""):
    try:
        val = input(f"  {prompt}{f' [{default}]' if default else ''}: ").strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)


def generate_config_js(supabase_url, supabase_anon_key, deploy_dir):
    """Gera config.js com as credenciais Supabase."""
    config_js = deploy_dir / "config.js"
    content = f"""// Configuracao Supabase — gerada pelo setup ZX Control Semana 2
window.SUPABASE_CONFIG = {{
  url: "{supabase_url}",
  anonKey: "{supabase_anon_key}"
}};
"""
    config_js.write_text(content, encoding="utf-8")
    return True, "config.js gerado"


def deploy_wrangler(deploy_dir, project_name):
    """Faz deploy via wrangler pages deploy."""
    wrangler = shutil.which("wrangler") or shutil.which("npx")
    if not wrangler:
        return False, "wrangler nao encontrado — instale com: npm install -g wrangler"

    cmd = (
        [wrangler, "pages", "deploy", str(deploy_dir), "--project-name", project_name]
        if "wrangler" in wrangler
        else ["npx", "wrangler", "pages", "deploy", str(deploy_dir), "--project-name", project_name]
    )

    print(f"  Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode == 0:
        # Extrai URL do output
        url_match = re.search(r"https://[a-z0-9\-]+\.pages\.dev", result.stdout + result.stderr)
        url = url_match.group(0) if url_match else "Ver no dashboard Cloudflare"
        return True, url
    return False, result.stderr.strip()[:300]


def main():
    print()
    print("Etapa 7 — Mini-CRM Cloudflare Pages")
    print("[███████░░] Etapa 7 de 8")
    print()
    print("  O Mini-CRM e uma interface web onde voce pode ver, buscar")
    print("  e gerenciar seus contatos — publicada no Cloudflare (gratis).")
    print()

    reconfigure = "--reconfigure" in sys.argv

    try:
        config = load_config()
    except FileNotFoundError:
        config = {}

    supabase_url = config.get("supabase_url", "")
    supabase_anon_key = config.get("supabase_anon_key", "")

    if supabase_url and supabase_anon_key and not reconfigure:
        print("  ✅ Credenciais Supabase encontradas no config — reutilizando")
    else:
        if not supabase_url or not supabase_anon_key:
            print("  ⚠️  Supabase nao configurado. Execute a Etapa 5 primeiro.")
            print("  Se quiser pular esta etapa, pressione Ctrl+C.")
            print()
        supabase_url = ask("SUPABASE_URL", default=supabase_url)
        supabase_anon_key = ask("SUPABASE_ANON_KEY", default=supabase_anon_key)

    # Coletar dados Cloudflare
    print("  Voce vai precisar de:")
    print("  - Account ID: Cloudflare Dashboard → lado direito")
    print("  - API Token: Cloudflare → My Profile → API Tokens → Create Token")
    print("  - Permissao necessaria: Cloudflare Pages (Edit)")
    print()

    cf_account_id = ask("Cole seu CLOUDFLARE_ACCOUNT_ID")
    while not cf_account_id:
        print("  ⚠️  Account ID nao pode ser vazio")
        cf_account_id = ask("CLOUDFLARE_ACCOUNT_ID")

    cf_api_token = ask("Cole seu CLOUDFLARE_API_TOKEN")
    while not cf_api_token or len(cf_api_token) < 10:
        print("  ⚠️  Token invalido")
        cf_api_token = ask("CLOUDFLARE_API_TOKEN")

    # Nome do projeto
    student_name = config.get("student_name", "aluno")
    default_project = re.sub(r"[^a-z0-9\-]", "-", student_name.lower().strip()) + "-crm"
    project_name = ask(f"Nome do projeto no Cloudflare Pages", default=default_project)

    print()
    print(f"  Preparando deploy do CRM como '{project_name}'...")

    # Verificar wrangler antes de rodar
    if not shutil.which("wrangler") and not shutil.which("npx"):
        print("  ❌ wrangler não encontrado. Instale com: npm install -g wrangler")
        print("  Depois rode: wrangler login")
        return

    # Copiar CRM para dir temporario de deploy
    import tempfile
    deploy_ok = False
    with tempfile.TemporaryDirectory() as tmp:
        deploy_dir = Path(tmp) / "crm"
        shutil.copytree(str(CRM_DIR), str(deploy_dir))

        # Gerar config.js com credenciais
        if supabase_url and supabase_anon_key:
            ok, msg = generate_config_js(supabase_url, supabase_anon_key, deploy_dir)
            print(f"  {'✅' if ok else '⚠️ '} {msg}")

        # Deploy
        import os
        env = os.environ.copy()
        env["CLOUDFLARE_ACCOUNT_ID"] = cf_account_id
        env["CLOUDFLARE_API_TOKEN"] = cf_api_token

        print("  Fazendo deploy...")
        wrangler = shutil.which("wrangler") or shutil.which("npx")
        if not wrangler:
            print("  ⚠️  wrangler nao encontrado. Instale com: npm install -g wrangler")
            mark_checkpoint("step_7_crm", "skipped", "wrangler nao disponivel")
            return

        cmd_base = ["wrangler"] if "wrangler" in str(wrangler) else ["npx", "wrangler"]
        cmd = cmd_base + ["pages", "deploy", str(deploy_dir), "--project-name", project_name]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)

        if result.returncode == 0:
            url_match = re.search(r"https://[a-zA-Z0-9\-]+\.pages\.dev", result.stdout + result.stderr)
            crm_url = url_match.group(0) if url_match else f"https://{project_name}.pages.dev"
            print(f"  ✅ CRM publicado!")
            print(f"  URL: {crm_url}")

            # Smoke test: verifica se config.js foi servido corretamente
            import urllib.request
            try:
                with urllib.request.urlopen(f"{crm_url}/config.js", timeout=10) as r:
                    body = r.read().decode()
                    if "SUPABASE_CONFIG" in body:
                        print("  ✅ Smoke test: config.js acessível e correto")
                    else:
                        print("  ⚠️  Smoke test: config.js servido mas sem SUPABASE_CONFIG")
            except Exception as e:
                print(f"  ⚠️  Smoke test: {e} (pode levar alguns minutos para propagar)")

            config["cloudflare_account_id"] = cf_account_id
            config["crm_project_name"] = project_name
            config["crm_url"] = crm_url
            save_config(config)
            mark_checkpoint("step_7_crm", "done", f"CRM: {crm_url}")
            deploy_ok = True
        else:
            print(f"  ❌ Erro no deploy: {result.stderr.strip()[:200]}")
            mark_checkpoint("step_7_crm", "error", "Deploy falhou")

    if deploy_ok:
        print()
        print("  ✅ Etapa 7 concluida!")
        print()
        print("  Proximo passo: Etapa 8 — Finalizacao")
        print("  Execute: python3 setup/setup_final.py")
        print()
    else:
        print()
        print("  ❌ Deploy nao concluido. Verifique o erro acima e tente novamente.")
        print()


if __name__ == "__main__":
    main()
