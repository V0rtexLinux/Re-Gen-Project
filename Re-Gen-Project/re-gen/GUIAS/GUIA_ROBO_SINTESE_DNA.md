# 🤖 Guia Completo: Construção do Robô de Síntese de DNA Líquido

## 📋 INTRODUÇÃO

Este guia detalha como construir um robô de síntese de DNA em forma líquida que pode ser injetado em embriões. É um sistema semi-automatizado com válvulas, bombas e controle de temperatura.

---

## 🎯 OVERVIEW DO SISTEMA

```
┌─────────────────────────────────────────┐
│     ROBÔ DE SÍNTESE DE DNA              │
├─────────────────────────────────────────┤
│                                         │
│  Componente 1: Reservatórios (4)        │
│  ├─ Nucleotídeos (A, T, G, C)          │
│  └─ Reagentes (tampão, enzimas, sais)  │
│                                         │
│  Componente 2: Sistema de Bombas        │
│  ├─ 4 bombas peristálticas (nucleotídeos)
│  ├─ 1 bomba enzima (DNA polimerase)     │
│  └─ 1 bomba tampão/regulador            │
│                                         │
│  Componente 3: Válvulas de Controle     │
│  ├─ 10 válvulas solenóides (abertura)   │
│  ├─ Controle digital (GPIO)             │
│  └─ Sequência de injeção automática      │
│                                         │
│  Componente 4: Reator (câmara de síntese)
│  ├─ Volume: 50mL (vidro/PTFE)           │
│  ├─ Temperatura: 37°C controlada        │
│  ├─ Agitação: Magnética suave           │
│  └─ Monitoramento: pH, condutividade    │
│                                         │
│  Componente 5: Controle (Raspberry Pi)  │
│  ├─ GPIO para válvulas                  │
│  ├─ Sensor de temperatura               │
│  ├─ Sensor de pH                        │
│  └─ Interface web/GUI                   │
│                                         │
└─────────────────────────────────────────┘
```

---

## 📦 LISTA DE COMPONENTES

### ESTRUTURA E HOUSING

| Item | Qtd | Especificação | Preço (R$) | Fornecedor |
|------|-----|---------------|-----------|-----------|
| Acrílico transparente | 1 | 30x30x20cm | 150-300 | Lojas de acrílico |
| Perfil alumínio | 2m | 20x20mm | 100-200 | Lojas de ferro |
| Parafusos/porcas | 50 | M4, M6, M8 | 50 | Lojas de hardware |
| Vedação de silicone | 10m | Para tubagens | 50 | Lojas de tintas |
| Tubing PTFE | 10m | 1/16", 1/8" | 200-400 | eBay/AliExpress |

### BOMBAS E VÁLVULAS

| Item | Qtd | Especificação | Preço (R$) | Obs |
|------|-----|---------------|-----------|-----|
| Bomba peristáltica | 4 | 0.1-10mL/min | 200-600 cada | Para nucleotídeos |
| Bomba peristáltica enzima | 1 | 0.5-50µL/min | 300-800 | Precisão maior |
| Válvula solenóide | 10 | 12V DC, PTFE | 50-150 cada | Controle GPIO |
| Válvula check | 6 | Retenção 1 sentido | 20-40 cada | Evita refluxo |
| Válvula manual 3-vias | 2 | Para seleção | 30-60 | Mudança manual |

### ELETRÔNICA E CONTROLE

| Item | Qtd | Especificação | Preço (R$) | Fornecedor |
|------|-----|---------------|-----------|-----------|
| Raspberry Pi Zero 2W | 1 | 4GB RAM, WiFi | 200-300 | Mercado Livre |
| Relé 4-canais | 3 | 12V, GPIO | 30-50 | AliExpress |
| Sensor temperatura | 2 | DS18B20 (1-wire) | 10-20 | AliExpress |
| Sensor pH | 1 | Analógico (0-14) | 100-200 | AliExpress |
| Sensor condutividade | 1 | 0-20mS/cm | 80-150 | AliExpress |
| Fonte 12V 5A | 1 | Para bombas/válvulas | 80-150 | AliExpress |
| Fonte 5V 2A | 1 | Para Pi | 30-50 | AliExpress |
| Fusível 5A | 2 | Proteção | 10 | Qualquer loja |

### CÂMARA DE REAÇÃO

