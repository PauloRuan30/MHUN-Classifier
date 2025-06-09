import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import os
import json
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="PIL")

# --- TODO O SEU CÓDIGO ATUAL DEVE SER COLOCADO AQUI, DENTRO DESTE BLOCO ---
# Por exemplo, suas prints e configurações:
# print("Iniciando o treinamento do modelo de IA com PyTorch...")

# --- Configurações ---
dataset_dir = '../../data/mhw_icons_dataset'
img_height = 128
img_width = 128
batch_size = 32
epochs = 20
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- Transformações de Imagem ---
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
train_transforms = transforms.Compose([
    transforms.RandomResizedCrop(img_height, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(5),
    transforms.ColorJitter(brightness=0.1, contrast=0.1),
    transforms.ToTensor(),
    normalize
])

def run_training():
    """Função que encapsula toda a lógica de treinamento."""
    print("Iniciando o treinamento do modelo de IA com PyTorch...")
    print(f"Usando dispositivo: {device}")

    # --- Carregando o Dataset ---
    try:
        full_dataset = datasets.ImageFolder(root=dataset_dir, transform=train_transforms)
        class_names = full_dataset.classes
        print(f"Classes (Monstros) encontradas: {class_names}")
    except Exception as e:
        print(f"ERRO ao carregar o dataset: {e}. Verifique se '{dataset_dir}' existe e contém imagens.")
        exit(1)

    # Nota: `num_workers` é a causa do problema. Em Windows,
    # se você tiver problemas persistentes com `num_workers > 0`,
    # pode tentar `num_workers=0` para depurar, mas isso desacelera.
    # A solução `if __name__ == '__main__':` é a correta.
    train_loader = DataLoader(full_dataset, batch_size=batch_size, shuffle=True, num_workers=os.cpu_count() // 2 or 1)

    # --- Construção do Modelo (ResNet18 com Transfer Learning) ---
    print("Construindo o modelo de Transfer Learning com ResNet18...")
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    for param in model.parameters():
        param.requires_grad = False

    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, len(class_names))
    model = model.to(device)

    # --- Função de Perda e Otimizador ---
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=0.001)

    # --- Treinamento ---
    print(f"Iniciando o treinamento por {epochs} épocas...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct_predictions = 0
        total_predictions = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs.data, 1)
            total_predictions += labels.size(0)
            correct_predictions += (predicted == labels).sum().item()

        epoch_loss = running_loss / len(full_dataset)
        epoch_accuracy = correct_predictions / total_predictions
        print(f"Época {epoch+1}/{epochs}, Perda: {epoch_loss:.4f}, Acurácia: {epoch_accuracy:.4f}")

    # --- Salvando o Modelo e as Classes ---
    model_save_path = '../../ml_model/mhw_monster_classifier_pytorch.pth'
    torch.save(model.state_dict(), model_save_path)
    classes_save_path = '../../ml_model/mhw_monster_classes.json'
    with open(classes_save_path, 'w') as f:
        json.dump(class_names, f)

    print(f"\nTreinamento concluído! Modelo em: {model_save_path}, Classes em: {classes_save_path}")

# ESTA É A PARTE MAIS IMPORTANTE PARA RESOLVER O ERRO
if __name__ == '__main__':
    run_training() # Chama a função que encapsula o treinamento