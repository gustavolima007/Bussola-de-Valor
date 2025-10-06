#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
>> Script Orquestrador para Pipeline de Dados

Executa os scripts de engenharia de dados em ordem, monitorando o tempo e o status.
"""

import re
import sys
import time
import subprocess
from pathlib import Path
from typing import List


def encontrar_scripts_ordenados(base_dir: Path) -> List[Path]:
    """Encontra e ordena os scripts a serem executados."""
    padrao_script = r"^\d{2}-.*\.py$"
    scripts_encontrados = [p for p in base_dir.glob("*.py") if re.match(padrao_script, p.name)]
    scripts_encontrados.sort(key=lambda p: p.name)
    return scripts_encontrados


def formatar_tempo(segundos: float) -> str:
    """Converte segundos para um formato legível (m, s)."""
    minutos, seg = divmod(int(segundos), 60)
    if minutos:
        return f"{minutos}m {seg:02d}s"
    return f"{seg}s"

def main() -> int:
    """Orquestra a execução de todo o pipeline de dados."""
    base_dir = Path(__file__).resolve().parent
    scripts_para_executar = encontrar_scripts_ordenados(base_dir)

    if not scripts_para_executar:
        print("AVISO Nenhum script no formato 'NN-arquivo.py' foi encontrado.")
        return 1

    print("=" * 60)
    print(">> Iniciando Pipeline de Dados de Engenharia")
    print("=" * 60)

    tempo_inicio_total = time.perf_counter()
    falha = False
    interrupcao_manual = False

    for script in scripts_para_executar:
        print(f">> Executando: {script.name}...", end='', flush=True)
        tempo_inicio_script = time.perf_counter()

        try:
            processo = subprocess.run(
                [sys.executable, "-u", str(script)],
                cwd=base_dir,
                capture_output=True,
                encoding='utf-8',
                errors='surrogateescape'
            )
        except KeyboardInterrupt:
            print('\r' + ' ' * 80 + '\r', end='')
            print(f"AVISO  Execução interrompida pelo usuário no script: {script.name}")
            interrupcao_manual = True
            falha = True
            break

        duracao_script = time.perf_counter() - tempo_inicio_script
        
        print('\r' + ' ' * 80 + '\r', end='')

        if processo.returncode == 0:
            print(f"OK {script.name:<45} | Duração: {formatar_tempo(duracao_script)}")
        else:
            print(f"ERRO {script.name:<45} | Duração: {formatar_tempo(duracao_script)}")
            print(f"   (Código de erro: {processo.returncode})")
            if processo.stderr:
                print("-" * 15 + " Detalhes do Erro " + "-" * 15)
                for line in processo.stderr.strip().split('\n'):
                    print(f"    > {line}")
                print("-" * (30 + len(" Detalhes do Erro ")))
            falha = True
            break

    duracao_total = time.perf_counter() - tempo_inicio_total
    
    print("-" * 60)
    if interrupcao_manual:
        print(f"PARADA Pipeline interrompido manualmente em {formatar_tempo(duracao_total)}.")
    elif falha:
        print(f"ERRO Pipeline interrompido por erro após {formatar_tempo(duracao_total)}.")
    else:
        print(f"SUCESSO Pipeline concluído com sucesso em {formatar_tempo(duracao_total)}!")
    print("=" * 60)

    if interrupcao_manual:
        return 130
    
    return 1 if falha else 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Falha inesperada no orquestrador: {e}", file=sys.stderr)
        sys.exit(1)
