# 🚀 LAUNCHER RE-DINO - Menu Interativo

## O que é?

O **launcher.sh** é um menu interativo em Bash que centraliza TUDO o que você pode fazer no projeto Re-Dino:

- 🎮 GUI (Interface gráfica PyQt5)
- 🧬 Síntese de DNA
- 🔬 Testes e validações
- 📚 Documentação
- 🤖 Gerenciador de robôs
- 📊 Visualização de dados
- 🛠️  Ferramentas utilitárias

---

## Como usar?

### Iniciar o launcher

```bash
cd /home/v0rtex/Documents/re-gen
./launcher.sh
```

Ou com bash explícito:

```bash
bash launcher.sh
```

### Menu Principal

```
╔════════════════════════════════════════════════════════════════╗
║           🦖 RE-DINO: SÍNTESE DE DNA DE DINOSSAUROS 🦕        ║
║                    LAUNCHER PRINCIPAL v3.0                    ║
╚════════════════════════════════════════════════════════════════╝

[1] 🎮 GUI - Interface Gráfica (PyQt5)
[2] 🧬 Síntese de DNA - Terminal
[3] 🔬 Testes e Validações
[4] 📚 Visualizar Documentação
[5] 🤖 Gerenciador de Robôs
[6] 📊 Visualizar Dados
[7] 🛠️  Ferramentas Utilitárias
[0] ❌ Sair
```

---

## 📖 Opções Disponíveis

### 1️⃣ GUI - Interface Gráfica

```
./launcher.sh → [1]
```

Abre a interface PyQt5 completa com:
- Seleção de dinossauros (500+ espécies)
- Síntese de DNA
- Injeção de embrião
- Monitoramento em tempo real

---

### 2️⃣ Síntese de DNA - Terminal

```
./launcher.sh → [2]
```

Submenu com 4 opções:

| Opção | Descrição |
|-------|-----------|
| [1] | ⚡ Síntese Rápida (3Gb em 47s) - Tyrannosaurus rex |
| [2] | 🎯 Síntese com Espécie Específica - Digite o nome |
| [3] | 📈 Síntese com Parâmetros Customizados - Customize tudo |
| [4] | 📊 Listar Todas as 500+ Espécies - Ver todas disponíveis |

**Exemplo:**

```bash
./launcher.sh → [2] → [1]
# Sinteza rápida começa automaticamente
# Resultado: 3 bilhões bp em ~47 segundos
```

---

### 3️⃣ Testes e Validações

```
./launcher.sh → [3]
```

Submenu com 5 testes:

| Teste | Função |
|-------|--------|
| [1] | ✅ Teste Rápido - Verifica se tudo está OK |
| [2] | 🧬 Validar Genoma - Valida genomas gerados |
| [3] | 🦖 Pipeline Completo - Demo do pipeline |
| [4] | 📋 Integração - Testa integração completa |
| [5] | 🐍 Dependências - Verifica Python packages |

**Exemplo:**

```bash
./launcher.sh → [3] → [5]
# Verifica se todas as dependências estão instaladas
# Mostra: ✓ PyQt5, ✓ numpy, ✓ scipy, etc.
```

---

### 4️⃣ Documentação

```
./launcher.sh → [4]
```

Acesso direto a todos os guias em PDF/Markdown:

- 📖 Quick Start
- 🧬 Processo de Transformação (21 dias)
- 🥚 Como Obter Ovos
- 🤖 Construir Robô de Síntese
- 💉 Construir Robô de Injeção
- 📋 Lista de Materiais
- ⚙️  Integração Completa

---

### 5️⃣ Gerenciador de Robôs

```
./launcher.sh → [5]
```

Submenu com 4 opções:

| Opção | Função |
|-------|--------|
| [1] | 🤖 Info Robô 1 - Síntese de DNA |
| [2] | 💉 Info Robô 2 - Injeção de Genoma |
| [3] | ⚙️  Teste GPIO - Testar Raspberry Pi |
| [4] | 📊 Dashboard - Status dos robôs |

**Exemplo:**

```bash
./launcher.sh → [5] → [1]
# Mostra especificações completas do robô de síntese
# Mostra custo, tempo de construção, componentes necessários
```

---

### 6️⃣ Visualizar Dados

```
./launcher.sh → [6]
```

Lista todos os arquivos na pasta DADOS/:
- `paleonto_data.json` - 500+ dados paleontológicos
- `*.fastq` - Sequências de teste
- `incubator_arduino_controller.ino` - Código Arduino

---

### 7️⃣ Ferramentas Utilitárias

```
./launcher.sh → [7]
```

Submenu com 5 ferramentas:

| Ferramenta | Função |
|-----------|--------|
| [1] | 📁 Explorador - Ver estrutura de pastas |
| [2] | 🔍 Buscar - Procurar espécie no banco |
| [3] | 📈 Histórico - Ver sínteses anteriores |
| [4] | 🧹 Limpar - Deletar arquivos temporários |
| [5] | 📋 Relatório - Gerar relatório do projeto |

