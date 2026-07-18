# Arquivos Novos — Re-Dino Engine v2

## Módulos Novos Criados

### 1. **paleontology.py** (413 linhas)
Base de dados paleontológica com dados reais de dinossauros.

**Classes principais:**
- `Dinossauro` — Representa uma espécie de dinossauro
- `SistemaReferencia` — Sistema centralizado de dinossauros
- `DinosauroGrupo`, `Period` — Enumerações para classificação

**Funções:**
- `criar_sistema_referencia_padrao()` — Popula BD com 5 dinossauros bem documentados
- `obter_sistema_referencia()` — Retorna instância singleton
- `listar_dinossauros_recomendados()` — Ordena por viabilidade de reconstrução

**Dinossauros Inclusos:**
- Tyrannosaurus rex (carnívoro, 9 t)
- Velociraptor mongoliensis (carnívoro, 10 kg)
- Archaeopteryx lithographica (carnívoro, 1 kg, transitório)
- Triceratops horridus (herbívoro, 6 t)
- Brachiosaurus altithorax (herbívoro, 60 t)

---

### 2. **dinosaur_selector.py** (280 linhas)
Motor de seleção automática de qual dinossauro reconstruir.

**Classes principais:**
- `CapacidadeHardware` — Enum com níveis: NENHUMA, BASICA, INTERMEDIARIA, AVANCADA
- `ConfiguracaoSelecao` — Parâmetros de preferência (dieta, tamanho, período)
- `SeletorDinossauro` — Engine de scoring + recomendação

**Funções principais:**
- `selecionar()` — Escolhe 1 dinossauro (score 0-1)
- `recomendar_multiplos()` — Retorna top N dinossauros
- `_score_compatibilidade_hardware()` — Avalia hardware vs características
- `_score_preferencias()` — Avalia aderência às preferências

**Algoritmo:**
- Score = (compatibilidade_hardware × score_preferencias) × bonus_tamanho
- Prioriza dinossauros com genoma mais conservado se hardware limitado

---

### 3. **descendant_mapper.py** (356 linhas)
Mapeia aves e crocodilianos vivos → características ancestrais preservadas.

**Classes principais:**
- `CaracteristicaAncestral` — Enum: OSSOS_OCOS, PENAS, GARRA_SICLE, VISAO_BINOCULAR, etc.
- `EspecieDescendente` — Representa uma ave/crocodiliano moderno
- `MapeadorDescendentes` — Sistema centralizado de mapeamento

**Funções principais:**
- `buscar_por_ancestral()` — Retorna descendentes vivos de um dinossauro
- `buscar_por_caracteristica()` — Retorna espécies que preservam uma característica
- `encontrar_melhor_referencia()` — Seleciona melhor espécie para NCBI
- `obter_mapeador()` — Retorna instância singleton

**Descendentes Inclusos:**
- Gallus gallus (galinha, 95/98 score)
- Struthio camelus (avestruz, 88/85 score)
- Falco peregrinus (falcão-peregrino, 82/78 score)
- Accipiter nisus (gavião-pequeno, 78/72 score)
- Crocodylus niloticus (jacaré-do-nilo, 92/96 score)
- Crocodylus acutus (crocodilo-americano, 85/88 score)

---

### 4. **ollama_integration.py** (300 linhas)
Cliente para integração com Ollama local (sem APIs externas).

**Classes principais:**
- `OllamaModeloRecomendado` — Enum: LLAMA2, MISTRAL, NEURAL_CHAT
- `ConfiguracaoOllama` — Parâmetros de conexão e comportamento
- `ClienteOllama` — Cliente HTTP para Ollama

**Funções principais:**
- `validar_conexao()` — Verifica se Ollama está acessível
- `listar_modelos_disponiveis()` — Lista modelos já baixados
- `gerar_texto()` — Gera texto (simples ou streaming)
- `embeddings()` — Gera representação vetorial
- `obter_cliente_ollama()` — Retorna instância singleton

**Features:**
- Retry com backoff exponencial
- Streaming de respostas
- Timeout configurável
- Rate limiting respeitado

---

