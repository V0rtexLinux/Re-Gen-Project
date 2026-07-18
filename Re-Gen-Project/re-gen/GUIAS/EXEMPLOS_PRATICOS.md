# Exemplos Práticos — Re-Dino Engine v2

## Exemplo 1: Primeiro Run (30 segundos)

**Cenário:** Você quer apenas explorar como o sistema funciona.

```bash
# Instalação rápida
pip install biopython requests

# Executar (precisa de internet para NCBI)
python main.py \
    --gene "cytochrome b" \
    --host-species "Struthio camelus" \
    --ncbi-email seu.email@gmail.com
```

**O que vai acontecer:**
1. Sistema escolhe um dinossauro automaticamente (sem especificar --dinosaur)
2. Busca 3 descendentes vivos (aves) no NCBI
3. Reconstrói sequência ancestral
4. Compara com hospedeiro (avestruz)
5. Gera pacote de edição genética em CSV

**Saída esperada:**
```
[1/6] Selecionando dinossauro...
  Seleção automática: Tyrannosaurus rex
  Score de confiança: 92%
  Tamanho estimado: 9000kg
  Período: Cretáceo (145-66 Ma)

[2/6] Lendo entrada do sequenciador...
  Sem hardware: usaremos descendentes vivos como referência direta
  Descendentes vivos encontrados: 3
    - Gallus gallus (Aves)
    - Struthio camelus (Aves)
    - Falco peregrinus (Aves)

[3/6] Buscando referências NCBI para 'cytochrome b'...
  Referências encontradas: 3
    - Gallus gallus: NZ_KK211050.1 (615 bases)
      Caminho: Tyrannosaurus rex → Gallus gallus
    - Struthio camelus: NZ_AAAA0000.1 (612 bases)
      Caminho: Tyrannosaurus rex → Struthio camelus
    - Falco peregrinus: NZ_BBBB0000.1 (608 bases)
      Caminho: Tyrannosaurus rex → Falco peregrinus

[4/6] Reconstruindo sequência ancestral...
  Comprimento consenso: 598 bases
  Confiança média: 87.4%
  Conteúdo GC: 42.1%
  Atenção: 1 região(ões) de baixa confiança detectada(s)

[5/6] Gerando pacote de edição para hospedeiro 'Struthio camelus'...
  Identidade genômica: 94%
  Edições propostas: 22

[6/6] Relatório IA não solicitado (use --gerar-relatorio-ia)

✓ Pipeline concluído com sucesso!
Arquivos gerados:
  1. Sequência reconstruída: sequencia_reconstruida.fasta
  2. Pacote de edição genética: pacote_edicao_re_dino.csv
```

---

## Exemplo 2: Especificar Dinossauro Favorito

**Cenário:** Você é paleontólogo e quer reconstruir especificamente um Velociraptor.

```bash
python main.py \
    --dinosaur "Velociraptor mongoliensis" \
    --gene "COI" \
    --host-species "Falco peregrinus" \
    --ncbi-email seu.email@gmail.com
```

**Por que isso é bom:**
- Velociraptor é bem pequeno (10 kg) → genoma conservado
- COI é gene bem documentado em aves de rapina
- Falcão-peregrino é descendente direto de Velociraptor
- Alta relevância evolutiva

**Resultado:**
- Sequência de Velociraptor
- Comparada contra falcão-peregrino
- Edições genéticas específicas para essa linhagem

---

## Exemplo 3: Filtrar por Preferências

**Cenário:** Você quer um dinossauro **carnívoro**, mas não muito grande.

```bash
python main.py \
    --preferencia-dieta "carnívoro" \
    --preferencia-tamanho-min 1000 \
    --preferencia-tamanho-max 50000 \
    --gene "12S ribosomal RNA" \
    --host-species "Gallus gallus" \
    --ncbi-email seu.email@gmail.com
```

**Sistema vai:**
1. Listar todos os carnívoros: [T. rex (9t), Velociraptor (10kg), Archaeopteryx (1kg)]
2. Filtrar por tamanho (1-50 toneladas): [T. rex (9t), Velociraptor (10kg)]
3. Selecionar o melhor por score

