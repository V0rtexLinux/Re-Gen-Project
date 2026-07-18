"""
scanner_input.py
----------------
Le a saida REAL de um hardware de sequenciamento de DNA.

Sequenciadores reais (ex: Oxford Nanopore MinION/GridION, Illumina MiSeq)
nao entregam "letras A T C G" direto por uma API simples. O fluxo real e:

  1. O hardware le a molecula de DNA fisicamente (corrente eletrica variando
     ao passar por um nanoporo, no caso da Nanopore; ou fluorescencia, no
     caso da Illumina).
  2. Um software de "basecalling" com rede neural (ex: Dorado, da Oxford
     Nanopore) traduz esse sinal bruto em bases -> gera um arquivo FASTQ
     (sequencia + qualidade por base) ou FAST5/POD5 (sinal bruto).
  3. Esse FASTQ e o que qualquer programa (incluindo este) realmente le.

Este modulo le esse arquivo real. Nao ha nenhuma simulacao de "escaneamento
magico" aqui: se voce tem um MinION, exporta o FASTQ do Dorado/MinKNOW e
aponta o caminho do arquivo pra essa funcao.

Como plugar hardware fisico de verdade:
  - Oxford Nanopore MinION -> roda via MinKNOW (software oficial) no seu PC
    -> ativa "basecalling" com Dorado -> exporta .fastq(.gz) na pasta de saida
    -> use esse caminho aqui.
  - Illumina (MiSeq/NextSeq) -> o proprio sequenciador gera FASTQ ao fim da
    corrida via bcl2fastq/BCL Convert -> use esse caminho aqui.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord


@dataclass
class ScannedRead:
    read_id: str
    sequence: str
    mean_quality: float | None  # Phred quality media (None se veio de FASTA sem qualidade)
    length: int


class ScannerInputError(Exception):
    pass


def _detect_format(path: Path) -> str:
    suffixes = "".join(path.suffixes).lower()
    if "fastq" in suffixes or suffixes.endswith(".fq") or suffixes.endswith(".fq.gz"):
        return "fastq"
    if "fasta" in suffixes or suffixes.endswith(".fa") or suffixes.endswith(".fna"):
        return "fasta"
    raise ScannerInputError(
        f"Formato de arquivo nao reconhecido em '{path}'. "
        "Exporte do seu sequenciador em FASTQ (.fastq/.fastq.gz) ou FASTA (.fasta/.fa)."
    )


def load_scanner_output(file_path: str, min_length: int = 50, min_mean_quality: float = 7.0) -> list[ScannedRead]:
    """
    Le o arquivo real exportado por um sequenciador (FASTQ ou FASTA) e
    devolve as leituras (reads) que passaram no filtro de qualidade minimo.

    Parametros:
        file_path: caminho do arquivo real gerado pelo hardware/basecaller.
        min_length: descarta reads menores que isso (ruido tipico de sequenciador).
        min_mean_quality: Phred score medio minimo (so aplica a FASTQ).

    Retorna:
        Lista de ScannedRead validos.
    """
    path = Path(file_path)
    if not path.exists():
        raise ScannerInputError(
            f"Arquivo '{file_path}' nao encontrado. Confirme o caminho exportado "
            "pelo software do seu sequenciador (MinKNOW/Dorado, bcl2fastq, etc.)."
        )

    fmt = _detect_format(path)
    records: Iterator[SeqRecord] = SeqIO.parse(str(path), fmt)

    reads: list[ScannedRead] = []
    for rec in records:
        seq = str(rec.seq).upper()
        if len(seq) < min_length:
            continue

        mean_q = None
        if fmt == "fastq":
            quals = rec.letter_annotations.get("phred_quality", [])
            if quals:
                mean_q = sum(quals) / len(quals)
                if mean_q < min_mean_quality:
                    continue

        reads.append(
            ScannedRead(
                read_id=rec.id,
                sequence=seq,
                mean_quality=mean_q,
                length=len(seq),
            )
        )

    if not reads:
        raise ScannerInputError(
            "Nenhuma leitura passou no filtro de qualidade. Verifique o arquivo "
            "de origem ou reduza min_length/min_mean_quality."
        )

    return reads


def summarize_reads(reads: list[ScannedRead]) -> dict:
    total_bases = sum(r.length for r in reads)
    avg_len = total_bases / len(reads)
    avg_q = [r.mean_quality for r in reads if r.mean_quality is not None]
    return {
        "n_reads": len(reads),
        "total_bases": total_bases,
        "avg_length": round(avg_len, 1),
        "avg_quality": round(sum(avg_q) / len(avg_q), 2) if avg_q else None,
    }
