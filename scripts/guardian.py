#!/usr/bin/env python3
"""
Guardiao + Heartbeat em 3 camadas — ZX Control Semana 2.
Verifica: Evolution API, dispatcher, LaunchAgent monitor, contacts.db.
Camadas: watchdog (5min), heartbeat (10min), last_resort (20min).
"""

import argparse
import json
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib import (
    BASE_DIR, DATA_DIR, HEARTBEAT_DIR, SCRIPTS_DIR,
    ensure_structure, latest_heartbeat_snapshot,
    load_config, mark_checkpoint, now_iso,
)


# ---------------------------------------------------------------------------
# Config helper — suporta chaves aninhadas e planas
# ---------------------------------------------------------------------------

def _cfg(config, *keys, default=""):
    """Lê config com suporte a chaves aninhadas (ex: 'evolution', 'base_url').
    Tenta o caminho aninhado primeiro; se vazio, tenta a chave plana legada."""
    nested_defaults = {
        ("evolution", "base_url"): ("evolution_api_url", "http://localhost:8080"),
        ("evolution", "api_key"): ("evolution_api_key", ""),
        ("evolution", "instance"): ("evolution_instance", ""),
        ("zapi", "instance_id"): ("zapi_instance_id", ""),
        ("zapi", "token"): ("zapi_token", ""),
    }
    # Tenta caminho aninhado
    value = config
    for key in keys:
        if not isinstance(value, dict):
            value = None
            break
        value = value.get(key)
    if value:
        return value
    # Fallback para chave plana legada
    flat_key, flat_default = nested_defaults.get(tuple(keys), (None, default))
    if flat_key is not None:
        return config.get(flat_key, flat_default)
    return default


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_evolution_api(config):
    """Verifica se a Evolution API esta respondendo."""
    base_url = _cfg(config, "evolution", "base_url", default="http://localhost:8080")
    try:
        req = urllib.request.Request(f"{base_url}/instance/fetchInstances",
                                     headers={"apikey": _cfg(config, "evolution", "api_key")})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200, "Evolution API respondendo"
    except Exception as exc:
        return False, f"Evolution API indisponivel: {exc}"


def check_dispatcher(config):
    """Verifica se o dispatcher.py existe."""
    dispatcher = SCRIPTS_DIR / "dispatcher.py"
    if dispatcher.exists():
        return True, "dispatcher.py encontrado"
    return False, "dispatcher.py nao encontrado em ~/.operacao-ia/scripts/"


