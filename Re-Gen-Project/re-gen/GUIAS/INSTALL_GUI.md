# 🦖 Re-Dino Synthesizer - Guia de Instalação

## Sistema Completo de Síntese de DNA de Dinossauros

### Hardware Necessário

**Raspberry Pi Zero 2W** (Sistema Principal)
- CPU: ARM Cortex-A72 1GHz dual-core
- RAM: 512 MB
- Pinos GPIO: 40
- Conectividade: WiFi/Bluetooth

**Periféricos de Síntese de DNA**
- 6x Bombas peristálticas 12V
- 4x Válvulas solenoides 3.3V
- 2x Sensores DS18B20 (temperatura)
- 1x Sensor de pH analógico
- Câmara de microfluidica (70µL)
- LEDs UV 365nm para crosslink
- Bomba de vácuo 12V

**Sistema de Injeção Robótica**
- 3x Servo motores (eixos XYZ)
- 1x Servo de seringa
- Suporte para embrião de galinha
- Agulha de injeção 30G

**Consumíveis**
- dATP 100mM (100µL)
- dTTP 100mM (100µL)
- dGTP 100mM (100µL)
- dCTP 100mM (100µL)
- DNA polimerase Phusion
- Buffer de síntese
- Embriões de galinha (Gallus gallus)

---

## Instalação de Software

### 1. Dependências Python

```bash
# Atualizar pip
pip3 install --upgrade pip

# Instalar PyQt5 (Interface Gráfica)
pip3 install PyQt5 PyQtChart

# Instalar Matplotlib (Visualização)
pip3 install matplotlib

# Instalar RPi.GPIO (Controle de GPIO)
pip3 install RPi.GPIO

# Instalar w1thermsensor (Sensor de Temperatura)
pip3 install w1thermsensor

# Instalar numpy (Processamento de dados)
pip3 install numpy

# Instalar Biopython (Sequências de DNA)
pip3 install biopython

# Instalar NCBI-Entrez (Busca de sequências)
pip3 install biopython
```

### 2. Configurar Raspberry Pi

```bash
# Habilitar 1-Wire (para sensores de temperatura)
sudo raspi-config
# > 3. Interface Options
# > P7 1-Wire
# > Sim

# Habilitar GPIO
sudo usermod -a -G gpio $(whoami)

# Reiniciar
sudo reboot
```

### 3. Clonar/Configurar Projeto

```bash
cd /home/v0rtex/Documents/re-gen

# Criar arquivo de configuração
cat > config.json << 'EOF'
{
  "hardware": {
    "raspberry_pi": true,
    "gpio_mode": "BCM",
    "pump_speed_default": 50,
    "servo_angle_default": 90
  },
  "synthesis": {
    "dna_target_size_bp": 3000000000,
    "temperature_optimal": 37.0,
    "ph_optimal": 7.5
  },
  "injection": {
    "volume_ul": 50.0,
    "depth_mm": 2.0,
    "x_position_mm": 0,
    "y_position_mm": 0
  }
}
EOF

# Verificar permissões
chmod +x gui_dino_synthesizer.py
chmod +x main_v3.py
```

### 4. Testar Conexão com Raspberry Pi

```bash
# Se rodando em outro computador, SSH para Raspberry Pi
ssh pi@raspberrypi.local

# Verificar GPIO
python3 -c "import RPi.GPIO as GPIO; print('✓ GPIO OK')"

# Testar sintaxe de todos os módulos
python3 -m py_compile *.py
```

---

## Como Usar a Interface Gráfica

### Modo Desktop (Teste)

```bash
# Em qualquer computador com PyQt5
python3 gui_dino_synthesizer.py
```

### Modo Raspberry Pi (Produção)

```bash
# SSH para o Pi
ssh pi@raspberrypi.local

# Executar com display remoto
export DISPLAY=:0
python3 gui_dino_synthesizer.py
```

---

## Interface Gráfica - Abas Principais

### 1️⃣ **Banco de Dinossauros (500+ espécies)**
- Buscar por nome científico ou comum
- Filtrar por período (Triássico, Jurássico, Cretáceo)
- Filtrar por dieta (herbívoro, carnívoro)
- Ver genoma, tamanho, peso
- Selecionar dinossauro para síntese

### 2️⃣ **Síntese de DNA**
- Configurar concentrações de dNTPs
- Definir temperatura e pH
- Iniciar síntese de genoma
- Monitor em tempo real:
  - Progresso (%)
  - Temperatura atual
  - Bomba status
  - Validação de sequência

