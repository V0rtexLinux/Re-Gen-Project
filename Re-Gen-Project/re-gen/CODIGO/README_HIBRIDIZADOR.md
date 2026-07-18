# 🧬 Hibridizador DNA 3000 - Sistema de Controle

Sistema completo de hibridização de DNA para síntese de genomas híbridos em projeto Re-Dino.

## 📦 Componentes

### 1. **hibridizador_core.py**
Motor principal do hibridizador
- `Hibridizador()`: Controlador principal
- `ModeloReacao()`: Modelagem matemática da reação
- Estados: DESLIGADO, PRONTO, AQUECENDO, RESFRIANDO, EM_REAÇÃO, CICLO_LIMPEZA, ERRO
- Threads de monitoramento contínuo

**Principais métodos:**
```python
hibridizador = Hibridizador()
hibridizador.ligar()                                    # Ligar sistema
hibridizador.configurar_parametros({...})              # Configurar parâmetros
hibridizador.iniciar_reacao()                          # Iniciar reação
hibridizador.obter_status()                            # Obter status atual
hibridizador.exportar_dados_reacao()                   # Exportar resultados
hibridizador.desligar()                                # Desligar
```

### 2. **hibridizador_hardware.py**
Simulador de hardware (sensores e atuadores)

**Sensores:**
- `SensorTemperatura`: DS18B20 (±0.5°C)
- `SensorPH`: Digital (±0.1 pH)
- `SensorCondutividade`: 0-20 mS/cm
- `SensorTurbidez`: Óptico (0-1000 NTU)

**Atuadores:**
- `BombaPeristaltica`: 1-50 mL/min
- `Aquecedor`: 20-45°C (500W)
- `Resfriador`: Ventilador
- `LEDRGB`: 10W ajustável
- `ValvulaSolenoide`: 5 válvulas (entrada/saída)

**Controles:**
- `BotaoRGB`: 16 botões com LED integrado (4x4)
- `EncoderRotativo`: 2 encoders (temperatura, velocidade)

**Uso básico:**
```python
hardware = ControladorHardware()
hardware.iniciar()                          # Iniciar simulação

# Controlar temperatura
hardware.ligar_aquecedor(37.5)

# Controlar bomba
hardware.set_velocidade_bomba(75)           # 75%
hardware.ligar_bomba()

# Obter leituras
status = hardware.obter_status_completo()
print(status['sensores'])
```

### 3. **hibridizador_gui.py**
Interface gráfica PyQt5 com 2 "monitores LCD"

**Monitores:**
- **Monitor LCD Esquerdo**: Parâmetros (temperatura, pH, condutividade, progresso)
- **Monitor LCD Direito**: Análise de DNA (gráficos, concentrações)

**Painel de Controle:** 16 botões RGB (4x4 grid)

```bash
# Executar GUI
python3 hibridizador_gui.py
```

### 4. **run_hibridizador.py**
Script de launcher com múltiplos modos

## 🚀 COMO USAR

### Modo 1: Interface Gráfica (GUI)

```bash
cd CODIGO/
python3 run_hibridizador.py --gui
```