def check_monitor_launchagent():
    """Verifica se o LaunchAgent do monitor esta carregado."""
    label = "br.zxlab.operacao-ia.monitor"
    try:
        result = subprocess.run(
            ["launchctl", "list", label],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return True, f"LaunchAgent {label} ativo"
        return False, f"LaunchAgent {label} nao encontrado"
    except Exception as exc:
        return False, f"Erro ao verificar LaunchAgent: {exc}"


def check_contacts_db():
    """Verifica se o banco de contatos existe."""
    contacts_db = DATA_DIR / "contacts.db"
    if contacts_db.exists():
        return True, "contacts.db encontrado"
    return False, "contacts.db nao encontrado — Etapa 6 pendente"


def run_all_checks(config):
    checks = []
    for label, fn, args in [
        ("Evolution API", check_evolution_api, (config,)),
        ("Dispatcher", check_dispatcher, (config,)),
        ("Monitor LaunchAgent", check_monitor_launchagent, ()),
        ("Contacts DB", check_contacts_db, ()),
    ]:
        try:
            ok, detail = fn(*args)
        except Exception as exc:
            ok, detail = False, str(exc)
        checks.append({"service": label, "ok": ok, "detail": detail})
    return checks


# ---------------------------------------------------------------------------
# Alertas via WhatsApp (urllib, sem deps externas)
# ---------------------------------------------------------------------------

def send_alert(config, title, lines):
    """Envia alerta WhatsApp via Evolution API ou Z-API."""
    student_phone = config.get("student_phone", "")
    if not student_phone:
        print("  [guardian] student_phone nao configurado — alerta nao enviado")
        return False

    message = title + "\n\n" + "\n".join(lines)

    # Tenta Evolution API
    evolution_url = _cfg(config, "evolution", "base_url")
    evolution_key = _cfg(config, "evolution", "api_key")
    evolution_instance = _cfg(config, "evolution", "instance")

    if evolution_url and evolution_key and evolution_instance:
        try:
            payload = json.dumps({
                "number": student_phone,
                "text": message
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{evolution_url}/message/sendText/{evolution_instance}",
                data=payload,
                headers={"Content-Type": "application/json", "apikey": evolution_key},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201):
                    return True
        except Exception as exc:
            print(f"  [guardian] Evolution API falhou: {exc}")

    # Fallback Z-API
    zapi_instance = _cfg(config, "zapi", "instance_id")
    zapi_token = _cfg(config, "zapi", "token")
    if zapi_instance and zapi_token:
        try:
            payload = json.dumps({"phone": student_phone, "message": message}).encode("utf-8")
            req = urllib.request.Request(
                f"https://api.z-api.io/instances/{zapi_instance}/token/{zapi_token}/send-text",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status in (200, 201)
        except Exception as exc:
            print(f"  [guardian] Z-API falhou: {exc}")

    return False


# ---------------------------------------------------------------------------
# Snapshot helpers
# ---------------------------------------------------------------------------

def write_snapshot(layer_name, payload):
    ensure_structure()
    path = HEARTBEAT_DIR / f"{layer_name}.json"
    payload["layer"] = layer_name
    payload["updated_at"] = now_iso()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def parse_iso(value):
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def is_recent(timestamp, max_age_minutes):
    if not timestamp:
        return False
    dt = parse_iso(timestamp)
    if not dt:
        return False
    delta = datetime.now() - dt
    return delta.total_seconds() <= max_age_minutes * 60


# ---------------------------------------------------------------------------
# Camadas
# ---------------------------------------------------------------------------

def run_watchdog(config):
    """Camada 1 — roda a cada 5 minutos. Verifica servicos diretamente."""
    checks = run_all_checks(config)
    failing = [c for c in checks if not c["ok"]]
    snapshot = {
        "status": "ok" if not failing else "degraded",
        "checks": checks,
        "failing_services": [c["service"] for c in failing],
    }
    return write_snapshot("watchdog", snapshot)


def run_heartbeat(config):
    """Camada 2 — roda a cada 10 minutos. Verifica se watchdog esta ativo."""
    snapshots = latest_heartbeat_snapshot()
    watchdog = snapshots.get("watchdog") or {}
    watchdog_fresh = is_recent(watchdog.get("updated_at"), 10)
    failing_services = watchdog.get("failing_services") or []
    status = "ok" if watchdog_fresh and not failing_services else "alert"

    path = write_snapshot("heartbeat", {
        "status": status,
        "watchdog_fresh": watchdog_fresh,
        "failing_services": failing_services,
    })

    if status != "ok":
        send_alert(config, "Aviso — Instabilidade detectada", [
            f"Watchdog recente: {'sim' if watchdog_fresh else 'nao'}",
            f"Servicos com problema: {', '.join(failing_services) if failing_services else 'watchdog sem snapshot recente'}",
            "Verifique sua conexao e os scripts em ~/.operacao-ia/scripts/",
        ])
    return path


def run_last_resort(config):
    """Camada 3 — roda a cada 20 minutos. Aciona alerta critico se heartbeat falhar."""
    snapshots = latest_heartbeat_snapshot()
    heartbeat = snapshots.get("heartbeat") or {}
    heartbeat_fresh = is_recent(heartbeat.get("updated_at"), 20)
    heartbeat_ok = heartbeat.get("status") == "ok"
    status = "ok" if heartbeat_fresh and heartbeat_ok else "critical"

    path = write_snapshot("last_resort", {
        "status": status,
        "heartbeat_fresh": heartbeat_fresh,
        "heartbeat_status": heartbeat.get("status", "missing"),
    })

    if status != "ok":
        send_alert(config, "ALERTA CRITICO — Guardian acionado", [
            f"Heartbeat recente: {'sim' if heartbeat_fresh else 'nao'}",
            f"Status heartbeat: {heartbeat.get('status', 'ausente')}",
            "Sua operacao pode estar comprometida.",
            "Verifique o Mac e os servicos em ~/.operacao-ia/",
        ])
    return path


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Guardian — Heartbeat 3 camadas")
    parser.add_argument(
        "--layer",
        choices=["watchdog", "heartbeat", "last_resort", "all"],
        default="all",
        help="Camada a executar (padrao: all)"
    )
    args = parser.parse_args()

    try:
        config = load_config()
    except FileNotFoundError:
        print("  [guardian] config.json nao encontrado — execute a Etapa 0 primeiro.")
        sys.exit(1)

    created = []
    if args.layer in {"watchdog", "all"}:
        created.append(run_watchdog(config))
    if args.layer in {"heartbeat", "all"}:
        created.append(run_heartbeat(config))
    if args.layer in {"last_resort", "all"}:
        created.append(run_last_resort(config))

    for path in created:
        print(f"  Snapshot: {path}")


if __name__ == "__main__":
    main()
