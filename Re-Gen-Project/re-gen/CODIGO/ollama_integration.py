"""
ollama_integration.py
---------------------
Integração com Ollama (https://ollama.ai): LLM local, sem APIs externas.

Substitui chamadas à API da Anthropic por requisições diretas a um servidor
Ollama rodando na máquina local. Completamente offline após download do modelo.

Modelos recomendados para esta tarefa:
- llama2:latest (modelo padrão, equilibrado)
- mistral:latest (rápido, bom para resumos)
- neural-chat:latest (otimizado para chat)

Para instalar Ollama:
  1. Baixe em https://ollama.ai
  2. Execute: `ollama serve`
  3. Em outro terminal: `ollama pull llama2` (ou seu modelo preferido)
  4. Está pronto! O endpoint fica em http://localhost:11434/api/generate

Este módulo oferece:
- Envio de prompts ao Ollama
- Streaming de respostas
- Retry com backoff exponencial
- Validação de conexão
"""

from __future__ import annotations
import requests
import json
import time
from typing import Optional, Generator
from dataclasses import dataclass
from enum import Enum


class OllamaModeloRecomendado(Enum):
    """Modelos recomendados para cada tarefa específica."""
    LLAMA2 = "llama2"  # Genérico, confiável
    MISTRAL = "mistral"  # Rápido
    NEURAL_CHAT = "neural-chat"  # Chat especializado


@dataclass
class ConfiguracaoOllama:
    """Configuração do cliente Ollama."""
    endpoint: str = "http://localhost:11434"  # URL padrão do Ollama
    modelo: str = "llama2"  # Modelo padrão
    temperatura: float = 0.7  # 0.0 = determinístico, 1.0 = criativo
    contexto_max_tokens: int = 2048  # Tamanho máximo de resposta
    timeout_segundos: int = 120  # Timeout para requisições
    max_retries: int = 3  # Número de tentativas
    retry_delay_segundos: float = 1.0  # Delay inicial entre retries


class ClienteOllama:
    """
    Cliente para comunicação com servidor Ollama local.
    Interface simples e confiável para geração de texto.
    """

    def __init__(self, config: Optional[ConfiguracaoOllama] = None):
        self.config = config or ConfiguracaoOllama()
        self._verificado = False

    def validar_conexao(self) -> bool:
        """
        Verifica se o Ollama está rodando e acessível.

        Retorna: True se validado, False caso contrário
        """
        if self._verificado:
            return True

        try:
            resp = requests.get(
                f"{self.config.endpoint}/api/tags",
                timeout=5,
            )
            if resp.status_code == 200:
                self._verificado = True
                return True
        except (requests.ConnectionError, requests.Timeout):
            pass

        return False

    def listar_modelos_disponiveis(self) -> list[str]:
        """
        Lista modelos que já foram baixados no Ollama.

        Retorna: Lista de nomes de modelos
        """
        try:
            resp = requests.get(
                f"{self.config.endpoint}/api/tags",
                timeout=10,
            )
            if resp.status_code == 200:
                dados = resp.json()
                return [m["name"] for m in dados.get("models", [])]
        except (requests.ConnectionError, requests.Timeout):
            pass

        return []

    def gerar_texto(
        self,
        prompt: str,
        modelo: Optional[str] = None,
        streaming: bool = False,
    ) -> str | Generator[str, None, None]:
        """
        Gera texto usando o modelo Ollama.

        Args:
            prompt: Texto de entrada
            modelo: Nome do modelo (usa config.modelo se None)
            streaming: Se True, retorna generator com chunks de texto

        Retorna:
            Se streaming=False: string completa
            Se streaming=True: Generator[str] com chunks
        """
        if not self.validar_conexao():
            raise RuntimeError(
                f"Ollama não está acessível em {self.config.endpoint}. "
                "Inicie com: `ollama serve`"
            )

        modelo = modelo or self.config.modelo

        url = f"{self.config.endpoint}/api/generate"
        payload = {
            "model": modelo,
            "prompt": prompt,
            "stream": streaming,
            "temperature": self.config.temperatura,
            "num_predict": self.config.contexto_max_tokens,
        }

        if streaming:
            return self._gerar_com_streaming(url, payload)
        else:
            return self._gerar_simples(url, payload)

    def _gerar_simples(self, url: str, payload: dict) -> str:
        """Gera texto sem streaming (aguarda resposta completa)."""
        for tentativa in range(self.config.max_retries):
            try:
                resp = requests.post(
                    url,
                    json=payload,
                    timeout=self.config.timeout_segundos,
                )
                if resp.status_code == 200:
                    resultado = resp.json()
                    return resultado.get("response", "")
            except (requests.ConnectionError, requests.Timeout) as e:
                if tentativa < self.config.max_retries - 1:
                    delay = self.config.retry_delay_segundos * (2 ** tentativa)
                    time.sleep(delay)
                else:
                    raise RuntimeError(f"Falha na requisição Ollama após retries: {e}")

        return ""

    def _gerar_com_streaming(self, url: str, payload: dict) -> Generator[str, None, None]:
        """Gera texto com streaming (yield de chunks conforme chegam)."""
        for tentativa in range(self.config.max_retries):
            try:
                resp = requests.post(
                    url,
                    json=payload,
                    stream=True,
                    timeout=self.config.timeout_segundos,
                )
                if resp.status_code == 200:
                    for linha in resp.iter_lines():
                        if linha:
                            try:
                                chunk = json.loads(linha)
                                texto = chunk.get("response", "")
                                if texto:
                                    yield texto
                            except json.JSONDecodeError:
                                pass
                    return
            except (requests.ConnectionError, requests.Timeout) as e:
                if tentativa < self.config.max_retries - 1:
                    delay = self.config.retry_delay_segundos * (2 ** tentativa)
                    time.sleep(delay)
                else:
                    raise RuntimeError(f"Falha no streaming Ollama: {e}")

    def embeddings(self, texto: str, modelo: Optional[str] = None) -> list[float]:
        """
        Gera embeddings (representação vetorial) de um texto.
        Útil para comparações genômicas conceptuais.

        Args:
            texto: Texto para embeddar
            modelo: Nome do modelo (usa config.modelo se None)

        Retorna: Lista de floats (vetor embedding)
        """
        if not self.validar_conexao():
            raise RuntimeError(f"Ollama não acessível em {self.config.endpoint}")

        modelo = modelo or self.config.modelo

        url = f"{self.config.endpoint}/api/embeddings"
        payload = {"model": modelo, "prompt": texto}

        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                dados = resp.json()
                return dados.get("embedding", [])
        except (requests.ConnectionError, requests.Timeout):
            pass

        return []


