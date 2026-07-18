#!/bin/bash
# Script para executar a interface gráfica do Re-Dino

echo "🦖 Re-Dino: Sistema de Síntese de DNA de Dinossauros"
echo "=================================================="
echo ""
echo "Iniciando interface gráfica..."
echo ""

# Verifica se PyQt5 está instalado
python3 -c "import PyQt5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ PyQt5 não está instalado!"
    echo "Instale com: pip3 install PyQt5 --break-system-packages"
    exit 1
fi

# Executa GUI
python3 /home/v0rtex/Documents/re-gen/CODIGO/gui_dino_synthesizer.py