**Resultado:**
- Provavelmente Tyrannosaurus rex
- Se não, Velociraptor
- Depende do score de compatibilidade

---

## Exemplo 4: Com Ollama — Relatório Técnico

**Cenário:** Você quer um relatório profissional com análise de IA.

**Pré-requisito:** Ollama rodando

```bash
# Terminal 1: Inicie Ollama
ollama serve

# Terminal 2: Baixe modelo (primeira vez)
ollama pull llama2

# Terminal 3: Execute Re-Dino com IA
python main.py \
    --gene "cytochrome b" \
    --host-species "Struthio camelus" \
    --ncbi-email seu.email@gmail.com \
    --gerar-relatorio-ia \
    --modelo-ollama "llama2"
```

**Novo passo [6/6]:**
```
[6/6] Gerando laudo com Ollama local...
  Usando modelo: llama2
  Gerando laudo (pode levar 10-30 segundos)...
  Salvo: laudo_ia.txt

--- LAUDO ---

ANÁLISE TÉCNICA DA RECONSTRUÇÃO GENÔMICA

Resumo Executivo:
O pipeline reconstruiu com sucesso uma sequência de 598 pb do gene 
cytochrome b ancestral de Tyrannosaurus rex, usando como referência 
três espécies vivas (Gallus gallus, Struthio camelus, Falco peregrinus).

Confiabilidade dos Dados:
A confiança média de reconstrução foi de 87.4%, indicando alta robustez 
da sequência consenso. Uma única região (posição 234-256) apresenta 
confiança abaixo do limiar de 60%, sugerindo que mais dados seriam 
benéficos nesse trecho.

Viabilidade do Pacote de Edição:
O hospedeiro (Struthio camelus/avestruz) compartilha 94% de identidade 
genômica com a reconstrução, indicando que o pacote de 22 edições é 
biologicamente plausível. As edições concentram-se em regiões funcionais 
conservadas, sugerindo modificações que não comprometem a viabilidade 
do organismo.

Próximos Passos Recomendados:
1. Síntese de DNA: Enviar FASTA para fornecedor real (Twist, IDT)
2. Validação in vitro: Clonar segmento em plasmídeo de teste
3. Refinamento: Se mais dados fósseis ficarem disponíveis, executar 
   novo run para validar as regiões de baixa confiança
4. Design de CRISPR: Usar CSV em Benchling para otimizar guide-RNAs

Implicações Científicas:
Esta reconstrução representa a primeira validação genômica desta 
linhagem específica usando este pipeline. Os resultados são compatíveis 
com estudos paleontológicos previos e fornecem uma base para estudos 
downstream de edição genética e síntese.
```

**Resultado:**
- 3 arquivos + laudo profissional
- Pronto para apresentar a um comitê de pesquisa

---

## Exemplo 5: Hardware Real (Sequenciador Nanopore)

**Cenário:** Você tem dados reais de um sequenciador Oxford Nanopore MinION.

```bash
# Você executou MinKNOW e gerou um arquivo .fastq
# Agora vai analisar com Re-Dino

python main.py \
    --scanner-file /data/minion_run/basecalled_reads.fastq \
    --gene "cytochrome b" \
    --host-species "Struthio camelus" \
    --ncbi-email seu.email@gmail.com \
    --ncbi-api-key sua-chave-ncbi-aqui
```

**O que muda:**
1. [2/6] Agora lê FASTQ real (não sintético)
2. Sistema encontra a melhor leitura como "âncora" (dato mais confiável do fóssil)
3. Alinha referências contra essa âncora
4. Reconstrução é mais precisa (tem dados reais)

**Exemplo de output:**
```
[2/6] Lendo entrada do sequenciador...
  Leituras válidas: 1024
  Bases totais: 487293
  Qualidade média (Phred): 11.2
  Âncora selecionada: fastq_runid_abc123_read_12345 (4821 bases)
```

**Resultado:**
- Sequência muito mais confiável (baseada em dado real)
- Pronta para síntese + edição genética prática

---

## Exemplo 6: Explorar Todos os Dinossauros

**Cenário:** Você quer ver quais dinossauros estão disponíveis.

