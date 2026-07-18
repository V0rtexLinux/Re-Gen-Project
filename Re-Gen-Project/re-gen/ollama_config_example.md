# Configuração do Ollama — Re-Dino Engine v2

## Instalação Rápida (Linux/macOS)

```bash
# Instale Ollama
curl https://ollama.ai/install.sh | sh

# Inicie o servidor (terminal 1)
ollama serve

# Baixe um modelo (terminal 2)
ollama pull llama2
```

## Modelos Disponíveis

### Recomendados para Re-Dino

```bash
# Padrão - Equilibrado
ollama pull llama2

# Rápido - Para máquinas lentas
ollama pull mistral

# Chat otimizado
ollama pull neural-chat

# Maior - Se tiver muita VRAM (12GB+)
ollama pull llama2:13b
```

## Verificar Modelos Instalados

```bash
ollama ls
```

Exemplo de saída:
```
NAME                ID              SIZE    MODIFIED
llama2:latest       c6d3f286b58d    3.8 GB  2 weeks ago
mistral:latest      f974a74358b6    4.1 GB  1 week ago
```

## Testar Conexão do Re-Dino

```bash
# Verifique se o servidor está acessível
curl http://localhost:11434/api/tags

# Deve retornar JSON com a lista de modelos
```

## Configurações Avançadas

### Customizar em `ollama_integration.py`

```python
from ollama_integration import ClienteOllama, ConfiguracaoOllama

# Configuração customizada
config = ConfiguracaoOllama(
    endpoint="http://localhost:11434",  # URL do Ollama
    modelo="mistral",  # Modelo a usar
    temperatura=0.7,  # 0.0=determinístico, 1.0=criativo
    contexto_max_tokens=2048,  # Tamanho máximo de resposta
    timeout_segundos=120,  # Timeout para requisições
    max_retries=3,  # Número de tentativas
)

cliente = ClienteOllama(config)
```

### Passando para main.py

```bash
python main.py \
    --gene "cytochrome b" \
    --host-species "Struthio camelus" \
    --ncbi-email seu.email@dominio.com \
    --gerar-relatorio-ia \
    --modelo-ollama "mistral"  # Usa Mistral em vez de llama2
```

## Otimizações por Hardware

### Máquina Fraca (4GB RAM)

```bash
# Use Mistral (mais rápido)
ollama pull mistral
```

No `main.py`:
```bash
--modelo-ollama "mistral"
--gerar-relatorio-ia
```

### Máquina Média (8GB RAM)

```bash
# Use Llama2 (padrão)
ollama pull llama2
```

### Máquina Potente (16GB+ VRAM)

```bash
# Use versão maior
ollama pull llama2:13b
```

No `main.py`:
```bash
--modelo-ollama "llama2:13b"
```

## Verificação de Saúde

```bash
# Endpoint tags (lista de modelos)
curl http://localhost:11434/api/tags

# Teste de geração (rápido)
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Olá",
  "stream": false
}'
```

## Troubleshooting

### Ollama não inicia
```bash
# macOS
brew services restart ollama

# Linux - reinstale
curl https://ollama.ai/install.sh | sh
```

### Modelo não foi baixado
```bash
# Limpe cache e tente novamente
ollama rm llama2
ollama pull llama2

# Ou verifique espaço em disco
df -h
# Precisa de pelo menos 5GB livre
```

### Re-Dino não encontra Ollama
```bash
# Verifique se está rodando
ps aux | grep ollama

# Ou inicie manualmente
ollama serve
```

### Resposta muito lenta
- Reduza `contexto_max_tokens` em `ollama_integration.py`
- Use modelo mais rápido (mistral)
- Aumente quantidade de RAM/GPU

## Integração com Re-Dino

O arquivo `ollama_integration.py` encapsula toda a lógica:

```python
from ollama_integration import obter_cliente_ollama

cliente = obter_cliente_ollama()

# Gerar texto
resposta = cliente.gerar_texto(
    prompt="Sua pergunta aqui",
    streaming=False
)
print(resposta)

# Com streaming
for chunk in cliente.gerar_texto(
    prompt="Sua pergunta aqui",
    streaming=True
):
    print(chunk, end="", flush=True)
```

## Parar o Servidor

```bash
# Ctrl+C no terminal onde ollama serve está rodando
# Ou:
killall ollama
```

## Recursos Adicionais

- **Modelos Disponíveis**: https://ollama.ai/library
- **API Docs**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **FAQ**: https://github.com/ollama/ollama#faqs

---

**Pronto!** Ollama está configurado para Re-Dino Engine v2.
