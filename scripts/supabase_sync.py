#!/usr/bin/env python3
"""
Cliente Supabase para contacts e dispatches — ZX Control Semana 2.
Usa apenas urllib (sem dependencias externas).
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib import load_config


# ---------------------------------------------------------------------------
# Helpers HTTP
# ---------------------------------------------------------------------------

def _headers(api_key, use_service_role=False):
    return {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _request(method, url, api_key, data=None):
    payload = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        url,
        data=payload,
        headers=_headers(api_key),
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body.strip() else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        return exc.code, body
    except Exception as exc:
        return 0, str(exc)


# ---------------------------------------------------------------------------
# Configuracao
# ---------------------------------------------------------------------------

def get_supabase_config():
    """Le credenciais do config.json."""
    config = load_config()
    url = config.get("supabase_url", "").rstrip("/")
    anon_key = config.get("supabase_anon_key", "")
    service_key = config.get("supabase_service_role_key", "")
    if not url or not anon_key:
        raise ValueError("supabase_url e supabase_anon_key sao obrigatorios no config.json")
    return url, anon_key, service_key


# ---------------------------------------------------------------------------
# Criar tabelas
# ---------------------------------------------------------------------------

def create_tables(supabase_url, service_role_key):
    """
    Instrui o aluno a rodar o SQL via dashboard Supabase.
    Valida conexao com uma query simples.
    """
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "001_init.sql"
    if sql_path.exists():
        sql = sql_path.read_text(encoding="utf-8")
    else:
        sql = "-- sql/001_init.sql nao encontrado"

    print()
    print("  Para criar as tabelas, acesse o Supabase Dashboard:")
    print("  1. Va em https://app.supabase.com → seu projeto → SQL Editor")
    print("  2. Cole e execute o conteudo de sql/001_init.sql")
    print()
    print("  (O arquivo esta em: sql/001_init.sql)")
    print()

    # Valida conexao
    status, result = _request("GET", f"{supabase_url}/rest/v1/contacts?select=id&limit=1", service_role_key)
    if status in (200, 206):
        return True, "Conexao validada — tabela contacts encontrada"
    elif status == 404:
        return False, "Tabela contacts nao encontrada — execute o SQL no dashboard primeiro"
    else:
        return False, f"Erro de conexao: HTTP {status} — {result}"


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def upsert_contacts(contacts_list):
    """
    Insere ou atualiza uma lista de contatos no Supabase.
    contacts_list: lista de dicts com chaves name, phone, email, tags, status, source, notes
    Retorna (ok, mensagem, count).
    """
    url, anon_key, service_key = get_supabase_config()
    key = service_key or anon_key
    endpoint = f"{url}/rest/v1/contacts"

    # Supabase upsert via header
    req_data = contacts_list
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(req_data).encode("utf-8"),
        headers={
            **_headers(key),
            "Prefer": "resolution=merge-duplicates,return=representation",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            inserted = json.loads(body) if body.strip() else []
            return True, f"{len(inserted)} contato(s) sincronizados", len(inserted)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        return False, f"Erro HTTP {exc.code}: {body}", 0
    except Exception as exc:
        return False, str(exc), 0


def get_contacts(limit=100, offset=0):
    """Retorna lista de contatos do Supabase."""
    url, anon_key, service_key = get_supabase_config()
    key = service_key or anon_key
    endpoint = f"{url}/rest/v1/contacts?select=*&order=created_at.desc&limit={limit}&offset={offset}"
    status, result = _request("GET", endpoint, key)
    if status == 200:
        return True, result
    return False, f"Erro HTTP {status}: {result}"


# ---------------------------------------------------------------------------
# Dispatches
# ---------------------------------------------------------------------------

def upsert_dispatch(record):
    """
    Insere um registro de disparo.
    record: dict com contact_phone, message, provider, status, sent_at, error_message
    """
    url, anon_key, service_key = get_supabase_config()
    key = service_key or anon_key
    endpoint = f"{url}/rest/v1/dispatches"
    status, result = _request("POST", endpoint, key, data=record)
    if status in (200, 201):
        return True, "Disparo registrado"
    return False, f"Erro HTTP {status}: {result}"


# ---------------------------------------------------------------------------
# Entrypoint de teste
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Testando conexao com Supabase...")
    try:
        url, anon_key, service_key = get_supabase_config()
        key = service_key or anon_key
        status, result = _request("GET", f"{url}/rest/v1/contacts?select=id&limit=1", key)
        if status == 200:
            print(f"  Conexao OK — {len(result)} registro(s) retornado(s)")
        else:
            print(f"  Erro: HTTP {status} — {result}")
    except Exception as exc:
        print(f"  Erro: {exc}")
