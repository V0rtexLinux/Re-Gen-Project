# 🔨 Hibridizador DNA - Guia de Construção Prática

## 📍 VISÃO GERAL DA CONSTRUÇÃO

**Tempo total:** 2-3 semanas (trabalhando 4-6 horas/dia)
**Complexidade:** Alta (eletrônica + mecânica integrada)
**Custo:** R$3,100-6,000
**Resultado:** Máquina totalmente funcional de hibridização de DNA

### Cronograma Resumido
```
SEMANA 1:
├─ Dias 1-3: Estrutura + Base + Pedestal
├─ Dias 4-5: Câmara de reação + Vedação
└─ Dia 6-7: Preparação para eletrônica

SEMANA 2:
├─ Dias 1-2: Painéis LCD (montagem física)
├─ Dias 3-4: Painel de botões RGB + cabeamento
├─ Dias 5-7: Sistema de aquecimento/resfriamento

SEMANA 3:
├─ Dias 1-3: Eletrônica + Sensores + Controladores
├─ Dias 4-5: Software + Testes iniciais
└─ Dia 6-7: Testes finais + Calibração
```

---

## FASE 1: ESTRUTURA (Dias 1-7)

### 🛠️ FERRAMENTAS NECESSÁRIAS

**Ferramentas básicas:**
```
- Chave inglesa (2 tamanhos)
- Martelo de borracha
- Nível digital (±0.05°)
- Fita métrica (5m)
- Broca e escareador
- Chave hexagonal (set completo)
- Alicate de corte
```

**Equipamento especializado (aluguel):**
```
- Furadeira de coluna (para precisão)
- CNC ou serra de vidro (para câmara)
- Solda MIG + equipamento
- Fresadora pequena (opcional)
```

---

### Passo 1: Montar Base/Pedestal

**Materiais:**
```
□ Alumínio anodizado 40x40x3mm (80cm) - 3 peças
□ Alumínio anodizado 40x40x3mm (60cm) - 3 peças
□ Parafusos M8x25 (48 unidades)
□ Arruelas de aço M8 (96 unidades)
□ Porcas M8 (48 unidades)
□ Escudos de borracha antivibrátil
□ Pés ajustáveis M10 (4 unidades)
```

**Passo-a-passo:**
```
1. Cortar alumínio para tamanho (comprimento já vem correto)
   
2. Marcar furos:
   ├─ Centro: 10cm das extremidades
   ├─ Espaçamento: 20cm entre furos
   └─ Usar gabarito para precisão

3. Fazer furos:
   ├─ Broca #6.8mm (furo piloto)
   ├─ Escareação para cabeça do parafuso
   └─ Limpeza de rebarbas

4. Montar estrutura quadrada:
   ├─ Posição 4 barras horizontalmente
   ├─ Inserir parafusos com arruelas
   ├─ Apertar com chave hexagonal
   └─ Nível preciso (±2mm em 1m)

5. Instalar pés ajustáveis:
   ├─ Cantos inferiores
   ├─ Permitir nivelamento fino
   └─ Escudos de borracha entre pé e solo
```

**Verificação:**
```
✓ Nível horizontal (todas as 4 direções)
✓ Diagonal 80cm = diagonal 60cm (quadrado)
✓ Nenhum movimento ao pressionar
```

---

### Passo 2: Montar Estrutura Vertical

**Materiais:**
```
□ Perfil alumínio 20x40mm (100cm) - 4 peças (pilares)
□ Perfil alumínio 20x40mm (80cm) - 4 peças (travessas front/back)
□ Perfil alumínio 20x40mm (60cm) - 4 peças (travessas left/right)
□ Ângulos de alumínio L-20x20 (conexões)
□ Parafusos M6x20 (80 unidades)
```

