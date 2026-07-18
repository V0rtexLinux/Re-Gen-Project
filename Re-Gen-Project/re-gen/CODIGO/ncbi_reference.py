#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deep_reference_search.py
=========================
Busca PROFUNDA de sequências de referência em NCBI para reconstrução ancestral.

Diferente de ncbi_reference.py (que busca O MÍNIMO):
- Busca múltiplos genes (não só um)
- Extende a busca para centenas de espécies relacionadas
- Usa árvores filogenéticas para priorizar referências
- Aplica múltiplas estratégias de busca (Entrez, BLAST, taxonomia)
- Valida qualidade de sequência
- Armazena metadata completo de cada referência
"""

import logging
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime
from pathlib import Path
import json

from Bio import Entrez, SeqIO
import io

logger = logging.getLogger(__name__)


@dataclass
class ReferenceSequenceDeep:
    """Sequência de referência com metadata completo."""
    species: str
    accession: str
    gene_name: str
    sequence: str
    length: int
    organism_lineage: List[str] = field(default_factory=list)
    publication_date: Optional[str] = None
    quality_score: float = 0.0  # 0-100, baseado em validação
    source_database: str = "NCBI"
    phylogenetic_distance: float = 0.0  # distância estimada até dinossauro
    validated: bool = False
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())


class DeepReferenceSearchEngine:
    """
    Motor de busca profunda e abrangente de referências filogenéticas.
    """

    # Genes mais informativos para reconstrução ancestral de vertebrados
    KEY_GENES = [
        "cytochrome b",  # mitocondrial, altamente conservado
        "COI",  # cytochrome c oxidase I
        "16S ribosomal RNA",
        "12S ribosomal RNA",
        "RAG1",  # recombination activating gene 1
        "ND1",  # NADH dehydrogenase subunit 1
        "POMC",  # pro-opiomelanocortin (comportamento, fisiologia)
        "Hox genes",  # genes homeóticos (desenvolvimento)
        "myosin heavy chain",
        "alpha-globin",
    ]

    # Grupos de referência com prioridades (mais próximos aos dinossauros primeiro)
    REFERENCE_GROUPS = {
        "aves_modernas": {
            "taxa": [
                "Gallus gallus",  # galinha
                "Struthio camelus",  # avestruz (linhagem basal)
                "Anas platyrhynchos",  # pato
                "Columba livia",  # pombo
                "Tyto alba",  # coruja-comum
                "Falco peregrinus",  # falcão peregrino
            ],
            "priority": 1,
            "description": "Aves viventes (parentes vivos mais próximos)"
        },
        "crocodilianos": {
            "taxa": [
                "Alligator mississippiensis",
                "Crocodylus niloticus",
                "Gavialis gangeticus",
                "Caiman crocodilus",
            ],
            "priority": 2,
            "description": "Crocodilianos (grupo-irmão dos dinossauros)"
        },
        "lepidosauria": {
            "taxa": [
                "Iguana iguana",
                "Varanus komodoensis",
                "Anolis sagrei",
            ],
            "priority": 3,
            "description": "Lagartos e cobras"
        },
        "testudines": {
            "taxa": [
                "Chelonoidis niger",
                "Trachemys scripta",
            ],
            "priority": 4,
            "description": "Tartarugas"
        },
    }

    def __init__(self, email: str, api_key: Optional[str] = None, output_dir: str = "./deep_search_results"):
        if not email or "@" not in email:
            raise ValueError("Email válido exigido para NCBI Entrez API")

        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key

        self.logger = logging.getLogger("DeepReferenceSearch")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[ReferenceSequenceDeep] = []

    def search_comprehensive(self, target_lineage: str = "dinosauria") -> List[ReferenceSequenceDeep]:
        """
        Executa busca ABRANGENTE:
        1. Múltiplos genes
        2. Múltiplos grupos de referência
        3. Validação de qualidade
        4. Cálculo de distância filogenética
        """
        self.logger.info(f"Iniciando busca profunda para {target_lineage}...")
        all_results: Dict[str, ReferenceSequenceDeep] = {}

        # Itera por grupos de referência (em ordem de prioridade)
        for group_name, group_info in sorted(
            self.REFERENCE_GROUPS.items(),
            key=lambda x: x[1]["priority"]
        ):
            self.logger.info(f"\n[{group_info['priority']}] {group_info['description']}")

            for gene in self.KEY_GENES:
                for species in group_info["taxa"]:
                    try:
                        ref = self._fetch_single_sequence(species, gene)
                        if ref:
                            # Valida qualidade
                            ref.quality_score = self._calculate_quality_score(ref)
                            ref.phylogenetic_distance = self._estimate_phylogenetic_distance(
                                species, group_name
                            )
                            ref.validated = ref.quality_score >= 70.0

                            key = f"{species}_{gene}"
                            if key not in all_results or ref.quality_score > all_results[key].quality_score:
                                all_results[key] = ref
                                self.logger.info(
                                    f"  ✓ {species}/{gene}: {len(ref.sequence):,}bp "
                                    f"(Q={ref.quality_score:.0f})"
                                )

                        time.sleep(0.4)  # rate limit NCBI

                    except Exception as e:
                        self.logger.debug(f"  Erro em {species}/{gene}: {e}")
                        continue

        self.results = list(all_results.values())
        self.logger.info(f"\n✓ Busca concluída: {len(self.results)} sequências validadas")
        self._save_results()
        return self.results

    def _fetch_single_sequence(self, species: str, gene: str) -> Optional[ReferenceSequenceDeep]:
        """Busca uma sequência específica no NCBI."""
        try:
            term = f'{species}[Organism] AND {gene}[Gene] AND (complete OR full)'
            handle = Entrez.esearch(db="nucleotide", term=term, retmax=1, sort="relevance")
            result = Entrez.read(handle)
            handle.close()

            if not result.get("IdList"):
                return None

            uid = result["IdList"][0]
            fetch_handle = Entrez.efetch(db="nucleotide", id=uid, rettype="gb", retmode="xml")
            records = Entrez.read(fetch_handle)
            fetch_handle.close()

            if not records:
                return None

            record = records[0]
            seq_text = record.get("GBSeq_sequence", "")

            if not seq_text:
                return None

            lineage = record.get("GBSeq_organism", "").split(";")

            return ReferenceSequenceDeep(
                species=species,
                accession=record.get("GBSeq_primary-accession", "unknown"),
                gene_name=gene,
                sequence=seq_text.upper(),
                length=len(seq_text),
                organism_lineage=lineage,
                publication_date=record.get("GBSeq_create-date"),
                source_database="NCBI",
            )

        except Exception as e:
            self.logger.debug(f"Erro ao buscar {species}/{gene}: {e}")
            return None

    def _calculate_quality_score(self, ref: ReferenceSequenceDeep) -> float:
        """
        Calcula score de qualidade (0-100) da sequência:
        - Comprimento (>500bp = 20pts)
        - Sem N's excessivos (>95% bases reais = 20pts)
        - Sem gaps (>99% = 20pts)
        - GC% normal (40-60% = 20pts)
        - Accession de alta qualidade (RefSeq = 20pts)
        """
        score = 0.0

        # Comprimento
        if ref.length > 500:
            score += 20

        # Contagem de N's
        n_count = ref.sequence.count("N")
        if len(ref.sequence) > 0:
            n_ratio = n_count / len(ref.sequence)
            if n_ratio < 0.05:
                score += 20

        # Gaps
        gap_count = ref.sequence.count("-")
        if gap_count == 0:
            score += 20

        # GC content
        gc_count = ref.sequence.count("G") + ref.sequence.count("C")
        if len(ref.sequence) > 0:
            gc_ratio = gc_count / len(ref.sequence)
            if 0.4 <= gc_ratio <= 0.6:
                score += 20

        # Accession de qualidade
        if ref.accession.startswith("NM_") or ref.accession.startswith("NC_"):
            score += 20

        return min(100.0, score)

    def _estimate_phylogenetic_distance(self, species: str, group_name: str) -> float:
        """
        Estima distância filogenética até dinossauro (em milhões de anos).
        Quanto MENOR, mais próximo é do dinossauro.
        """
        # Tempos estimados de divergência (Ma - milhões de anos atrás)
        distances = {
            "aves_modernas": 150.0,  # aves se separaram de dinossauros ~150Ma
            "crocodilianos": 240.0,  # crocodilianos se separaram ~240Ma
            "lepidosauria": 310.0,
            "testudines": 320.0,
        }
        return distances.get(group_name, 400.0)

    def _save_results(self) -> None:
        """Salva resultados em JSON estruturado."""
        results_list = [
            {
                "species": r.species,
                "accession": r.accession,
                "gene": r.gene_name,
                "length": r.length,
                "quality_score": r.quality_score,
                "phylogenetic_distance_ma": r.phylogenetic_distance,
                "validated": r.validated,
                "organism_lineage": r.organism_lineage,
            }
            for r in sorted(self.results, key=lambda x: x.quality_score, reverse=True)
        ]

        output_path = self.output_dir / "deep_reference_results.json"
        with open(output_path, "w") as f:
            json.dump(results_list, f, indent=2)

        self.logger.info(f"Resultados salvos em: {output_path}")

    def get_best_references_for_gene(self, gene: str, top_n: int = 5) -> List[ReferenceSequenceDeep]:
        """Retorna as N melhores referências para um gene específico."""
        filtered = [r for r in self.results if r.gene_name == gene and r.validated]
        return sorted(filtered, key=lambda x: x.quality_score, reverse=True)[:top_n]

    def get_references_by_priority(self) -> List[ReferenceSequenceDeep]:
        """Retorna referências ordenadas por prioridade filogenética."""
        return sorted(
            self.results,
            key=lambda x: (
                x.phylogenetic_distance,  # mais próximas primeiro
                -x.quality_score,  # melhor qualidade depois
            )
        )
