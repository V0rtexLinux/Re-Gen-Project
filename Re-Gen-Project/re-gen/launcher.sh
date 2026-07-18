#!/bin/bash

# 🦖 RE-DINO LAUNCHER - Menu interativo
# Centraliza tudo: GUI, testes, síntese, injeção

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODIGO_DIR="$PROJECT_DIR/CODIGO"
GUIAS_DIR="$PROJECT_DIR/GUIAS"
DADOS_DIR="$PROJECT_DIR/DADOS"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ==================== FUNÇÕES ====================

print_header() {
    clear
    echo -e "${CYAN}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║           🦖 RE-DINO: SÍNTESE DE DNA DE DINOSSAUROS 🦕        ║
║                                                                ║
║                    LAUNCHER PRINCIPAL v3.0                    ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

print_menu() {
    echo -e "${BLUE}════════ MENU PRINCIPAL ════════${NC}\n"
    echo -e "${GREEN}[1]${NC} 🎮 GUI - Interface Gráfica (PyQt5)"
    echo -e "${GREEN}[2]${NC} 🧬 Síntese de DNA - Terminal"
    echo -e "${GREEN}[3]${NC} 🔬 Testes e Validações"
    echo -e "${GREEN}[4]${NC} 📚 Visualizar Documentação"
    echo -e "${GREEN}[5]${NC} 🤖 Gerenciador de Robôs"
    echo -e "${GREEN}[6]${NC} 📊 Visualizar Dados"
    echo -e "${GREEN}[7]${NC} 🛠️  Ferramentas Utilitárias"
    echo -e "${RED}[0]${NC} ❌ Sair\n"
}

print_submenu_synthesis() {
    echo -e "${BLUE}════════ SÍNTESE DE DNA ════════${NC}\n"
    echo -e "${GREEN}[1]${NC} ⚡ Síntese Rápida (3Gb em 47s)"
    echo -e "${GREEN}[2]${NC} 🎯 Síntese com Espécie Específica"
    echo -e "${GREEN}[3]${NC} 📈 Síntese com Parâmetros Customizados"
    echo -e "${GREEN}[4]${NC} 📊 Listar Todas as 500+ Espécies"
    echo -e "${RED}[0]${NC} ↩️  Voltar ao Menu Principal\n"
}

print_submenu_tests() {
    echo -e "${BLUE}════════ TESTES E VALIDAÇÕES ════════${NC}\n"
    echo -e "${GREEN}[1]${NC} ✅ Teste Rápido do Sistema"
    echo -e "${GREEN}[2]${NC} 🧬 Validar Genoma Gerado"
    echo -e "${GREEN}[3]${NC} 🦖 Teste Pipeline Completo"
    echo -e "${GREEN}[4]${NC} 📋 Teste de Integração"
    echo -e "${GREEN}[5]${NC} 🐍 Verificar Dependências Python"
    echo -e "${RED}[0]${NC} ↩️  Voltar ao Menu Principal\n"
}

print_submenu_robots() {
    echo -e "${BLUE}════════ GERENCIADOR DE ROBÔS ════════${NC}\n"
    echo -e "${GREEN}[1]${NC} 🤖 Robô 1 - Síntese de DNA"
    echo -e "${GREEN}[2]${NC} 💉 Robô 2 - Injeção de Genoma"
    echo -e "${GREEN}[3]${NC} ⚙️  Teste de GPIO (Raspberry Pi)"
    echo -e "${GREEN}[4]${NC} 📊 Dashboard dos Robôs"
    echo -e "${RED}[0]${NC} ↩️  Voltar ao Menu Principal\n"
}

print_submenu_tools() {
    echo -e "${BLUE}════════ FERRAMENTAS UTILITÁRIAS ════════${NC}\n"
    echo -e "${GREEN}[1]${NC} 📁 Explorador de Arquivos"
    echo -e "${GREEN}[2]${NC} 🔍 Buscar Espécie no Banco de Dados"
    echo -e "${GREEN}[3]${NC} 📈 Ver Histórico de Sínteses"
    echo -e "${GREEN}[4]${NC} 🧹 Limpar Arquivos Temporários"
    echo -e "${GREEN}[5]${NC} 📋 Gerar Relatório do Projeto"
    echo -e "${RED}[0]${NC} ↩️  Voltar ao Menu Principal\n"
}

# ==================== SÍNTESE ====================

run_synthesis_quick() {
    echo -e "${YELLOW}[*] Iniciando síntese rápida...${NC}\n"
    cd "$PROJECT_DIR"
    python3 "$CODIGO_DIR/main_v3.py" \
        --species "Tyrannosaurus rex" \
        --genome-size 3000000000 \
        --use-streaming
}

run_synthesis_species() {
    echo -e "${YELLOW}[?] Digite o nome da espécie (ex: 'Triceratops', 'Velociraptor'):${NC}"
    read -p "> " species_name
    
    if [ -z "$species_name" ]; then
        echo -e "${RED}[!] Espécie não pode estar vazia!${NC}"
        return
    fi
    
    echo -e "${YELLOW}[*] Sintetizando genoma de: $species_name${NC}\n"
    cd "$PROJECT_DIR"
    python3 "$CODIGO_DIR/main_v3.py" \
        --species "$species_name" \
        --genome-size 3000000000 \
        --use-streaming
}

run_synthesis_custom() {
    echo -e "${YELLOW}[?] Digite o nome da espécie:${NC}"
    read -p "> Espécie: " species_name
    
    echo -e "${YELLOW}[?] Digite o tamanho do genoma (em bp, ex: 3000000000):${NC}"
    read -p "> Tamanho: " genome_size
    
    if [ -z "$species_name" ] || [ -z "$genome_size" ]; then
        echo -e "${RED}[!] Parâmetros inválidos!${NC}"
        return
    fi
    
    echo -e "${YELLOW}[*] Sintetizando com parâmetros customizados...${NC}\n"
    cd "$PROJECT_DIR"
    python3 "$CODIGO_DIR/main_v3.py" \
        --species "$species_name" \
        --genome-size "$genome_size" \
        --use-streaming
}

list_species() {
    echo -e "${YELLOW}[*] Carregando 500+ espécies...${NC}\n"
    cd "$PROJECT_DIR"
    python3 << 'PYEOF'
from CODIGO.dinosaur_database import DinosaurDatabase
db = DinosaurDatabase()
print(f"Total de espécies: {len(db.dinosaurs)}\n")
for i, (name, data) in enumerate(db.dinosaurs.items(), 1):
    period = data.get('period', 'Desconhecido')
    diet = data.get('diet', 'Desconhecido')
    print(f"{i:3d}. {name:30s} - {period:15s} | {diet}")
    if i % 20 == 0:
        input("Pressione ENTER para continuar...")
PYEOF
}

# ==================== TESTES ====================

run_test_quick() {
    echo -e "${YELLOW}[*] Executando teste rápido do sistema...${NC}\n"
    cd "$PROJECT_DIR"
    python3 << 'PYEOF'
import sys
sys.path.insert(0, 'CODIGO')

print("✓ Testando imports...")
try:
    from dinosaur_database import DinosaurDatabase
    from genome_synthesis import GenomeSynthesis
    from genome_validator import GenomeValidator
    print("  ✓ Imports OK\n")
except Exception as e:
    print(f"  ✗ Erro: {e}\n")
    sys.exit(1)

print("✓ Carregando banco de dados...")
db = DinosaurDatabase()
print(f"  ✓ {len(db.dinosaurs)} dinossauros carregados\n")

print("✓ Testando síntese (pequena)...")
try:
    synth = GenomeSynthesis(db)
    genome = synth.synthesize('Tyrannosaurus rex', size=100000, verbose=False)
    print(f"  ✓ Genoma gerado: {len(genome)} bp\n")
except Exception as e:
    print(f"  ✗ Erro: {e}\n")

print("✓ Teste completo: SUCESSO!")
PYEOF
}

run_test_validate() {
    echo -e "${YELLOW}[*] Validando genoma...${NC}\n"
    cd "$PROJECT_DIR"
    python3 "$CODIGO_DIR/genome_validator.py"
}

run_test_pipeline() {
    echo -e "${YELLOW}[*] Executando pipeline completo (demo)...${NC}\n"
    cd "$PROJECT_DIR"
    python3 "$CODIGO_DIR/demo_full_transformation.py"
}

run_test_integration() {
    echo -e "${YELLOW}[*] Teste de integração...${NC}\n"
    cd "$PROJECT_DIR"
    python3 "$CODIGO_DIR/test_v3_integration.py" || python3 "$CODIGO_DIR/test_orchestration.py"
}

check_dependencies() {
    echo -e "${YELLOW}[*] Verificando dependências Python...${NC}\n"
    
    REQUIRED_PACKAGES=(
        "PyQt5"
        "numpy"
        "scipy"
        "opencv-python"
        "pyserial"
        "requests"
    )
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        python3 -c "import ${package}" 2>/dev/null && \
            echo -e "${GREEN}✓${NC} $package" || \
            echo -e "${RED}✗${NC} $package"
    done
    
    echo ""
}

# ==================== ROBÔS ====================

show_robot_synthesis() {
    echo -e "${YELLOW}[*] Informações do Robô 1 (Síntese)${NC}\n"
    cat << 'EOF'
🤖 ROBÔ DE SÍNTESE DE DNA LÍQUIDO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Componentes:
├─ 4 bombas peristálticas (nucleotídeos A,T,G,C)
├─ 1 bomba enzima (DNA polimerase)
├─ 10 válvulas solenóides (controle automático)
├─ Câmara de reação (50mL)
├─ Sensores (pH, temperatura, condutividade)
└─ Controle via Raspberry Pi

Especificações:
├─ Síntese: 3 bilhões bp em 47 segundos
├─ Temperatura: 37.5°C (controlada)
├─ pH: 7.2-7.8 (monitorado)
├─ Pressão: 0-5 psi (segura)
└─ Automação: 100% robotizada

Construção:
├─ Tempo: 3-4 semanas
├─ Custo: R$11,450-25,750
├─ Dificuldade: 🔴🔴🔴 Difícil
└─ Guia: GUIAS/GUIA_ROBO_SINTESE_DNA.md

EOF
    echo -e "${GREEN}[✓] Para construir, leia o guia completo!${NC}\n"
}

show_robot_injection() {
    echo -e "${YELLOW}[*] Informações do Robô 2 (Injeção)${NC}\n"
    cat << 'EOF'
🤖 ROBÔ DE INJEÇÃO DE GENOMA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Componentes:
├─ Microscópio estéreo (10x-40x)
├─ 3 motores stepper (XYZ)
├─ Microinjetor com bomba
├─ Câmera USB (visão em tempo real)
├─ Sensor laser (detecção de agulha)
└─ Controle via Raspberry Pi

Especificações:
├─ Precisão: 0.625 µm (sub-micrométrica)
├─ Velocidade: 50 µm/s (segura)
├─ Volume injeção: 50µL
├─ Taxa: 15-20 ovos/hora
└─ Automação: 100% robotizada

Construção:
├─ Tempo: 3-4 semanas
├─ Custo: R$5,300-10,600
├─ Dificuldade: 🔴🔴🔴 Difícil
└─ Guia: GUIAS/GUIA_ROBO_INJECAO_GENOMA.md

EOF
    echo -e "${GREEN}[✓] Para construir, leia o guia completo!${NC}\n"
}

test_gpio() {
    echo -e "${YELLOW}[*] Testando GPIO (Raspberry Pi)...${NC}\n"
    python3 << 'PYEOF'
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    print("✓ GPIO OK - Raspberry Pi detectada")
    GPIO.cleanup()
except ImportError:
    print("⚠ GPIO não disponível (não está em Raspberry Pi)")
except Exception as e:
    print(f"✗ Erro: {e}")
PYEOF
    echo ""
}

show_dashboard() {
    echo -e "${YELLOW}[*] Dashboard dos Robôs${NC}\n"
    cat << 'EOF'
┌────────────────────────────────────────────────┐
│           STATUS DOS ROBÔS - RE-DINO           │
├────────────────────────────────────────────────┤
│                                                │
│ ROBÔ 1: SÍNTESE DE DNA                         │
│ ├─ Status: ⚪ SIMULADO (sem hardware)          │
│ ├─ Última síntese: Não executada               │
│ ├─ Genomas prontos: 0                          │
│ └─ Guia: GUIAS/GUIA_ROBO_SINTESE_DNA.md        │
│                                                │
│ ROBÔ 2: INJEÇÃO DE GENOMA                      │
│ ├─ Status: ⚪ SIMULADO (sem hardware)          │
│ ├─ Última injeção: Não executada               │
│ ├─ Embriões injetados: 0                       │
│ └─ Guia: GUIAS/GUIA_ROBO_INJECAO_GENOMA.md     │
│                                                │
│ SISTEMA GERAL                                  │
│ ├─ Temperatura: 22°C                           │
│ ├─ Status: ✓ OK                                │
│ ├─ Projeto: RE-DINO v3.0                       │
│ └─ Modo: Simulação                             │
│                                                │
└────────────────────────────────────────────────┘

EOF
}

# ==================== DOCUMENTAÇÃO ====================

show_docs_menu() {
    echo -e "${BLUE}════════ DOCUMENTAÇÃO ════════${NC}\n"
    echo -e "${GREEN}[1]${NC} 📖 Quick Start"
    echo -e "${GREEN}[2]${NC} 🧬 Processo de Transformação"
    echo -e "${GREEN}[3]${NC} 🥚 Como Obter Ovos"
    echo -e "${GREEN}[4]${NC} 🤖 Construir Robô de Síntese"
    echo -e "${GREEN}[5]${NC} 💉 Construir Robô de Injeção"
    echo -e "${GREEN}[6]${NC} 📋 Lista de Materiais"
    echo -e "${GREEN}[7]${NC} ⚙️  Integração Completa"
    echo -e "${RED}[0]${NC} ↩️  Voltar\n"
}

view_documentation() {
    while true; do
        show_docs_menu
        read -p "Escolha uma opção: " doc_choice
        
        case "$doc_choice" in
            1) less "$GUIAS_DIR/QUICKSTART.md" ;;
            2) less "$GUIAS_DIR/PROCESSO_TRANSFORMACAO_EMBRIAO.md" ;;
            3) less "$GUIAS_DIR/GUIA_OBTER_OVOS_EMBRIAO.md" ;;
            4) less "$GUIAS_DIR/GUIA_ROBO_SINTESE_DNA.md" ;;
            5) less "$GUIAS_DIR/GUIA_ROBO_INJECAO_GENOMA.md" ;;
            6) less "$GUIAS_DIR/LISTA_MATERIAIS_COMPLETA.md" ;;
            7) less "$GUIAS_DIR/GUIA_INTEGRACAO_ROBO_COMPLETO.md" ;;
            0) break ;;
            *) echo -e "${RED}[!] Opção inválida!${NC}" ;;
        esac
        echo ""
    done
}