### 5. **paleonto_data.json** (250 linhas)
Arquivo de dados estruturados em JSON com informações paleontológicas.

**Seções:**
- `dinossauros` — 5 dinossauros com metadados completos
- `descendentes_vivos` — 6 espécies modernas com anotações NCBI
- `caracteristicas_filogenticas` — Mapeamento de características ancestrais
- `referencias_paleontologos` — Referências a cientistas-chave
- `recomendacoes_reconstrucao` — Guia por nível de hardware

**Uso:** Fonte de dados para validação, logging, e recomendações

---

## Arquivos Refatorados (Novas Dependências)

### 1. **ai_report.py** (150 linhas → 110 linhas)
**Antes:** Usava API da Anthropic (precisava de ANTHROPIC_API_KEY)  
**Depois:** Usa Ollama local (sem dependências externas)

**Mudanças:**
- ❌ Removido: `import anthropic`
- ✅ Adicionado: `from ollama_integration import ClienteOllama, ...`
- ✅ Nova função: `gerar_relatorio_com_ollama()`
- ✅ Mantém retrocompatibilidade: `generate_lab_report()` como wrapper

**Benefício:** Zero dependências de API externas

---

### 2. **ncbi_reference.py** (120 linhas → 220 linhas)
**Antes:** Busca simples por espécie/gene  
**Depois:** Integrado com genealogia de descendentes

**Mudanças:**
- ✅ Nova função: `buscar_painel_referencia_por_paleontologia()`
- ✅ Seleciona automaticamente descendentes usando `descendant_mapper`
- ✅ Prioriza por qualidade genômica
- ✅ Adiciona metadados genealógicos às referências
- ✅ Mantém interface retrocompatível com aliases

**Benefício:** Recomendações inteligentes automáticas

---

### 3. **main.py** (120 linhas → 350 linhas)
**Antes:** Requer --scanner-file e --target-label obrigatórios  
**Depois:** Seleção automática de dinossauro, sem hardware opcional

**Mudanças:**
- ✅ Novo passo 1: Seleção automática ou manual de dinossauro
- ✅ Scanner agora opcional (--scanner-file)
- ✅ Novas flags: --dinosaur, --preferencia-*, --hardware, --modelo-ollama
- ✅ Integrado com `dinosaur_selector`, `descendant_mapper`, `ollama_integration`
- ✅ Melhor logging e resumo final
- ✅ 6 passos (antes 5) com nomes claros

**Benefício:** Modo totalmente automático sem hardware

---

## Documentação Nova

### 1. **README.md** (Expandido)
**Antes:** ~80 linhas  
**Depois:** ~250 linhas

**Novos conteúdos:**
- Seção "Novidades v2" com 3 principais melhorias
- Arquitetura modular com diagrama
- Modo 1-4: Exemplos de uso (Seleção Automática, Preferências, Hardware Real, IA)
- Tabela de dinossauros disponíveis
- Tabela de genes recomendados
- Guia de próximos passos em laboratório (~$50-500k, 2-5 anos)

---

### 2. **QUICKSTART.md** (100 linhas) — NOVO
Guia de 5 minutos para começar.

**Conteúdos:**
- Instalação rápida de dependências
- Setup de Ollama
- Teste rápido com um comando único
- 4 exemplos prontos para copiar/colar
- Tabela de modelos Ollama
- Troubleshooting common

---

### 3. **ollama_config_example.md** (200 linhas) — NOVO
Guia completo de configuração e troubleshooting do Ollama.

**Conteúdos:**
- Instalação para Linux/macOS
- Modelos recomendados
- Verificação de modelos instalados
- Configurações avançadas
- Otimizações por hardware
- Troubleshooting detalhado
- Testes de saúde

---

### 4. **ARQUIVOS_NOVOS.md** (Este arquivo) — NOVO
Inventário de mudanças na arquitetura.

---

## Estrutura de Diretórios Atualizada

