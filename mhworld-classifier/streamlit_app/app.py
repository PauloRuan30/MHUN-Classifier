import streamlit as st
from PIL import Image
import requests
import json
import io
import os

# --- Configurações da Aplicação ---
MONSTERS_JSON_PATH = os.path.join('data', 'monsters.json')
GO_API_URL = "http://localhost:8080/classify"

# --- Funções Auxiliares (com Caching) ---
@st.cache_data
def load_monster_data(path):
    """Carrega os dados dos monstros do arquivo JSON."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('monsters', [])
    except FileNotFoundError:
        st.error(f"Erro: Arquivo JSON de monstros não encontrado em **{path}**. "
                 f"Certifique-se de que o caminho está correto e que o arquivo existe.")
        return []
    except json.JSONDecodeError:
        st.error(f"Erro ao decodificar JSON em **{path}**. Verifique a sintaxe do arquivo JSON.")
        return []

def get_monster_details(monster_name, all_monster_data):
    """Busca os detalhes de um monstro específico (focando em MHW) no JSON carregado."""
    for monster_entry in all_monster_data:
        if monster_entry['name'].lower() == monster_name.lower():
            for game_info in monster_entry['games']:
                if game_info['game'] == 'Monster Hunter World':
                    return monster_entry
    return None

# --- Configuração da Página Streamlit ---
st.set_page_config(layout="centered", page_title="MHW Icon Classifier")

st.title("Classificador de Ícones de Monstros de Monster Hunter World")
st.markdown("Envie um ícone de monstro de MHW (ex: 'MHW-Anjanath_Icon.png') para obter suas informações.")

# Carrega os dados dos monstros no início do script.
all_monster_data = load_monster_data(MONSTERS_JSON_PATH)

uploaded_file = st.file_uploader("Escolha um ícone de monstro...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('RGB')
    st.image(image, caption='Ícone Carregado.', use_column_width=False, width=150)
    st.write("")
    st.write("Classificando...")

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()

    # --- Chamada à API Go ---
    try:
        response = requests.post(GO_API_URL, files={'image': (uploaded_file.name, img_byte_arr, 'image/png')})
        response.raise_for_status() # Lança exceção para status HTTP 4xx/5xx

        prediction_result = response.json()

        predicted_monster_name = prediction_result.get("monster_name")
        confidence = prediction_result.get("confidence")
        api_error_message = prediction_result.get("error")

        if api_error_message:
            st.error(f"Erro da API de Classificação: **{api_error_message}**")
        elif predicted_monster_name and confidence is not None:
            st.success(f"Previsão: **{predicted_monster_name.capitalize()}** com **{confidence:.2f}%** de confiança.")

            found_monster_details = get_monster_details(predicted_monster_name, all_monster_data)

            if found_monster_details:
                st.subheader(f"Detalhes de {found_monster_details['name']}:")
                st.markdown(f"**Tipo:** {found_monster_details.get('type', 'N/A')}")
                elements = found_monster_details.get('elements', [])
                st.markdown(f"**Elementos:** {', '.join(elements) if elements else 'N/A'}")
                weaknesses = found_monster_details.get('weakness', [])
                st.markdown(f"**Fraquezas:** {', '.join(weaknesses) if weaknesses else 'N/A'}")
                ailments = found_monster_details.get('ailments', [])
                st.markdown(f"**Afliges:** {', '.join(ailments) if ailments else 'N/A'}")
                
                mhw_info = next((g['info'] for g in found_monster_details['games'] if g['game'] == 'Monster Hunter World'), "N/A")
                st.markdown(f"**Descrição MHW:** *{mhw_info}*")
            else:
                st.info("Detalhes adicionais para este monstro em Monster Hunter World não foram encontrados no banco de dados. O banco de dados pode estar incompleto ou o monstro não é de MHW.")
        else:
            st.error("Resposta inválida da API Go. Os dados de previsão (nome do monstro ou confiança) estão incompletos.")
            st.code(f"Resposta bruta da API para depuração: {prediction_result}")

    except requests.exceptions.ConnectionError:
        st.error("❌ **Erro de Conexão:** A API Go não está rodando ou não está acessível.")
        st.info("Por favor, certifique-se de que a API Go está iniciada e acessível em `http://localhost:8080`.")
    except requests.exceptions.Timeout:
        st.error("⏳ **Tempo Limite Excedido:** A API Go demorou muito para responder. A API pode estar sobrecarregada ou lenta.")
    except json.JSONDecodeError:
        st.error(f"⚠️ **Erro na Resposta da API:** Não foi possível decodificar a resposta JSON da API Go. A API pode ter retornado dados inesperados. "
                 f"Resposta bruta: \n```\n{response.text}\n```")
    except requests.exceptions.RequestException as e:
        st.error(f"🚨 **Erro na Requisição para a API Go:** {e}")
        st.info(f"Código de Status da Requisição: **{response.status_code}**")
        st.code(f"Corpo da Resposta do Servidor para depuração: \n```\n{response.text}\n```")
    except Exception as e:
        st.error(f"🐞 **Ocorreu um erro inesperado:** {e}")

st.markdown("---")
st.markdown("Este projeto é para fins educacionais e de demonstração. Desenvolvido com ❤️ para a comunidade Monster Hunter.")