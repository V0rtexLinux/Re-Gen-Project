#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
#  RE-GEN PROJECT — Menu Interativo
#  Pipeline de Ressurreição de Dinossauros
#  Compatível com: Linux · macOS · Git Bash (Windows)
# ═══════════════════════════════════════════════════════════════════════════════

set -uo pipefail

# ─── CORES E ESTILOS ──────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
  R='\033[0;31m'   # vermelho
  G='\033[0;32m'   # verde
  Y='\033[1;33m'   # amarelo
  B='\033[0;34m'   # azul
  C='\033[0;36m'   # ciano
  M='\033[0;35m'   # magenta
  W='\033[1;37m'   # branco brilhante
  DIM='\033[2m'
  BLD='\033[1m'
  RST='\033[0m'
else
  R='' G='' Y='' B='' C='' M='' W='' DIM='' BLD='' RST=''
fi

# ─── SÍMBOLOS UNICODE ─────────────────────────────────────────────────────────
# Definidos via printf/octal para evitar literal multi-byte no código fonte.
TICK=$(  printf '\342\234\223')   # U+2713  check mark        ✓
CROSS=$( printf '\342\234\227')   # U+2717  ballot x          ✗
RARR=$(  printf '\342\226\266')   # U+25B6  black right tri   ▶
RARR2=$( printf '\342\226\267')   # U+25B7  white right tri   ▷
WARN=$(  printf '\342\232\240')   # U+26A0  warning sign      ⚠
MDOT=$(  printf '\302\267')       # U+00B7  middle dot        ·
ARR=$(   printf '\342\206\222')   # U+2192  right arrow       →

# ─── LARGURA DO TERMINAL ──────────────────────────────────────────────────────
COLS=$(tput cols 2>/dev/null || echo 80)
[[ $COLS -lt 72 ]] && COLS=72
[[ $COLS -gt 100 ]] && COLS=100

# ─── ARQUIVO DE CONFIGURAÇÃO ──────────────────────────────────────────────────
# Fica na mesma pasta do script para ser portável com o projeto.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/.re_gen_config"
LOG_DIR="${SCRIPT_DIR}/re_gen_logs"
mkdir -p "$LOG_DIR"

# ─── VALORES PADRÃO DE CONFIGURAÇÃO ──────────────────────────────────────────
CFG_EMAIL="v0rtexlinux32@gmail.com"
CFG_API_KEY=""
CFG_DINOSAUR=""          # vazio = seleção automática
CFG_HOSPEDEIRO="Gallus gallus"
CFG_FOSSIL=""            # vazio = sem fóssil
CFG_OUTPUT="./re_gen_output"
CFG_CONFIANCA="0.60"
CFG_OLLAMA_MODELO="llama2"
CFG_HARDWARE="false"
CFG_SEM_IA="false"
PYTHON_BIN=""            # detectado automaticamente

# ─── CARREGA CONFIGURAÇÃO ─────────────────────────────────────────────────────
load_config() {
  [[ -f "$CONFIG_FILE" ]] && source "$CONFIG_FILE"
}

# ─── SALVA CONFIGURAÇÃO ───────────────────────────────────────────────────────
save_config() {
  cat > "$CONFIG_FILE" <<EOF
CFG_EMAIL="${CFG_EMAIL}"
CFG_API_KEY="${CFG_API_KEY}"
CFG_DINOSAUR="${CFG_DINOSAUR}"
CFG_HOSPEDEIRO="${CFG_HOSPEDEIRO}"
CFG_FOSSIL="${CFG_FOSSIL}"
CFG_OUTPUT="${CFG_OUTPUT}"
CFG_CONFIANCA="${CFG_CONFIANCA}"
CFG_OLLAMA_MODELO="${CFG_OLLAMA_MODELO}"
CFG_HARDWARE="${CFG_HARDWARE}"
CFG_SEM_IA="${CFG_SEM_IA}"
PYTHON_BIN="${PYTHON_BIN}"
EOF
}