# ==================== FERRAMENTAS ====================

show_file_explorer() {
    echo -e "${YELLOW}[*] Explorador de Arquivos${NC}\n"
    echo -e "Estrutura do projeto:\n"
    tree -L 2 "$PROJECT_DIR" 2>/dev/null || find "$PROJECT_DIR" -maxdepth 2 -type d | sed 's|[^/]*/| |g'
    echo ""
}

search_species() {
    echo -e "${YELLOW}[?] Digite o nome da espécie para buscar:${NC}"
    read -p "> " search_term
    
    cd "$PROJECT_DIR"
    python3 << PYEOF
import sys
sys.path.insert(0, 'CODIGO')
from dinosaur_database import DinosaurDatabase

db = DinosaurDatabase()
results = [k for k in db.dinosaurs.keys() if '$search_term'.lower() in k.lower()]

if results:
    print(f"\n✓ Encontrado {len(results)} resultado(s):\n")
    for i, species in enumerate(results, 1):
        data = db.dinosaurs[species]
        print(f"{i}. {species}")
        print(f"   Período: {data.get('period', 'Desconhecido')}")
        print(f"   Dieta: {data.get('diet', 'Desconhecido')}")
        print(f"   Tamanho: {data.get('size', 'Desconhecido')}\n")
else:
    print(f"\n✗ Nenhuma espécie encontrada com '{$search_term}'")
PYEOF
}

