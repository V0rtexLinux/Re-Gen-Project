#!/bin/bash

# 🦖 RE-DINO QUICK START
# Alias simples para launcher.sh

cd "$(dirname "$0")"

# Se passou argumentos, processa-os
if [ $# -gt 0 ]; then
    case "$1" in
        gui)
            python3 CODIGO/gui_dino_synthesizer.py
            ;;
        synth)
            python3 CODIGO/main_v3.py --species "${2:-Tyrannosaurus rex}" --genome-size 3000000000
            ;;
        test)
            python3 CODIGO/test_v3_integration.py
            ;;
        launcher)
            ./launcher.sh
            ;;
        *)
            echo "Uso: ./START.sh [comando]"
            echo ""
            echo "Comandos disponíveis:"
            echo "  gui        - Abrir interface gráfica"
            echo "  synth      - Sintetizar genoma (specify: ./START.sh synth 'Triceratops')"
            echo "  test       - Executar testes"
            echo "  launcher   - Abrir menu interativo"
            echo ""
            echo "Se nenhum comando for especificado, abre o launcher."
            ;;
    esac
else
    # Sem argumentos, abre o launcher
    ./launcher.sh
fi
