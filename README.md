# 🐾 Terraria Desktop Pet (Python)

Mascote interativo para Windows desenvolvido em Python utilizando `tkinter`, `Pillow`, `pywin32` e `pystray`. O pet caminha pela área de trabalho, segue o cursor, comemora e altera de visual nas bordas da tela.

## 🚀 Funcionalidades

- 🟢 **Processo Único (Mutex)**: Garante que apenas uma instância rode por vez.
- 🖼️ **Janela Transparente & Click-Through**: Transparente e clique através da janela sem interferir no uso do PC.
- 🎯 **Modos de Comportamento**:
  - **Seguir**: Acompanha o cursor do mouse e pula ao alcançar.
  - **Parado**: Fixa-se na barra de tarefas acima do relógio.
  - **Andar**: Anda continuamente de um lado a outro da tela.
  - **Randômico**: Troca de mascote automaticamente ao atingir qualquer borda dos monitores.
- 🎨 **Galeria de Seleção**: Interface compacta de 5 colunas para escolha rápida dos mascotes.
- 📏 **Escala Otimizada**: Largura máxima fixa de 40px com proporção de altura automática.

## 🛠️ Como Executar

### 1. Instalação e Ambiente
\`\`\`bash
# Criar e ativar ambiente virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar dependências
pip install pillow pystray pywin32 pyinstaller
\`\`\`

### 2. Imagens / Sprites
Adicione os arquivos `.gif` ou `.webp` na raiz do projeto conforme registrado em `slime_pet.py`:
- `Slime_Yellow.gif`
- `Slime_Prince.gif`
- `Slime_Princess.gif`
- `Bunny.gif`
- ... (outros mascotes)

> **Nota**: As artes protegidas por copyright não estão incluídas neste repositório.

### 3. Rodar o Projeto
\`\`\`bash
python slime_pet.py
\`\`\`

## 📦 Compilação (.exe)

\`\`\`bash
pyinstaller --noconsole --onefile --add-data "Slime_Yellow.gif;." --add-data "Slime_Prince.gif;." --add-data "Slime_Princess.gif;." --add-data "Bunny.gif;." --add-data "Volt_Bunny.gif;." --add-data "Explosive_Bunny.gif;." --add-data "Duck_Fly.gif;." --add-data "Duck_Walk.gif;." --add-data "Goldfish_Walker.gif;." --add-data "Goldfish.gif;." --add-data "Honey_Bee.gif;." --add-data "Spiffo.gif;." --add-data "Blue_Chicken.gif;." --add-data "Dynamite_Kitten.gif;." --add-data "Junimo.gif;." slime_pet.py
\`\`\`