#!/usr/bin/env python3
"""
check_prerequisites.py — Confere o ambiente antes de comecar o Setup 2.

Modo somente-leitura: nao cria pastas, nao escreve config, nao instala nada.
E idempotente — pode rodar quantas vezes quiser.

Quem prepara a estrutura de fato e a Etapa 0 (`setup/setup_base.py`); este
arquivo e o atalho pra saber, antes de comecar, se falta alguma coisa.

A deteccao da Semana 1 e importada de setup_base.py (fonte unica), pros dois
nunca divergirem.

Compativel com Python 3.9 na leitura do arquivo (o setup em si pede 3.10+).
"""
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Permite rodar tanto da raiz (`python3 setup/check_prerequisites.py`)
# quanto de dentro da pasta setup/.
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from setup_base import detect_semana1
except ImportError as e:  # pragma: no cover - so acontece em repo incompleto
    print("Nao consegui carregar setup/setup_base.py: {}".format(e))
    print("Confirme que voce clonou o repositorio inteiro e tente de novo.")
    sys.exit(1)

MIN_PYTHON = (3, 10)


def _mostrar(ok: bool, texto: str) -> bool:
    print(("  ✅ " if ok else "  ❌ ") + texto)
    return ok


def checar_python() -> bool:
    v = sys.version_info
    return _mostrar(
        v >= MIN_PYTHON,
        "Python {}.{} (o setup pede {}.{}+)".format(
            v.major, v.minor, MIN_PYTHON[0], MIN_PYTHON[1]
        ),
    )


def checar_comando(nome: str, rotulo: Optional[str] = None) -> bool:
    rotulo = rotulo or nome
    achou = shutil.which(nome) is not None
    return _mostrar(achou, "{} {}".format(rotulo, "encontrado" if achou else "NAO encontrado"))


def checar_opcional(nome: str, rotulo: str, dica: str) -> None:
    """Item que so faz falta numa etapa especifica — avisa, nunca bloqueia."""
    if shutil.which(nome):
        print("  ✅ {} disponivel".format(rotulo))
    else:
        print("  ⚠️  {} nao encontrado".format(rotulo))
        print("      " + dica)


def checar_semana1() -> None:
    ok, info = detect_semana1()
    if ok:
        print("  ✅ Semana 1 concluida (aluno: {})".format(info))
    else:
        print("  ⚠️  Semana 1 nao detectada ({})".format(info))
        print("      Da pra continuar mesmo assim — algumas etapas se adaptam.")
    # Nunca bloqueia — mesmo criterio da Etapa 0.


def main() -> int:
    print("\nConferindo o que o Setup 2 (Operacao Profissional) precisa...\n")

    # (rotulo, passou?) — sem estes tres o setup nao roda.
    bloqueantes: List[Tuple[str, bool]] = [
        ("Python 3.10+", checar_python()),
        ("git", checar_comando("git")),
        ("Claude Code CLI", checar_comando("claude", "Claude Code CLI")),
    ]

    # Estes so fazem falta numa etapa especifica — avisam e seguem.
    checar_opcional("node", "Node.js",
                    "Precisa dele na Etapa 7 (publicar o CRM). Instale: https://nodejs.org")
    checar_opcional("wrangler", "wrangler (Cloudflare)",
                    "Precisa dele na Etapa 7. Instale: npm install -g wrangler")
    checar_opcional("brew", "Homebrew",
                    "Usado na Etapa 2 pra instalar o RTK. Instale: https://brew.sh")
    checar_semana1()

    faltando = [rotulo for rotulo, ok in bloqueantes if not ok]

    print("")
    if faltando:
        print("Falta resolver antes de comecar:")
        for rotulo in faltando:
            print("  - {}".format(rotulo))
        print("\nResolva os itens acima e rode este check de novo.")
        return 1

    print("Ambiente pronto. Pode abrir o Claude Code aqui e digitar: INICIAR SETUP SEMANA 2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
