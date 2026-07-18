# Re-Dino Engine v2 — Quick Start

## 1. Visão Geral Rápida

Este guia mostra como iniciar o Re-Dino Engine em modo de software e hardware, montar os principais dispositivos, posicioná-los no laboratório, e escolher dinossauros iniciais.

O fluxo completo é:
1. Seleção do dinossauro
2. Reconstrução do genoma ancestral
3. Síntese de DNA líquido
4. Injeção no embrião
5. Monitoramento da incubação

O código central de orquestração está em:
- `CODIGO/hardware_orchestrator.py`
- `CODIGO/hardware_devices.py`
- `CODIGO/dna_to_dinosaur_pipeline.py`

O hardware principal é composto por:
- `DNA Synthesizer` (`CODIGO/dna_synthesizer_device.py`)
- `Embryo Injector` (`CODIGO/embryo_injector_device.py`)
- `Incubator` (`CODIGO/incubator_device.py`)

---

## 2. Instalar Dependências de Software

### 2.1 Passo rápido

```bash
cd /path/to/re-gen
pip install biopython requests --break-system-packages
```

### 2.2 Instalar Ollama (opcional)

Se você quer gerar relatórios de IA:

```bash
curl https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama2
```

### 2.3 Obter NCBI API Key

O NCBI exige email real e recomenda API key.
1. Acesse https://www.ncbi.nlm.nih.gov/account/
2. Crie conta gratuita
3. Gere API key em `Account Settings`
4. Salve em local seguro

---

## 3. Executar o Pipeline Básico

### 3.1 Teste rápido de 5 minutos

```bash
cd /path/to/re-gen/re-gen/CODIGO
python main.py \
    --gene "cytochrome b" \
    --host-species "Struthio camelus" \
    --ncbi-email seu.email@dominio.com \
    --ncbi-api-key SUA_CHAVE_NCBI
```

O que acontece:
- Seleção do dinossauro
- Busca de referências NCBI
- Reconstrução do genoma ancestral
- Geração de pacote de edição genética

### 3.2 Rodar com hardware real

```bash
python main.py \
    --scanner-file /mnt/minion/run_001.fastq \
    --dinosaur "Tyrannosaurus rex" \
    --gene "cytochrome b" \
    --host-species "Struthio camelus" \
    --ncbi-email seu.email@dominio.com
```

### 3.3 Gerar relatório de IA

```bash
python main.py \
    --gene "COI" \
    --host-species "Falco peregrinus" \
    --ncbi-email seu.email@dominio.com \
    --gerar-relatorio-ia
```

---

## 4. Conceito de Arquitetura do Sistema

### 4.1 Arquitetura lógica

O sistema foi organizado em camadas:
- `main.py`: interface de entrada e seleção
- `dna_to_dinosaur_pipeline.py`: pipeline completo e coordenação do processo
- `hardware_orchestrator.py`: orquestrador de hardware que conecta os dispositivos
- `hardware_devices.py`: fábrica de dispositivos e ordem de inicialização
- `device_base.py`: classe base comum

### 4.2 Fluxo de hardware

1. `HardwareOrchestrator` inicializa:
   - `synthesizer`
   - `injector`
   - `incubator`
2. `DNA Synthesizer` prepara e sintetiza o DNA
3. `Embryo Injector` calibra, encontra núcleo e injeta
4. `Incubator` recebe notificação de injeção e monitora

### 4.3 Por que essa arquitetura faz sentido

- Centraliza o controle em um único orquestrador
- Separa responsabilidades de cada dispositivo
- Permite adicionar mais dispositivos no futuro
- Facilita debug e shutdown ordenado

---

## 5. Checklist de Hardware

### 5.1 Dispositivos essenciais

- **DNA Synthesizer** (síntese líquida)
  - Bomba peristáltica para cada nucleotídeo
  - Válvulas solenóides
  - Câmara de reação com aquecimento e agitação
  - Sensores de temperatura e pH

- **Embryo Injector**
  - Robô XYZ ou SCARA para posicionar agulha
  - Microscópio ou câmera para visão do embrião
  - Microinjetor com controle de volume nL
  - Plataformas de ovo e suporte de manipulação

- **Incubator**
  - Câmara isolada com controle de temperatura e umidade
  - Arduino/placa de controle serial
  - Sensores de temperatura, umidade e posição
  - Ventilador e sistema de aquecimento

- **Controle / Música de integração**
  - Raspberry Pi Zero 2W para rodar Python
  - Fonte 5V e 12V
  - Cabos USB e serial para Arduino
  - Relés, drivers e protoboard

### 5.2 Dispositivos adicionais recomendados

- `FossilGrinderDevice` e `FossilCleanerDevice` para manuseio de amostras
- `DinoVeterinarySyringeDevice` para suporte veterinário
- `EnvironmentalMonitorDevice` para leitura de ambiente
- `LabSafetyDevice` para emergências e alarmes

---

## 6. Instruções de Montagem dos Dispositivos

### 6.1 Montar o DNA Synthesizer