# ─── DETECTA PYTHON ───────────────────────────────────────────────────────────
detect_python() {
  if [[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]]; then
    return 0
  fi
  for candidate in python3 python3.12 python3.11 python3.10 python; do
    if command -v "$candidate" &>/dev/null; then
      local ver
      ver=$("$candidate" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
      local major minor
      major=$(echo "$ver" | cut -d. -f1)
      minor=$(echo "$ver" | cut -d. -f2)
      if [[ "$major" -ge 3 && "$minor" -ge 9 ]]; then
        PYTHON_BIN=$(command -v "$candidate")
        return 0
      fi
    fi
  done
  return 1
}

# ─── FUNÇÕES DE DESENHO ───────────────────────────────────────────────────────
line_h() {  # linha horizontal cheia
  printf '%*s' "$COLS" '' | tr ' ' '─'
  echo
}

line_top()    { printf '╔'; printf '%*s' $(( COLS - 2 )) '' | tr ' ' '═'; printf '╗\n'; }
line_bottom() { printf '╚'; printf '%*s' $(( COLS - 2 )) '' | tr ' ' '═'; printf '╝\n'; }
line_mid()    { printf '╠'; printf '%*s' $(( COLS - 2 )) '' | tr ' ' '═'; printf '╣\n'; }
line_sep()    { printf '├'; printf '%*s' $(( COLS - 2 )) '' | tr ' ' '─'; printf '┤\n'; }
line_row()    {  # linha ║ texto ║, centraliza ou alinha à esquerda
  local txt="${1:-}"
  local pad=$(( COLS - 2 - ${#txt} ))
  printf '║ %s%*s║\n' "$txt" $(( pad - 1 )) ''
}
line_blank()  { line_row ""; }

clear_screen() { printf '\033[2J\033[H'; }

# ─── CABEÇALHO ────────────────────────────────────────────────────────────────
draw_header() {
  clear_screen
  echo -e "${C}"
  line_top
  line_row "$(printf '%*s' $(( (COLS - 2 - 30) / 2 )) '')██████╗ ███████╗      ██████╗ ███████╗███╗   ██╗"
  line_row "$(printf '%*s' $(( (COLS - 2 - 30) / 2 )) '')██╔══██╗██╔════╝     ██╔════╝ ██╔════╝████╗  ██║"
  line_row "$(printf '%*s' $(( (COLS - 2 - 30) / 2 )) '')██████╔╝█████╗  █████╗██║  ███╗█████╗  ██╔██╗ ██║"
  line_row "$(printf '%*s' $(( (COLS - 2 - 30) / 2 )) '')██╔══██╗██╔══╝  ╚════╝██║   ██║██╔══╝  ██║╚██╗██║"
  line_row "$(printf '%*s' $(( (COLS - 2 - 30) / 2 )) '')██║  ██║███████╗     ╚██████╔╝███████╗██║ ╚████║"
  line_row "$(printf '%*s' $(( (COLS - 2 - 30) / 2 )) '')╚═╝  ╚═╝╚══════╝      ╚═════╝ ╚══════╝╚═╝  ╚═══╝"
  line_blank
  line_mid
  local titulo="PIPELINE DE RESSURREIÇÃO DE DINOSSAUROS"
  local pad=$(( (COLS - 2 - ${#titulo}) / 2 ))
  line_row "$(printf '%*s%s' $pad '' "$titulo")"
  local sub="8 Fases · EPB · NCBI · CRISPR · Síntese · Embriologia · IA"
  pad=$(( (COLS - 2 - ${#sub}) / 2 ))
  line_row "$(printf '%*s%s' $pad '' "$sub")"
  line_mid
  # Status de configuração
  local email_str="${CFG_EMAIL:-${R}não configurado${RST}${C}}"
  local dino_str="${CFG_DINOSAUR:-${DIM}automático${RST}${C}}"
  local py_str; py_str="${PYTHON_BIN:-${Y}não detectado${RST}${C}}"
  py_str=$(basename "$py_str" 2>/dev/null || echo "${py_str}")
  line_row " E-mail  : ${email_str}  │  Dinossauro : ${dino_str}  │  Python : ${py_str}"
  line_row " Saída   : ${CFG_OUTPUT}  │  Confiança  : ${CFG_CONFIANCA}  │  IA : ${CFG_OLLAMA_MODELO}"
  line_bottom
  echo -e "${RST}"
}

# ─── BLOCO DE SEÇÃO ───────────────────────────────────────────────────────────
section() {  # section "TÍTULO" cor
  local titulo="${1}"; local cor="${2:-$B}"
  echo -e "${cor}"
  printf '  ┌─ %s ' "$titulo"
  local len=$(( COLS - 7 - ${#titulo} ))
  printf '%*s' "$len" '' | tr ' ' '─'
  printf '┐\n'
  echo -e "${RST}"
}
section_end() {
  echo -e "${B}"
  printf '  └'
  printf '%*s' $(( COLS - 4 )) '' | tr ' ' '─'
  printf '┘\n'
  echo -e "${RST}"
}
item() {  # item num label desc
  local num="${1}" label="${2}" desc="${3:-}"
  printf "  │  ${W}%-3s${RST}  ${BLD}%-38s${RST}  ${DIM}%s${RST}\n" "$num" "$label" "$desc"
}
item_warn() {  # item com aviso de dependência
  local num="${1}" label="${2}" warn="${3:-}"
  printf "  │  ${Y}%-3s${RST}  ${BLD}%-38s${RST}  ${Y}⚠ %s${RST}\n" "$num" "$label" "$warn"
}

# ─── MENU PRINCIPAL ───────────────────────────────────────────────────────────
draw_menu() {
  section "PIPELINE COMPLETO" "$G"
  item  "1"  "${RARR}  Pipeline Completo  (Fases 0-8)"  "selecao ${ARR} genoma ${ARR} CRISPR ${ARR} embriao ${ARR} IA"
  section_end

  section "EXECUÇÃO POR FASE (inicia em Fase 0)" "$C"
  item  "2"  "Fase 0  · Seleção Paleontológica"    "escolhe espécie; banco de 500+ dinossauros"
  item  "3"  "Fases 0–1 · + Mapeamento NCBI"       "filogenética + busca de referências NCBI"
  item  "4"  "Fases 0–2 · + Extração de Fóssil"    "fragmento FASTA real (requer --fossil)"
  item  "5"  "Fases 0–3 · + Reconstrução Genômica" "EPB Needleman-Wunsch + escala 2–3 Gb"
  item  "6"  "Fases 0–4 · + Pacote CRISPR"         "guias gRNA; SNPs ancestral vs hospedeiro"
  item  "7"  "Fases 0–5 · + Síntese Física de DNA" "protocolo de síntese oligo a oligo"
  item  "8"  "Fases 0–6 · + Injeção no Embrião"    "robô XYZ + seringa; fallback manual"
  item  "9"  "Fases 0–7 · + Incubação Monitorada"  "DHT22 + DS18B20 + controle Arduino"
  item  "10" "Fases 0–8 · + Relatório Final com IA" "laudo completo via Ollama LLM"
  section_end

  section "RANGE PERSONALIZADO" "$M"
  item  "11" "▷  Fases N–M (intervalo livre)"      "define início e fim manualmente"
  section_end

  section "FERRAMENTAS STANDALONE" "$Y"
  item  "12" "Construtor de Genoma 2–3 Gb"          "genome_scale_builder.py direto"
  item  "13" "Listar Espécies Disponíveis"           "banco de 500+ espécies catalogadas"
  item  "14" "Mapa de Arquitetura do Projeto"        "diagrama completo dos módulos"
  item  "15" "Ver Logs da Última Execução"           "tail -n 80 do log mais recente"
  item  "16" "Verificar Dependências Python"         "biopython, requests, ollama, RPi..."
  section_end

  section "CONFIGURAÇÃO" "$B"
  item  "17" "Configurar Parâmetros"                "e-mail, espécie, saída, hardware..."
  item  "18" "Redefinir Configuração Padrão"        "apaga .re_gen_config"
  section_end

  echo -e "  ${DIM}0  Sair${RST}"
  echo
}

# ─── EXIBE O MENU E LÊ OPÇÃO ─────────────────────────────────────────────────
prompt_choice() {
  echo -ne "${W}  Opção: ${RST}"
  read -r CHOICE
}

# ─── VALIDA EMAIL ─────────────────────────────────────────────────────────────
check_email() {
  if [[ -z "$CFG_EMAIL" ]]; then
    echo -e "\n${R}  ✗  E-mail NCBI não configurado. Configure primeiro (opção 17).${RST}\n"
    return 1
  fi
  return 0
}

# ─── MONTA FLAGS GLOBAIS ──────────────────────────────────────────────────────
build_flags() {
  local flags=(
    "--email"    "$CFG_EMAIL"
    "--output"   "$CFG_OUTPUT"
    "--confianca" "$CFG_CONFIANCA"
    "--hospedeiro" "$CFG_HOSPEDEIRO"
    "--ollama-modelo" "$CFG_OLLAMA_MODELO"
  )
  [[ -n "$CFG_API_KEY"  ]] && flags+=("--api-key"   "$CFG_API_KEY")
  [[ -n "$CFG_DINOSAUR" ]] && flags+=("--dinosaur"  "$CFG_DINOSAUR")
  [[ -n "$CFG_FOSSIL"   ]] && flags+=("--fossil"    "$CFG_FOSSIL")
  [[ "$CFG_HARDWARE" == "true" ]] && flags+=("--hardware")
  [[ "$CFG_SEM_IA"   == "true" ]] && flags+=("--sem-ia")
  echo "${flags[@]}"
}

# ─── EXECUTA PIPELINE ─────────────────────────────────────────────────────────
run_pipeline() {
  local fase_inicio="${1:-0}"
  local fase_fim="${2:-8}"

  check_email || return

  local ts; ts=$(date +"%Y%m%d_%H%M%S")
  local logfile="${LOG_DIR}/pipeline_f${fase_inicio}-${fase_fim}_${ts}.log"

  local -a flags
  read -ra flags <<< "$(build_flags)"
  flags+=("--fase-inicio" "$fase_inicio" "--fase-fim" "$fase_fim")

  echo
  echo -e "${G}  ▶  Executando Fases ${fase_inicio}–${fase_fim}${RST}"
  echo -e "${DIM}  Comando: ${PYTHON_BIN} re_gen_unified_architecture.py ${flags[*]}${RST}"
  echo -e "${DIM}  Log: ${logfile}${RST}"
  echo
  echo -e "${Y}$(line_h)${RST}"

  # Executa e faz tee para o log
  if "$PYTHON_BIN" "${SCRIPT_DIR}/re_gen_unified_architecture.py" "${flags[@]}" \
       2>&1 | tee "$logfile"; then
    echo
    echo -e "${G}  ✓  Execução concluída.${RST}"
  else
    echo
    echo -e "${R}  ✗  Execução encerrada com erro (código $?).${RST}"
  fi

  echo -e "${Y}$(line_h)${RST}"
  echo
  echo -ne "  Ver log completo? [s/N] "
  read -r resp
  if [[ "$resp" =~ ^[sS]$ ]]; then
    less -R "$logfile"
  fi
}

# ─── RANGE LIVRE ─────────────────────────────────────────────────────────────
run_range() {
  echo
  echo -e "${M}  EXECUÇÃO DE RANGE PERSONALIZADO${RST}"
  echo -e "  Fases disponíveis:"
  echo -e "    0  Seleção Paleontológica"
  echo -e "    1  Mapeamento Filogenético + NCBI"
  echo -e "    2  Extração de DNA Fóssil"
  echo -e "    3  Reconstrução Genômica (EPB + 2–3 Gb)"
  echo -e "    4  Pacote CRISPR"
  echo -e "    5  Síntese Física de DNA"
  echo -e "    6  Injeção no Embrião"
  echo -e "    7  Incubação Monitorada"
  echo -e "    8  Relatório Final com IA"
  echo
  echo -ne "  Fase inicial (0–8): "
  read -r fi
  echo -ne "  Fase final   (${fi}–8): "
  read -r ff
  if ! [[ "$fi" =~ ^[0-8]$ && "$ff" =~ ^[0-8]$ && $fi -le $ff ]]; then
    echo -e "${R}  ✗  Intervalo inválido.${RST}"
    return
  fi
  run_pipeline "$fi" "$ff"
}

# ─── GENOME SCALE BUILDER STANDALONE ─────────────────────────────────────────
run_genome_builder() {
  check_email || return

  local ts; ts=$(date +"%Y%m%d_%H%M%S")
  local logfile="${LOG_DIR}/genome_scale_${ts}.log"

  echo
  echo -e "${Y}  CONSTRUTOR DE GENOMA 2–3 Gb (standalone)${RST}"
  echo

  echo -ne "  Dinossauro (Enter = '${CFG_DINOSAUR:-Dinosauria sp.'): "
  read -r dino_input
  local dino="${dino_input:-${CFG_DINOSAUR:-Dinosauria sp.}}"

  echo -ne "  Tamanho alvo em Gb (2.0–3.0, Enter = 2.1): "
  read -r gb_input
  local gb="${gb_input:-2.1}"

  echo -ne "  Diretório de saída (Enter = ./genoma_escala_completa): "
  read -r out_input
  local out="${out_input:-./genoma_escala_completa}"

  echo -ne "  Cromossomos específicos (ex: chr1,chr2 — Enter = todos): "
  read -r chr_input

  local -a args=(
    "--email"   "$CFG_EMAIL"
    "--dinosaur" "$dino"
    "--target-gb" "$gb"
    "--output"  "$out"
  )
  [[ -n "$CFG_API_KEY"  ]] && args+=("--api-key" "$CFG_API_KEY")
  [[ -n "$chr_input"    ]] && args+=("--cromossomos" "$chr_input")

  echo
  echo -e "${DIM}  Comando: ${PYTHON_BIN} genome_scale_builder.py ${args[*]}${RST}"
  echo -e "${DIM}  Log: ${logfile}${RST}"
  echo
  echo -e "${Y}$(line_h)${RST}"

  if "$PYTHON_BIN" "${SCRIPT_DIR}/genome_scale_builder.py" "${args[@]}" \
       2>&1 | tee "$logfile"; then
    echo -e "${G}  ✓  Genoma construído com sucesso.${RST}"
  else
    echo -e "${R}  ✗  Erro na construção do genoma.${RST}"
  fi

  echo -e "${Y}$(line_h)${RST}"
  echo -ne "  Ver log completo? [s/N] "
  read -r resp
  [[ "$resp" =~ ^[sS]$ ]] && less -R "$logfile"
}

# ─── LISTAR ESPÉCIES ─────────────────────────────────────────────────────────
run_lista() {
  check_email || return
  echo
  echo -e "${Y}$(line_h)${RST}"
  "$PYTHON_BIN" "${SCRIPT_DIR}/re_gen_unified_architecture.py" \
    --email "$CFG_EMAIL" --lista 2>&1 | less -R
}

# ─── MAPA DE ARQUITETURA ──────────────────────────────────────────────────────
run_arquitetura() {
  echo
  echo -e "${Y}$(line_h)${RST}"
  "$PYTHON_BIN" "${SCRIPT_DIR}/re_gen_unified_architecture.py" \
    --email "noop@noop.com" --arquitetura 2>&1 | less -R
}

# ─── VER LOGS ─────────────────────────────────────────────────────────────────
run_logs() {
  local latest
  latest=$(ls -t "${LOG_DIR}"/*.log 2>/dev/null | head -1)
  if [[ -z "$latest" ]]; then
    echo -e "\n${Y}  Nenhum log encontrado em ${LOG_DIR}/${RST}\n"
    return
  fi
  echo
  echo -e "${DIM}  Logs disponíveis em ${LOG_DIR}/:${RST}"
  ls -lt --color=never "${LOG_DIR}"/*.log 2>/dev/null | head -10 | \
    awk '{printf "  %-40s %s %s %s\n", $NF, $6, $7, $8}'
  echo
  echo -ne "  Abrir log mais recente? [S/n] "
  read -r resp
  if [[ ! "$resp" =~ ^[nN]$ ]]; then
    less -R "$latest"
  fi
}

# ─── VERIFICAR DEPENDÊNCIAS ──────────────────────────────────────────────────
run_check_deps() {
  echo
  echo -e "${C}  VERIFICAÇÃO DE DEPENDÊNCIAS${RST}"
  echo -e "${Y}$(line_h)${RST}"
  echo

  # Python
  if [[ -n "$PYTHON_BIN" ]]; then
    local pyver; pyver=$("$PYTHON_BIN" --version 2>&1)
    echo -e "  ${G}✓${RST}  Python : ${pyver} (${PYTHON_BIN})"
  else
    echo -e "  ${R}✗${RST}  Python : não encontrado (Python ≥ 3.9 necessário)"
  fi

  echo

  # Pacotes Python
  local pkgs=("Bio" "requests" "ollama" "numpy" "scipy")
  for pkg in "${pkgs[@]}"; do
    local status
    if "$PYTHON_BIN" -c "import ${pkg}" &>/dev/null 2>&1; then
      local ver; ver=$("$PYTHON_BIN" -c "import ${pkg}; print(getattr(${pkg},'__version__','?'))" 2>/dev/null || echo "?")
      status="${G}✓${RST}  ${pkg} ${DIM}(${ver})${RST}"
    else
      status="${R}✗${RST}  ${pkg} ${Y}— não instalado${RST}"
    fi
    echo -e "  ${status}"
  done

  # RPi.GPIO (mock é injetado automaticamente se não estiver)
  echo
  if "$PYTHON_BIN" -c "import RPi.GPIO" &>/dev/null 2>&1; then
    echo -e "  ${G}✓${RST}  RPi.GPIO : instalado (hardware real disponível)"
  else
    echo -e "  ${Y}~${RST}  RPi.GPIO : não instalado ${DIM}(mock injetado automaticamente — OK para PC/Mac)${RST}"
  fi

  # Ollama
  echo
  if command -v ollama &>/dev/null; then
    local olv; olv=$(ollama --version 2>&1 | head -1)
    echo -e "  ${G}✓${RST}  ollama CLI : ${olv}"
  else
    echo -e "  ${Y}~${RST}  ollama CLI : não encontrado ${DIM}(Fase 8 usará fallback sem laudo IA)${RST}"
  fi

  echo
  echo -e "${Y}$(line_h)${RST}"
  echo
  echo -ne "  Instalar pacotes faltantes com pip? [s/N] "
  read -r resp
  if [[ "$resp" =~ ^[sS]$ ]]; then
    echo
    "$PYTHON_BIN" -m pip install biopython requests ollama numpy scipy 2>&1
    echo -e "\n${G}  ✓  Instalação concluída.${RST}\n"
  fi
}

# ─── MENU DE CONFIGURAÇÃO ─────────────────────────────────────────────────────
run_config() {
  while true; do
    draw_header
    echo -e "${B}  CONFIGURAÇÃO DE PARÂMETROS${RST}"
    echo
    echo -e "  ${W}1${RST}  E-mail NCBI      : ${CFG_EMAIL:-${R}(obrigatório)${RST}}"
    echo -e "  ${W}2${RST}  API Key NCBI     : ${CFG_API_KEY:-${DIM}(opcional — aumenta rate limit)${RST}}"
    echo -e "  ${W}3${RST}  Dinossauro alvo  : ${CFG_DINOSAUR:-${DIM}(automático)${RST}}"
    echo -e "  ${W}4${RST}  Hospedeiro CRISPR: ${CFG_HOSPEDEIRO}"
    echo -e "  ${W}5${RST}  Arquivo de fóssil: ${CFG_FOSSIL:-${DIM}(nenhum)${RST}}"
    echo -e "  ${W}6${RST}  Diretório saída  : ${CFG_OUTPUT}"
    echo -e "  ${W}7${RST}  Confiança mínima : ${CFG_CONFIANCA}"
    echo -e "  ${W}8${RST}  Modelo Ollama    : ${CFG_OLLAMA_MODELO}"
    echo -e "  ${W}9${RST}  Hardware físico  : ${CFG_HARDWARE}"
    echo -e "  ${W}10${RST} Pular laudo IA   : ${CFG_SEM_IA}"
    echo -e "  ${W}11${RST} Python binário   : ${PYTHON_BIN:-${R}não detectado${RST}}"
    echo
    echo -e "  ${W}s${RST}  Salvar e voltar"
    echo -e "  ${W}0${RST}  Voltar sem salvar"
    echo
    echo -ne "  Opção: "
    read -r opt

    case "$opt" in
      1)  echo -ne "  E-mail NCBI: "; read -r CFG_EMAIL ;;
      2)  echo -ne "  API Key (Enter = limpar): "; read -r CFG_API_KEY ;;
      3)  echo -ne "  Nome científico (Enter = automático): "; read -r CFG_DINOSAUR ;;
      4)  echo -ne "  Espécie hospedeira [${CFG_HOSPEDEIRO}]: "; read -r tmp
          [[ -n "$tmp" ]] && CFG_HOSPEDEIRO="$tmp" ;;
      5)  echo -ne "  Caminho do arquivo FASTA (Enter = nenhum): "; read -r CFG_FOSSIL ;;
      6)  echo -ne "  Diretório de saída [${CFG_OUTPUT}]: "; read -r tmp
          [[ -n "$tmp" ]] && CFG_OUTPUT="$tmp" ;;
      7)  echo -ne "  Confiança mínima 0.0–1.0 [${CFG_CONFIANCA}]: "; read -r tmp
          [[ -n "$tmp" ]] && CFG_CONFIANCA="$tmp" ;;
      8)  echo -ne "  Modelo Ollama [${CFG_OLLAMA_MODELO}]: "; read -r tmp
          [[ -n "$tmp" ]] && CFG_OLLAMA_MODELO="$tmp" ;;
      9)  echo -ne "  Hardware físico (true/false) [${CFG_HARDWARE}]: "; read -r tmp
          [[ "$tmp" == "true" || "$tmp" == "false" ]] && CFG_HARDWARE="$tmp" ;;
      10) echo -ne "  Pular laudo IA (true/false) [${CFG_SEM_IA}]: "; read -r tmp
          [[ "$tmp" == "true" || "$tmp" == "false" ]] && CFG_SEM_IA="$tmp" ;;
      11) echo -ne "  Caminho do Python (Enter = detectar): "; read -r tmp
          if [[ -n "$tmp" ]]; then
            PYTHON_BIN="$tmp"
          else
            PYTHON_BIN=""
            detect_python && echo -e "  ${G}✓ Detectado: ${PYTHON_BIN}${RST}" || \
              echo -e "  ${R}✗ Python ≥ 3.9 não encontrado.${RST}"
          fi ;;
      s|S) save_config
           echo -e "\n  ${G}✓  Configuração salva em ${CONFIG_FILE}${RST}\n"
           sleep 1
           return ;;
      0)  return ;;
    esac
  done
}

# ─── REDEFINIR CONFIGURAÇÃO ───────────────────────────────────────────────────
run_reset() {
  echo
  echo -ne "${R}  Apagar configuração e redefinir padrões? [s/N]: ${RST}"
  read -r resp
  if [[ "$resp" =~ ^[sS]$ ]]; then
    rm -f "$CONFIG_FILE"
    CFG_EMAIL=""; CFG_API_KEY=""; CFG_DINOSAUR=""; CFG_HOSPEDEIRO="Gallus gallus"
    CFG_FOSSIL=""; CFG_OUTPUT="./re_gen_output"; CFG_CONFIANCA="0.60"
    CFG_OLLAMA_MODELO="llama2"; CFG_HARDWARE="false"; CFG_SEM_IA="false"
    PYTHON_BIN=""
    detect_python
    echo -e "  ${G}✓  Configuração redefinida.${RST}\n"
    sleep 1
  fi
}

# ─── PAUSA ────────────────────────────────────────────────────────────────────
pause() {
  echo
  echo -ne "  ${DIM}Pressione Enter para continuar...${RST}"
  read -r
}

# ─── VERIFICAÇÕES INICIAIS ────────────────────────────────────────────────────
initial_checks() {
  load_config

  if ! detect_python; then
    echo -e "\n${R}  AVISO: Python ≥ 3.9 não encontrado no PATH.${RST}"
    echo -e "  Configure o caminho manualmente em Configuração (opção 17).\n"
  fi

  # Avisa se não configurado
  if [[ -z "$CFG_EMAIL" ]]; then
    FIRST_RUN=true
  else
    FIRST_RUN=false
  fi
}

# ─── PRIMEIRA EXECUÇÃO ────────────────────────────────────────────────────────
first_run_wizard() {
  clear_screen
  echo
  echo -e "${G}  Bem-vindo ao Re-Gen Project!${RST}"
  echo -e "  Configuração inicial necessária.\n"
  echo -ne "  E-mail para NCBI Entrez API (obrigatório): "
  read -r CFG_EMAIL
  echo -ne "  API Key NCBI (opcional, Enter = pular): "
  read -r CFG_API_KEY
  echo -ne "  Dinossauro alvo (Enter = seleção automática): "
  read -r CFG_DINOSAUR
  echo -ne "  Diretório de saída [${CFG_OUTPUT}]: "
  read -r tmp; [[ -n "$tmp" ]] && CFG_OUTPUT="$tmp"
  save_config
  echo -e "\n  ${G}✓  Configuração salva.${RST}\n"
  sleep 1
}

# ─── LOOP PRINCIPAL ───────────────────────────────────────────────────────────
main() {
  initial_checks

  if [[ "${FIRST_RUN}" == "true" ]]; then
    first_run_wizard
  fi

  while true; do
    draw_header
    draw_menu

    prompt_choice

    case "${CHOICE:-}" in

      # ── Pipeline completo
      1) run_pipeline 0 8 ;;

      # ── Fases individuais (sempre a partir de 0)
      2)  run_pipeline 0 0 ;;
      3)  run_pipeline 0 1 ;;
      4)  run_pipeline 0 2 ;;
      5)  run_pipeline 0 3 ;;
      6)  run_pipeline 0 4 ;;
      7)  run_pipeline 0 5 ;;
      8)  run_pipeline 0 6 ;;
      9)  run_pipeline 0 7 ;;
      10) run_pipeline 0 8 ;;

      # ── Range livre
      11) run_range ;;

      # ── Ferramentas standalone
      12) run_genome_builder ;;
      13) run_lista ;;
      14) run_arquitetura ;;
      15) run_logs ;;
      16) run_check_deps; pause ;;

      # ── Configuração
      17) run_config ;;
      18) run_reset ;;

      # ── Sair
      0|q|Q|exit|sair)
        echo -e "\n${DIM}  Re-Gen Project — encerrado.${RST}\n"
        exit 0
        ;;

      *)
        echo -e "\n${R}  Opção inválida: '${CHOICE}'.${RST}"
        sleep 1
        ;;
    esac
  done
}

# ─── MODO NÃO-INTERATIVO (argumentos de linha de comando) ────────────────────
if [[ $# -gt 0 ]]; then
  case "${1:-}" in
    --pipeline)   initial_checks; run_pipeline 0 8 ;;
    --fase)       initial_checks; run_pipeline "${2:-0}" "${3:-8}" ;;
    --genoma)     initial_checks; run_genome_builder ;;
    --lista)      initial_checks; run_lista ;;
    --arquitetura) initial_checks; run_arquitetura ;;
    --check-deps) initial_checks; run_check_deps ;;
    --help|-h)
      echo "Uso: $0 [opção]"
      echo "  (sem args)           Abre o menu interativo"
      echo "  --pipeline           Roda pipeline completo (fases 0–8)"
      echo "  --fase N M           Roda fases N até M"
      echo "  --genoma             Construtor de genoma standalone"
      echo "  --lista              Lista espécies disponíveis"
      echo "  --arquitetura        Exibe mapa de arquitetura"
      echo "  --check-deps         Verifica dependências"
      exit 0
      ;;
    *)
      echo "Argumento desconhecido: ${1}. Use --help para ajuda."
      exit 1
      ;;
  esac
  exit $?
fi

# ─── ENTRADA PADRÃO — MENU INTERATIVO ─────────────────────────────────────────
main
