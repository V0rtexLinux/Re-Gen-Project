# 🤖 Guia Completo: Construção do Robô de Injeção de Genoma em Embrião

## 📋 INTRODUÇÃO

Este guia detalha como construir um robô automatizado para injetar DNA de dinossauro em embriões de galinha com precisão micrométrica. Sistema baseado em microscópio + microinjetor + controle XYZ.

---

## 🎯 OVERVIEW DO SISTEMA

```
┌──────────────────────────────────────┐
│  ROBÔ DE INJEÇÃO DE GENOMA           │
├──────────────────────────────────────┤
│                                      │
│  Componente 1: Microscópio           │
│  ├─ Zoom 4x-40x (estéreo)            │
│  ├─ Câmera USB para visão            │
│  └─ Iluminação coaxial (LED)         │
│                                      │
│  Componente 2: Manipulador Robótico  │
│  ├─ Eixo X (horizontal)              │
│  ├─ Eixo Y (horizontal)              │
│  ├─ Eixo Z (vertical)                │
│  └─ Motores: Stepper 1.5A NEMA23     │
│                                      │
│  Componente 3: Porta-Ovo Motorizado  │
│  ├─ Rotação 360° em XY               │
│  ├─ Movimento fino em Z (0.1µm)      │
│  └─ Sensor de posição (encoder)      │
│                                      │
│  Componente 4: Sistema de Injeção    │
│  ├─ Microinjetor com bomba           │
│  ├─ Agulha 30G (0.31mm)              │
│  ├─ Controle de volume (nL)          │
│  └─ Detecção de ponta da agulha      │
│                                      │
│  Componente 5: Controle (Raspberry Pi)
│  ├─ Drivers stepper A4988            │
│  ├─ Visão por câmera                 │
│  ├─ Detecção de agulha (laser)       │
│  └─ Interface web/GUI                │
│                                      │
└──────────────────────────────────────┘
```

---

## 📦 LISTA DE COMPONENTES

### ÓPTICA E MICROSCÓPIO

| Item | Qtd | Especificação | Preço (R$) |
|------|-----|---------------|-----------|
| Microscópio estéreo | 1 | 10x-40x, zoom | 1000-3000 |
| Câmera USB | 1 | 1080p 30fps | 150-300 |
| LED iluminação | 1 | Coaxial, 5000K | 200-500 |
| Lente objetiva | 1 | 10x, apocromática | 500-1000 |
| Vidro protetor | 1 | Placa de vidro 5cm | 20 |

### ESTRUTURA MECÂNICA

| Item | Qtd | Especificação | Preço (R$) |
|------|-----|---------------|-----------|
| Railslinear | 6m | 20x20mm, precisão | 300-600 |
| Rolamentos | 12 | THK linear | 200-400 |
| Fusos de esferas | 3 | M8, 2mm passo | 400-800 |
| Acoplamentos flex | 3 | 5x8mm | 50 |
| Estrutura alumínio | - | Perfil 20x40mm | 300 |

### MOTORES E MOVIMENTO

| Item | Qtd | Especificação | Preço (R$) |
|------|-----|---------------|-----------|
| Motor stepper | 3 | NEMA23, 1.5A | 200-400 cada |
| Driver stepper | 3 | A4988 com dissipador | 50-100 cada |
| Servo de precisão | 1 | 0.1° resolução | 300-600 |
| Encoder óptico | 3 | 2000 PPR | 100 cada |
| Polia GT2 | 6 | 20 dentes | 20 cada |

### SISTEMA DE INJEÇÃO

| Item | Qtd | Especificação | Preço (R$) |
|------|-----|---------------|-----------|
| Microinjetor | 1 | Bomba pneumática | 500-1200 |
| Agulhas finas | 50 | 30G, estéreis | 100-200 |
| Seringa 1mL | 10 | Para pressão | 50 |
| Tubing PTFE | 5m | 1/32", precisão | 100 |
| Câmara injection | 1 | Vidro 10cm | 50 |

### ELETRÔNICA E CONTROLE

| Item | Qtd | Especificação | Preço (R$) |
|------|-----|---------------|-----------|
| Raspberry Pi Zero 2W | 1 | 4GB RAM, WiFi | 200-300 |
| Fonte 5V 5A | 1 | Para motores | 100-150 |
| Sensor laser | 1 | Detecção agulha | 100-200 |
| Joystick analógico | 1 | Para manual | 20 |
| Botão pedal | 1 | Para injeção | 30 |
| LED RGB | 2 | Status (RGB) | 10 |