### 3️⃣ **Injeção em Embrião**
- Posicionar embrião (XYZ)
- Configurar volume de injeção
- Definir profundidade
- Executar injeção automática
- Visualização 3D da posição

---

## Fluxo de Trabalho Completo

```
┌─────────────────────────────────────────────┐
│ 1. Selecionar Dinossauro                    │
│    (ex: Tyrannosaurus rex)                  │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 2. Gerar Genoma (3Gb)                       │
│    $ python main_v3.py \                   │
│      --species "Tyrannosaurus rex" \        │
│      --genome-size 3000000000               │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 3. Síntese de DNA Líquido                   │
│    - Preparar dNTPs                         │
│    - Polimerase Phusion                     │
│    - Temperatura: 37°C                      │
│    - pH: 7.5                                │
│    - Duração: ~48 horas                     │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 4. Crosslink UV                             │
│    - LED 365nm                              │
│    - 5 segundos                             │
│    - Intensidade: 100%                      │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 5. Purificação e Extração                   │
│    - Bomba de vácuo                         │
│    - Coluna de purificação                  │
│    - Volume final: 50µL                     │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 6. Injeção em Embrião de Galinha            │
│    - Posicionar embrião                     │
│    - Volume: 50µL                           │
│    - Profundidade: 2mm                      │
│    - Injetar DNA de dinossauro              │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ 7. Incubação                                │
│    - Temperatura: 37.5°C                    │
│    - Umidade: 75%                           │
│    - Duração: 21 dias                       │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│ ✨ RESULTADO: DINOSSAURO VIVO               │
│    (Híbrido Galinha-Dinossauro)             │
└─────────────────────────────────────────────┘
```

---

## Troubleshooting

### Erro: "GPIO não encontrado"
```bash
# Verificar se está rodando como root
sudo python3 gui_dino_synthesizer.py

# Ou adicionar usuário ao grupo gpio
sudo usermod -a -G gpio pi
sudo reboot
```

### Erro: "Sensor de temperatura não responde"
```bash
# Verificar conexão 1-Wire
ls /sys/bus/w1/devices/

# Se vazio, habilitar:
sudo raspi-config > Interface > 1-Wire > Sim
```

### GUI não aparece
```bash
# Verificar display
echo $DISPLAY

# Se vazio, configurar:
export DISPLAY=:0

# Ou executar via VNC
vncserver
```

---

## Banco de Dinossauros (500+ Espécies)

### Populares (20)
- Tyrannosaurus rex
- Triceratops horridus
- Stegosaurus stenops
- Velociraptor mongoliensis
- Brachiosaurus altithorax
- ... (16 mais)

### Impopulares (50)
- Allosaurus fragilis
- Carnotaurus sastrei
- Giganotosaurus carolinii
- Compsognathus longipes
- ... (46 mais)

### Desconhecidos (430+)
- Abelisaurus comahuensis
- Acrocanthosaurus atokensis
- Amargasaurus cazaui
- Anchisaurus polyzelus
- Andesaurus delgadoi
- ... (425 mais espécies obscuras)

---

## Especificações Técnicas

### Raspberry Pi Zero 2W
- CPU: ARMv7 Cortex-A72 1GHz x2
- RAM: 512MB LPDDR2
- GPIO: 40 pinos
- Frequência PWM: até 20MHz
- Resolução ADC: 10-bit (via MCP3008)

### Síntese de DNA
- Velocidade: 1000 bp/seg (Phusion)
- Tempo para 3Gb: ~48 horas
- Acurácia: 99.9% (Phusion 3000)
- Fidelidade: 0.5 µM-1 (erros por base)

### Injeção Robótica
- Precisão XYZ: ±0.5mm
- Volume: 0.1-100µL
- Velocidade: 1 injeção/minuto

---

## Próximas Etapas

1. ✅ Banco de dados de 500+ dinossauros
2. ✅ Hardware real (Raspberry Pi Zero 2W)
3. ✅ Interface gráfica PyQt5
4. ⏳ Sistema de incubação automática
5. ⏳ Monitoramento do embrião (webcam)
6. ⏳ Análise genômica pós-nascimento
7. ⏳ Habitat para dinossauro híbrido

---

## Licença & Disclaimer

⚠️ **AVISO LEGAL**: Este é um **projeto experimental** para fins educacionais. 

A criação de novos organismos requer aprovação ética e regulatória. Consulte autoridades competentes antes de qualquer procedimento biológico real.

---

**Última atualização:** Julho 2026
**Status:** 🚀 Desenvolvimento Ativo
