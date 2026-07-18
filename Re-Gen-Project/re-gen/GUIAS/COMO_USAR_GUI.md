# 🦖 Como Usar a Interface Gráfica Re-Dino

## ✅ Verificação Rápida

```bash
cd /home/v0rtex/Documents/re-gen
python3 -c "from dinosaur_database import DINOSAUR_DATABASE; print(f'✅ {len(DINOSAUR_DATABASE)} dinossauros carregados')"
```

## 🚀 Executar a Interface

### Opção 1: Via Script (Recomendado)
```bash
cd /home/v0rtex/Documents/re-gen
./run_gui.sh
```

### Opção 2: Direto com Python
```bash
cd /home/v0rtex/Documents/re-gen
python3 gui_dino_synthesizer.py
```

### Opção 3: Em Segundo Plano
```bash
cd /home/v0rtex/Documents/re-gen
nohup python3 gui_dino_synthesizer.py > gui.log 2>&1 &
```

---

## 🎨 Interface - 3 Abas

### 1️⃣ 🦖 **Banco de Dinossauros**
- Tabela com TODOS os dinossauros conhecidos
- Colunas: Nome Comum, Científico, Período, Dieta, Comprimento, Peso, Popularidade
- **Botão "Selecionar este Dinossauro"**: Carrega detalhes
- **Botão "Dinossauro Aleatório"**: Escolhe um aleatoriamente
- **Campo de Busca**: Filtra por nome

### 2️⃣ 🧬 **Síntese de DNA**
- Configurações de dNTPs (concentração em mM)
- Barra de progresso
- Log em tempo real
- Botões: "Iniciar Síntese" e "Parar Síntese"

### 3️⃣ 🐣 **Injeção em Embrião**
- Volume de DNA (µL)
- Profundidade de injeção (mm)
- Visualização 3D (posição XYZ)
- Log de operações
- Botão "Injetar DNA no Embrião"

---

## 💻 Requisitos de Sistema

- Python 3.6+
- PyQt5 5.15+
- Matplotlib
- Numpy

### Instalar Dependências (Se Necessário)
```bash
pip3 install PyQt5 --break-system-packages
pip3 install matplotlib numpy --break-system-packages
```

---

## 🔧 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'PyQt5'"
```bash
pip3 install PyQt5 --break-system-packages
```

### Erro: "Can only be used with threads started with QThread"
- Normal em modo headless/sem display
- Ignore se a interface carregar mesmo com o aviso

### GUI não aparece
```bash
# Se estiver via SSH, configure X11 forwarding
ssh -X user@host
python3 gui_dino_synthesizer.py

# Ou use VNC
vncserver :1
export DISPLAY=:1
python3 gui_dino_synthesizer.py
```

---

## 📊 Fluxo de Uso Típico

```
1. Abrir GUI (run_gui.sh)
   ↓
2. Aba "Banco de Dinossauros"
   - Selecionar dinossauro (ou aleatório)
   - Ver detalhes
   ↓
3. Aba "Síntese de DNA"
   - Configurar concentrações
   - Clicar "Iniciar Síntese"
   - Monitorar progresso
   ↓
4. Aba "Injeção em Embrião"
   - Definir volume e profundidade
   - Clicar "Injetar"
   - Ver logs
   ↓
5. Resultado: DNA injetado em embrião
```

---

## 🎓 Estrutura de Dados

### Dinossauro (Banco)
```python
{
    'scientific_name': str,      # Ex: "Tyrannosaurus rex"
    'common_name': str,          # Ex: "Tiranossauro"
    'period': str,               # Ex: "Cretáceo"
    'diet': str,                 # Ex: "carnívoro"
    'length_meters': float,      # Ex: 12.3
    'height_meters': float,      # Ex: 4.0
    'weight_kg': int,            # Ex: 8800
    'popularity': str,           # "popular", "impopular", "desconhecido"
    'description': str           # Descrição textual
}
```

---

## 📝 Logs

Logs são salvos em:
- Arquivo: `/var/log/dna_synthesizer.log` (se via Raspberry Pi)
- Console: Saída padrão (se via GUI local)

---

## 🔐 Segurança

- GUI não faz I/O de arquivos críticos
- Nenhuma requisição de rede
- Simula apenas síntese e injeção
- Hardware real requer autorização admin (GPIO do Pi)

---

## 📞 Suporte

### Verificar Instalação
```bash
python3 << 'EOF'
import sys
print(f"Python: {sys.version}")

try:
    import PyQt5
    print("✅ PyQt5 OK")
except:
    print("❌ PyQt5 falta")

try:
    import matplotlib
    print("✅ Matplotlib OK")
except:
    print("❌ Matplotlib falta")

try:
    import numpy
    print("✅ Numpy OK")
except:
    print("❌ Numpy falta")

try:
    from dinosaur_database import DINOSAUR_DATABASE
    print(f"✅ Banco de dados: {len(DINOSAUR_DATABASE)} dinossauros")
except:
    print("❌ Banco de dados falta")
EOF
```

---

**Última atualização:** Julho 2026  
**Status:** ✅ Pronto para Uso
