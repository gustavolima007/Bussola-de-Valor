import importlib
import sys
import os
import time

# Adiciona o diretório atual ao path para permitir a importação dos módulos
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

def formatar_tempo(segundos: float) -> str:
    """Converte segundos para um formato legível (m, s)."""
    minutos, seg = divmod(int(segundos), 60)
    if minutos:
        return f"{minutos}m {seg:02d}s"
    return f"{seg}s"

def run_step(module_name: str) -> bool:
    """Executa um módulo de carga, mede o tempo e imprime o status, retornando True em sucesso."""
    print(f"⏳ Executando: {module_name}...", end='', flush=True)
    start_time = time.perf_counter()

    try:
        module = importlib.import_module(module_name)
        if hasattr(module, 'main'):
            module.main()
        else:
            # Se o módulo não tem main, consideramos um aviso, não um erro fatal.
            duration = time.perf_counter() - start_time
            print('\r' + ' ' * 80 + '\r', end='')
            print(f"⚠️ {module_name:<45} | ⏱️  Duração: {formatar_tempo(duration)}")
            print(f"   (Aviso: Módulo não possui função 'main'. Nada foi executado.)")
            return True # Retorna True pois não é um erro que deva parar o pipeline

        duration = time.perf_counter() - start_time
        print('\r' + ' ' * 80 + '\r', end='')
        print(f"✅ {module_name:<45} | ⏱️  Duração: {formatar_tempo(duration)}")
        return True  # Sucesso

    except Exception as e:
        duration = time.perf_counter() - start_time
        print('\r' + ' ' * 80 + '\r', end='')
        print(f"❌ {module_name:<45} | ⏱️  Duração: {formatar_tempo(duration)}")
        print(f"   (Erro fatal: {e})")
        # Em um cenário real, aqui poderia ser logado o traceback completo.
        return False  # Falha

def main():
    """
    Orquestrador principal que executa todos os passos do processo de carga de dados.
    """
    print("=" * 60)
    print("🚀 Iniciando Carga para o Data Warehouse")
    print("=" * 60)

    # Lista de módulos a serem executados em ordem
    steps = [
        '01-carga_completa',
        '02-carga_incremental',
        '03-duckdb_dw'
    ]

    tempo_inicio_total = time.perf_counter()
    falha = False

    for step_name in steps:
        success = run_step(step_name)
        if not success:
            falha = True
            break

    duracao_total = time.perf_counter() - tempo_inicio_total

    print("-" * 60)
    if falha:
        print(f"🔥 Carga interrompida por erro após {formatar_tempo(duracao_total)}.")
    else:
        print(f"🎉 Carga finalizada com sucesso em {formatar_tempo(duracao_total)}!")
    print("=" * 60)

    if falha:
        sys.exit(1)

if __name__ == "__main__":
    main()