# Arquitetura — Re-Dino Engine v2

## Diagrama de Fluxo

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRADA DO USUÁRIO                        │
│  (--gene, --host-species, --ncbi-email, opções de dinossauro)   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PASSO 1: SELEÇÃO DE DINOSSAURO                                 │
│  ────────────────────────────────                               │
│  • Se --dinosaur fornecido → usa direto (paleontology.py)       │
│  • Senão → seletor automático (dinosaur_selector.py):           │
│    - Score compatibilidade (hardware + características)          │
│    - Score preferências (dieta, tamanho, período)               │
│    - Resultado: 1 dinossauro selecionado + score de confiança    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PASSO 2: LEITURA DE SEQUENCIADOR (opcional)                    │
│  ────────────────────────────────────                           │
│  • Se --scanner-file → carrega FASTQ/FASTA (scanner_input.py)   │
│  • Senão → usa âncora sintética (descend entes como fonte)       │
│  • Output: "best_read" (sequência de DNA) + scanner_summary     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PASSO 3: BUSCA INTELIGENTE DE DESCENDENTES                     │
│  ────────────────────────────────────────────                   │
│  • Pega dinossauro do passo 1                                    │
│  • Consulta descendant_mapper.py:                               │
│    - Busca aves/crocodilianos que descendem desse dinossauro    │
│    - Filtra por característica (opcional)                        │
│    - Ordena por score de utilidade genômica                     │
│  • Para cada descendente, busca NCBI (ncbi_reference.py):       │
│    - Busca gene específico (--gene)                             │
│    - Respeita rate limit, retry com backoff                     │
│  • Output: painel de referências ordenado por qualidade         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PASSO 4: RECONSTRUÇÃO ANCESTRAL                                │
│  ──────────────────────────────────                             │
│  • Alinha best_read (fossil) vs painel de referências           │
│    - Usa Needleman-Wunsch (Bio.Align.PairwiseAligner)           │
│  • Consenso por maioria ponderado (reconstruct.py):            │
│    - Coluna por coluna                                          │
│    - Voto duplo pro dado fossil (mais confiável)               │
│  • Output: sequência consenso + confiança por base              │
│           + regiões de baixa confiança (< 60%)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PASSO 5: PACOTE DE EDIÇÃO GENÉTICA                             │
│  ──────────────────────────────────                             │
│  • Busca sequência do hospedeiro (--host-species)               │
│  • Compara reconstruído vs hospedeiro (gene_edit_package.py):   │
│    - Diferenças (SNPs, indels)                                  │
│    - Mapeia para posições de CRISPR                            │
│  • Output: CSV com edições propostas                            │
│           + % de identidade genômica                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PASSO 6: LAUDO COM IA (opcional)                               │
│  ────────────────────────────────                               │
│  • Se --gerar-relatorio-ia:                                      │
│    - Valida conexão com Ollama (ollama_integration.py)          │
│    - Envia prompt técnico ao LLM                                │
│    - Ollama gera laudo de 300 palavras                          │
│  • Output: laudo_ia.txt com análise profissional                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SAÍDAS GERADAS                              │
│  ────────────────────────────────────                           │
│  1. sequencia_reconstruida.fasta                                │
│     └─ Enviar para síntese de DNA (Twist, IDT)                 │
│  2. pacote_edicao_re_dino.csv                                   │
│     └─ Importar em Benchling/CHOPCHOP para CRISPR              │
│  3. laudo_ia.txt (opcional)                                     │
│     └─ Documentação técnica                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Dependências Entre Módulos

```
main.py (orquestrador)
├──> paleontology.py (dados estáticos)
│    └──> paleonto_data.json (fonte de dados)
├──> dinosaur_selector.py (seleção automática)
│    └──> paleontology.py
├──> descendant_mapper.py (genealogia)
│    └──> paleonto_data.json (implícito)
├──> ncbi_reference.py (busca NCBI)
│    └──> descendant_mapper.py (seleção inteligente)
│    └──> paleontology.py (tipo Dinossauro)
├──> reconstruct.py (alinhamento + consenso)
│    └──> Bio (Biopython)
├──> gene_edit_package.py (edições genéticas)
├──> scanner_input.py (leitura FASTQ)
├──> ai_report.py (laudo IA)
│    └──> ollama_integration.py (cliente Ollama)
│        └──> requests (HTTP)
└──> ollama_integration.py (cliente Ollama)
     └──> requests (HTTP)
```

## Fluxo de Dados