**Exemplo:**

```bash
./launcher.sh → [7] → [2]
# Digite: "Triceratops"
# Mostra: Triceratops | Período: Cretáceo | Dieta: Herbívoro
```

---

## 🎯 Casos de Uso

### Caso 1: Apenas gerar um genoma rápido

```bash
./launcher.sh
[2] → [1]
# Gera 3Gb de DNA em 47 segundos
```

### Caso 2: Testar se tudo está funcionando

```bash
./launcher.sh
[3] → [5]
# Verifica todas as dependências
[3] → [1]
# Teste rápido do sistema
```

### Caso 3: Construir os robôs

```bash
./launcher.sh
[4] → [6]
# Lê Lista de Materiais (ver o que comprar)
[4] → [4]
# Lê Guia de Construção do Robô 1
[4] → [5]
# Lê Guia de Construção do Robô 2
```

### Caso 4: Usar a interface gráfica

```bash
./launcher.sh
[1]
# Abre GUI PyQt5 completa
# Selecione dinossauro, gere genoma, simule injeção
```

### Caso 5: Procurar uma espécie específica

```bash
./launcher.sh
[7] → [2]
# Digite o nome da espécie
# Mostra período, dieta, tamanho
```

---

## 🌈 Cores e Símbolos

O launcher usa cores para melhor visualização:

| Cor | Significado |
|-----|-----------|
| 🔵 CYAN | Cabeçalhos e divisores |
| 🟢 GREEN | Opções disponíveis |
| 🔴 RED | Erros e sair |
| 🟡 YELLOW | Informações e ações |

Símbolos:
- ✓ = Sucesso
- ✗ = Erro
- ⚠ = Aviso
- ℹ = Informação
- ↩ = Voltar

---

## 📋 Estrutura de Pastas Acessadas

O launcher acessa automaticamente:

```
re-gen/
├── GUIAS/              # Documentação (leitura com 'less')
├── CODIGO/             # Scripts Python (execução)
├── DADOS/              # Dados e arquivos (visualização)
├── OUTPUT/             # Resultados gerados
└── launcher.sh         # Este launcher
```

---

## 🔧 Requisitos

**Sistema:**
- Linux/Mac/WSL2
- Bash 4+
- Python 3.7+

**Dependências Python:**
```bash
pip3 install PyQt5 numpy scipy opencv-python pyserial requests
```

**Testar:**
```bash
./launcher.sh → [3] → [5]
# Verifica tudo automaticamente
```

---

## 🚀 Comandos Diretos

Você também pode usar direto sem o menu:

```bash
# Gerar genoma rápido
python3 CODIGO/main_v3.py --species "Tyrannosaurus rex" --genome-size 3000000000

# Abrir GUI
python3 CODIGO/gui_dino_synthesizer.py

# Listar todas as espécies
python3 -c "from CODIGO.dinosaur_database import DinosaurDatabase; db = DinosaurDatabase(); print(len(db.dinosaurs))"

# Teste rápido
python3 CODIGO/test_v3_integration.py
```

---

## 💡 Dicas

1. **Primeira vez?** Comece com `[3] → [1]` (teste rápido)
2. **Quer GUI?** Use `[1]` para interface gráfica completa
3. **Quer robôs?** Leia `[4] → [6]` (lista de materiais)
4. **Está lento?** Use `[7] → [4]` para limpar temporários
5. **Dúvidas?** Leia `[4]` (documentação completa)

---

## 🐛 Troubleshooting

### "bash: ./launcher.sh: Permission denied"

```bash
chmod +x launcher.sh
./launcher.sh
```

### "No module named PyQt5"

```bash
pip3 install PyQt5 --break-system-packages
./launcher.sh → [3] → [5]  # Verifica novamente
```

### "Opção inválida!"

Você pressionou uma tecla errada. Digite apenas o NÚMERO da opção (1-7 ou 0).

### Menu não limpa corretamente

```bash
clear
./launcher.sh
```

---

## 📞 Suporte

- **Documentação:** Acesse dentro do launcher `[4]`
- **Código:** Explore em `CODIGO/`
- **Dados:** Veja em `DADOS/`
- **Relatório:** Gere com `[7] → [5]`

---

## 📊 Resumo Rápido

| Opção | Atalho | Tempo | Uso |
|-------|--------|-------|-----|
| GUI | `[1]` | 5s | Gráfico |
| Síntese | `[2]` | 47s | Terminal |
| Testes | `[3]` | 5-30s | Validação |
| Docs | `[4]` | ∞ | Leitura |
| Robôs | `[5]` | 5s | Info |
| Dados | `[6]` | 2s | Listar |
| Tools | `[7]` | Varia | Utilitários |

---

**Versão:** 1.0  
**Status:** ✅ Pronto para uso  
**Data:** Julho 2026

🦖 **Bem-vindo ao Re-Dino Launcher!** 🦕