```
re-gen/
├── main.py                          [REFATORADO] Orquestrador principal
├── paleontology.py                  [NOVO] BD de paleontologia
├── dinosaur_selector.py             [NOVO] Motor de seleção automática
├── descendant_mapper.py             [NOVO] Genealogia de descendentes
├── ollama_integration.py            [NOVO] Cliente Ollama local
├── paleonto_data.json               [NOVO] Dados paleontológicos JSON
├── ncbi_reference.py                [REFATORADO] Busca integrada com genealogia
├── ai_report.py                     [REFATORADO] Agora usa Ollama
├── reconstruct.py                   [SEM MUDANÇAS] Reconstrução ancestral
├── gene_edit_package.py             [SEM MUDANÇAS] Pacote de edição genética
├── scanner_input.py                 [SEM MUDANÇAS] Leitura de FASTQ/FASTA
├── mock_refs.py                     [SEM MUDANÇAS] Dados mock para testes
├── README.md                        [EXPANDIDO] Documentação principal
├── QUICKSTART.md                    [NOVO] Guia rápido (5 min)
├── ollama_config_example.md         [NOVO] Guia de Ollama
├── ARQUIVOS_NOVOS.md                [NOVO] Este arquivo
└── re_dino_output/                  [DIRETÓRIO DE SAÍDA]
    ├── sequencia_reconstruida.fasta
    ├── pacote_edicao_re_dino.csv
    └── laudo_ia.txt
```

---

## Resumo de Mudanças

| Aspecto | Antes | Depois |
|--------|-------|--------|
| **Hardware** | Obrigatório | Opcional |
| **IA** | API Anthropic (externa) | Ollama (local) |
| **Seleção de Dinossauro** | Manual (--target-label) | Automática + preferências |
| **Descendentes** | Lista fixa | Seleção inteligente por genealogia |
| **Modularização** | 8 arquivos | 13 arquivos (5 novos) |
| **Linhas de Código** | ~1000 | ~2500 |
| **Documentação** | README.md | README + QUICKSTART + CONFIG |
| **Dependências Externas** | anthropic, biopython | biopython, requests |
| **API Keys Necessárias** | ANTHROPIC_API_KEY | Apenas NCBI (obrigatório antes já) |

---

## Retrocompatibilidade

✅ **Mantida para:**
- `ncbi_reference.fetch_reference_panel()` → alias para `buscar_painel_referencia()`
- `ai_report.generate_lab_report()` → wrapper para novo `gerar_relatorio_com_ollama()`
- Todos os módulos base (reconstruct, gene_edit_package, scanner_input)

❌ **Quebrada para:**
- `main.py` agora tem interface diferente (mas é mais flexível)
- Removido `--target-label` (agora automático via `--dinosaur` ou seleção)

---

## Como Usar os Novos Módulos

### Importar Seletor
```python
from dinosaur_selector import SeletorDinossauro, ConfiguracaoSelecao, CapacidadeHardware
seletor = SeletorDinossauro()
dino, score = seletor.selecionar(ConfiguracaoSelecao(hardware=CapacidadeHardware.NENHUMA))
```

### Importar Mapeador
```python
from descendant_mapper import obter_mapeador
mapeador = obter_mapeador()
descendentes = mapeador.buscar_por_ancestral("Tyrannosaurus rex")
```

### Importar Ollama
```python
from ollama_integration import obter_cliente_ollama
cliente = obter_cliente_ollama()
resposta = cliente.gerar_texto("Sua pergunta aqui")
```

### Usar Busca Inteligente
```python
from ncbi_reference import buscar_painel_referencia_por_paleontologia
from paleontology import obter_sistema_referencia
sr = obter_sistema_referencia()
dino = sr.buscar_por_nome("Tyrannosaurus rex")
painel = buscar_painel_referencia_por_paleontologia(dino, "cytochrome b", seu_email)
```

---

## Próximos Passos Possíveis

1. ✅ **v2.0** — Atual (Ollama + Seleção + Genealogia)
2. 🔄 **v2.1** — Cache de NCBI (evita buscas repetidas)
3. 🔄 **v2.2** — UI web (Streamlit/Gradio)
4. 🔄 **v2.3** — Support para múltiplos genes (pipeline paralelo)
5. 🔄 **v3.0** — Genoma completo (integração com SPAdes)

---

**Data:** Julho 2026  
**Versão:** 2.0  
**Status:** ✅ Completo e funcional
