#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Script Principal de Execução do Pipeline Completo

Executa em ordem:
1. Pipeline de Engenharia de Dados (data_engineer/loader.py)
2. Pipeline de Carga DuckDB (duckdb/carga/loader.py)
"""

import logging
import sys
import time
import subprocess
from pathlib import Path
from typing import Tuple


def setup_logging(base_dir: Path) -> None:
    """
    Configura o logging para salvar em arquivo e exibir no console.
    
    Args:
        base_dir: Diretório base do projeto para criar a pasta de logs.
    """
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_filename = f"pipeline_run_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
    log_filepath = log_dir / log_filename
    
    # Configuração do logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler(log_filepath, encoding='utf-8'),
            logging.StreamHandler(sys.stdout) # Continua exibindo no console
        ]
    )
    
    # Reduz o log de bibliotecas muito verbosas, se necessário
    logging.getLogger("urllib3").setLevel(logging.WARNING)


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
    logging.info("=" * 80)
    logging.info(f"🚀 Iniciando: {nome_pipeline}")
    logging.info("=" * 80)
    
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
        logging.info(f"--- Início da Saída de {caminho_loader.name} ---")
        if processo.stdout:
            logging.info(processo.stdout.strip())
        if processo.stderr:
            logging.error(processo.stderr.strip())
        logging.info(f"--- Fim da Saída de {caminho_loader.name} ---")
            
        tempo_fim = time.perf_counter()
        duracao = tempo_fim - tempo_inicio
        
        if processo.returncode == 0:
            logging.info(f"✅ {nome_pipeline} concluído com sucesso!")
        else:
            logging.error(f"❌ {nome_pipeline} falhou com código: {processo.returncode}")
            
        return processo.returncode, duracao
        
    except KeyboardInterrupt:
        tempo_fim = time.perf_counter()
        duracao = tempo_fim - tempo_inicio
        logging.warning(f"⚠️ {nome_pipeline} interrompido pelo usuário.")
        return 130, duracao
    except Exception as e:
        tempo_fim = time.perf_counter()
        duracao = tempo_fim - tempo_inicio
        logging.critical(f"🔥 Erro inesperado ao executar {nome_pipeline}: {e}", exc_info=True)
        return 1, duracao


def main() -> int:
    """
    Orquestra a execução completa do pipeline de dados.
    
    Returns:
        Código de saída (0 = sucesso, != 0 = erro)
    """
    base_dir = Path(__file__).resolve().parent
    
    # Configura o logging no início da execução
    setup_logging(base_dir)
    
    # Define os loaders a serem executados
    pipelines = [
        (base_dir / "data_engineer" / "loader.py", "Pipeline de Engenharia de Dados"),
        (base_dir / "duckdb" / "carga" / "loader.py", "Pipeline de Carga DuckDB")
    ]
    
    # Verifica se os loaders existem
    for caminho, nome in pipelines:
        if not caminho.exists():
            logging.error(f"❌ ERRO: Arquivo não encontrado: {caminho}")
            return 1
    
    logging.info("=" * 80)
    logging.info("🎯 EXECUÇÃO COMPLETA DO PIPELINE DE DADOS")
    logging.info("=" * 80)
    logging.info(f"📂 Diretório base: {base_dir}")
    logging.info(f"🐍 Python: {sys.executable}")
    logging.info("=" * 80)
    
    tempo_inicio_total = time.perf_counter()
    resultados = []
    
    # Executa cada pipeline em sequência
    for caminho_loader, nome_pipeline in pipelines:
        codigo_retorno, duracao = executar_loader(caminho_loader, nome_pipeline)
        resultados.append((nome_pipeline, codigo_retorno, duracao))
        
        # Se houver erro, interrompe a execução
        if codigo_retorno != 0:
            logging.warning(f"Pipeline interrompido devido a erro em: {nome_pipeline}")
            break
    
    tempo_fim_total = time.perf_counter()
    duracao_total = tempo_fim_total - tempo_inicio_total
    
    # --- Resumo Final ---
    logging.info("=" * 80)
    logging.info("📊 RESUMO GERAL DA EXECUÇÃO")
    logging.info("-" * 80)
    
    for nome, codigo, duracao in resultados:
        if codigo == 0:
            status = "✅ Sucesso"
        elif codigo == 130:
            status = "⚠️ Interrompido"
        else:
            status = f"❌ Erro ({codigo})"
        
        logging.info(f"  {nome:<40} | {status:<20} | {formatar_tempo(duracao)}")
    
    logging.info("-" * 80)
    logging.info(f"⏱️ Tempo total de execução: {formatar_tempo(duracao_total)}")
    logging.info("=" * 80)
    
    # Retorna o código de erro do último pipeline com falha, ou 0 se todos tiveram sucesso
    codigo_saida_final = next((rc for _, rc, _ in reversed(resultados) if rc != 0), 0)
    
    if codigo_saida_final == 0:
        logging.info("🎉 TODOS OS PIPELINES FORAM EXECUTADOS COM SUCESSO! 🎉")
    else:
        logging.warning("⚠️ Execução finalizada com erros. Verifique os logs.")
    
    return codigo_saida_final


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logging.warning("Execução principal interrompida pelo usuário.")
        sys.exit(130)
    except Exception as e:
        logging.critical(f"🔥 Falha crítica no orquestrador principal: {e}", exc_info=True)
        sys.exit(1)