---

## 💰 CUSTO TOTAL ESTIMADO

```
Óptica e microscópio:    R$1500-4000
Estrutura mecânica:      R$800-1500
Motores e movimento:     R$1500-2500
Sistema de injeção:      R$800-1500
Eletrônica e controle:   R$500-800
Acessórios e testes:     R$200-300
────────────────────────────────────
TOTAL:                   R$5300-10600

Opções de economia:
├─ Microscópio usado: -R$500-1500
├─ Motores mais simples: -R$300-500
├─ Estrutura DIY: -R$200
└─ Mínimo viável: ~R$3000-5000
```

---

## 🔨 CONSTRUÇÃO PASSO-A-PASSO

### FASE 1: ESTRUTURA MECÂNICA (8-10 horas)

**Passo 1: Montar base XYZ**

```
Rails lineares (Rails):
├─ Eixo X (horizontal): 1 rail de 50cm
├─ Eixo Y (horizontal perpendicular): 1 rail de 30cm
├─ Eixo Z (vertical): 1 rail de 20cm

Montagem:
├─ Fixar rails em estrutura de alumínio
├─ Usar esquadros L para alinhamento
├─ Verificar perpendicularidade com nível
└─ Aperto final com chave sextavada

Folgas aceitáveis:
├─ Horizontal (X,Y): < 0.05mm
├─ Vertical (Z): < 0.02mm (crítico!)
└─ Usar folhas de shim para ajuste fino
```

**Passo 2: Instalar fusos de esferas**

```
Fusos (ballscrews):
├─ Fuso X: 50cm, 2mm passo
├─ Fuso Y: 30cm, 2mm passo
├─ Fuso Z: 20cm, 1mm passo (mais precisão em Z)

Cálculos de resolução:
├─ Fuso com passo 2mm e motor 1/16 stepping
├─ Resolução = 2mm / (200 * 16) = 0.625 µm
└─ Atinge resolução sub-micrométrica ✓

Montagem:
├─ Conectar fuso ao motor via acoplamento flex
├─ Instalar rolamentos nas extremidades
└─ Pré-carga leve (evita backlash)
```

**Passo 3: Montar porta-ovo**

```
Estrutura:
├─ Plataforma 10x10cm em acrílico
├─ Centro: Suporte para ovo (V-block)
├─ 2 parafusos de ajuste fino (Z)
└─ 1 parafuso de fixação

Posicionamento:
├─ Ovo na horizontal (não inclinado)
├─ Local de injeção acessível (topo)
├─ Câmara de ar claramente visível
└─ Altura: ~50cm acima da mesa

Movimento:
├─ Motor Z: Ajusta altura para foco
├─ Motores X,Y: Posicionam ovo para diferentes locais
└─ Resolução: 0.625 µm (sub-micrométrica)
```

---

### FASE 2: ÓPTICA E MICROSCÓPIO (3-4 horas)

**Passo 1: Montar microscópio**

```
Posicionamento:
├─ Altura: 60-70cm da mesa (ergonômico)
├─ Orientação: Perpendicular ao ovo
├─ Distância focal: 15-20cm do ovo
└─ Eixo óptico: Alinhado com eixo Z

Fixação:
├─ Use base robusta (reduz vibração)
├─ Braço articulado opcional (movimento fino)
└─ Isolamento anti-vibração (colchonete)
```

**Passo 2: Instalar câmera USB**

```
Posicionamento:
├─ Acoplada à ocular do microscópio
├─ Ou inserida no tubo de imagem (adaptador)
└─ Resolução mínima: 720p (640x480)

Configuração:
├─ Ligar à porta USB do Raspberry Pi
├─ Ativar câmera no raspi-config
└─ Testar com: fswebcam test.jpg

Captura de imagem:
└─ Frame rate: 30 fps mínimo
└─ Latência: < 50ms (resposta rápida)
```

**Passo 3: Instalar iluminação**

