# 🧬 Extrator de DNA - Guia Completo de Construção

## 📋 INTRODUÇÃO

O **Extrator de DNA** é um equipamento de laboratório automatizado que extrai DNA de amostras biológicas (sangue, tecido, saliva, plumas) usando protocolos científicos padrão.

**Características:**
- Centrifugação controlada (até 15.000 RPM)
- Aquecimento preciso (20-100°C)
- Dosagem automática de reagentes
- Medição de pureza (A260/A280)
- Tempo total: ~30-45 minutos por amostra
- Taxa de sucesso: 85-90%

---

## 🔧 COMPONENTES NECESSÁRIOS

### ESTRUTURA MECÂNICA
```
├─ Frame de alumínio 40x40mm (estrutura 60x40x50cm)
├─ Base anti-vibratória
├─ Placas de acrílico (proteção)
└─ Vedações de borracha
```

### CENTRIFUGA
```
├─ Motor DC 24V (até 15.000 RPM)
├─ Rotor de alumínio
├─ Tubo de amostras (24 posições)
├─ Encodador para velocidade
└─ Sensor de vibração
```

### AQUECEDOR/RESFRIADOR
```
├─ Bloco de aquecimento alumínio (100W)
├─ Sensor PT100 (±0.1°C)
├─ Ventilador 12V (resfriamento)
├─ Termopar tipo K
└─ Controlador PID (Raspberry Pi)
```

### DOSAGEM DE REAGENTES
```
├─ Bomba peristáltica (5µL-50µL/min)
├─ Válvulas solenóides (6x)
├─ Tubagens silicone médico (6m)
├─ Reservatórios (5 de 100mL)
└─ Tubos de destino (24 tubos)
```

### SENSORES
```
├─ Sensor temperatura DS18B20 (±0.5°C)
├─ Sensor absorbância 260/280nm (espectrofotômetro)
├─ Sensor turbidez (verificação de limpeza)
└─ Sensor nível (reservatórios)
```

### ELETRÔNICA
```
├─ Raspberry Pi Zero 2W
├─ Motor driver BTS7960 (para centrifuga)
├─ PWM driver 16ch (para bombas/válvulas)
├─ Fonte 24V 5A
├─ Fonte 12V 3A
├─ Relé de 8 canais
└─ Sensor multiplexer I2C
```

### DISPLAY E CONTROLE
```
├─ LCD 16x2 (status)
├─ Botões de controle (5x)
├─ Botão de emergência
└─ LED indicadores RGB (status)
```

---

## 💰 CUSTO ESTIMADO

```
ESTRUTURA:                R$200-400
├─ Alumínio/acrílico
├─ Parafusos/arruelas
└─ Vedações

CENTRIFUGA:               R$400-800
├─ Motor 24V + rotor
├─ Bearings de precisão
└─ Sensor de velocidade

AQUECIMENTO:              R$300-600
├─ Bloco alumínio
├─ Sensor PT100
├─ Ventilador
└─ Controlador

DOSAGEM:                  R$250-500
├─ Bomba peristáltica
├─ Válvulas solenóides
├─ Tubagens
└─ Reservatórios

ELETRÔNICA:               R$400-800
├─ Raspberry Pi Zero 2W
├─ Drivers/relés
├─ Sensores
└─ Fiação/conectores

DISPLAY:                  R$100-200
├─ LCD 16x2
├─ Botões
└─ LEDs

TOTAL:                    R$1,650-3,300
```

---

## 🏗️ CONSTRUÇÃO PASSO-A-PASSO

### FASE 1: Estrutura Base (2-3 dias)

#### Passo 1: Montar Frame de Alumínio

**Materiais:**
```
□ Perfil alumínio 40x40mm:
  - 4x 50cm (pilares verticais)
  - 4x 60cm (travessas horizontais)
  - 4x 40cm (travessas profundidade)
□ Parafusos M8 (40 unidades)
□ Escudos de borracha
□ Pés ajustáveis
```

**Procedimento:**
```
1. Cortar alumínio para tamanho exato
2. Marcar furos (10cm das extremidades)
3. Fazer furos com broca #6.8mm
4. Montar base horizontal primeiro
5. Inserir pilares verticais
6. Montar travessas horizontais (altura 30cm)
7. Nivelar com precisão (±2mm)
8. Apertarar com chave hexagonal
```