```
┌──────────────────────────────────────────────────────────┐
│ scanner_input.py                                         │
│ ─────────────────                                        │
│ FASTQ/FASTA → [parse] → list[Read] → summarize_reads()  │
│                                    → dict[str, Any]      │
└──────────────────────────────────────────────────────────┘
          │
          │ best_read.sequence
          ▼
┌──────────────────────────────────────────────────────────┐
│ reconstruct.py                                           │
│ ────────────────                                        │
│ ancestral_seq + panel[ReferenceSequence]                │
│ → [Needleman-Wunsch] → ReconstructionResult             │
│   • consensus_sequence: str                             │
│   • per_base_confidence: list[float]                    │
│   • mean_confidence: float                              │
│   • gc_content: float                                   │
└──────────────────────────────────────────────────────────┘
          │
          │ ReconstructionResult
          ▼
┌──────────────────────────────────────────────────────────┐
│ gene_edit_package.py                                    │
│ ────────────────────────                               │
│ reconstruction + host_sequence → [diff] → EditPackage   │
│   • n_total_edits: int                                  │
│   • pct_genome_identity: float                          │
│   • edits: list[GeneticEdit]                           │
└──────────────────────────────────────────────────────────┘
          │
          │ EditPackage + ReconstructionResult
          ▼
┌──────────────────────────────────────────────────────────┐
│ ai_report.py (via ollama_integration.py)                │
│ ────────────────────────────────────────                │
│ [dados] → [prompt] → Ollama → [resposta] → str(laudo)   │
└──────────────────────────────────────────────────────────┘
```

## Decisões de Design

### 1. Seleção Automática (dinosaur_selector.py)

**Problema:** Como escolher um dinossauro sem hardware?

**Solução:** Score composto
```
Score = (
    score_compatibilidade_hardware(hw, dino) ×
    score_preferencias(config, dino) ×
    (1.0 + bonus_tamanho(dino.peso_kg))
)
```

**Rationale:**
- Hardware limitado → prioriza genomas conservados
- Hardware potente → qualquer dinossauro é viável
- Preferências do usuário → ajusta ranking
- Dinossauros maiores → mais restos fósseis preservados

---

### 2. Genealogia Inteligente (descendant_mapper.py)

**Problema:** Qual descendente vivo usar como referência?

**Solução:** Mapeamento de características + scores NCBI
```
descendentes = [
    EspecieDescendente(
        nome="Gallus gallus",
        score_utilidade_genomica=95,
        qualidade_anotacao_ncbi=98,
        caracteristicas_preservadas=[OSSOS_OCOS, PENAS, ...],
    ),
    ...
]
melhor = max(descendentes, key=lambda e: (util + ncbi) / 2)
```

**Rationale:**
- Aves descendem diretamente de terapodes
- Crocodilianos parentes evolutivos distantes (mas genoma bem conservado)
- Score genômico favorece espécies bem-sequenciadas no NCBI
- Seleção automática = sem erro de usuário

---

### 3. Ollama Local (ollama_integration.py)

**Problema:** IA externa depende de API keys, internet, custos

**Solução:** LLM local (Ollama)
```
ClienteOllama(
    endpoint="http://localhost:11434",
    modelo="llama2",  # ou mistral, etc.
)
cliente.gerar_texto(prompt) → str
```

**Rationale:**
- Offline após download do modelo (~4GB)
- Sem API keys nem custos
- Privacidade: nada sai da máquina
- Fallback: se Ollama não está rodando, avisa e continua sem laudo

---

### 4. Busca Inteligente (ncbi_reference.py)

**Problema:** Qual descendente buscar no NCBI?

**Solução:** Integração com descendant_mapper
```python
dino = Tyrannosaurus rex
descendentes = mapeador.buscar_por_ancestral(dino)
# [Gallus gallus, Struthio camelus, Falco peregrinus, ...]
# Tenta cada um em ordem até sucesso
```

**Rationale:**
- Priorização automática = sem erro de usuário
- Fallback automático se espécie não tem gene
- Metadados genealógicos preservados em cada referência
- Rastreabilidade: sabe-se de qual dinossauro ancestral virou

---

### 5. Arquivos Separados por Responsabilidade

**Máxima:** Single Responsibility Principle

```
paleontology.py      → dados de dinossauros (READ-ONLY)
dinosaur_selector.py → seleção automática (LOGIC)
descendant_mapper.py → genealogia (READ-ONLY mapping)
ncbi_reference.py    → busca NCBI (NETWORK I/O)
reconstruct.py       → alinhamento (COMPUTATION)
gene_edit_package.py → comparação (COMPUTATION)
scanner_input.py     → I/O de arquivo (FILE I/O)
ai_report.py         → IA (NETWORK I/O)
ollama_integration.py → cliente HTTP (NETWORK I/O)
main.py              → orquestração (LOGIC)
```