```
LED coaxial:
├─ Integrado no microscópio (ideal)
├─ Ou LED separado 5000K (branco neutro)
└─ Intensidade: Ajustável via PWM

Posicionamento:
├─ Lado oposto ao operador
├─ Luz vem pelo objetivo (coaxial)
└─ Sem sombras na região de injeção

Controle:
├─ PWM GPIO do Pi
├─ Joystick analógico para brilho
└─ Gravação automática de video com luz ideal
```

---

### FASE 3: SISTEMA DE INJEÇÃO (6-8 horas)

**Passo 1: Montar microinjetor**

```
Componentes:
├─ Bomba pneumática
├─ Câmara de ar (pressão constante)
├─ Válvula de controle (micro ajuste)
└─ Tubing 1/32" para agulha

Posicionamento:
├─ Acima do ovo (~30cm)
├─ Alinhado com eixo Z do microscópio
├─ Suportado por braço articulado
└─ Fácil acesso para trocar agulha

Calibração de pressão:
├─ Válvula reguladora 0-10 psi
├─ Iniciar em 0.5 psi (muito baixo)
├─ Aumentar até obter fluxo (ideal: 2-3 psi)
└─ Não exceder 5 psi (rompe agulha)
```

**Passo 2: Montar suporte para agulha**

```
Posicionamento:
├─ Agulha em ângulo 45° em relação ao ovo
├─ Ponta a ~2-3mm do ponto de injeção
├─ Dentro do campo de visão do microscópio
└─ Acessível para reposicionamento

Suporte mecânico:
├─ Aro de plástico ou acrílico (20mm)
├─ Agulha presa com parafuso de pressão suave
├─ Permite rotação ±5° (ajuste fino)
└─ Conector rápido para trocar agulha

Troca de agulha:
├─ Solte parafuso de pressão
├─ Remova agulha usada
├─ Insira agulha nova (estéril)
├─ Aperte parafuso suavemente
└─ Teste fluxo antes de injetar
```

**Passo 3: Sistema de medição de volume**

```
Método 1: Câmara de calibração
├─ Frasco graduado 1mL
├─ Marcar nível antes/depois
└─ Volume = Diferença de nível

Método 2: Cronometragem
├─ Ativar bomba por tempo T fixo
├─ Medir volume V em câmara
├─ Volume por tempo = V/T
└─ Exemplo: 50µL em 10s = 5µL/s

Método 3: Sensor de gotejamento
├─ Fotodiodo detecta gotas
├─ Cada gota = ~50 nL
├─ Contar gotas para validar
└─ Precisão: ±10%

Esperado:
├─ Injeção 50µL em 2-5 segundos
├─ Taxa: 10-25 µL/s
└─ Mínimo viável: 5µL
```

---

### FASE 4: SISTEMA DE POSICIONAMENTO (8-10 horas)

**Passo 1: Configurar motores stepper**

```
Motores (NEMA23):
├─ Motor X: Deslocamento horizontal
├─ Motor Y: Deslocamento perpendicular
├─ Motor Z: Ajuste de profundidade

Especificações:
├─ Torque: 3 Nm (suficiente para carga leve)
├─ Corrente: 1.5A por fase
├─ Passo: 1.8° (200 passos por revolução)
└─ Half-stepping: 400 passos/rev

Conexão a drivers A4988:
├─ Motor A (coil 1): Pino OUT1-2 do driver
├─ Motor B (coil 2): Pino OUT3-4 do driver
├─ Dirección: GPIO HIGH/LOW (sentido)
├─ Pulse: GPIO PWM (velocidade)
└─ Enable: GPIO (ligar/desligar)
```

**Passo 2: Calibrar resolução**

```
Cálculo de precisão:

Fuso com passo P mm, motor com N passos/rev:
└─ Resolução = P / N

Exemplo (Fuso 2mm, 200 passos):
├─ Resolução bruta: 2 / 200 = 0.01mm = 10µm
├─ Com half-stepping (400 passos): 0.005mm = 5µm
├─ Com microstepping 1/16: 0.625µm
└─ Atinge precisão necessária!

Teste de repetibilidade:
1. Mover para posição A
2. Mover para posição B (10mm de distância)
3. Voltar para posição A
4. Verificar erro (deve ser < 1µm)
5. Repetir 10x e calcular desvio padrão
└─ Erro < 2µm é aceitável
```

**Passo 3: Configurar encoders**