**Verificação:**
```
✓ Frame é quadrado (diagonais iguais)
✓ Sem vibração ao pressionar
✓ Nivelado em todas direções
✓ Altura 50cm exata
```

#### Passo 2: Montar Plataformas

**Materiais:**
```
□ Placa acrílico 5mm:
  - 1x 60x40cm (base inferior)
  - 1x 60x40cm (plataforma centrifuga)
  - 1x 60x40cm (plataforma aquecedor)
□ Parafusos aço M6 (24 unidades)
□ Arandelas plásticas
```

**Procedimento:**
```
1. Fazer furos nas placas acrílico (4 cantos + 2 centro)
2. Fixar base inferior na estrutura
3. Fixar plataforma da centrifuga (altura 10cm)
4. Fixar plataforma do aquecedor (altura 25cm)
5. Testar rigidez de cada plataforma
```

---

### FASE 2: Sistema de Centrifugação (3-4 dias)

#### Passo 1: Montar Rotor de Centrifuga

**Materiais:**
```
□ Motor DC 24V (3000-15000 RPM)
□ Acoplamento flexível
□ Rotor de alumínio (24 posições)
□ Tubo de amostras (24x)
□ Bearings ABEC-7 (2x)
□ Eixo de aço inoxidável
```

**Procedimento:**
```
1. Fixar motor na plataforma com suportes de borracha
2. Alinhar eixo do motor com centro do rotor
3. Instalar bearing inferior
4. Instalar acoplamento flexível
5. Instalar rotor de alumínio
6. Instalar bearing superior
7. Equilibrar rotor dinamicamente
   └─ Girar em baixa velocidade (1000 RPM)
   └─ Ajustar contrapeso até vibração = 0
8. Testar velocidade máxima (15.000 RPM)
```

#### Passo 2: Instalar Sensor de Velocidade

**Materiais:**
```
□ Encoder óptico (1000 PPR)
□ Roda de código (24 furos)
□ Suporte de alumínio
```

**Procedimento:**
```
1. Montar roda de código no eixo
2. Fixar sensor óptico na lateral
3. Testar leitura de velocidade
4. Calibrar encoder (deve ler 15000 RPM máx)
```

---

### FASE 3: Sistema de Aquecimento (2-3 dias)

#### Passo 1: Montar Bloco de Aquecimento

**Materiais:**
```
□ Bloco de alumínio 80x40x20mm
□ Resistência elétrica 100W (24V)
□ Sensor PT100 (±0.1°C)
□ Pasta térmica de silicone
□ Dissipador de calor (15x15cm)
```

**Procedimento:**
```
1. Fazer cavidade no bloco para resistência
   └─ Profundidade: 15mm
   └─ Diâmetro: 10mm
2. Inserir resistência com pasta térmica
3. Fazer furo para sensor PT100
   └─ Profundidade: 12mm
   └─ 5mm do centro
4. Inserir sensor PT100
5. Montar dissipador na plataforma
6. Testar temperatura (deve atingir 100°C)
```

#### Passo 2: Instalar Resfriador

**Materiais:**
```
□ Ventilador 12V (60mm)
□ Dissipador radial pequeno
□ Termostato 12V
```

**Procedimento:**
```
1. Montar dissipador radial no bloco de aquecimento
2. Fixar ventilador lateralmente
3. Conectar termostato (liga a <95°C)
4. Testar resfriamento (20°C em <2 min)
```

---

### FASE 4: Sistema de Dosagem (3-4 dias)

#### Passo 1: Montar Bomba Peristáltica

**Materiais:**
```
□ Motor 12V DC
□ Cabeça peristáltica (5 rolos)
□ Tubing silicone 2.4mm ID
□ Suporte de alumínio
```

**Procedimento:**
```
1. Montar motor no suporte
2. Acoplar cabeça peristáltica
3. Inserir tubing nos rolos
4. Testar fluxo (5µL-50µL/min)
5. Calibrar velocidade via PWM
```

#### Passo 2: Instalar Válvulas Solenóides

