"""
ai_report.py
------------
Gera o relatório final do laboratório usando Ollama (LLM local, 100% offline).

O Ollama deve estar rodando localmente:
  1. Instale: https://ollama.ai
  2. Execute: `ollama serve`
  3. Em outro terminal: `ollama pull llama2` (ou seu modelo preferido)
  4. Pronto! Endpoint em http://localhost:11434

Vantagens vs API externa:
- Sem dependência de internet após download do modelo
- Sem chaves de API
- Sem custos recorrentes
- Privacidade: tudo roda localmente
- Offline-first para laboratório real

O modelo recomendado é `llama2` (7B, equilibrado) ou `mistral` (7B, mais rápido).
Para máquinas com muita VRAM, considere `llama2:13b`.
"""

from __future__ import annotations

from collections.abc import Generator

from re_gen.ai.ollama_integration import (
    PROMPT_TEMPLATE_RELATORIO,
    ClienteOllama,
    obter_cliente_ollama,
)
from re_gen.core.gene_edit_package import EditPackage
from re_gen.core.reconstruct import ReconstructionResult


class AIReportError(Exception):
    pass


def gerar_relatorio_com_ollama(
    reconstruction: ReconstructionResult,
    edit_package: EditPackage,
    scanner_summary: dict,
    target_species_label: str,
    cliente: ClienteOllama | None = None,
    streaming: bool = False,
) -> str | Generator[str, None, None]:
    """
    Gera relatório técnico usando Ollama local.

    Args:
        reconstruction: Resultado da reconstrução ancestral
        edit_package: Pacote de edição genética
        scanner_summary: Resumo das leituras do sequenciador
        target_species_label: Rótulo do dinossauro (ex: "Tyrannosaurus rex")
        cliente: ClienteOllama personalizado (usa global se None)
        streaming: Se True, retorna chunks conforme chegam

    Retorna:
        String com o relatório completo (ou generator se streaming=True)

    Levanta:
        AIReportError: Se Ollama não estiver acessível
    """
    if cliente is None:
        cliente = obter_cliente_ollama()

    # Valida conexão com Ollama
    if not cliente.validar_conexao():
        raise AIReportError(
            f"Ollama não está acessível em {cliente.config.endpoint}. "
            "Inicie com: `ollama serve` e baixe um modelo com `ollama pull llama2`"
        )

    # Formata o prompt com dados reais
    prompt = PROMPT_TEMPLATE_RELATORIO.format(
        especie=target_species_label,
        tamanho_sequencia=len(reconstruction.consensus_sequence),
        confianca_media=round(reconstruction.mean_confidence * 100, 1),
        gc_content=reconstruction.gc_content,
        n_referencias=reconstruction.n_references_used,
        especies_ref=", ".join(reconstruction.reference_species),
    )

    # Prompt adicional: contexto específico do laboratório
    prompt_completo = f"""{prompt}

DADOS DO SEQUENCIADOR REAL:
- Leituras válidas: {scanner_summary["n_reads"]}
- Bases totais: {scanner_summary["total_bases"]}
- Qualidade média (Phred): {scanner_summary.get("avg_quality", "N/A")}

PACOTE DE EDIÇÃO GENÉTICA (hospedeiro: {edit_package.host_species}):
- Identidade genômica: {edit_package.pct_genome_identity}%
- Número de edições: {edit_package.n_total_edits}

ESTRUTURE O RELATÓRIO EM:
1. Resumo executivo da reconstrução
2. Análise de confiabilidade dos dados
3. Viabilidade técnica do pacote de edição
4. Próximos passos recomendados para laboratório (síntese, validação)

Seja preciso, use apenas os números fornecidos, tom técnico e científico.
Máximo 300 palavras. Em português.
"""

    try:
        if streaming:
            return cliente.gerar_texto(prompt_completo, streaming=True)
        else:
            resposta = cliente.gerar_texto(prompt_completo, streaming=False)
            if not resposta or resposta.strip() == "":
                raise AIReportError("Ollama retornou resposta vazia")
            return resposta
    except RuntimeError as e:
        raise AIReportError(f"Erro ao comunicar com Ollama: {e}") from e


def generate_lab_report(
    reconstruction: ReconstructionResult,
    edit_package: EditPackage,
    scanner_summary: dict,
    target_species_label: str,
) -> str:
    """
    Interface compatível com versão anterior (para manter retrocompatibilidade).
    Wrapper que chama gerar_relatorio_com_ollama().
    """
    return gerar_relatorio_com_ollama(  # type: ignore[return-value]
        reconstruction=reconstruction,
        edit_package=edit_package,
        scanner_summary=scanner_summary,
        target_species_label=target_species_label,
        streaming=False,
    )