| Item | Qtd | Especificação | Preço (R$) | Obs |
|------|-----|---------------|-----------|-----|
| Frasco vidro | 1 | 50mL, boca larga | 50-100 | PTFE é melhor |
| Barra magnética | 1 | 5cm, revestida PTFE | 20-40 | Para agitação |
| Agitador magnético | 1 | Com aquecimento | 200-400 | Temp + agitação |
| Resistência aquecimento | 1 | 12V, 50W | 50-100 | Backup térmica |
| Isolamento térmico | 1 | Poliestireno/lã | 30 | Para estabilidade |
| Eletrodo pH | 1 | Digital, calibrado | 150-300 | Precisão |

### REAGENTES E CONSUMÍVEIS

| Item | Qtd | Especificação | Preço (R$) | Fornecedor |
|------|-----|---------------|-----------|-----------|
| dATP/dGTP/dCTP/dTTP | 4 | 100mM (1mL) | 200-400 cada | Sigma-Aldrich |
| DNA Polimerase | 1 | Taq/Phi29 (5U/µL) | 500-1000 | Bio-Rad/NEB |
| Tampão reação | 1 | Pré-mix (10x) | 200-500 | Sigma |
| MgCl2 | 1 | 25mM | 100-200 | Sigma |
| Template DNA | 1 | Sequência dino (3Gb) | 5000-15000 | Síntese externa |
| Primers | 1 | Set 500+ species | 2000-5000 | Síntese externa |

### PERIFÉRICOS E ACESSÓRIOS

| Item | Qtd | Especificação | Preço (R$) | Obs |
|------|-----|---------------|-----------|-----|
| Webcam USB | 1 | 1080p, para monitorar | 50-100 | Opcional |
| LED RGB | 3 | 5mm, status visual | 5 | Status: Verde/Amarelo/Vermelho |
| Buzzer piezo | 1 | 12V, alerta | 10 | Avisos |
| Botão emergência | 1 | Vermelho com trava | 20 | Segurança |
| Painel de controle | 1 | Acrílico com furos | 50 | DIY |

---

## 💰 CUSTO TOTAL ESTIMADO

```
Estrutura:              R$300-500
Bombas/Válvulas:        R$2000-3500
Eletrônica:             R$600-900
Câmara reação:          R$400-700
Reagentes iniciais:     R$8000-20000
Periféricos:            R$150
────────────────────────────────
TOTAL:                  R$11,450-25,750

Opções de economia:
├─ Usar bombas mais simples: -R$500-1000
├─ Sensor pH caseiro: -R$100
├─ Fazer câmara: -R$200
└─ Mínimo viável: ~R$8,000-10,000
```

---

## 🔨 CONSTRUÇÃO PASSO-A-PASSO

### FASE 1: ESTRUTURA FÍSICA (4-6 horas)

**Passo 1: Montar o frame**

```
Material: Perfil alumínio 20x20mm
Dimensões: 40cm (L) x 30cm (P) x 40cm (A)

Corte (4 peças):
├─ 2 peças 40cm (laterais verticais)
├─ 2 peças 30cm (frente-trás verticais)
└─ 4 peças 40cm (base e topo)

Montagem:
└─ Use esquadros L e parafusos M8
└─ Aperte com chave (2.5mm)
└─ Verifique alinhamento com nível
```

**Passo 2: Montar caixa acrílica**

```
Cortes (usar serra quente ou serrador):
├─ Frente e trás: 40 x 30cm
├─ Laterais: 30 x 30cm
├─ Topo: 40 x 30cm
└─ Base: 40 x 30cm

Furos para:
├─ 2 furos topo (entrada ar)
├─ 2 furos base (saída ar)
├─ 6 furos laterais (tubagens)
├─ 4 furos fundo (eletrodos)
└─ Parafuso no topo (componentes)
```

**Passo 3: Instalar suportes internos**

```
├─ Suporte para câmara reação (centro)
├─ Suporte para bombas (esquerda)
├─ Suporte para válvulas (direita)
├─ Suporte para agitador magnético (base)
├─ Suporte para Raspberry Pi (lateral)
└─ Todos com isolamento térmico
```

---

### FASE 2: SISTEMA DE BOMBAS (6-8 horas)

**Passo 1: Instalar bombas peristálticas**

```
Posicionamento:
├─ Bomba A (dATP):        Esquerda, altura média
├─ Bomba G (dGTP):        Esquerda, abaixo de A
├─ Bomba C (dCTP):        Centro-esquerda, altura média
├─ Bomba T (dTTP):        Centro-esquerda, abaixo de C
├─ Bomba Enzima:          Direita, altura máxima
└─ Bomba Tampão:          Direita, altura mínima

Fixação:
├─ Use suportes 3D impresos em ABS
├─ Ou suportes de aço inox parafusados
└─ Deixe espaço para tubing
```