**Materiais:**
```
□ Válvulas solenóides 3/2 (6x)
□ Manifold de distribuição
□ Conectores rápidos
□ Tubing silicone (6m)
```

**Procedimento:**
```
1. Montar manifold na estrutura
2. Fixar 6 válvulas solenóides
   └─ V1: Entrada amostra
   └─ V2: Entrada buffer lise
   └─ V3: Entrada etanol 1
   └─ V4: Entrada etanol 2
   └─ V5: Saída final
   └─ V6: Rejeito
3. Conectar tubing de entrada/saída
4. Testar cada válvula (abertura/fechamento)
```

#### Passo 3: Montar Reservatórios

**Materiais:**
```
□ Frascos de 100mL (5x)
□ Caps com tubing de entrada
□ Sensor de nível (opcional)
□ Suporte de plástico
```

**Procedimento:**
```
1. Preparar 5 frascos:
   └─ R1: Buffer de lise (80mL)
   └─ R2: Etanol 70% (50mL)
   └─ R3: Etanol 100% (50mL)
   └─ R4: Buffer TE (20mL)
   └─ R5: Rejeito (100mL)
2. Instalar tubing de sucção em cada frasco
3. Conectar à bomba peristáltica
4. Testar sucção (sem vazamentos)
```

---

### FASE 5: Eletrônica (4-5 dias)

#### Passo 1: Montagem da Placa Principal

**Materiais:**
```
□ Raspberry Pi Zero 2W
□ Motor driver BTS7960
□ PWM driver 16 canais (PCA9685)
□ Relé 8 canais 5V
□ Conversor I2C para sensores
```

**Procedimento:**
```
1. Instalar Raspberry Pi Zero 2W em suporte
2. Conectar motor driver ao GPIO
   └─ IN1 → GPIO 17
   └─ IN2 → GPIO 27
   └─ PWM → GPIO 22
3. Conectar PWM driver via I2C
   └─ SDA → GPIO 2
   └─ SCL → GPIO 3
4. Conectar relé ao GPIO 4-11
5. Testar comunicação I2C
6. Instalar SD card com Raspberry Pi OS
```

#### Passo 2: Cabeamento de Sensores

**Materiais:**
```
□ Sensor DS18B20 (temperatura)
□ Cabo Cat5e (para dados)
□ Conectores rápidos
□ Fita isolante
```

**Procedimento:**
```
1. Conectar DS18B20 ao GPIO 26 (OneWire)
   └─ VCC → 3.3V
   └─ GND → GND
   └─ DATA → GPIO 26
2. Testar com: python3 -c "import board; import digitalio"
3. Rotular todos os cabos
4. Fazer amarrilho dos cabos
```

---

### FASE 6: Testes (2-3 dias)

#### Teste 1: Funcionalidade Mecânica

```
✓ Centrifuga atinge 15.000 RPM
✓ Rotor não vibra em alta velocidade
✓ Aquecedor atinge 100°C
✓ Resfriador volta a 20°C em <2 min
✓ Bomba dispensa 50µL/min
✓ Válvulas abrem/fecham certo
✓ Sensor de temperatura lê valores reais
```

#### Teste 2: Sistema de Controle

```
✓ Raspberry Pi comunicação OK
✓ Motor responde a comandos
✓ PWM controla velocidade
✓ Sensores leem valores
✓ Display mostra dados
✓ Botões funcionam
```

#### Teste 3: Extração em Seco

```
✓ Ciclo completo roda (sem amostra)
✓ Dosagens estão corretas
✓ Temperaturas chegam a alvo
✓ Não há vazamentos
✓ Sistema pronto para amostra real
```

---

## 🧪 PROTOCOLO DE EXTRAÇÃO

### Materiais Necessários

```
AMOSTRA: 5mL de sangue total (EDTA)
REAGENTES:
├─ Buffer de lise (80mL)
├─ Etanol 70% (50mL)
├─ Etanol 100% (30mL)
└─ Buffer TE pH 8.0 (20mL)

MATERIAL DESCARTÁVEL:
├─ Tubos de 1.5mL (24x)
├─ Dicas de pipeta (50x)
└─ Luvas nitrílicas (2 caixas)
```

### Procedimento Completo

