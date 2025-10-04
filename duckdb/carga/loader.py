import importlib
import sys
import os

# Adiciona o diretório atual ao path para permitir a importação dos módulos
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

def run_step(module_name, step_number, total_steps):
    """Executa um módulo de carga e imprime o status."""
    print(f"\n--- PASSO {step_number}/{total_steps}: Executando {module_name} ---")
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, 'main'):
            module.main()
            print(f"--- SUCESSO: {module_name} concluído ---")
        else:
            print(f"⚠️  Aviso: O módulo {module_name} não possui uma função 'main'.")
    except Exception as e:
        print(f"❌  ERRO FATAL ao executar {module_name}: {e}")
        # Decide se deve parar ou continuar em caso de erro.
        # Para este fluxo, vamos parar se um passo falhar.
        sys.exit(1)

def main():
    """
    Orquestrador principal que executa todos os passos do processo de carga de dados.
    """
    print("=================================================")
    print("🚀  INICIANDO PROCESSO DE CARGA DO DATA WAREHOUSE  🚀")
    print("=================================================")

    # Lista de módulos a serem executados em ordem
    steps = [
        '01-carga_completa',
        '02-carga_incremental',
        '03-duckdb_dw'
    ]
    total_steps = len(steps)

    for i, step_name in enumerate(steps, 1):
        run_step(step_name, i, total_steps)

    print("\n===============================================")
    print("🎉  PROCESSO DE CARGA FINALIZADO COM SUCESSO!  🎉")
    print("===============================================")

if __name__ == "__main__":
    main()