```
Encoders ópticos (2000 PPR):
├─ Encoder X: Eixo X
├─ Encoder Y: Eixo Y
├─ Encoder Z: Eixo Z

Função:
├─ Feedback de posição real
├─ Detecta patinação de motor
├─ Permite correção de erro
└─ Precisão aumenta significativamente

Conexão GPIO:
├─ Cada encoder: 2 fios (A, B)
├─ Raspberry Pi com GPIO a 3.3V
├─ Filtro RC para ruído (10kΩ + 100nF)
└─ Contagem em software
```

---

### FASE 5: DETECÇÃO DE AGULHA (3-4 horas)

**Passo 1: Sistema de detecção óptica**

```
Laser pointer + Fotodiodo:
├─ Laser 5mW, 650nm (vermelho)
├─ Fotodiodo + amplificador transimpedância
├─ Posicionar perpendicular à agulha
└─ Detecção de sombra = agulha presente

Posicionamento:
├─ Laser a 10mm lateral da agulha
├─ Fotodiodo no lado oposto
├─ Ambos no mesmo plano
└─ Alinhamento: ±1mm crítico

Calibração:
1. Sem agulha: Fotodiodo = 5V (luz máxima)
2. Com agulha: Fotodiodo < 2V (sombra)
3. Threshold de detecção: ~3V
4. Teste: Passar agulha pela frente
└─ Sinal deve ser claro e rápido
```

**Passo 2: Detecção de ponta**

```
Método: Análise de imagem em tempo real
├─ Câmera detecta ponta da agulha
├─ Software calcula posição subpixel
├─ Compara com posição do ovo
└─ Distância ponta-ovo em tempo real

Algoritmo:
1. Capturar frame (30 fps)
2. Converter BGR → Gray
3. Aplicar threshold (agulha é escura)
4. Encontrar contorno (Canny edge detection)
5. Calcular centroide
6. Distância = |centroide_agulha - centro_ovo|

Precisão esperada:
└─ ±50 µm (1/6 da espessura de um fio de cabelo)
```

---

### FASE 6: ELETRÔNICA E CONTROLE (6-8 horas)

**Passo 1: Montar shield dos motores**

```
Conexões GPIO (Raspberry Pi):

Motores Stepper (via A4988):
├─ GPIO 17: Motor X STEP
├─ GPIO 27: Motor X DIR
├─ GPIO 22: Motor Y STEP
├─ GPIO 23: Motor Y DIR
├─ GPIO 24: Motor Z STEP
├─ GPIO 25: Motor Z DIR

Controle de injeção:
├─ GPIO 18: Válvula solenóide (PWM)
├─ GPIO 12: Laser detecção (on/off)
└─ GPIO 26: LED status (RGB via PWM)

Sensores:
├─ GPIO 4: Encoder X (A)
├─ GPIO 5: Encoder X (B)
├─ GPIO 6: Encoder Y (A)
├─ GPIO 13: Encoder Y (B)
├─ GPIO 19: Encoder Z (A)
├─ GPIO 20: Encoder Z (B)
├─ GPIO 21: Fotodiodo (ADC via MCP3008)

Interface:
├─ GPIO 2/3: I2C (joystick analógico)
└─ GPIO 14/15: UART (debug serial)
```

**Passo 2: Montar drivers e fonte**

```
Drivers A4988 (3 unidades):
├─ Cada um controla 1 motor
├─ Corrente max: 1.5A (adequado para NEMA23)
├─ Dissipador térmico obrigatório
└─ Isolamento com folha de mica

Fonte de alimentação:
├─ 24V 3A (para motores)
├─ 5V 2A (para Raspberry Pi e sensores)

Circuito protetor:
├─ Capacitor 100µF antes de driver (suaviza tensão)
├─ Diodo 1N4007 em paralelo com motor (proteção)
├─ Fusível 3A em série
└─ Botão emergência desliga tudo
```

---

### FASE 7: SOFTWARE E CALIBRAÇÃO (10-12 horas)

**Passo 1: Instalar software**

```bash
# Clonar repositório
cd ~/Documents/re-gen
git clone . embryo_injection_robot

# Instalar dependências
pip3 install RPi.GPIO pyserial opencv-python numpy scipy

# Habilitar interface
sudo raspi-config
# Habilitar I2C, SPI, camera
```

**Passo 2: Calibração de motores**

