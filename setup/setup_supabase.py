#!/usr/bin/env python3
"""
Etapa 5 — Supabase
Coleta credenciais, valida conexao e orienta criacao de tabelas.
"""

import getpass
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from lib import CONFIG_PATH, load_config, mark_checkpoint, save_config


def ask(prompt, secret=False):
    try:
        if secret:
            value = getpass.getpass(f"  {prompt}: ").strip()
        else:
            value = input(f"  {prompt}: ").strip()
        return value
    except (KeyboardInterrupt, EOFError):
        print()
        print("  Setup cancelado.")
        sys.exit(0)


def validate_connection(url, key):
    """Testa conexao com a API REST do Supabase."""
    endpoint = f"{url.rstrip('/')}/rest/v1/"
    req = urllib.request.Request(
        endpoint,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 204), f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        # 404 em /rest/v1/ e normal para projetos sem tabelas ainda
        if exc.code == 404:
            return True, "Conexao OK (projeto sem tabelas ainda)"
        return False, f"HTTP {exc.code}: {exc.reason}"
    except Exception as exc:
        return False, str(exc)


def show_sql_instructions():
    sql_path = ROOT_DIR / "sql" / "001_init.sql"
    print()
    print("  Para criar as tabelas no Supabase:")
    print("  1. Acesse: https://app.supabase.com → seu projeto → SQL Editor")
    print("  2. Cole e execute o conteudo de sql/001_init.sql")
    print()
    if sql_path.exists():
        print(f"  Arquivo: {sql_path}")
        print()
        print("  Conteudo do SQL:")
        print("  " + "-" * 50)
        for line in sql_path.read_text(encoding="utf-8").split("\n")[:20]:
            print(f"  {line}")
        print("  ...")
        print("  " + "-" * 50)


def main():
    print()
    print("Etapa 5 — Supabase")
    print("[█████░░░░] Etapa 5 de 8")
    print()
    print("  O Supabase e um banco de dados na nuvem onde seus contatos")
    print("  e registros de disparos ficam guardados — acessiveis de")
    print("  qualquer lugar e com backup automatico.")
    print()
    print("  Voce vai precisar das credenciais do seu projeto Supabase.")
    print("  Acesse: https://app.supabase.com → Settings → API")
    print()

    # Carrega config existente
    try:
        config = load_config()
    except FileNotFoundError:
        config = {}

    # Coleta credenciais
    supabase_url = ask("Cole sua SUPABASE_URL (ex: https://xxx.supabase.co)")
    while not supabase_url or not supabase_url.startswith("https://"):
        print("  ⚠️  URL invalida. Deve comecar com https://")
        supabase_url = ask("SUPABASE_URL")

    anon_key = ask("Cole sua SUPABASE_ANON_KEY (chave publica)", secret=True)
    while not anon_key or len(anon_key) < 20:
        print("  ⚠️  Chave invalida. Verifique em Settings → API → anon key")
        anon_key = ask("SUPABASE_ANON_KEY", secret=True)

    service_key = ask("Cole sua SUPABASE_SERVICE_ROLE_KEY (chave privada — nao compartilhe)", secret=True)
    while not service_key or len(service_key) < 20:
        print("  ⚠️  Chave invalida.")
        service_key = ask("SUPABASE_SERVICE_ROLE_KEY", secret=True)

    print()
    print("  Validando conexao...")
    ok, msg = validate_connection(supabase_url, anon_key)
    if ok:
        print(f"  ✅ Conexao validada: {msg}")
    else:
        print(f"  ❌ Erro de conexao: {msg}")
        print("  Verifique a URL e a chave e tente novamente.")
        sys.exit(1)

    # Salvar no config
    config["supabase_url"] = supabase_url
    config["supabase_anon_key"] = anon_key
    config["supabase_service_role_key"] = service_key
    save_config(config)
    print("  ✅ Credenciais salvas em ~/.operacao-ia/config/config.json")

    # Instrucoes SQL
    show_sql_instructions()

    mark_checkpoint("step_5_supabase", "done", f"Supabase configurado: {supabase_url}")

    print()
    print("  ✅ Etapa 5 concluida!")
    print()
    print("  Proximo passo: Etapa 6 — Importar Contatos")
    print("  Execute: python3 setup/import_contacts.py")
    print()


if __name__ == "__main__":
    main()
