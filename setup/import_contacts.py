#!/usr/bin/env python3
"""
Etapa 6 — Importar Contatos
Detecta contacts.db da Semana 1, migra para Supabase ou permite importacao manual.
"""

import csv
import io
import json
import re
import sqlite3
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from lib import DATA_DIR, ensure_structure, mark_checkpoint

CONTACTS_DB = DATA_DIR / "contacts.db"
SEM1_DB = Path.home() / ".operacao-ia" / "data" / "contacts.db"


def normalize_phone(phone):
    """Remove tudo que nao for digito."""
    digits = re.sub(r"\D", "", str(phone))
    if len(digits) >= 10:
        return digits
    return None


def load_from_sqlite(db_path):
    """Carrega contatos de um arquivo SQLite (padrao Semana 1)."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT * FROM contacts").fetchall()
        contacts = []
        for row in rows:
            d = dict(row)
            phone = normalize_phone(d.get("phone", ""))
            if phone:
                contacts.append({
                    "name": d.get("name", ""),
                    "phone": phone,
                    "email": d.get("email", ""),
                    "tags": [],
                    "status": d.get("status", "active"),
                    "source": "semana1_migration",
                    "notes": d.get("notes", ""),
                })
        return contacts
    except Exception as exc:
        print(f"  Erro ao ler banco: {exc}")
        return []
    finally:
        conn.close()


def parse_csv_text(text):
    """Tenta parsear texto como CSV com colunas nome,telefone[,email]."""
    contacts = []
    reader = csv.reader(io.StringIO(text.strip()))
    for row in reader:
        if not row:
            continue
        name = row[0].strip() if len(row) > 0 else ""
        phone = normalize_phone(row[1]) if len(row) > 1 else normalize_phone(row[0])
        email = row[2].strip() if len(row) > 2 else ""
        if phone:
            contacts.append({
                "name": name,
                "phone": phone,
                "email": email,
                "tags": [],
                "status": "active",
                "source": "manual_import",
                "notes": "",
            })
    return contacts


def sync_to_supabase(contacts):
    """Envia contatos para Supabase via supabase_sync.py."""
    sync_path = ROOT_DIR / "scripts" / "supabase_sync.py"
    if not sync_path.exists():
        return False, "supabase_sync.py nao encontrado"
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("supabase_sync", sync_path)
        ss = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ss)
        ok, msg, count = ss.upsert_contacts(contacts)
        return ok, f"{msg} ({count} contatos)"
    except Exception as exc:
        return False, str(exc)


def save_local_db(contacts):
    """Salva contatos no SQLite local como backup."""
    ensure_structure()
    conn = sqlite3.connect(str(CONTACTS_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT UNIQUE NOT NULL,
            email TEXT,
            tags TEXT DEFAULT '[]',
            status TEXT DEFAULT 'active',
            source TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    for c in contacts:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO contacts (name, phone, email, tags, status, source, notes) VALUES (?,?,?,?,?,?,?)",
                (c["name"], c["phone"], c["email"], json.dumps(c.get("tags", [])), c["status"], c["source"], c["notes"])
            )
        except Exception:
            pass
    conn.commit()
    inserted = conn.total_changes
    conn.close()
    return inserted


def ask(prompt):
    try:
        return input(f"  {prompt}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)


def ask_yn(prompt, default="s"):
    r = ask(f"{prompt} [s/n, padrao={default}]")
    return (r.lower() if r else default).startswith("s")


def main():
    print()
    print("Etapa 6 — Importar Contatos")
    print("[██████░░░] Etapa 6 de 8")
    print()
    print("  Agora vamos colocar seus contatos no banco de dados na nuvem.")
    print()

    contacts = []
    source_desc = ""

    # 1. Verificar Semana 1
    if SEM1_DB.exists():
        print(f"  Banco da Semana 1 encontrado: {SEM1_DB}")
        if ask_yn("  Quer migrar os contatos da Semana 1 para o Supabase?"):
            contacts = load_from_sqlite(SEM1_DB)
            source_desc = f"Semana 1 ({len(contacts)} contatos)"
            print(f"  ✅ {len(contacts)} contatos carregados do banco da Semana 1")
        print()

    # 2. Importacao manual se nao tem contatos ou quer adicionar mais
    if not contacts:
        print("  Opcoes de importacao:")
        print("  1. Colar lista (um por linha: nome,telefone ou so telefone)")
        print("  2. Informar caminho de arquivo CSV")
        print("  3. Pular esta etapa")
        print()
        escolha = ask("  Escolha [1/2/3]")

        if escolha == "1":
            print()
            print("  Cole seus contatos abaixo (nome,telefone ou so telefone).")
            print("  Quando terminar, pressione Enter duas vezes.")
            lines = []
            while True:
                try:
                    line = input()
                    if line == "" and lines and lines[-1] == "":
                        break
                    lines.append(line)
                except (KeyboardInterrupt, EOFError):
                    break
            text = "\n".join(lines)
            contacts = parse_csv_text(text)
            source_desc = f"cola manual ({len(contacts)} contatos)"

        elif escolha == "2":
            csv_path_str = ask("  Caminho do arquivo CSV")
            csv_path = Path(csv_path_str.strip().replace("~", str(Path.home())))
            if csv_path.exists():
                contacts = parse_csv_text(csv_path.read_text(encoding="utf-8"))
                source_desc = f"{csv_path.name} ({len(contacts)} contatos)"
            else:
                print(f"  ⚠️  Arquivo nao encontrado: {csv_path}")

        else:
            print("  Etapa pulada.")
            mark_checkpoint("step_6_contacts", "skipped", "Importacao pulada pelo aluno")
            print()
            print("  Voce pode importar contatos depois com /dedup")
            print()
            return

    if not contacts:
        print("  Nenhum contato valido encontrado.")
        mark_checkpoint("step_6_contacts", "skipped", "Nenhum contato valido")
        return

    print()
    print(f"  {len(contacts)} contato(s) prontos para sincronizar.")

    # 3. Salvar local
    local_count = save_local_db(contacts)
    print(f"  ✅ {local_count} contatos salvos em backup local (contacts.db)")

    # 4. Sincronizar Supabase
    print("  Sincronizando com Supabase...")
    ok, msg = sync_to_supabase(contacts)
    if ok:
        print(f"  ✅ {msg}")
    else:
        print(f"  ⚠️  Supabase: {msg}")
        print("  Os contatos foram salvos localmente. Tente /dedup depois para sincronizar.")

    mark_checkpoint("step_6_contacts", "done", f"Importados: {source_desc}")

    print()
    print("  ✅ Etapa 6 concluida!")
    print()
    print("  Proximo passo: Etapa 7 — Mini-CRM Cloudflare")
    print("  Execute: python3 setup/setup_crm.py")
    print()


if __name__ == "__main__":
    main()