**Funcionalidades:**
- Monitores LCD simulados (10.1" cada)
- Painel de controles com 16 botões RGB
- Gráficos em tempo real
- Visualização da câmara central
- Todos os parâmetros monitoráveis

**Controles (Botões):**
```
FILA 1 (Sistema):
  [1] Liga/Desliga (Vermelho)
  [2] Iniciar Processo (Azul)
  [3] Pausa (Amarelo)
  [4] Reset (Vermelho)

FILA 2 (Parâmetros):
  [5] Aumentar Temperatura (Laranja)
  [6] Diminuir Temperatura (Cyan)
  [7] Aumentar Velocidade (Roxo)
  [8] Diminuir Velocidade (Pink)

FILA 3 (Modo):
  [9] Manual (Verde)
  [10] Automático (Azul)
  [11] Calibrar (Amarelo)
  [12] Diagnóstico (Branco)

FILA 4 (Dados):
  [13] Salvar (Verde)
  [14] Carregar (Azul)
  [15] Exportar (Amarelo)
  [16] Menu Avançado (Roxo)
```

### Modo 2: Terminal (Sem GUI)

```bash
python3 run_hibridizador.py --terminal -t 37.5 -d 4 -v 75

Parâmetros:
  -t, --temperatura    Temperatura alvo em °C (padrão: 37.5)
  -d, --duracao        Duração em minutos (padrão: 4)
  -v, --velocidade     Velocidade bomba em % (padrão: 75)
```

**Exemplo:**
```bash
# Reação de 3 horas a 37°C, 80% de bomba
python3 run_hibridizador.py --terminal -t 37 -d 180 -v 80
```

**Saída:**
```
🧬 HIBRIDIZADOR DNA 3000 - MODO TERMINAL
[✓] Sistema ligado
[✓] Parâmetros configurados
[▶] Iniciando reação...

[📊] Monitorando reação:
Tempo      Temp        pH         Progresso    DNA-H
00:00      37.0°C      7.1        0.1%         0.02 µM
00:02      37.0°C      7.1        5.2%         0.15 µM
...
✓ REAÇÃO CONCLUÍDA COM SUCESSO!
```

### Modo 3: Diagnóstico

```bash
python3 run_hibridizador.py --diagnostico
```

**Testa:**
- Sensores (temperatura, pH, condutividade, turbidez)
- Atuadores (aquecedor, bomba, resfriador)
- LED RGB (todas as cores)

### Modo 4: Calibração

```bash
python3 run_hibridizador.py --calibracao
```

**Procedimento:**
1. Coloque sensores de referência
2. Leia valores atuais
3. Ajuste no código se necessário

---

## 📊 PROTOCOLO DE HIBRIDIZAÇÃO

### Pré-requisitos
```
DNA-A: 100-500 ng/µL (puro, RNA-free)
DNA-B: 100-500 ng/µL (puro, RNA-free)
Buffer: TE pH 8.0 ou similar
Temperatura: 37°C (ótima para síntese)
```

### Passo 1: INICIALIZAR
```python
hibridizador = Hibridizador()
hardware = ControladorHardware()
hibridizador.set_hardware(hardware)

hardware.iniciar()
hibridizador.ligar()        # Aquecedor ligado, esperando 2-3 min
```

### Passo 2: CONFIGURAR PARÂMETROS
```python
hibridizador.configurar_parametros({
    "temperatura_alvo": 37.5,       # °C
    "duracao_reacao": 14400,        # 4 horas em segundos
    "velocidade_bomba": 75.0        # %
})
```

### Passo 3: INJETA AMOSTRAS
```python
# Simular injeção
hardware.abrir_valvula(1)           # DNA-A
time.sleep(1)
hardware.fechar_valvula(1)

hardware.abrir_valvula(2)           # DNA-B
time.sleep(1)
hardware.fechar_valvula(2)

hardware.abrir_valvula(3)           # Reagentes
time.sleep(1)
hardware.fechar_valvula(3)
```

### Passo 4: INICIAR REAÇÃO
```python
hibridizador.iniciar_reacao()
```

### Passo 5: MONITORAR
```python
while hibridizador.reacao_ativa:
    status = hibridizador.obter_status()
    print(f"Progresso: {status['dados_reacao']['progresso_percentual']:.1f}%")
    time.sleep(5)
```

### Passo 6: RESULTADO
```python
dados = hibridizador.exportar_dados_reacao()
print(f"DNA Hibridizado Final: {dados['resultado_final']['DNA_hibridizado_final']} µM")
```

### Passo 7: LIMPEZA
```python
hibridizador.resetar_sistema()      # Esterilização 95°C + resfriamento
```

---

## 📈 MODELO MATEMÁTICO

A reação de hibridização segue cinética de segunda ordem:

```
d[DNA-H]/dt = k1 * [DNA-A] * [DNA-B] * exp(-Ea/RT) - k-1 * [DNA-H]

Parâmetros:
- k1: Taxa de associação (0.001 s⁻¹)
- k-1: Taxa de desnaturação (0.0002 s⁻¹)
- Ea: Energia de ativação (50 kJ/mol)
- T: Temperatura absoluta (K)
```

**Resultado esperado** (37.5°C, 4 horas):
```
DNA Hibridizado: ~180-200 µM
DNA-A restante: ~10-20 µM
DNA-B restante: ~10-20 µM
Eficiência: ~90-95%
```

---

## 🔧 ESTRUTURA DE DADOS

### SensorLeitura
```python
{
    "temperatura": 37.5,        # °C
    "pH": 7.4,                  # Unidades pH
    "condutividade": 12.3,      # mS/cm
    "turbidez": 0.5,            # NTU
    "timestamp": "2024-07-14T15:30:45"
}
```

### DadosReacao
```python
{
    "DNA_A_livre": 95.5,        # µM
    "DNA_B_livre": 94.2,        # µM
    "Complexo_AB": 2.3,         # µM
    "DNA_hibridizado": 180.5,   # µM
    "progresso_percentual": 89.5,   # %
    "tempo_decorrido": 3240     # segundos
}
```

### ResultadoFinal
```python
{
    "status": "sucesso",
    "DNA_hibridizado_final": 195.3,
    "DNA_A_restante": 12.1,
    "DNA_B_restante": 11.8,
    "temperatura_media": 37.48,
    "pH_final": 7.42,
    "timestamp_conclusao": "2024-07-14T19:30:45"
}
```

---

## 💾 EXPORTAÇÃO DE DADOS

Dados são exportados em JSON:

```json
{
  "timestamp": "2024-07-14T19:30:45",
  "parametros": {
    "temperatura_alvo": 37.5,
    "duracao_reacao": 14400,
    "velocidade_bomba": 75.0,
    ...
  },
  "resultado_final": {
    "DNA_hibridizado_final": 195.3,
    ...
  },
  "historico_sensores": [
    {"temperatura": 37.50, "pH": 7.41, ...},
    ...
  ]
}
```

**Salvo em:**
```
hibridizacao_YYYYMMDD_HHMMSS.json
```

---

## 🐛 TROUBLESHOOTING

### Problema: "ModuleNotFoundError: No module named 'PyQt5'"
**Solução:**
```bash
pip3 install PyQt5
```

### Problema: Temperatura não aumenta
**Verificar:**
```python
# Diagnóstico
python3 run_hibridizador.py --diagnostico
# Verificar leitura do sensor
```

### Problema: Reação não inicia
**Verificar:**
```python
status = hibridizador.obter_status()
print(status['estado'])  # Deve ser 'pronto'
```

### Problema: Dados não salvam
**Verificar permissões:**
```bash
ls -la CODIGO/
chmod 755 CODIGO/
```

---

## 📚 REFERÊNCIAS

- **Cinética química**: Levine, Physical Chemistry (6ª ed.)
- **DNA synthesis**: Gillespie & Myers, Molecular Cloning (4ª ed.)
- **PyQt5**: Qt Documentation, Riverbank Computing
- **Control systems**: Åström & Murray, Feedback Systems

---

## ✅ CHECKLIST DE INSTALAÇÃO

```
- [ ] Python 3.8+
- [ ] pip3 install PyQt5 numpy scipy opencv-python
- [ ] Arquivos baixados em CODIGO/
- [ ] Permissões de execução: chmod +x run_hibridizador.py
- [ ] Teste: python3 run_hibridizador.py --gui
- [ ] Diagnóstico: python3 run_hibridizador.py --diagnostico
```

---

**Re-Dino Hibridizador v1.0 - 2026**
*Sistema de Hibridização de DNA para Síntese de Genomas Híbridos*

🧬 ✨ 🔬