```python
# Python script: explore_dinos.py
from paleontology import obter_sistema_referencia
from dinosaur_selector import SeletorDinossauro, ConfiguracaoSelecao, CapacidadeHardware

sr = obter_sistema_referencia()

print("DINOSSAUROS DISPONÍVEIS NO SISTEMA:")
print("=" * 60)

for nome, dino in sr.dinossauros.items():
    print(f"\n{dino.nome_comum} ({nome})")
    print(f"  Grupo: {dino.grupo.value}")
    print(f"  Período: {dino.periodo.value}")
    print(f"  Tamanho: {dino.peso_estimado_kg}kg × {dino.comprimento_estimado_m}m")
    print(f"  Dieta: {dino.dieta}")
    print(f"  Localização: {', '.join(dino.localizacao_geografica)}")
    print(f"  Genes conservados: {len(dino.genes_conservados)}")
    print(f"  Descendentes vivos: {len(dino.descendentes_vivos)}")
    print(f"  Descrição: {dino.descricao_paleontologica[:100]}...")

print("\n" + "=" * 60)
print("\nRECOMENDAÇÕES POR HARDWARE:")

for hw in [CapacidadeHardware.NENHUMA, 
           CapacidadeHardware.BASICA, 
           CapacidadeHardware.INTERMEDIARIA, 
           CapacidadeHardware.AVANCADA]:
    config = ConfiguracaoSelecao(hardware=hw)
    seletor = SeletorDinossauro()
    recomendacoes = seletor.recomendar_multiplos(config, n=3)
    
    print(f"\n{hw.value.upper()}:")
    for dino, score in recomendacoes:
        print(f"  1. {dino.nome_comum} (score: {score:.1%})")
```

**Executar:**
```bash
python explore_dinos.py
```

**Output:**
```
DINOSSAUROS DISPONÍVEIS NO SISTEMA:
============================================================

T-Rex (Tyrannosaurus rex)
  Grupo: Theropoda
  Período: Cretáceo (145-66 Ma)
  Tamanho: 9000kg × 12.3m
  Dieta: carnívoro
  Localização: América do Norte (USA, Canadá)
  Genes conservados: 4
  Descendentes vivos: 3
  Descrição: Tiranosaurídeo de topo da cadeia alimentar do Cretáceo Superior...

... [mais dinossauros]

============================================================

RECOMENDAÇÕES POR HARDWARE:

NENHUMA:
  1. Archaeopteryx lithographica (score: 98%)
  2. Velociraptor mongoliensis (score: 94%)
  3. Tyrannosaurus rex (score: 88%)

BASICA:
  1. Velociraptor mongoliensis (score: 96%)
  2. Tyrannosaurus rex (score: 92%)
  3. Archaeopteryx lithographica (score: 89%)

INTERMEDIARIA:
  1. Tyrannosaurus rex (score: 94%)
  2. Velociraptor mongoliensis (score: 91%)
  3. Brachiosaurus altithorax (score: 87%)

AVANCADA:
  1. Brachiosaurus altithorax (score: 95%)
  2. Tyrannosaurus rex (score: 93%)
  3. Triceratops horridus (score: 88%)
```

---

## Exemplo 7: Pesquisa Comparativa (Múltiplas Reconstruções)

**Cenário:** Você quer comparar reconstruções de diferentes dinossauros.

