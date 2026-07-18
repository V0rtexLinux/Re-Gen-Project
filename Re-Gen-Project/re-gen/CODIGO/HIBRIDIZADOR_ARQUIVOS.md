# 🧬 Hibridizador DNA 3000 - Arquivos de Código

## 📁 Estrutura de Arquivos

```
CODIGO/
├── hibridizador_core.py              ⭐ MOTOR PRINCIPAL
├── hibridizador_hardware.py          ⚙️ SIMULADOR DE HARDWARE
├── hibridizador_gui.py               🖥️ INTERFACE GRÁFICA PyQt5
├── run_hibridizador.py               🚀 SCRIPT DE LAUNCHER
├── README_HIBRIDIZADOR.md            📖 DOCUMENTAÇÃO COMPLETA
└── HIBRIDIZADOR_ARQUIVOS.md          📋 ESTE ARQUIVO
```

---

## 📄 DESCRIÇÃO DETALHADA

### 1️⃣ **hibridizador_core.py** (⭐ Core)
**Tamanho:** ~800 linhas
**Dependências:** `numpy`, `scipy`

**O que faz:**
- Motor principal do hibridizador
- Controla toda a lógica de reação
- Modelagem matemática via ODEs (scipy.odeint)
- Threads de monitoramento contínuo
- Gerencia estados (DESLIGADO → PRONTO → EM_REAÇÃO → etc)

**Principais classes:**
```python
class Hibridizador:              # Controlador principal
    - ligar()
    - desligar()
    - iniciar_reacao()
    - pausar_reacao()
    - parar_reacao()
    - resetar_sistema()
    - obter_status()
    - exportar_dados_reacao()

class ModeloReacao:              # Modelagem matemática
    - simular_reacao()           # Usa scipy.odeint

@dataclass
class ParametroReacao:           # Config de parâmetros
class SensorLeitura:             # Leitura de sensores
class HibridizadorState:         # Estados possíveis
```

**Algoritmos:**
- Cinética de segunda ordem (DNA associação)
- Ajuste da taxa com temperatura (Arrhenius)
- Integração numérica (ODE solver)
- Threads de monitoramento de sensores

---

### 2️⃣ **hibridizador_hardware.py** (⚙️ Hardware)
**Tamanho:** ~700 linhas
**Dependências:** `numpy`

**O que faz:**
- Simula sensores e atuadores físicos
- Representa 4 sensores (T, pH, Cond, Turb)
- Controla 5 componentes principais (bomba, aquecedor, resfriador, LED, válvulas)
- Interface com 16 botões RGB (4x4)
- 2 encoders rotativos + 2 potenciômetros

**Principais classes:**
```python
class SensorTemperatura:         # DS18B20 (±0.5°C)
class SensorPH:                  # Digital (±0.1 pH)
class SensorCondutividade:       # 0-20 mS/cm
class SensorTurbidez:            # Óptico (0-1000 NTU)

class BombaPeristaltica:         # 1-50 mL/min
class Aquecedor:                 # 20-45°C, 500W
class Resfriador:                # Ventilador
class LEDRGB:                    # 10W, 8 cores
class ValvulaSolenoide:          # 5 válvulas

class BotaoRGB:                  # LED RGB integrado
class EncoderRotativo:           # Controle contínuo
class CorLED(Enum):              # 8 cores disponíveis

class ControladorHardware:       # Interface unificada
    - iniciar()
    - parar()
    - obter_status_completo()
    - ligar_aquecedor()
    - set_velocidade_bomba()
    - set_cor_led()
    - abrir_valvula() / fechar_valvula()
    - pressionar_botao()
```

**Simulação:**
- Thread de simulação ambiental
- Aquecimento gradual (~1°C/min)
- Resfriamento natural
- Ruído realista em leituras
- Precisão configurável por sensor

---

### 3️⃣ **hibridizador_gui.py** (🖥️ GUI)
**Tamanho:** ~900 linhas
**Dependências:** `PyQt5` (QtWidgets, QtChart, QtCore, QtGui)

**O que faz:**
- Interface gráfica completa
- Simula 2 monitores LCD de 10.1"
- Painel de controle com 16 botões RGB
- Gráficos em tempo real
- Status da câmara central
- Display LCD para valores

