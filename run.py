#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Script Principal de Execução do Pipeline Completo

Executa em ordem:
1. Pipeline de Engenharia de Dados (data_engineer/loader.py)
2. Pipeline de Carga DuckDB (duckdb/carga/loader.py)
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import Tuple


def formatar_tempo(segundos: float) -> str:
    """
    Converte segundos para um formato legível (m, s).
    
    Args:
        segundos: Tempo em segundos
        
    Returns:
        String formatada com minutos e segundos
    """
    minutos, seg = divmod(int(segundos), 60)
    if minutos:
        return f"{minutos}m {seg:02d}s"
    return f"{seg}s"


def executar_loader(caminho_loader: Path, nome_pipeline: str) -> Tuple[int, float]:
    """
    Executa um script loader e retorna o código de saída e duração.
    
    Args:
        caminho_loader: Caminho absoluto para o script loader.py
        nome_pipeline: Nome descritivo do pipeline para exibição
        
    Returns:
        Tupla com (código_retorno, duração_em_segundos)
    """
    print("\n" + "=" * 80)
    print(f"🚀 Iniciando: {nome_pipeline}")
    print("=" * 80)
    
    tempo_inicio = time.perf_counter()
    
    try:
        processo = subprocess.run(
            [sys.executable, "-X", "utf8", "-u", str(caminho_loader)],
            cwd=caminho_loader.parent,
            capture_output=True,
            encoding='utf-8',
            errors='surrogateescape'
        )
        
        # Imprime a saída do script
        if processo.stdout:
            print(processo.stdout.strip())
        if processo.stderr:
            print(processo.stderr.strip(), file=sys.stderr)
            
        tempo_fim = time.perf_counter()
        duracao = tempo_fim - tempo_inicio
        
        if processo.returncode == 0:
            print(f"\n✅ {nome_pipeline} concluído com sucesso!")
        else:
            print(f"\n❌ {nome_pipeline} falhou com código: {processo.returncode}")
            
        return processo.returncode, duracao
        
    except KeyboardInterrupt:
        tempo_fim = time.perf_counter()
        duracao = tempo_fim - tempo_inicio
        print(f"\n⚠️ {nome_pipeline} interrompido pelo usuário.")
        return 130, duracao
        
    except Exception as e:
        tempo_fim = time.perf_counter()
        duracao = tempo_fim - tempo_inicio
        print(f"\n🔥 Erro inesperado ao executar {nome_pipeline}: {e}", file=sys.stderr)
        return 1, duracao


def main() -> int:
    """
    Orquestra a execução completa do pipeline de dados.
    
    Returns:
        Código de saída (0 = sucesso, != 0 = erro)
    """
    base_dir = Path(__file__).resolve().parent
    
    # Define os loaders a serem executados
    pipelines = [
        (base_dir / "data_engineer" / "loader.py", "Pipeline de Engenharia de Dados"),
        (base_dir / "duckdb" / "carga" / "loader.py", "Pipeline de Carga DuckDB")
    ]
    
    # Verifica se os loaders existem
    for caminho, nome in pipelines:
        if not caminho.exists():
            print(f"❌ ERRO: Arquivo não encontrado: {caminho}")
            return 1
    
    print("=" * 80)
    print("🎯 EXECUÇÃO COMPLETA DO PIPELINE DE DADOS")
    print("=" * 80)
    print(f"📂 Diretório base: {base_dir}")
    print(f"🐍 Python: {sys.executable}")
    print("=" * 80)
    
    tempo_inicio_total = time.perf_counter()
    resultados = []
    
    # Executa cada pipeline em sequência
    for caminho_loader, nome_pipeline in pipelines:
        codigo_retorno, duracao = executar_loader(caminho_loader, nome_pipeline)
        resultados.append((nome_pipeline, codigo_retorno, duracao))
        
        # Se houver erro, interrompe a execução
        if codigo_retorno != 0:
            print(f"\n⚠️ Pipeline interrompido devido a erro em: {nome_pipeline}")
            break
    
    tempo_fim_total = time.perf_counter()
    duracao_total = tempo_fim_total - tempo_inicio_total
    
    # --- Resumo Final ---
    print("\n" + "=" * 80)
    print("📊 RESUMO GERAL DA EXECUÇÃO")
    print("-" * 80)
    
    for nome, codigo, duracao in resultados:
        if codigo == 0:
            status = "✅ Sucesso"
        elif codigo == 130:
            status = "⚠️ Interrompido"
        else:
            status = f"❌ Erro ({codigo})"
        
        print(f"  {nome:<40} | {status:<20} | {formatar_tempo(duracao)}")
    
    print("-" * 80)
    print(f"⏱️ Tempo total de execução: {formatar_tempo(duracao_total)}")
    print("=" * 80)
    
    # Retorna o código de erro do último pipeline com falha, ou 0 se todos tiveram sucesso
    codigo_saida_final = next((rc for _, rc, _ in reversed(resultados) if rc != 0), 0)
    
    if codigo_saida_final == 0:
        print("\n🎉 TODOS OS PIPELINES FORAM EXECUTADOS COM SUCESSO! 🎉\n")
    else:
        print("\n⚠️ Execução finalizada com erros. Verifique os logs acima.\n")
    
    return codigo_saida_final


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Execução interrompida pelo usuário.")
        sys.exit(130)
    except Exception as e:
        print(f"\n🔥 Falha crítica no orquestrador principal: {e}", file=sys.stderr)
        sys.exit(1)