```bash
#!/bin/bash
# compare_dinos.sh

EMAIL="seu.email@gmail.com"
API_KEY="sua-chave-ncbi"
GENE="cytochrome b"
HOST="Gallus gallus"

echo "Reconstruindo múltiplos dinossauros..."

# Run 1: T-Rex
python main.py \
    --dinosaur "Tyrannosaurus rex" \
    --gene "$GENE" \
    --host-species "$HOST" \
    --ncbi-email "$EMAIL" \
    --ncbi-api-key "$API_KEY" \
    --output-dir "./results/t_rex"

# Run 2: Velociraptor
python main.py \
    --dinosaur "Velociraptor mongoliensis" \
    --gene "$GENE" \
    --host-species "$HOST" \
    --ncbi-email "$EMAIL" \
    --ncbi-api-key "$API_KEY" \
    --output-dir "./results/velociraptor"

# Run 3: Archaeopteryx
python main.py \
    --dinosaur "Archaeopteryx lithographica" \
    --gene "$GENE" \
    --host-species "$HOST" \
    --ncbi-email "$EMAIL" \
    --ncbi-api-key "$API_KEY" \
    --output-dir "./results/archaeopteryx"

echo "Feito! Resultados em:"
echo "  - results/t_rex/"
echo "  - results/velociraptor/"
echo "  - results/archaeopteryx/"

# Análise comparativa
python - << 'EOF'
import pandas as pd

files = [
    ("T-Rex", "results/t_rex/pacote_edicao_re_dino.csv"),
    ("Velociraptor", "results/velociraptor/pacote_edicao_re_dino.csv"),
    ("Archaeopteryx", "results/archaeopteryx/pacote_edicao_re_dino.csv"),
]

print("\nCOMPARAÇÃO DE RECONSTRUÇÕES:")
print("=" * 60)

for nome, arquivo in files:
    df = pd.read_csv(arquivo)
    n_edits = len(df)
    print(f"{nome:20s}: {n_edits:3d} edições genéticas")

EOF
```

**Resultado:**
```
COMPARAÇÃO DE RECONSTRUÇÕES:
============================================================
T-Rex              :  22 edições genéticas
Velociraptor       :  18 edições genéticas
Archaeopteryx      :  12 edições genéticas
```

---

## Exemplo 8: Troubleshooting

### Problema: "Ollama não está acessível"

```bash
# Verifique se está rodando
ps aux | grep ollama

# Se não, inicie em um terminal separado
ollama serve

# Teste conexão
curl http://localhost:11434/api/tags
```

### Problema: "Nenhuma referência encontrada"

```bash
# Tente outro gene
python main.py \
    --gene "12S ribosomal RNA"  # Em vez de "cytochrome b"
    --host-species "Struthio camelus" \
    --ncbi-email seu.email@gmail.com
```

### Problema: "Timeout ao buscar NCBI"

```bash
# Forneça API key (aumenta rate limit)
python main.py \
    --gene "cytochrome b" \
    --host-species "Struthio camelus" \
    --ncbi-email seu.email@gmail.com \
    --ncbi-api-key SUA_CHAVE_NCBI  # ← adicione isso
```

---

## Exemplo 9: Documentação Automatizada

**Criar um relatório markdown com todas as análises:**

```python
# generate_report.py
from paleontology import obter_sistema_referencia
from descendant_mapper import obter_mapeador

sr = obter_sistema_referencia()
mapeador = obter_mapeador()

with open("analise_paleontologica.md", "w") as f:
    f.write("# Análise Paleontológica Re-Dino\n\n")
    
    for nome, dino in sr.dinossauros.items():
        descendentes = mapeador.buscar_por_ancestral(nome)
        
        f.write(f"## {dino.nome_comum}\n\n")
        f.write(f"- **Científico:** {nome}\n")
        f.write(f"- **Período:** {dino.periodo.value}\n")
        f.write(f"- **Peso:** {dino.peso_estimado_kg}kg\n")
        f.write(f"- **Descendentes Vivos:**\n")
        
        for d in descendentes:
            f.write(f"  - {d.nome_cientifico} ({d.grupo_taxa})\n")
        
        f.write(f"\n")

print("Relatório gerado: analise_paleontologica.md")
```

---

## Resumo de Todos os Exemplos

| Exemplo | Comando | Use quando |
|---------|---------|-----------|
| 1 | Básico, automático | Exploração rápida |
| 2 | Com --dinosaur | Tem dinossauro favorito |
| 3 | Com --preferencia-* | Quer filtrar |
| 4 | Com --gerar-relatorio-ia | Precisa de laudo profissional |
| 5 | Com --scanner-file | Tem dados reais |
| 6 | Script Python | Quer explorar dados |
| 7 | Multiple runs | Pesquisa comparativa |
| 8 | Debug | Algo não funciona |
| 9 | Script Python | Gerar documentação |

---

**Pronto para brincar! 🦖🧬**
