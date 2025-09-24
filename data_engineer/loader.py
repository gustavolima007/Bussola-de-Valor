#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Script Orquestrador para Pipeline de Dados

Este script funciona como o ponto de entrada para executar todo o pipeline de
engenharia de dados de forma sequencial e controlada.

Funcionalidades:
- Encontra todos os scripts Python na pasta `data_engineer` que seguem o padrão
  de nomenclatura `NN-nome.py` (onde NN são dois dígitos).
- Executa os scripts em ordem numérica (01, 02, 03, ...).
- Mede e exibe o tempo de execução de cada script individualmente.
- Exibe o tempo total de execução do pipeline completo.
- Interrompe a execução imediatamente se qualquer um dos scripts falhar.
- Retorna um código de saída apropriado (0 para sucesso, >0 para falha).
"""

import re
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Tuple

# --- Logging (Loguru) ---
from loguru import logger

# Configure logging: colored console
# Reset default handlers and set up sinks
logger.remove()
# Colored console output
logger.add(sys.stdout,
           colorize=True,
           backtrace=True,
           diagnose=True,
           level="INFO",
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

# --- Funções Auxiliares ---

def encontrar_scripts_ordenados(base_dir: Path) -> List[Path]:
    """
    Encontra e ordena os scripts a serem executados no diretório.

    Args:
        base_dir (Path): O diretório onde os scripts estão localizados.

    Returns:
        List[Path]: Uma lista de caminhos de scripts, ordenada numericamente.
    """
    # Regex para encontrar arquivos no formato "NN-qualquercoisa.py"
    padrao_script = r"^\d{2}-.*\.py$"
    scripts_encontrados = [p for p in base_dir.glob("*.py") if re.match(padrao_script, p.name)]

    logger.debug(f"Scripts candidatos encontrados: {[p.name for p in scripts_encontrados]}")

    # Ordena os scripts pelo nome do arquivo, garantindo a ordem de execução
    scripts_encontrados.sort(key=lambda p: p.name)
    return scripts_encontrados

def formatar_tempo(segundos: float) -> str:
    """
    Converte um tempo em segundos para um formato legível (horas, minutos, segundos).

    Args:
        segundos (float): O tempo total em segundos.

    Returns:
        str: A string formatada, por exemplo, "1h 02m 30s" ou "5m 15s".
    """
    minutos, seg = divmod(int(segundos), 60)
    horas, minutos = divmod(minutos, 60)
    if horas:
        return f"{horas}h {minutos:02d}m {seg:02d}s"
    if minutos:
        return f"{minutos}m {seg:02d}s"
    return f"{seg}s"

# --- Função Principal ---

def main() -> int:
    """Orquestra a execução de todo o pipeline de dados."""
    base_dir = Path(__file__).resolve().parent
    scripts_para_executar = encontrar_scripts_ordenados(base_dir)

    if not scripts_para_executar:
        logger.warning("Nenhum script no formato 'NN-arquivo.py' foi encontrado para execução.")
        return 1

    logger.info("Iniciando a execução do pipeline de dados:")
    for script in scripts_para_executar:
        logger.info(f" - {script.name}")

    # Lista para armazenar os resultados de cada execução
    execucoes: List[Tuple[str, float, int]] = []
    tempo_inicio_total = time.perf_counter()

    interrupcao_manual = False

    for script in scripts_para_executar:
        logger.info("\n" + "=" * 80)
        logger.info(f"▶️  Executando: {script.name}")
        tempo_inicio_script = time.perf_counter()

        # Executa o script como um subprocesso usando o mesmo interpretador Python
        # O argumento "-u" força o output a não ter buffer, exibindo em tempo real
        try:
            processo = subprocess.run([sys.executable, "-u", str(script)], cwd=base_dir)
        except KeyboardInterrupt:
            tempo_fim_script = time.perf_counter()
            duracao_script = tempo_fim_script - tempo_inicio_script
            execucoes.append((script.name, duracao_script, 130))
            logger.warning("Execução interrompida manualmente pelo usuário. Encerrando pipeline.")
            interrupcao_manual = True
            break

        tempo_fim_script = time.perf_counter()
        duracao_script = tempo_fim_script - tempo_inicio_script
        execucoes.append((script.name, duracao_script, processo.returncode))

        if processo.returncode == 0:
            status = "SUCESSO"
            logger.success(f"Finalizado: {script.name} | Duração: {formatar_tempo(duracao_script)} | Status: {status}")
        else:
            status = f"ERRO (código de saída: {processo.returncode})"
            logger.error(f"Finalizado: {script.name} | Duração: {formatar_tempo(duracao_script)} | Status: {status}")
            logger.error("Interrompendo o pipeline devido a erro no script anterior.")
            break  # Interrompe o loop em caso de erro

    tempo_fim_total = time.perf_counter()
    duracao_total = tempo_fim_total - tempo_inicio_total

    # --- Resumo Final ---
    logger.info("\n" + "=" * 80)
    logger.info("📊 Resumo da Execução do Pipeline")
    logger.info("-" * 80)
    for nome, duracao, codigo_retorno in execucoes:
        if codigo_retorno == 0:
            status = "Sucesso"
            level = logger.success
        elif codigo_retorno == 130:
            status = "Interrompido pelo usuário"
            level = logger.warning
        else:
            status = f"Erro (código: {codigo_retorno})"
            level = logger.error
        level(f"  - {nome:<30} | {status:<18} | Duração: {formatar_tempo(duracao)}")
    logger.info("-" * 80)
    logger.info(f"⏱️  Tempo total do pipeline: {formatar_tempo(duracao_total)}")
    logger.info("=" * 80)

    if interrupcao_manual:
        return 130

    # Retorna o último código de erro encontrado, ou 0 se tudo ocorreu bem
    codigo_saida_final = next((rc for _, _, rc in reversed(execucoes) if rc != 0), 0)
    return codigo_saida_final

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.warning("Pipeline interrompido manualmente pelo usuário.")
        sys.exit(130)
    except Exception as e:
        # Log full exception with traceback in both console and file
        logger.exception(f"Falha inesperada no loader: {e}")
        sys.exit(1)
