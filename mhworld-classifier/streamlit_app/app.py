# --- Imports ---
import streamlit as st
from PIL import Image
import requests
import json
import io # Importante para manipular dados de imagem em bytes
import os # Para lidar com caminhos de arquivo, se necessário

# --- Configurações da Aplicação ---
# Caminho para o JSON de monstros.
# Usamos 'os.path.join' para garantir que o caminho funcione em diferentes sistemas operacionais.
# O caminho é relativo à raiz do projeto, então 'data' é a pasta.
MONSTERS_JSON_PATH = os.path.join('data', 'monsters.json') # Ajustado para o caminho correto

# URL da API Go.
# Se você estiver executando a API Go em um contêiner Docker ou serviço de nuvem,
# este endereço precisará ser alterado. Por enquanto, local.
GO_API_URL = "http://localhost:8080/classify"

# --- Funções Auxiliares (com Caching do Streamlit) ---

@st.cache_data
def load_monster_data(path):
    """
    Carrega os dados dos monstros do arquivo JSON.
    @st.cache_data garante que esta função só será executada uma vez
    e o resultado será armazenado em cache, otimizando o desempenho.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Retorna apenas a lista de monstros, que é o que precisamos para a busca.
            return data.get('monsters', [])
    except FileNotFoundError:
        st.error(f"Erro: Arquivo JSON de monstros não encontrado em {path}. Verifique o caminho.")
        # Retorna uma lista vazia para evitar erros posteriores se o arquivo não for encontrado.
        return []
    except json.JSONDecodeError:
        st.error(f"Erro ao decodificar JSON em {path}. Verifique a sintaxe do arquivo JSON.")
        return []

def get_monster_details(monster_name, all_monster_data):
    """
    Busca os detalhes de um monstro específico (focando em MHW) no JSON carregado.
    """
    for monster_entry in all_monster_data:
        # Compara o nome previsto (em minúsculas para robustez) com os nomes do JSON.
        if monster_entry['name'].lower() == monster_name.lower():
            # Itera sobre as informações de jogo para encontrar os detalhes de MHW.
            for game_info in monster_entry['games']:
                if game_info['game'] == 'Monster Hunter World':
                    # Retorna o dicionário completo do monstro encontrado.
                    return monster_entry
    return None # Retorna None se o monstro não for encontrado ou não for de MHW.


# --- Configuração da Página Streamlit ---
# st.set_page_config deve ser a primeira chamada do Streamlit.
st.set_page_config(layout="centered", page_title="MHW Icon Classifier")

st.title("Classificador de Ícones de Monstros de Monster Hunter World")
st.markdown("Envie um ícone de monstro de MHW (ex: 'MHW-Anjanath_Icon.png') para obter suas informações.")

# Carrega os dados dos monstros no início do script.
all_monster_data = load_monster_data(MONSTERS_JSON_PATH)

# O restante do código do Streamlit (`uploaded_file`, lógica de upload, etc.)
# virá após essas definições de funções.
# ... (código que já existe para upload e exibição de resultados)