```
PASSO 1: PREPARAÇÃO (5 min)
├─ Colocar amostra nos tubos
├─ Adicionar 200µL de buffer lise
└─ Homogeneizar

PASSO 2: LISE (10 min)
├─ Incubar a 65°C por 10 minutos
├─ Permitir lise das células
└─ Temperatura mantida automaticamente

PASSO 3: PRECIPITAÇÃO (3 min)
├─ Adicionar 300µL etanol 100%
├─ Centrifugar 10.000 RPM por 2 min
└─ DNA precipita

PASSO 4: TRANSFERÊNCIA (2 min)
├─ Transferir sobrenadante para novo tubo
├─ Pellet de DNA fica no fundo
└─ Descartar em reservatório de rejeito

PASSO 5: PRIMEIRA LAVAGEM (3 min)
├─ Adicionar 500µL etanol 70%
├─ Centrifugar 10.000 RPM por 2 min
└─ Remover sais

PASSO 6: SEGUNDA LAVAGEM (3 min)
├─ Adicionar 500µL etanol 100%
├─ Centrifugar 10.000 RPM por 2 min
└─ Remover água residual

PASSO 7: SECAGEM (5 min)
├─ Incubar a 55°C por 5 min
├─ Etanol evapora
└─ DNA seco

PASSO 8: RECOLHIMENTO (2 min)
├─ Adicionar 50µL buffer TE pH 8.0
├─ Deixar hidratar 2 min
├─ DNA em solução
└─ Pronto para uso

TEMPO TOTAL: ~30 minutos
RESULTADO: ~3-5 µg de DNA por tubo
PUREZA: A260/A280 = 1.8-2.0
CONCENTRAÇÃO: ~60-100 ng/µL
```

---

## ✅ CHECKLIST FINAL

```
ESTRUTURA:
- [ ] Frame de alumínio montado e nivelado
- [ ] Plataformas fixas e estáveis
- [ ] Sem vibração ao pressionar

CENTRIFUGA:
- [ ] Rotor balanceado (15.000 RPM)
- [ ] Sensor de velocidade calibrado
- [ ] Tubos de amostras seguros

AQUECIMENTO:
- [ ] Aquecedor atinge 100°C
- [ ] Resfriador funciona <2 min
- [ ] Sensor PT100 preciso (±0.5°C)

DOSAGEM:
- [ ] Bomba dispensa volumes corretos
- [ ] Válvulas abrem/fecham
- [ ] Sem vazamentos em tubagens

ELETRÔNICA:
- [ ] Raspberry Pi comunicação OK
- [ ] Sensores leem valores reais
- [ ] Motor responde a comandos

DISPLAY:
- [ ] LCD mostra dados
- [ ] Botões funcionam
- [ ] LEDs indicam status

TESTES:
- [ ] Ciclo em seco concluído
- [ ] Nenhum vazamento
- [ ] Sistema pronto para amostras
```

---

## 📊 ESPECIFICAÇÕES FINAIS

```
DIMENSÕES:
├─ 60 x 40 x 50 cm
├─ Peso: 15-20 kg
└─ Potência: 200W máximo

CAPACIDADE:
├─ 24 amostras simultâneas
├─ 30-45 min por ciclo
└─ ~100 ciclos/semana

PRECISÃO:
├─ Temperatura: ±0.5°C
├─ Volume: ±1%
├─ Pureza DNA: A260/A280 1.8-2.0
└─ Taxa de sucesso: 85-90%

RENDIMENTO:
├─ 3-5 µg de DNA por amostra (sangue)
├─ 10-20 µg de DNA por amostra (tecido)
└─ Pronto para PCR, sequenciamento, hibridização
```

---

## 🎓 REFERÊNCIAS

- Sambrook & Russell, "Molecular Cloning: A Laboratory Manual" (4ª ed.)
- Qiagen, QIAamp DNA Extraction Protocol
- Rohland & Hofreiter, "Ancient DNA extraction review"
- Wheeler et al., "The Complete Mitochondrial DNA Sequence"

---

**Extrator de DNA v1.0 - 2026**
*Sistema Automatizado de Extração de DNA para Síntese de Genomas*

🧬 ✨ 🔬
