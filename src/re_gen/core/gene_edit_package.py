"""
gene_edit_package.py
---------------------
Gera o "DNA especial Re-Dino": nao e mais um DNA magico que regenera
materia morta -- e o PACOTE DE EDICOES GENICAS. Ou seja, a lista de
diferencas (mutacoes pontuais, insercoes, delecoes) entre:

  (a) a sequencia ancestral reconstruida (reconstruct.py)
  (b) o genoma do hospedeiro vivo escolhido (ex: um embriao de avestruz
      ou jacare, especies aparentadas ao dinossauro alvo)

Essa lista de edicoes e exatamente o tipo de dado que ferramentas reais de
CRISPR (ex: Benchling, CHOPCHOP, Synthego) usam para desenhar guide-RNAs
que editam um embriao hospedeiro para expressar caracteristicas do
ancestral -- e o metodo real usado pela Colossal Biosciences no projeto
do lobo-gigante e do mamute.

Isso NAO transforma o hospedeiro no dinossauro original; produz um HIBRIDO
editado, que e o limite real da tecnica hoje.
"""

from __future__ import annotations

from dataclasses import dataclass

from re_gen.core.reconstruct import ReconstructionResult


@dataclass
class GeneEdit:
    position: int  # posicao na sequencia consenso alinhada
    host_base: str
    target_base: str
    edit_type: str  # "substituicao" | "insercao" | "delecao"
    confidence: float  # confianca da reconstrucao ancestral nessa posicao


@dataclass
class EditPackage:
    target_species_label: str
    host_species: str
    edits: list[GeneEdit]
    n_total_edits: int
    pct_genome_identity: float  # % de posicoes ja identicas entre hospedeiro e ancestral


def build_edit_package(
    reconstruction: ReconstructionResult,
    host_sequence: str,
    host_species: str,
    target_species_label: str,
    min_confidence_to_edit: float = 0.55,
) -> EditPackage:
    """
    Compara a sequencia ancestral reconstruida com a sequencia do hospedeiro
    vivo escolhido, posicao a posicao (assumindo que ja estao no mesmo
    frame/regiao -- em uso real isso exige alinhamento previo, aqui usamos
    a mesma ancora de reconstruct.py).

    Só gera edicoes onde a confianca da reconstrucao ancestral for >=
    min_confidence_to_edit -- editar um embriao real com base em uma
    posicao de baixa confianca seria irresponsavel mesmo hipoteticamente,
    entao o pacote deliberadamente omite essas posicoes.
    """
    consensus = reconstruction.consensus_sequence
    confidences = reconstruction.per_base_confidence

    n = min(len(consensus), len(host_sequence), len(confidences))
    edits: list[GeneEdit] = []
    identical = 0

    for i in range(n):
        target_base = consensus[i]
        host_base = host_sequence[i]
        conf = confidences[i]

        if target_base == host_base:
            identical += 1
            continue

        if conf < min_confidence_to_edit:
            continue  # nao propoe edicao em posicao pouco confiavel

        edits.append(
            GeneEdit(
                position=i,
                host_base=host_base,
                target_base=target_base,
                edit_type="substituicao",
                confidence=round(conf, 3),
            )
        )

    pct_identity = round(100 * identical / n, 2) if n else 0.0

    return EditPackage(
        target_species_label=target_species_label,
        host_species=host_species,
        edits=edits,
        n_total_edits=len(edits),
        pct_genome_identity=pct_identity,
    )


def export_edit_package_csv(package: EditPackage, path: str) -> None:
    """Exporta o pacote de edicoes como CSV -- formato que uma ferramenta real
    de design de CRISPR guide-RNA (ex: CHOPCHOP, Benchling) consegue importar."""
    import csv

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["position", "host_base", "target_base", "edit_type", "confidence"])
        for e in package.edits:
            writer.writerow([e.position, e.host_base, e.target_base, e.edit_type, e.confidence])