**Passo-a-passo:**
```
1. Marcar posição dos 4 pilares:
   ├─ 10cm do canto (cada lado)
   ├─ Todos na mesma vertical
   └─ Usar nível laser se possível

2. Inserir pilares:
   ├─ Furos no piso da base
   ├─ Pilares em ângulo reto (90°)
   ├─ Parafusos M8 de cima
   └─ Verificar vertical com nível digital

3. Montar travessas horizontais (altura 50cm):
   ├─ Frente (80cm)
   ├─ Trás (80cm)
   ├─ Esquerda (60cm)
   ├─ Direita (60cm)
   └─ Usar ângulos para conexão com pilares

4. Montar travessas em altura (100cm):
   ├─ Mesmo padrão de posição
   └─ Para suportar teto dos painéis

5. Montar teto de suporte (para painéis LCD):
   ├─ Barras alumínio 80x60cm
   ├─ Articulação para monitores
   └─ Espaço livre central para câmara
```

**Verificação:**
```
✓ Todos ângulos 90°
✓ Sem vibração ao bater levemente
✓ Diagonal ≈ √(80²+60²) = 100cm (precisão ±1cm)
✓ Altura exata 120cm
```

---

### Passo 3: Revestimento Externo

**Materiais:**
```
□ Painel acrílico preto 5mm (80x100cm) - 2 peças (frente/trás)
□ Painel acrílico preto 5mm (60x100cm) - 2 peças (lados)
□ Fita LED RGB autoadesiva (20m total)
□ Vedação de borracha preta
□ Parafusos de aço inox M4x12
```

**Passo-a-passo:**
```
1. Cortar painéis acrílicos:
   ├─ CNC ou serra com proteção
   ├─ Bordas polidas
   └─ Dimensões exatas do esquadro

2. Furar para parafusos (quadrantes):
   ├─ 6 furos por painel (simetria)
   ├─ Broca #3.2mm
   ├─ Distância das bordas: 5cm
   └─ Limpeza de micro-fissuras

3. Instalar LED RGB fita (traseira):
   ├─ Limpeza da superfície com álcool
   ├─ Cole ao longo das bordas
   ├─ Deixe espaço para cabeamento
   └─ Teste cores antes de finalizar

4. Parafusar painéis:
   ├─ Arandelas plásticas (não arrancar acrílico)
   ├─ Sem apertar excessivamente
   ├─ Distribuição uniforme de força
   └─ Vedação nas junções
```

**Verificação:**
```
✓ Painéis encaixam perfeitamente
✓ Sem fendas nas junções
✓ LED RGB responde à alimentação (teste rápido)
✓ Transparência adequada (fumaça suave)
```


---

## FASE 2: CÂMARA DE REAÇÃO (Dias 4-7)

### 🧪 PREPARAR CILINDRO DE VIDRO

**Materiais:**
```
□ Tubo de vidro borossilicato (Pyrex) - Ø20cm x H30cm x 5mm
   Alternativa: Acrílico PMMA (mais barato, menos resistente)
□ Óleo de corte (para usinagem)
□ Areia fina (para polimento)
□ Papel de lixa 120, 400, 1000
□ Álcool etílico 99.5%
```

**Fornecedores no Brasil:**
```
- Vidraria de laboratório:
  └─ Laborclin, Glasscol, Vidraria São Paulo
  └─ Preço: R$300-600

- Acrílico (backup):
  └─ Plasflex, Plascril
  └─ Preço: R$150-300
```

**Passo-a-passo:**

```
1. Encomenda (ou corte local):
   ├─ Se tubo completo: pedir corte na fornecedora
   ├─ Se feita sob medida: CNC de vidro (3-5 dias)
   └─ Testar compatibilidade com operações posteriores

2. Recebimento e inspeção:
   ├─ Verificar dimensões com paquímetro
   ├─ Nenhuma trinca ou bolha
   ├─ Bordas lisas (não cortantes)
   └─ Armazenar em caixa com espuma

3. Polimento das bordas:
   ├─ Lixa #120 (desbaste) - 5 minutos
   ├─ Lixa #400 (intermediária) - 3 minutos
   ├─ Lixa #1000 (acabamento) - 2 minutos
   └─ Limpeza com água destilada

4. Limpeza final:
   ├─ Banho em álcool 99.5%
   ├─ Secar com ar comprimido
   └─ Inspeccionar luz transmitida
```

