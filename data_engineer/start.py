#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Executa todos os scripts Python numerados da pasta data_engineer em ordem
(Ex.: 01-*.py, 02-*.py, ...), medindo o tempo de execução de cada um e o tempo total.
Uso: python start.py
"""
from __future__ import annotations

import re
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Tuple


def encontrar_scripts(base_dir: Path) -> List[Path]:
    """Encontra scripts no formato NN-nome.py (NN = 2 dígitos) na pasta informada."""
    candidatos = list(base_dir.glob("*.py"))
    scripts = [p for p in candidatos if re.match(r"^\d{2}-.*\.py$", p.name)]
    # Ordena lexicograficamente, o que respeita a ordem 01-, 02-, ...
    scripts.sort(key=lambda p: p.name)
    return scripts


def formatar_tempo(segundos: float) -> str:
    minutos, seg = divmod(int(segundos), 60)
    horas, minutos = divmod(minutos, 60)
    if horas:
        return f"{horas:d}h {minutos:02d}m {seg:02d}s"
    if minutos:
        return f"{minutos:d}m {seg:02d}s"
    return f"{seg}s"


def main() -> int:
    base_dir = Path(__file__).resolve().parent

    scripts = encontrar_scripts(base_dir)
    if not scripts:
        print("Nenhum script no formato 'NN-arquivo.py' encontrado em data_engineer.")
        return 1

    print("Iniciando execução sequencial dos scripts:")
    for s in scripts:
        print(f" - {s.name}")

    execucoes: List[Tuple[str, float, int]] = []  # (nome, duracao, returncode)

    t0_total = time.perf_counter()
    for script in scripts:
        print("\n" + "=" * 80)
        print(f"Iniciando: {script.name}")
        t0 = time.perf_counter()
        # Executa com o mesmo interpretador e com stdout/stderr na tela (sem captura)
        proc = subprocess.run([sys.executable, "-u", str(script)], cwd=str(base_dir))
        dt = time.perf_counter() - t0
        execucoes.append((script.name, dt, proc.returncode))

        status = "OK" if proc.returncode == 0 else f"ERRO (code={proc.returncode})"
        print(f"Finalizado: {script.name} | Tempo: {formatar_tempo(dt)} | Status: {status}")

        if proc.returncode != 0:
            print("Interrompendo devido a erro.")
            break

    total = time.perf_counter() - t0_total

    print("\n" + "-" * 80)
    print("Resumo de execução:")
    for nome, dur, rc in execucoes:
        status = "OK" if rc == 0 else f"ERRO (code={rc})"
        print(f" - {nome}: {status} em {formatar_tempo(dur)}")
    print("-" * 80)
    print(f"Tempo total: {formatar_tempo(total)}")

    # Retorna 0 se todos OK, senão o último código de erro
    ultimo_rc = next((rc for _, _, rc in reversed(execucoes) if rc != 0), 0)
    return ultimo_rc


if __name__ == "__main__":
    sys.exit(main())