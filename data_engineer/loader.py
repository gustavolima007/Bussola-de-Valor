#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Script Orquestrador para Pipeline de Dados

Executa os scripts de engenharia de dados em ordem, monitorando o tempo e o status.
"""

import re
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Tuple


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
        print("⚠️ Nenhum script no formato 'NN-arquivo.py' foi encontrado.")
        return 1

    print("="*80)
    print("🚀 Iniciando Pipeline de Dados")
    print("="*80)

    execucoes: List[Tuple[str, float, int]] = []
    tempo_inicio_total = time.perf_counter()
    interrupcao_manual = False

    for script in scripts_para_executar:
        print(f"\n▶️ Executando: {script.name}")
        tempo_inicio_script = time.perf_counter()

        try:
            processo = subprocess.run([sys.executable, "-X", "utf8", "-u", str(script)], cwd=base_dir, capture_output=True, encoding='utf-8', errors='surrogateescape')
            
            # Imprime a saída do script em tempo real (ou quase)
            if processo.stdout:
                print(processo.stdout.strip())
            if processo.stderr:
                print(processo.stderr.strip(), file=sys.stderr)

        except KeyboardInterrupt:
            print("\n⚠️ Execução interrompida pelo usuário.")
            interrupcao_manual = True
            execucoes.append((script.name, time.perf_counter() - tempo_inicio_script, 130))
            break

        tempo_fim_script = time.perf_counter()
        duracao_script = tempo_fim_script - tempo_inicio_script
        execucoes.append((script.name, duracao_script, processo.returncode))

        if processo.returncode != 0:
            print(f"❌ ERRO: O script {script.name} falhou (código: {processo.returncode}).")
            print("Pipeline interrompido.")
            break

    tempo_fim_total = time.perf_counter()
    duracao_total = tempo_fim_total - tempo_inicio_total

    # --- Resumo Final ---
    print("\n" + "=" * 80)
    print("📊 Resumo do Pipeline")
    print("-" * 80)
    for nome, duracao, codigo_retorno in execucoes:
        if codigo_retorno == 0:
            status = "✅ Sucesso"
        elif codigo_retorno == 130:
            status = "⚠️ Interrompido"
        else:
            status = f"❌ Erro ({codigo_retorno})"
        
        print(f"  - {nome:<30} | {status:<15} | Duração: {formatar_tempo(duracao)}")
    print("-" * 80)
    print(f"⏱️ Tempo total do pipeline: {formatar_tempo(duracao_total)}")
    print("=" * 80)

    if interrupcao_manual:
        return 130

    codigo_saida_final = next((rc for _, _, rc in reversed(execucoes) if rc != 0), 0)
    return codigo_saida_final

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"🔥 Falha inesperada no orquestrador: {e}", file=sys.stderr)
        sys.exit(1)