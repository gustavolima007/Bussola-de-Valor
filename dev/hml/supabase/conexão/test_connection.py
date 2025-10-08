
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém a URL e a chave da API do Supabase a partir das variáveis de ambiente
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Verifica se a URL e a chave foram definidas
if not url or not key:
    print("URL do Supabase ou a Chave não foram definidas no seu arquivo .env")
    print("Crie um arquivo .env na raiz do projeto com as seguintes variáveis:")
    print("SUPABASE_URL=SUA_URL_AQUI")
    print("SUPABASE_KEY=SUA_CHAVE_AQUI")
else:
    # Cria o cliente Supabase
    try:
        supabase: Client = create_client(url, key)
        print("Conexão com o Supabase estabelecida com sucesso!")
        
        # Opcional: Teste fazendo uma chamada simples
        # response = supabase.from_('sua_tabela').select("*").limit(1).execute()
        # print("Resposta do teste de select:", response)

    except Exception as e:
        print(f"Falha ao conectar com o Supabase: {e}")