1. Fixe a estrutura em uma bancada estável.
2. Instale os reservatórios de reagentes no topo.
3. Coloque as bombas peristálticas em linha.
4. Conecte as válvulas solenóides entre bombas e câmara de reação.
5. Prepare a câmara de reação com barra magnética e isolamento.
6. Ligue sensores DS18B20 e pH ao Raspberry Pi.
7. Teste o fluxo com água destilada antes de usar reagentes.

### 6.2 Montar o Embryo Injector

1. Posicione o microscópio à frente do operador.
2. Monte o manipulador XYZ ou braço robótico ao lado do ovo.
3. Fixe o suporte de ovo centralizado sob a agulha.
4. Instale a câmera USB no microscópio ou posição de visão clara.
5. Conecte os drivers de motor ao Raspberry Pi / controlador.
6. Calibre movimentos em X, Y e Z com percurso curto.

### 6.3 Montar a Incubadora

1. Escolha local com ventilação e ausência de luz direta.
2. Construa uma câmara isolante com portas de acesso.
3. Instale sensores de temperatura/umidade internamente.
4. Coloque o Arduino em um local seco e acessível.
5. Garanta caminho de comunicação serial/USB para o Pi.
6. Teste o aquecimento e a circulação antes de usar ovos.

---

## 7. Posicionamento no Espaço de Trabalho

### 7.1 Disposição recomendada

- **Esquerda:** `DNA Synthesizer`
- **Centro:** `Embryo Injector` + microscópio
- **Direita:** `Incubator`
- **Frente:** monitor / teclado / Raspberry Pi
- **Trás:** cabos organizados e ventilação

### 7.2 Regras de posição

- Mantenha o `DNA Synthesizer` longe de poeira e vibrações.
- Posicione o `Embryo Injector` onde o operador enxergue a câmera com conforto.
- Deixe o `Incubator` isolado para estabilidade térmica.
- Use um tapete antiestático sob eletrônica sensível.
- Reserve espaço livre para acesso e manutenção.

### 7.3 Sugestões para o laboratório

- Mesa larga e firme
- Cadeira ergonômica ajustável
- Iluminação indireta suave
- Controle de temperatura ambiente entre 20-25°C

---

## 8. Sugestões de Dinossauros para Começar

### 8.1 Melhores escolhas iniciais

- `Tyrannosaurus rex` — ícone clássico, ideal para demonstração
- `Velociraptor mongoliensis` — tamanho médio, rápido e conhecido
- `Triceratops horridus` — herbívoro robusto, bom para simular adaptação
- `Stegosaurus stenops` — dinossauro amigável para testes conceptuais

### 8.2 Selecione com base no hardware

- **Hardware básico**: escolha espécies menores e mais simples, como `Velociraptor` ou `Compsognathus`.
- **Hardware intermediário**: use `Triceratops`, `Stegosaurus` ou `Ankylosaurus`.
- **Hardware avançado**: tente `Tyrannosaurus rex`, `Spinosaurus` ou `Carnotaurus`.

### 8.3 Observações de compatibilidade

- O pipeline aceita seleção automática; use `--hardware intermedia` para balancear.
- Espécies com maiores genomas podem levar mais tempo.
- Use `--dinosaur` apenas se quiser pular a seleção automática.

---

## 9. Executando o Hardware de Orquestração

### 9.1 Teste de inicialização rápida

```bash
cd /path/to/re-gen/re-gen/CODIGO
python hardware_orchestrator.py
```

Esse comando:
- inicializa todos os dispositivos do `hardware_devices.py`
- faz `ping` na incubadora
- tenta preparar síntese, injeção e monitoramento

### 9.2 Validar cada dispositivo

- `DNA Synthesizer`: deve passar por `initialize()` e preparar mix
- `Embryo Injector`: deve calibrar e preparar injeção
- `Incubator`: deve responder a `ping()` e exibir status

### 9.3 Verificar logs

O orquestrador imprime eventos e erros na tela. Se algo falhar, revise:
- `hardware_orchestrator.py`
- `hardware_devices.py`
- `device_base.py`

---

## 10. Solução de Problemas Rápida

### Problema: `Ollama não está acessível`

```bash
ollama serve
ollama ls
```

### Problema: `Erro de conexão com incubadora`

- Verifique cabo USB/serial
- Confira port name (`/dev/ttyUSB0` ou `/dev/ttyACM0`)
- Garanta que o Arduino esteja ligado

### Problema: `Falha na inicialização do injetor`

- Reinicie o robô XYZ
- Verifique drivers dos motores
- Refaça calibração em `EmbryoInjectorDevice.initialize()`

### Problema: `Volume de DNA insuficiente`

- Use mais reagente na mistura dNTP
- Verifique fluxo de bombas peristálticas
- Confira válvulas e tubagem

---

## 11. Próximos Passos

1. Leia `README.md` para entender o sistema completo.
2. Use `main.py --help` para descobrir opções de seleção e hardware.
3. Explore `GUIAS/GUIA_ROBO_SINTESE_DNA.md`, `GUIAS/GUIA_ROBO_INJECAO_GENOMA.md` e `GUIAS/INCUBADORA_CONSTRUCAO_COMPLETA.md`.
4. Adicione seus próprios dispositivos em `hardware_devices.py`.

---

**Comece agora:**

```bash
python main.py --gene "cytochrome b" --host-species "Struthio camelus" --ncbi-email seu.email@dominio.com
```