**Passo 2: Conectar tubagens**

```
Entrada (Reservatórios no topo):
├─ Reserv. A → Tubing 1/8" → Bomba A
├─ Reserv. G → Tubing 1/8" → Bomba G
├─ Reserv. C → Tubing 1/8" → Bomba C
├─ Reserv. T → Tubing 1/8" → Bomba T
├─ Reserv. Enzima → Tubing 1/16" → Bomba Enzima
└─ Reserv. Tampão → Tubing 1/8" → Bomba Tampão

Saída (Todas para válvulas):
├─ Bomba A → Válvula Solenóide 1
├─ Bomba G → Válvula Solenóide 2
├─ Bomba C → Válvula Solenóide 3
├─ Bomba T → Válvula Solenóide 4
├─ Bomba Enzima → Válvula Solenóide 5
└─ Bomba Tampão → Válvula Solenóide 6
```

**Passo 3: Testar bombas**

```
Procedimento:
1. Encher reservatórios com água destilada
2. Conectar bomba à fonte 12V
3. Ativar potenciômetro (velocidade) lentamente
4. Observar fluxo de água
5. Medir volume/tempo (ex: 1mL em 60s)

Especificação esperada:
├─ Bomba nucleotídeo: 0.1-10 mL/min
├─ Bomba enzima: 0.5-50 µL/min
└─ Bomba tampão: 1-20 mL/min
```

---

### FASE 3: SISTEMA DE VÁLVULAS (4-6 horas)

**Passo 1: Instalar válvulas solenóides**

```
Posicionamento (no centro):
├─ Válvulas 1-4 (nucleotídeos): Lado esquerdo
├─ Válvulas 5-6 (enzima/tampão): Lado direito
└─ Válvulas check (antifluxo): Após cada solenóide

Conexão:
├─ Entrada (de bombas): 1/8" PTFE
├─ Saída (para câmara): 1/8" PTFE
└─ Sinal (GPIO): Fio 22AWG
```

**Passo 2: Instalar válvulas check**

```
Posição: Imediatamente após válvula solenóide
Função: Impedir refluxo

Instalação:
├─ Entrada: Do fluido (fluxo normal)
├─ Saída: Para câmara reação
└─ Teste: Aplicar pressão reversa (não flui)
```

**Passo 3: Interligar à câmara de reação**

```
Final (Câmara de Reação):
├─ Todas 6 válvulas → Coletores T-junction
├─ Todos os coletores → Única entrada na câmara
├─ Entrada possui filtro 0.2µm (estéril)
└─ Saída possui válvula de alívio (pressão max 5psi)
```

---

### FASE 4: CÂMARA DE REAÇÃO (3-4 horas)

**Passo 1: Preparar frasco**

```
Frasco: Vidro borossilicato 50mL, boca larga

Furos necessários:
├─ 1 orifício (lado): Entrada de reagentes (1/4")
├─ 1 orifício (lado): Saída de ar (1/8")
├─ 1 orifício (base): Para barra magnética (leve)
├─ 1 orifício (topo): Eletrodo temperatura (1/8")
├─ 1 orifício (topo): Eletrodo pH (1/8")
└─ 1 orifício (lateral): Sensor condutividade (opcional)

Vedação:
├─ Use PTFE threading tape
├─ Aplique silicone de alto ponto (para 100°C+)
└─ Deixe secar 24h antes de usar
```

**Passo 2: Instalar agitador magnético**

```
Sistema: Agitador com aquecimento integrado

Posicionamento:
├─ Câmara fica sobre agitador
├─ Barra magnética dentro da câmara (5cm)
├─ Controle de velocidade: 100-800 RPM

Calibração:
├─ Velocidade mínima: Apenas agitar (sem vórtice)
├─ Velocidade máxima: Homogeneização completa
└─ Velocidade ideal para DNA: 300-400 RPM
```

**Passo 3: Instalar sensores**

```
Sensor temperatura (DS18B20):
├─ Instalação: Ponta em contato com líquido
├─ Precisão: ±0.5°C
├─ Fio: 3 pinos (GND, +5V, Data)
├─ Conexão GPIO: GPIO 4 (Raspberry Pi)
└─ Resistência pull-up: 4.7k Ohm

Sensor pH:
├─ Eletrodo com amplificador (0-3.3V → 0-14 pH)
├─ Instalação: Mergulhado no líquido
├─ Calibração: 2 pontos (pH 7 e pH 4 ou 10)
├─ Conexão GPIO: GPIO 17 (Raspberry Pi)
└─ Tempo resposta: 30-60 segundos

Sensor condutividade (opcional):
├─ 2 eletrodos Pt
├─ Leitura em mS/cm
└─ Detecta concentração iônica
```