def criar_cliente_padrao() -> ClienteOllama:
    """Factory: cria cliente com configuração padrão."""
    return ClienteOllama()


# Instância global
_CLIENTE_GLOBAL = None


def obter_cliente_ollama() -> ClienteOllama:
    """Retorna a instância singleton do cliente Ollama."""
    global _CLIENTE_GLOBAL
    if _CLIENTE_GLOBAL is None:
        _CLIENTE_GLOBAL = criar_cliente_padrao()
    return _CLIENTE_GLOBAL


# ==================== PROMPTS PADRÃO ====================

PROMPT_TEMPLATE_RELATORIO = """
Tu és um especialista em paleontologia molecular e genômica evolutiva.
Dado um resultado de reconstrução genômica de um dinossauro extinto,
gera um laudo técnico profissional.

DADOS DA RECONSTRUÇÃO:
- Espécie: {especie}
- Comprimento da sequência consenso: {tamanho_sequencia} bases
- Confiança média da reconstrução: {confianca_media}%
- Conteúdo GC: {gc_content}%
- Número de espécies de referência usadas: {n_referencias}
- Espécies de referência: {especies_ref}

TAREFA:
1. Explica o significado dos números acima em linguagem clara
2. Descreve os pontos fortes e limitações da reconstrução
3. Sugere próximos passos práticos (síntese de DNA, edição genética)
4. Menciona implicações científicas dessa reconstrução

Responde em tom profissional, científico, mas acessível a biólogos e engenheiros genéticos.
"""

PROMPT_TEMPLATE_VALIDACAO = """
Tu és um especialista em filogenia molecular.
Valida a seguinte reconstrução genômica ancestral:

SEQUÊNCIA RECONSTRUÍDA:
{sequencia}

ESPÉCIES DESCENDENDENTES CONSULTADAS:
{species_list}

PERGUNTA:
Esta reconstrução faz sentido do ponto de vista evolutivo?
Quais são as características notáveis dessa reconstrução?
Há regiões suspeitas ou ambíguas?

Responde de forma concisa, apontando força/fraqueza.
"""