**Benefício:** Cada módulo testável isoladamente

---

## Fluxo de Dados Detalhado (Caso Típico)

### Entrada:
```bash
python main.py \
    --gene "cytochrome b" \
    --host-species "Struthio camelus" \
    --ncbi-email seu@email.com \
    --preferencia-dieta "carnívoro"
```

### Execução:

1. **main.py parse_args()** → `Namespace(...)`

2. **dinosaur_selector.selecionar()** (sem --dinosaur)
   ```
   ConfiguracaoSelecao(
       hardware=NENHUMA,
       preferencia_tipo_dieta="carnívoro",
       ...
   )
   → SeletorDinossauro().selecionar()
   → (Tyrannosaurus rex, 0.92)
   ```

3. **paleontology.obter_sistema_referencia()** → SR com 5 dinossauros

4. **descendant_mapper.obter_mapeador()** → mapeador com 6 espécies

5. **ncbi_reference.buscar_painel_referencia_por_paleontologia()**
   ```
   dinosaur=T. rex
   mapeador.buscar_por_ancestral("Tyrannosaurus rex")
   → [Gallus gallus, Struthio camelus, Falco peregrinus, ...]
   
   Para cada:
     buscar_sequencia_gene(esp, "cytochrome b")
     → HTTP GET NCBI → fasta → ReferenceSequence
   
   → lista ordenada por score genômico
   ```

6. **reconstruct.reconstruct_ancestral_sequence()**
   ```
   dna_ancora (do fossil ou descendente)
   panel (referências vivas)
   → Needleman-Wunsch alignment
   → majority-rule consensus
   → ReconstructionResult
   ```

7. **gene_edit_package.build_edit_package()**
   ```
   reconstruction
   host_sequence (Struthio camelus)
   → diff SNP/indel
   → EditPackage
   ```

8. **ai_report.gerar_relatorio_com_ollama()** (se --gerar-relatorio-ia)
   ```
   ClienteOllama().validar_conexao()
   → POST http://localhost:11434/api/generate
   ← stream de chunks
   → texto completo
   ```

9. **Salva arquivos**
   ```
   re_dino_output/
   ├── sequencia_reconstruida.fasta
   ├── pacote_edicao_re_dino.csv
   └── laudo_ia.txt (se gerado)
   ```

### Saída:
```
[1/6] Selecionando dinossauro...
  Seleção automática: Tyrannosaurus rex
  Score de confiança: 92%

[2/6] Lendo entrada do sequenciador...
  Sem hardware: usaremos descendentes vivos como referência direta
  Descendentes vivos encontrados: 3

[3/6] Buscando referências NCBI...
  Referências encontradas: 3
  - Gallus gallus: NZ_...
  - Struthio camelus: NZ_...
  - Falco peregrinus: NZ_...

[4/6] Reconstruindo sequência ancestral...
  Comprimento consenso: 598 bases
  Confiança média: 87.3%
  Conteúdo GC: 42.1%

[5/6] Gerando pacote de edição para hospedeiro 'Struthio camelus'...
  Identidade genômica: 94%
  Edições propostas: 35

[6/6] Gerando laudo com Ollama...
  Usando modelo: llama2
  Salvo: laudo_ia.txt

✓ Pipeline concluído com sucesso!
Arquivos gerados:
  1. Sequência reconstruída: sequencia_reconstruida.fasta
  2. Pacote de edição genética: pacote_edicao_re_dino.csv
  3. Laudo técnico: laudo_ia.txt
```

---

## Performance Estimada

| Passo | Tempo | Limitações |
|-------|-------|-----------|
| Seleção dinossauro | <1s | Instantâneo |
| Busca NCBI (3 espécies) | 10-30s | Rate limit (3-10 req/s) |
| Reconstrução | <1s | Tamanho do gene |
| Edição genética | <1s | Computação local |
| IA (Ollama) | 5-30s | Modelo + velocidade CPU |
| **Total** | **15-60s** | Maioria é NCBI + IA |

---

## Escalabilidade Futura

### v2.1 — Cache NCBI
```python
# Evita buscar repetidamente a mesma sequência
cache = {
    "Gallus gallus:cytochrome b": ReferenceSequence(...),
    ...
}
```

### v2.2 — UI Web
```bash
streamlit run ui.py
# Interface visual para seleção de dinossauro + parâmetros
```

### v3.0 — Genoma Completo
```python
# Integração com SPAdes/Trycycler
montador = GenomeAssembler(reads, references)
genoma_completo = montador.montar()
# Agora retorna genoma inteiro, não só 1 gene
```

---

**Data:** Julho 2026  
**Versão:** 2.0  
**Arquitetura:** Modular, testável, escalável