---

### FASE 5: ELETRÔNICA E CONTROLE (6-8 horas)

**Passo 1: Montar shield GPIO**

```
Esquema de conexão (Raspberry Pi GPIO):

Bombas (via Relé 12V):
├─ GPIO 22: Bomba A (dATP)
├─ GPIO 23: Bomba G (dGTP)
├─ GPIO 24: Bomba C (dCTP)
├─ GPIO 25: Bomba T (dTTP)
├─ GPIO 26: Bomba Enzima
└─ GPIO 27: Bomba Tampão

Válvulas Solenóides (via Relé 12V):
├─ GPIO 5: Válvula solenóide 1 (A)
├─ GPIO 6: Válvula solenóide 2 (G)
├─ GPIO 12: Válvula solenóide 3 (C)
├─ GPIO 13: Válvula solenóide 4 (T)
├─ GPIO 19: Válvula solenóide 5 (Enzima)
└─ GPIO 20: Válvula solenóide 6 (Tampão)

Sensores:
├─ GPIO 4: Sensor temperatura DS18B20 (1-wire)
├─ GPIO 17: Sensor pH (ADC via MCP3008)
├─ GPIO 10: SPI Clock (para ADC)
├─ GPIO 9: SPI MOSI (para ADC)
├─ GPIO 11: SPI MISO (para ADC)
└─ GPIO 8: SPI CE0 (para ADC)

Periféricos:
├─ GPIO 14/15: UART (Terminal serial)
├─ GPIO 2/3: I2C (Expansão futura)
└─ GPIO 21: LED status (vermelho)
```

**Passo 2: Montar relés e fonte**

```
Esquema de Potência:

Fonte 12V 5A (Bombas/Válvulas):
├─ Positivo (+12V) → Relé VCC
├─ Negativo (GND) → GND Comum
└─ Proteção: Fusível 5A em série

Relés (3 unidades, cada 4 canais):
├─ Relé 1: Canais 1-4 (Bombas A,G,C,T)
├─ Relé 2: Canais 1-2 (Bombas Enzima, Tampão)
├─ Relé 3: Canais 1-6 (Válvulas solenóides)

Sinal GPIO (3.3V):
├─ Cada GPIO → Opto-isolador → Bobina Relé
└─ Proteção contra surtos com diodo 1N4007

Circuito de potência:
├─ Fonte (+12V) → Relé (NC) → Bomba/Válvula → GND
└─ Quando GPIO=HIGH → Relé fecha → Bomba/Válvula ativa
```

**Passo 3: Conectar Raspberry Pi**

```
Hardware necessário:
├─ Raspberry Pi Zero 2W com 4GB RAM
├─ Fonte 5V 2A USB-C
├─ Cartão SD 32GB (classe 10)
├─ Dissipador térmico (opcional mas recomendado)
└─ Case acrílico para proteção

Instalação:
1. Flashar SD com Raspberry Pi OS Lite
2. Habilitar SSH e I2C/SPI via raspi-config
3. Conectar GPIO conforme esquema acima
4. Instalar bibliotecas Python:
   └─ pip install RPi.GPIO pyserial Adafruit_MCP3008
```

---

### FASE 6: CALIBRAÇÃO E TESTES (8-10 horas)

**Passo 1: Teste de pressão**

```
Procedimento:
1. Encher tubing com água destilada
2. Fechar saída da câmara
3. Ativar bombas (1 por vez)
4. Medir pressão com manômetro (deve ser < 5 psi)

Teste de vazamento:
├─ Aplique 2 psi por 5 minutos
├─ Procure gotejamento em todas conexões
├─ Aperte se necessário
└─ Não deve haver vazamento
```

**Passo 2: Teste de fluxo**

```
Calibração de velocidade:

Para cada bomba:
1. Colocar na saída um frasco graduado (1-10mL)
2. Ativar bomba por tempo T
3. Medir volume V
4. Calcular fluxo: V/T (mL/min)

Ajustar potenciômetro para atingir:
├─ Bombas nucleotídeo: 0.5 mL/min
├─ Bomba enzima: 1 µL/min  
└─ Bomba tampão: 1 mL/min
```

**Passo 3: Teste de temperatura**

