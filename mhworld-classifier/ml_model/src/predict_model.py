import sys
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import numpy as np
import json
import warnings

# Suprimir avisos específicos
warnings.filterwarnings("ignore", category=UserWarning, module="PIL")

# --- Configurações de Caminho para o Modelo e Classes ---
MODEL_PATH = '../../ml_model/mhw_monster_classifier_pytorch.pth'
CLASSES_PATH = '../../ml_model/mhw_monster_classes.json'

# --- Configurações de Tamanho da Imagem ---
IMG_HEIGHT = 128
IMG_WIDTH = 128

# Determina se uma GPU (CUDA) está disponível
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_ml_artifacts():
    """
    Carrega o modelo de Machine Learning e os nomes das classes.
    """
    try:
        # 1. Carregar os nomes das classes primeiro
        with open(CLASSES_PATH, 'r') as f:
            class_names = json.load(f)

        # 2. Reconstruir a arquitetura do modelo (ResNet18)
        # É importante que a arquitetura seja a mesma do treinamento.
        model = models.resnet18(weights=None) # Não carrega pesos pré-treinados aqui
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(class_names))

        # 3. Carregar os pesos treinados no modelo recém-construído
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.eval() # Coloca o modelo em modo de avaliação (importante para inferência)
        model = model.to(device) # Move o modelo para o dispositivo (GPU/CPU)

        return model, class_names
    except FileNotFoundError:
        sys.stderr.write(f"Erro: Arquivo do modelo '{MODEL_PATH}' ou classes '{CLASSES_PATH}' não encontrado.\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Erro ao carregar modelo ou classes: {e}\n")
        sys.exit(1)

def preprocess_image(image_path):
    """
    Carrega uma imagem do disco e a pré-processa para ser compatível com o modelo PyTorch.
    """
    # As transformações devem ser as mesmas usadas para o conjunto de VALIDAÇÃO no treinamento.
    val_transforms = transforms.Compose([
        transforms.Resize((IMG_HEIGHT, IMG_WIDTH)),
        transforms.ToTensor(), # Converte PIL para Tensor (0-255 -> 0-1)
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) # Normaliza
    ])

    try:
        image = Image.open(image_path).convert('RGB')
        # Aplica as transformações
        processed_image = val_transforms(image)
        # Adiciona uma dimensão de batch (o modelo espera um batch de imagens)
        processed_image = processed_image.unsqueeze(0) # Adiciona dimensão no índice 0
        return processed_image
    except Exception as e:
        sys.stderr.write(f"Erro ao pré-processar imagem {image_path}: {e}\n")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Uso: python predict_model.py <caminho_da_imagem>\n")
        sys.exit(1)

    image_path = sys.argv[1]

    model, class_names = load_ml_artifacts()
    processed_image = preprocess_image(image_path)
    processed_image = processed_image.to(device) # Move a imagem para o dispositivo

    try:
        with torch.no_grad(): # Desabilita o cálculo de gradientes durante a inferência (economiza memória e é mais rápido)
            outputs = model(processed_image)
            # Aplica softmax para obter probabilidades se a camada final do modelo não o fizer
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
            # Pega o índice da classe com a maior probabilidade
            confidence, predicted_class_index = torch.max(probabilities, 1)

            predicted_monster_name = class_names[predicted_class_index.item()] # .item() para pegar o valor escalar do tensor
            confidence = confidence.item() # .item() para pegar o valor escalar do tensor

            result = {
                "monster_name": predicted_monster_name,
                "confidence": confidence
            }
            print(json.dumps(result))

    except Exception as e:
        sys.stderr.write(f"Erro durante a inferência: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()