```
Procedimento:

1. Teste individual cada motor:
   └─ Motor X: Mover +10mm, depois -10mm
   └─ Motor Y: Mover +10mm, depois -10mm
   └─ Motor Z: Mover +5mm, depois -5mm

2. Verificar com régua/paquímetro:
   └─ Erro aceitável: ±0.1mm

3. Se houver erro:
   ├─ Aumentar microsteps (resolução)
   ├─ Reduzir velocidade (pode estar perdendo passos)
   └─ Verificar torque (motor muito lento?)

4. Teste de repetibilidade:
   └─ 10x ida e volta
   └─ Erro máximo: ±0.05mm
```

**Passo 3: Calibração de visão**

```python
# calibrate_vision.py
import cv2
import numpy as np

cap = cv2.VideoCapture(0)  # Câmera USB

# Detectar círculo do ovo
while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detectar centro do ovo (círculo)
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, 1, 20,
        param1=50, param2=30, minRadius=50, maxRadius=100
    )
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        cv2.circle(frame, tuple(circles[0,0,:2]), circles[0,0,2], (0,255,0), 2)
        print(f"Centro: {circles[0,0,:2]}")
    
    cv2.imshow('Calibração', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 🎯 PROTOCOLO DE INJEÇÃO

**Passo-a-passo da injeção automatizada:**

```
1. PREPARO (5 min):
   └─ Colocar ovo no suporte
   └─ Localizar câmara de ar (via microscópio)
   └─ Alinhar ponto de injeção (2mm abaixo câmara)
   └─ Preparar agulha com DNA

2. POSICIONAMENTO AUTOMÁTICO (30 seg):
   └─ Mover ovo até câmara de ar estar visível
   └─ Mover agulha até ponta estar no foco
   └─ Algoritmo detecta ponta automaticamente

3. INSERÇÃO (10 seg):
   └─ Motor Z avança lentamente (50 µm/s)
   └─ Sensor óptico detecta penetração
   └─ Para quando agulha atingir profundidade desejada (2-3mm)

4. INJEÇÃO (5-10 seg):
   └─ Bomba injeta 50µL de DNA
   └─ Câmera monitora volume (medição por imagem)
   └─ Verifica se gotejando

5. RETIRADA (5 seg):
   └─ Motor Z recua (50 µm/s)
   └─ Agulha sai do ovo
   └─ Verifica se há vazamento (normal: pequeno)

6. VERIFICAÇÃO (30 seg):
   └─ Câmera tira foto final
   └─ Sensores registram: pressão, volume, duração
   └─ Ovo retorna à incubadora

TEMPO TOTAL POR OVO: ~2 minutos
CAPACIDADE: ~30 ovos/hora
```

---

## ⚠️ SEGURANÇA E BOAS PRÁTICAS

```
✓ FAÇA:
├─ Usar EPI (luvas, jaleco, óculos)
├─ Desinfectar tudo com álcool 70%
├─ Testar em ovos mortos primeiro
├─ Ter botão de emergência visível
├─ Documentar cada injeção
└─ Descartar agulhas em container biohazard

✗ NÃO FAÇA:
├─ Não exceder pressão de 5 psi
├─ Não tocar na lente do microscópio
├─ Não deixar agulha seca (mantém em solução PBS)
├─ Não trabalhar muito rápido (cause erro)
├─ Não ignorar alarmes do sistema
└─ Não reutilizar agulhas (usar nova cada vez)
```

---

## 📊 CRONOGRAMA DE CONSTRUÇÃO

```
Semana 1:
└─ Dias 1-3: Estrutura mecânica
└─ Dias 4-5: Motores e fusos
└─ Dias 6-7: Testes mecânicos

Semana 2:
└─ Dias 1-2: Óptica e microscópio
└─ Dias 3-4: Sistema de injeção
└─ Dias 5-6: Eletrônica GPIO
└─ Dias 7: Primeiro teste

Semana 3:
└─ Dias 1-3: Calibração de visão
└─ Dias 4-5: Testes com ovos mortos
└─ Dias 6-7: Otimização

TOTAL: 3-4 semanas
```

---

**PARABÉNS!** Você agora tem um robô completo de injeção de genoma em embriões! 🦖

Próximos passos: Executar PROCESSO_TRANSFORMACAO_EMBRIAO.md com o robô em funcionamento.