```
Calibração do agitador:

1. Encher câmara com 40mL de água destilada
2. Colocar sobre agitador
3. Ativar aquecimento a 37°C
4. Monitorar temperatura com sensor DS18B20
5. Tempo esperado: 15-20 minutos até estabilizar

Estabilidade térmica:
├─ Variação máxima: ±0.5°C
├─ Tempo resposta: < 2 minutos após mudança
└─ Drift longo prazo: < 0.1°C/hora
```

**Passo 4: Teste de sensores**

```
Sensor pH:
├─ Calibrar em pH 7.0 (solução tampão)
├─ Depois calibrar em pH 4.0 e pH 10.0
├─ Erro esperado: ±0.1 pH

Sensor temperatura:
├─ Comparar com termômetro digital
├─ Erro esperado: ±0.5°C
└─ Fazer leitura a cada 10 segundos

Sensor condutividade:
├─ Testar em água destilada (0 mS/cm)
├─ Testar em solução 10mM NaCl (~1 mS/cm)
└─ Calibração linear
```

---

## 🎮 SOFTWARE DE CONTROLE

### Instalação e configuração

```bash
# Conectar ao Pi via SSH
ssh pi@raspberrypi.local

# Atualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar dependências
sudo apt-get install python3-pip python3-dev git

# Clonar código do projeto
cd ~/Documents/re-gen
git clone . dna_synthesizer_robot

# Instalar bibliotecas Python
pip3 install RPi.GPIO pyserial requests flask

# Copiar script de controle
cp dna_synthesizer_hardware.py ~/

# Testar GPIO
python3 -c "import RPi.GPIO; print('GPIO OK')"
```

### Script de teste

```python
# test_robot.py
import time
from dna_synthesizer_hardware import DNASynthesizerRobot

robot = DNASynthesizerRobot()

# Teste cada bomba
for pump in ['A', 'G', 'C', 'T']:
    print(f"Testando bomba {pump}...")
    robot.activate_pump(pump, duration=5)
    time.sleep(1)

# Teste validação térmica
print("Validando temperatura...")
temp = robot.get_temperature()
print(f"Temperatura: {temp}°C")

# Teste injeção de DNA
print("Iniciando síntese...")
robot.start_dna_synthesis()
```

---

## ⚠️ SEGURANÇA

### Protocolos de segurança

```
1. DESLIGAMENTO DE EMERGÊNCIA
   └─ Botão físico vermelho
   └─ Desliga tudo (bombas, válvulas, aquecimento)

2. PROTEÇÃO CONTRA PRESSÃO
   └─ Válvula de alívio a 5 psi
   └─ Manômetro em local visível

3. PROTEÇÃO TÉRMICA
   └─ Sensor temperatura com limite max 45°C
   └─ Cutoff automático se exceder

4. BIOSSEGURANÇA
   └─ EPI: Luvas, jaleco, óculos
   └─ Descarte: Container biohazard
   └─ Limpeza: Álcool 70% + hipoclorito 0.5%

5. ELETRICIDADE
   └─ Fonte 12V isolada (não é 110V)
   └─ Fusível 5A protege circuito
   └─ Disjuntor no painel de entrada
```

---

## 📊 CRONOGRAMA DE CONSTRUÇÃO

```
Semana 1:
└─ Dias 1-2: Pedidos e recebimento de componentes
└─ Dias 3-5: Construção estrutura (frame + acrílico)
└─ Dias 6-7: Inspeção e ajustes

Semana 2:
└─ Dias 1-3: Instalação de bombas
└─ Dias 4-5: Instalação de válvulas
└─ Dias 6-7: Testes de vazamento

Semana 3:
└─ Dias 1-2: Preparo da câmara
└─ Dias 3-5: Eletrônica e conexões GPIO
└─ Dias 6-7: Testes finais

TOTAL: 3-4 semanas (trabalhando 2-3 horas/dia)
```

---

## ✅ CHECKLIST FINAL

- [ ] Estrutura montada e alinhada
- [ ] Todas as bombas funcionam
- [ ] Todas as válvulas abrem/fecham
- [ ] Sem vazamentos em nenhuma conexão
- [ ] Temperatura estável em 37°C
- [ ] Sensores calibrados e funcionando
- [ ] GPIO todos conectados corretamente
- [ ] Software instalado e testado
- [ ] Botão de emergência funciona
- [ ] Toda documentação revisada

---

**PRÓXIMO PASSO:** Leia o "GUIA_ROBO_INJECAO_GENOMA.md" para construir o robô de injeção!
