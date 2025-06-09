import os
import json
import shutil

print("Iniciado organização de ícones...")

# ---- Confiurações de caminhos/rotas ----
# rota da pasta de icons
icons_source_dir = 'data/icons'

# Caminho para o seu arquivo JSON de monstros
monsters_json_path = 'data/monsters.json'

# Diretório de saída onde o dataset organizado será criado
# Ele será criado dentro da pasta 'data/'
output_dataset_dir = 'data/mhw_icons_dataset'

# --- Criação do Diretório de Saída ---
os.makedirs(output_dataset_dir, exist_ok=True)
print (f"Diretório de dataset de saída criado/verificado: {output_dataset_dir}")

# --- Carregando os Dados do JSON ---
print (f"Carregando dados de monstros de: {monsters_json_path}")
try:
    with open(monsters_json_path, 'r', encoding='utf-8') as f:
        monsters_data = json.load(f)
except FileNotFoundError :
    print(f"ERRO: Arquivo JSON não encontrado em '{monsters_json_path}'. Verifique o caminho.")
    exit(1) # Sai do script se o arquivo não for encontrado
except json.JSONDecodeError:
    print(f"ERRO: Não foi possível decodificar o JSON em '{monsters_json_path}'. Verifique a sintaxe.")
    exit(1)

# --- Processando e Organizando Ícones ---
print("Filtrando e copiando ícones de Monster Hunter World...")
mhw_monsters_count = 0
for monster in monsters_data['monsters']:
    # Iterar sobre as informações de jogo para cada monstro
    for game_info in monster['games']:
        # Se o jogo for 'Monster Hunter World', processar o ícone
        if game_info['game'] == 'Monster Hunter World':
            monster_name = monster['name']
            icon_filename = game_info['image'] # Nome do arquivo do ícone, ex: "MHW-Anjanath_Icon.png"

            # Caminho completo do ícone original
            source_path = os.path.join(icons_source_dir, icon_filename)

            # Criar o subdiretório para o monstro dentro do dataset de saída
            # Usamos .lower() para garantir nomes de pastas consistentes e sem espaços
            target_monster_dir = os.path.join(output_dataset_dir, monster_name.lower())
            os.makedirs(target_monster_dir, exist_ok=True)

            # Caminho completo para onde o ícone será copiado
            target_path = os.path.join(target_monster_dir, icon_filename)

            # Verificar se o arquivo de origem existe antes de copiar
            if os.path.exists(source_path):
                # shutil.copy copia o arquivo. Se já existir no destino, ele sobrescreve.
                shutil.copy(source_path, target_path)
                mhw_monsters_count += 1
                # print(f"Copiado: {icon_filename} para {target_monster_dir}") # Descomente para ver cada cópia
            else:
                print(f"ATENÇÃO: Ícone não encontrado: {source_path}. Ignorando.")

print(f"\nOrganização concluída! {mhw_monsters_count} ícones de MHW foram copiados para '{output_dataset_dir}'.")