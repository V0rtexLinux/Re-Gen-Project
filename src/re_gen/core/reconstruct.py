"""
reconstruct.py
--------------
O "Re-Dino Engine": reconstrucao de uma sequencia ancestral a partir de
sequencias reais de especies vivas aparentadas.

Tecnica usada: alinhamento par-a-par (algoritmo de Needleman-Wunsch, via
Bio.Align.PairwiseAligner) contra uma sequencia de referencia, seguido de
reconstrucao por consenso ponderado por posicao (majority-rule consensus).

Isso E uma tecnica real de bioinformatica evolutiva (Ancestral Sequence
Reconstruction / ASR usa metodos mais sofisticados como maxima
verossimilhanca sobre uma arvore filogenetica, ex: ferramentas como PAML
ou FastML) -- aqui implementamos uma versao simplificada e honesta:
consenso por alinhamento multiplo estrela (star alignment), que e um
metodo real, so que mais simples que ASR de maxima verossimilhanca.

O que este modulo NAO faz (e nunca vai fazer): inventar bases sem base em
dado real, ou fingir 100% de certeza. Cada posicao reconstruida carrega um
"confidence score" = fracao de sequencias de referencia que concordam
naquela posicao.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from Bio import Align


class ReferenceLike(Protocol):
    """Protocol for any reference with species, accession, and sequence."""

    species: str
    accession: str
    sequence: str


@dataclass
class ReconstructedPosition:
    base: str
    confidence: float  # 0.0 a 1.0


@dataclass
class ReconstructionResult:
    consensus_sequence: str
    per_base_confidence: list[float]
    mean_confidence: float
    n_references_used: int
    reference_species: list[str]
    gc_content: float


def _make_aligner() -> Align.PairwiseAligner:
    aligner = Align.PairwiseAligner()
    aligner.mode = "global"  # Needleman-Wunsch (alinhamento global)
    aligner.match_score = 2.0
    aligner.mismatch_score = -1.0
    aligner.open_gap_score = -2.0
    aligner.extend_gap_score = -0.5
    return aligner


def _align_to_reference(reference: str, query: str, aligner: Align.PairwiseAligner) -> tuple[str, str]:
    """Alinha `query` contra `reference`, retorna as duas strings alinhadas (com gaps '-')."""
    alignment = aligner.align(reference, query)[0]
    aligned_ref, aligned_query = alignment[0], alignment[1]
    return str(aligned_ref), str(aligned_query)


def reconstruct_ancestral_sequence(
    scanned_fragment: str,
    reference_panel: Sequence[ReferenceLike],
) -> ReconstructionResult:
    """
    Reconstroi a sequencia ancestral (do dinossauro fossil) usando:
      1. O fragmento realmente lido no fossil/scanner (`scanned_fragment`),
         usado como ANCORA/backbone do alinhamento (e o dado mais direto
         que temos do organismo extinto, mesmo que curto/degradado).
      2. O painel de referencias vivas (`reference_panel`), alinhadas contra
         essa ancora, pra "preencher" e confirmar trechos via consenso
         evolutivo nos pontos onde o fragmento fossil for curto/ambiguo.

    Retorna a sequencia consenso + confiabilidade por base.
    """
    if not scanned_fragment:
        raise ValueError("scanned_fragment vazio: preciso de ao menos um fragmento real do fossil.")
    if not reference_panel:
        raise ValueError("reference_panel vazio: rode ncbi_reference.fetch_reference_panel primeiro.")

    aligner = _make_aligner()

    # Alinha cada referencia viva contra o fragmento fossil (ancora)
    aligned_pairs: list[str] = []
    backbone_aligned = None
    for ref in reference_panel:
        aligned_ref_backbone, aligned_query = _align_to_reference(scanned_fragment, ref.sequence, aligner)
        if backbone_aligned is None:
            backbone_aligned = aligned_ref_backbone
        aligned_pairs.append(aligned_query)

    assert backbone_aligned is not None
    backbone_len = len(backbone_aligned)

    # Constroi consenso coluna a coluna (majority-rule), usando a base do
    # fossil como voto extra de peso (e o dado mais proximo do organismo real)
    consensus_chars: list[str] = []
    confidences: list[float] = []

    for col in range(backbone_len):
        votes: dict[str, int] = {}

        fossil_base = backbone_aligned[col]
        if fossil_base != "-":
            votes[fossil_base] = votes.get(fossil_base, 0) + 2  # peso 2 pro dado fossil direto

        for aligned_query in aligned_pairs:
            if col < len(aligned_query):
                base = aligned_query[col]
                if base != "-":
                    votes[base] = votes.get(base, 0) + 1

        if not votes:
            continue  # coluna e so gap em todo mundo, ignora

        total_votes = sum(votes.values())
        best_base, best_count = max(votes.items(), key=lambda kv: kv[1])
        consensus_chars.append(best_base)
        confidences.append(best_count / total_votes)

    consensus_seq = "".join(consensus_chars)
    gc = (consensus_seq.count("G") + consensus_seq.count("C")) / len(consensus_seq) if consensus_seq else 0.0

    return ReconstructionResult(
        consensus_sequence=consensus_seq,
        per_base_confidence=confidences,
        mean_confidence=sum(confidences) / len(confidences) if confidences else 0.0,
        n_references_used=len(reference_panel),
        reference_species=[r.species for r in reference_panel],
        gc_content=round(gc * 100, 2),
    )


def low_confidence_regions(result: ReconstructionResult, threshold: float = 0.6) -> list[tuple[int, int]]:
    """Retorna intervalos [inicio, fim) onde a confianca ficou abaixo do limite -- trechos que precisariam de mais dado real (mais reads do fossil ou mais especies de referencia) antes de qualquer uso pratico."""
    regions = []
    start = None
    for i, conf in enumerate(result.per_base_confidence):
        if conf < threshold:
            if start is None:
                start = i
        else:
            if start is not None:
                regions.append((start, i))
                start = None
    if start is not None:
        regions.append((start, len(result.per_base_confidence)))
    return regions