---

### Instalar Portas Rosqueadas

**Materiais:**
```
□ Rosca de vidro/PTFE M10 (5 unidades) - R$50-100
□ Adaptadores parafuso rosqueado M10 (5)
□ O-ring silicone #008 (50 unidades) - R$30-50
□ Tubing silicone médico (5m) - R$40-80
□ Conectores de vidro estéreis (10) - R$60-100
□ Broca de vidro especial Ø6mm - R$20-40
```

**Passo-a-passo:**

```
1. Marcar posição das portas:
   ├─ Porta 1 (DNA-A): Lateral esquerda, altura 10cm
   ├─ Porta 2 (DNA-B): Lateral direita, altura 10cm
   ├─ Porta 3 (Reagentes): Lateral superior, altura 25cm
   ├─ Porta 4 (Saída): Lateral inferior, altura 5cm
   └─ Porta 5 (Overflow): Lateral superior direita, altura 28cm
   └─ Usar marcador permanente

2. Fazer furos no vidro:
   ├─ MUITO CUIDADO: vidro quebra facilmente!
   ├─ Usar broca de vidro com velocidade baixa
   ├─ Refrigerar com água constantemente
   ├─ Pressão leve e constante
   └─ Furo com Ø6mm (para rosca M10)

3. Instalar rosca de vidro:
   ├─ Inserir com lubrificante (silicone óleo)
   ├─ Girar manualmente até travar
   ├─ NÃO forçar (pode quebrar vidro)
   └─ Testar com chave hexagonal (suave)

4. Instalar O-rings:
   ├─ Um O-ring em cada porta
   ├─ Antes do adaptador parafuso
   ├─ Garantir vedação hermética
   └─ Testar com água (0 vazamentos)

5. Teste de vazamento:
   ├─ Encher câmara com água destilada
   ├─ Esperar 24 horas
   ├─ Nenhuma gota de vazamento
   └─ Se vaza: reposicionar O-ring ou resselador
```

**Verificação:**
```
✓ Todas 5 portas instaladas
✓ Nenhum vazamento após 24h
✓ O-rings visíveis mas não danificados
✓ Tubing entra/sai com firmeza moderada
```

---

### Instalar LED RGB Interno

**Materiais:**
```
□ LED RGB 10W (3000K-6500K) - R$50-100
□ Driver LED 12V PWM - R$30-60
□ Radiador alumínio mini - R$20-40
□ Tubo de vidro isolante (Ø5cm x 20cm) - R$30-50
□ Fio silicone 22AWG colorido - R$20-40
□ Conector JST macho/fêmea - R$10-20
```

**Passo-a-passo:**

```
1. Preparar suporte para LED:
   ├─ Montar radiador no LED RGB
   ├─ Fixar com pasta térmica
   └─ Deixar dissipar calor

2. Instalar no tubo isolante:
   ├─ LED dentro do tubo de vidro
   ├─ Permitir passagem de luz
   ├─ Isolamento elétrico
   └─ Tubo fixo na lateral da câmara

3. Conectar eletricamente:
   ├─ Fio V+ (vermelho) → 12V do driver
   ├─ Fio GND (preto) → GND comum
   ├─ Fios RGB → GPIO do controlador
   ├─ Conector JST para desconexão fácil
   └─ Teste de cores: R, G, B, sequência

4. Teste final:
   ├─ Ligação de teste 12V
   ├─ Cores todas respondem
   ├─ Brilho ajustável (PWM)
   └─ Temperatura do radiador moderada (<60°C)
```

**Verificação:**
```
✓ LED RGB visível de todos os lados (câmara iluminada)
✓ Todas 3 cores primárias funcionam
✓ Sem vazamento de luz exterior
✓ Resistência térmica adequada
```