**Componentes da UI:**
```
┌─────────────────────────────────────────────┐
│        HIBRIDIZADOR DNA 3000                │
├──────────────┬─────────────┬────────────────┤
│ MONITOR LCD  │  CÂMARA DE  │ MONITOR LCD    │
│  ESQUERDO    │  REAÇÃO +   │   DIREITO      │
│              │     LED     │                │
│ • Temp       │   CENTRAL   │ • Gráfico DNA  │
│ • pH         │             │ • Análise      │
│ • Cond       │             │ • Dados        │
│ • Progresso  │             │                │
└──────────────┴─────────────┴────────────────┘
├──────────────────────────────────────────────┤
│          PAINEL DE CONTROLE (4x4)            │
├──────────────────────────────────────────────┤
│  [BOTÃO] [BOTÃO] [BOTÃO] [BOTÃO]            │
│  [BOTÃO] [BOTÃO] [BOTÃO] [BOTÃO]            │
│  [BOTÃO] [BOTÃO] [BOTÃO] [BOTÃO]            │
│  [BOTÃO] [BOTÃO] [BOTÃO] [BOTÃO]            │
└──────────────────────────────────────────────┘
```

**Principais classes:**
```python
class MonitorLCDEsquerdo(QWidget):   # Monitor de parâmetros
    - Temperatura (LCD)
    - pH (LCD)
    - Condutividade (LCD)
    - Progress Bar
    - Tempo decorrido

class MonitorLCDDireito(QWidget):    # Monitor de análise
    - Gráfico de concentrações
    - DNA-A livre
    - DNA-B livre
    - Complexo AB
    - DNA Hibridizado

class PainelControles(QWidget):      # 16 botões RGB (4x4)
    - Códigos de cores
    - Callbacks configuráveis

class JanelaHibridizador(QMainWindow): # Janela principal
    - Integra todos os componentes
    - Timer de atualização (500ms)
    - Interação com hibridizador_core
    - Interação com hibridizador_hardware
```

**Cores utilizadas:**
```
Monitor Esquerdo:  Verde (#00FF00) - Estilo terminal
Monitor Direito:   Azul (#0080FF) - Estilo análise
Câmara:            Múltiplas cores (status)
Botões:            Cores RGB customizadas
```

---

### 4️⃣ **run_hibridizador.py** (🚀 Launcher)
**Tamanho:** ~400 linhas
**Dependências:** `argparse`, módulos do hibridizador

**O que faz:**
- Script de entrada única
- 4 modos de operação
- Argumentos via linha de comando
- CLI amigável

**Modos disponíveis:**
```bash
1. GUI (padrão)
   python3 run_hibridizador.py --gui
   
2. TERMINAL (sem GUI)
   python3 run_hibridizador.py --terminal -t 37.5 -d 4 -v 75
   
3. DIAGNÓSTICO
   python3 run_hibridizador.py --diagnostico
   
4. CALIBRAÇÃO
   python3 run_hibridizador.py --calibracao
```

**Parâmetros (terminal):**
```
-t, --temperatura  Temperatura alvo em °C (padrão: 37.5)
-d, --duracao      Duração em minutos (padrão: 4)
-v, --velocidade   Velocidade bomba em % (padrão: 75)
```

**Funções principais:**
```python
def modo_terminal(args)          # Execução sem GUI
def modo_diagnostico()           # Teste de hardware
def modo_calibracao()            # Calibrar sensores
def modo_gui()                   # Executar interface gráfica
def main()                       # Parser de argumentos
```

---

## 🔄 FLUXO DE DADOS