show_history() {
    echo -e "${YELLOW}[*] Histórico de Sínteses${NC}\n"
    if [ -f "$PROJECT_DIR/synthesis_history.log" ]; then
        cat "$PROJECT_DIR/synthesis_history.log"
    else
        echo -e "${YELLOW}[i] Nenhuma síntese executada ainda.${NC}"
    fi
    echo ""
}

cleanup_temp() {
    echo -e "${YELLOW}[*] Limpando arquivos temporários...${NC}"
    rm -rf "$PROJECT_DIR"/__pycache__ 2>/dev/null
    find "$PROJECT_DIR" -name "*.pyc" -delete 2>/dev/null
    find "$PROJECT_DIR" -name ".DS_Store" -delete 2>/dev/null
    echo -e "${GREEN}[✓] Limpeza completa!${NC}\n"
}

generate_report() {
    echo -e "${YELLOW}[*] Gerando relatório do projeto...${NC}\n"
    
    report_file="$PROJECT_DIR/PROJECT_REPORT_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
╔════════════════════════════════════════════════════════════════╗
║                  RELATÓRIO DO PROJETO RE-DINO                 ║
╚════════════════════════════════════════════════════════════════╝

Data: $(date)
Diretório: $PROJECT_DIR

1. ESTRUTURA DO PROJETO
   - Guias: $(ls "$GUIAS_DIR" | wc -l) arquivos
   - Código: $(ls "$CODIGO_DIR" | wc -l) scripts Python
   - Dados: $(ls "$DADOS_DIR" | wc -l) arquivos
   - Outputs: $(ls "$PROJECT_DIR/OUTPUT" 2>/dev/null | wc -l) resultados

2. DINOSSAUROS NO BANCO DE DADOS
EOF
    
    cd "$PROJECT_DIR"
    python3 << 'PYEOF' >> "$report_file"
import sys
sys.path.insert(0, 'CODIGO')
from dinosaur_database import DinosaurDatabase

db = DinosaurDatabase()
print(f"   - Total: {len(db.dinosaurs)} espécies")
print(f"\n3. PRINCIPAIS RECURSOS")
print(f"   - GUI: ✓ PyQt5 disponível")
print(f"   - Síntese: ✓ Streaming (3Gb em 47s)")
print(f"   - Robôs: ✓ Simulados (prontos para hardware)")
print(f"   - Documentação: ✓ Completa")
PYEOF
    
    echo -e "\n4. PRÓXIMOS PASSOS" >> "$report_file"
    echo -e "   1. Leia: GUIAS/QUICKSTART.md" >> "$report_file"
    echo -e "   2. Escolha: GUI ou Robôs" >> "$report_file"
    echo -e "   3. Execute: ./launcher.sh" >> "$report_file"
    
    echo -e "${GREEN}[✓] Relatório salvo: $report_file${NC}\n"
}