```
┌─────────────────────────────────────────────┐
│      ENTRADA DO USUÁRIO                     │
│  (GUI / CLI / Hardware físico)              │
└────────────────────┬────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  ControladorHardware       │
        │  (hibridizador_hardware.py)│
        │  - Sensores simulados      │
        │  - Atuadores simulados     │
        └────────────────┬───────────┘
                         │
                         ▼
        ┌────────────────────────────┐
        │  Hibridizador              │
        │  (hibridizador_core.py)    │
        │  - Lógica de controle      │
        │  - Modelagem de reação     │
        │  - Gerenciamento de threads│
        └────────────────┬───────────┘
                         │
        ┌────────────────┴───────────┐
        ▼                            ▼
   ┌─────────────┐          ┌────────────────┐
   │ Dados de    │          │ Interface      │
   │ Reação      │          │ Gráfica        │
   │ (JSON)      │          │ (PyQt5)        │
   └─────────────┘          └────────────────┘
        │                            │
        ▼                            ▼
   [ARQUIVO]                  [TELA DO USUÁRIO]
```

---

## 📊 ESTATÍSTICAS

```
Linhas de código:
  hibridizador_core.py:     ~800
  hibridizador_hardware.py: ~700
  hibridizador_gui.py:      ~900
  run_hibridizador.py:      ~400
  ─────────────────────────────
  TOTAL:                   ~2,800 linhas

Complexidade:
  Classes:     ~30+
  Métodos:     ~120+
  Threads:     3 (monitoramento, reação, GUI)
  
Dependências externas:
  PyQt5
  numpy
  scipy
  
Padrões de design:
  MVC (Model-View-Controller)
  Observer (sinais PyQt5)
  Strategy (diferentes modos)
  Singleton (ControladorHardware)
```

---

## 🎯 CASOS DE USO

### Caso 1: Pesquisador rápido
```bash
# Apenas quer resultados, sem detalhes
python3 run_hibridizador.py --terminal -t 37.5 -d 4 -v 75
```

### Caso 2: Monitoramento completo
```bash
# Quer visualizar tudo em tempo real
python3 run_hibridizador.py --gui
```

### Caso 3: Troubleshooting
```bash
# Hardware com problema?
python3 run_hibridizador.py --diagnostico
```

### Caso 4: Setup novo
```bash
# Primeira vez calibrando sensores
python3 run_hibridizador.py --calibracao
```

### Caso 5: Integração com outro software
```python
# Usar como biblioteca
from hibridizador_core import Hibridizador
from hibridizador_hardware import ControladorHardware

hibridizador = Hibridizador()
hardware = ControladorHardware()
hibridizador.set_hardware(hardware)
# ... usar normalmente
```

---

## ⚙️ CONFIGURAÇÃO & CUSTOMIZAÇÃO

### Mudar parâmetros padrão
**Arquivo:** `hibridizador_core.py`
```python
class ParametroReacao:
    temperatura_alvo: float = 37.5  # ← Mudar aqui
    duracao_reacao: int = 14400     # ← Mudar aqui (segundos)
    velocidade_bomba: float = 75.0  # ← Mudar aqui (%)
```

### Mudar cores dos botões
**Arquivo:** `hibridizador_gui.py`
```python
cores = [
    "#FF0000",  # ← Mudar cores aqui
    "#0000FF",
    ...
]
```

### Ajustar precisão dos sensores
**Arquivo:** `hibridizador_hardware.py`
```python
class SensorTemperatura:
    precisao: float = 0.5  # ± 0.5°C (mudar aqui)
```

---

## 🔬 VERIFICAÇÃO

Para verificar se tudo está funcionando:

```bash
# 1. Teste de import
python3 -c "import hibridizador_core; print('✓ Core OK')"
python3 -c "import hibridizador_hardware; print('✓ Hardware OK')"
python3 -c "from PyQt5.QtWidgets import QApplication; print('✓ PyQt5 OK')"

# 2. Teste de execução (diagnóstico)
python3 run_hibridizador.py --diagnostico

# 3. Teste de interface gráfica
python3 run_hibridizador.py --gui
```

---

## 📝 NOTAS DE DESENVOLVIMENTO

- **Threads:** Usadas para não bloquear UI
- **Simulação:** Hardware é 100% simulado (sem GPIO real)
- **Escalabilidade:** Fácil adicionar sensores/atuadores reais
- **Performance:** Otimizado para Raspberry Pi Zero 2W
- **Portabilidade:** Funciona em Linux, macOS, Windows

---

**Re-Dino Hibridizador v1.0 - 2026**
*Sistema de Hibridização de DNA para Síntese de Genomas Híbridos*

🧬 🔬 ✨