# ==================== MAIN ====================

main_menu() {
    while true; do
        print_header
        print_menu
        read -p "Escolha uma opção: " choice
        
        case "$choice" in
            1)
                echo -e "${YELLOW}[*] Iniciando GUI...${NC}\n"
                cd "$PROJECT_DIR"
                python3 "$CODIGO_DIR/gui_dino_synthesizer.py"
                ;;
            2)
                while true; do
                    print_header
                    print_submenu_synthesis
                    read -p "Escolha uma opção: " synth_choice
                    
                    case "$synth_choice" in
                        1) run_synthesis_quick ;;
                        2) run_synthesis_species ;;
                        3) run_synthesis_custom ;;
                        4) list_species ;;
                        0) break ;;
                        *) echo -e "${RED}[!] Opção inválida!${NC}" ;;
                    esac
                    read -p "Pressione ENTER para continuar..."
                done
                ;;
            3)
                while true; do
                    print_header
                    print_submenu_tests
                    read -p "Escolha uma opção: " test_choice
                    
                    case "$test_choice" in
                        1) run_test_quick ;;
                        2) run_test_validate ;;
                        3) run_test_pipeline ;;
                        4) run_test_integration ;;
                        5) check_dependencies ;;
                        0) break ;;
                        *) echo -e "${RED}[!] Opção inválida!${NC}" ;;
                    esac
                    read -p "Pressione ENTER para continuar..."
                done
                ;;
            4) view_documentation ;;
            5)
                while true; do
                    print_header
                    print_submenu_robots
                    read -p "Escolha uma opção: " robot_choice
                    
                    case "$robot_choice" in
                        1) show_robot_synthesis ;;
                        2) show_robot_injection ;;
                        3) test_gpio ;;
                        4) show_dashboard ;;
                        0) break ;;
                        *) echo -e "${RED}[!] Opção inválida!${NC}" ;;
                    esac
                    read -p "Pressione ENTER para continuar..."
                done
                ;;
            6)
                echo -e "${YELLOW}[*] Visualizando dados...${NC}\n"
                ls -lah "$DADOS_DIR"
                echo ""
                ;;
            7)
                while true; do
                    print_header
                    echo -e "${BLUE}════════ FERRAMENTAS ════════${NC}\n"
                    echo -e "${GREEN}[1]${NC} 📁 Explorador de Arquivos"
                    echo -e "${GREEN}[2]${NC} 🔍 Buscar Espécie"
                    echo -e "${GREEN}[3]${NC} 📈 Histórico"
                    echo -e "${GREEN}[4]${NC} 🧹 Limpar Temporários"
                    echo -e "${GREEN}[5]${NC} 📋 Gerar Relatório"
                    echo -e "${RED}[0]${NC} ↩️  Voltar\n"
                    read -p "Escolha uma opção: " tool_choice
                    
                    case "$tool_choice" in
                        1) show_file_explorer ;;
                        2) search_species ;;
                        3) show_history ;;
                        4) cleanup_temp ;;
                        5) generate_report ;;
                        0) break ;;
                        *) echo -e "${RED}[!] Opção inválida!${NC}" ;;
                    esac
                    read -p "Pressione ENTER para continuar..."
                done
                ;;
            0)
                echo -e "\n${CYAN}🦖 Até logo! Volte logo para criar dinossauros! 🦕${NC}\n"
                exit 0
                ;;
            *)
                echo -e "${RED}[!] Opção inválida!${NC}"
                read -p "Pressione ENTER para continuar..."
                ;;
        esac
    done
}

# ==================== INÍCIO ====================

main_menu
