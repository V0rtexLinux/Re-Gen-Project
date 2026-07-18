#!/usr/bin/env python3
"""
genome_streaming.py -- Processamento Streaming de Genomas Gigantes
===================================================================
Lê FASTA/FASTQ em chunks sem carregar tudo na RAM.
Ideal para genomas de 2-3 bilhões de bp.

Classes principais:
- GenomeStreamReader: Iterator para sequências FASTA
- ChunkProcessor: Processa chunks individualmente
- StreamingValidator: Valida conforme lê
- StreamingAnalyzer: Coleta estatísticas sem buffer

USO:
    reader = GenomeStreamReader("genome.fasta", chunk_size=100_000)
    for chunk in reader:
        print(f"Processando {len(chunk.sequence)} bp...")
        validator.validate(chunk)
"""

from __future__ import annotations

import gzip
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

# ==================== ESTRUTURAS ====================


@dataclass
class StreamChunk:
    """Um fragmento de genoma lido em streaming."""

    chunk_id: int
    """ID único do chunk."""

    sequence: str
    """Sequência DNA (ATGC...)."""

    quality: str | None = None
    """Scores de qualidade (FASTQ)."""

    metadata: dict = field(default_factory=dict)
    """Metadados opcionais."""

    start_bp: int = 0
    """Posição inicial no genoma (0-indexed)."""

    end_bp: int = 0
    """Posição final no genoma (exclusivo)."""

    def __len__(self) -> int:
        """Retorna tamanho da sequência em bp."""
        return len(self.sequence)

    def gc_content(self) -> float:
        """Calcula conteúdo GC."""
        if not self.sequence:
            return 0.0
        gc_count = self.sequence.count("G") + self.sequence.count("C")
        return gc_count / len(self.sequence)

    def has_invalid_chars(self) -> bool:
        """Verifica caracteres inválidos."""
        valid = set("ATGCNRYSWKMBDHV")
        return bool(set(self.sequence.upper()) - valid)

    def mean_quality(self) -> float:
        """Calcula qualidade média (FASTQ)."""
        if not self.quality:
            return 0.0
        # ASCII quality scores: Phred+33
        scores = [ord(c) - 33 for c in self.quality]
        return sum(scores) / len(scores) if scores else 0.0


@dataclass
class StreamingStats:
    """Estatísticas coletadas durante streaming."""

    total_bp_read: int = 0
    """Total de bp lidos."""

    chunks_processed: int = 0
    """Número de chunks processados."""

    invalid_bases: int = 0
    """Bases inválidas encontradas."""

    gc_mean: float = 0.0
    """Média de GC%."""

    gc_min: float = 100.0
    """Mínimo GC%."""

    gc_max: float = 0.0
    """Máximo GC%."""

    quality_mean: float = 0.0
    """Qualidade média (FASTQ)."""

    errors: list[str] = field(default_factory=list)
    """Erros encontrados."""

    def update(self, chunk: StreamChunk) -> None:
        """Atualiza stats com novo chunk."""
        self.chunks_processed += 1
        self.total_bp_read += len(chunk)

        # GC content
        gc = chunk.gc_content()
        self.gc_min = min(self.gc_min, gc)
        self.gc_max = max(self.gc_max, gc)
        self.gc_mean = (self.gc_mean * (self.chunks_processed - 1) + gc) / self.chunks_processed

        # Quality
        if chunk.quality:
            q = chunk.mean_quality()
            self.quality_mean = (self.quality_mean * (self.chunks_processed - 1) + q) / self.chunks_processed

        # Invalid bases
        if chunk.has_invalid_chars():
            invalid_count = sum(1 for c in chunk.sequence if c.upper() not in "ATGCNRYSWKMBDHV")
            self.invalid_bases += invalid_count


# ==================== READERS ====================


class GenomeStreamReader(ABC):
    """Leitor base para genomas em streaming."""

    def __init__(self, file_path: str, chunk_size: int = 100_000):
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size
        self.current_chunk_id = 0
        self.current_bp_position = 0
        self.file_handle = None
        self.is_gzipped = str(self.file_path).endswith(".gz")

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()

    def open(self) -> None:
        """Abre arquivo para leitura."""
        if self.is_gzipped:
            self.file_handle = gzip.open(self.file_path, "rt")
        else:
            self.file_handle = open(self.file_path)

    def close(self) -> None:
        """Fecha arquivo."""
        if self.file_handle:
            self.file_handle.close()

    @abstractmethod
    def __iter__(self) -> Iterator[StreamChunk]:
        """Itera sobre chunks."""
        pass


class FastaStreamReader(GenomeStreamReader):
    """Leitor FASTA em streaming."""

    def __iter__(self) -> Iterator[StreamChunk]:
        """Itera sobre sequências FASTA."""
        if not self.file_handle:
            self.open()

        self.file_handle.seek(0)
        self.current_chunk_id = 0
        self.current_bp_position = 0

        current_sequence = ""
        current_header = ""

        for line in self.file_handle:
            line = line.rstrip("\n")

            if not line:
                continue

            if line.startswith(">"):
                # Nova sequência
                if current_sequence:
                    # Processa sequência anterior
                    yield from self._process_sequence(current_sequence, current_header)
                    current_sequence = ""

                current_header = line[1:]
            else:
                # Acumula sequência
                current_sequence += line

        # Processa última sequência
        if current_sequence:
            yield from self._process_sequence(current_sequence, current_header)

    def _process_sequence(self, sequence: str, header: str) -> Iterator[StreamChunk]:
        """Divide sequência em chunks."""
        for i in range(0, len(sequence), self.chunk_size):
            chunk_seq = sequence[i : i + self.chunk_size]

            chunk = StreamChunk(
                chunk_id=self.current_chunk_id,
                sequence=chunk_seq,
                metadata={"header": header},
                start_bp=self.current_bp_position,
                end_bp=self.current_bp_position + len(chunk_seq),
            )

            self.current_chunk_id += 1
            self.current_bp_position += len(chunk_seq)

            yield chunk


class FastqStreamReader(GenomeStreamReader):
    """Leitor FASTQ em streaming."""

    def __iter__(self) -> Iterator[StreamChunk]:
        """Itera sobre sequências FASTQ."""
        if not self.file_handle:
            self.open()

        self.file_handle.seek(0)
        self.current_chunk_id = 0
        self.current_bp_position = 0

        lines = []

        for line in self.file_handle:
            line = line.rstrip("\n")
            lines.append(line)

            if len(lines) == 4:
                # Processa record FASTQ completo
                header = lines[0][1:]  # Remove @
                sequence = lines[1]
                lines[2]
                quality = lines[3]

                # Divide em chunks
                for i in range(0, len(sequence), self.chunk_size):
                    chunk_seq = sequence[i : i + self.chunk_size]
                    chunk_qual = quality[i : i + self.chunk_size]

                    chunk = StreamChunk(
                        chunk_id=self.current_chunk_id,
                        sequence=chunk_seq,
                        quality=chunk_qual,
                        metadata={"header": header},
                        start_bp=self.current_bp_position,
                        end_bp=self.current_bp_position + len(chunk_seq),
                    )

                    self.current_chunk_id += 1
                    self.current_bp_position += len(chunk_seq)

                    yield chunk

                lines = []


# ==================== PROCESSADORES ====================


class ChunkProcessor:
    """Processador de chunks com pipeline."""

    def __init__(self):
        self.pipeline: list[Callable[[StreamChunk], StreamChunk]] = []

    def add_filter(self, func: Callable[[StreamChunk], bool]) -> ChunkProcessor:
        """Adiciona filtro."""

        def wrapper(chunk: StreamChunk) -> StreamChunk | None:
            return chunk if func(chunk) else None

        self.pipeline.append(wrapper)
        return self

    def add_transform(self, func: Callable[[StreamChunk], StreamChunk]) -> ChunkProcessor:
        """Adiciona transformação."""
        self.pipeline.append(func)
        return self

    def process(self, chunk: StreamChunk) -> StreamChunk | None:
        """Processa chunk através do pipeline."""
        current = chunk

        for step in self.pipeline:
            if current is None:
                return None
            current = step(current)

        return current

    def process_stream(self, reader: GenomeStreamReader) -> Iterator[StreamChunk]:
        """Processa stream de chunks."""
        for chunk in reader:
            processed = self.process(chunk)
            if processed is not None:
                yield processed


class StreamingValidator:
    """Validador que funciona com streaming."""

    def __init__(self):
        self.stats = StreamingStats()
        self.errors: list[dict] = []

    def validate_chunk(self, chunk: StreamChunk) -> bool:
        """Valida um chunk."""
        self.stats.update(chunk)

        is_valid = True

        # Check 1: Caracteres inválidos
        if chunk.has_invalid_chars():
            is_valid = False
            self.errors.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "type": "invalid_chars",
                    "message": "Sequência contém caracteres inválidos",
                }
            )

        # Check 2: GC content anormal
        gc = chunk.gc_content()
        if gc < 0.20 or gc > 0.80:
            self.errors.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "type": "extreme_gc",
                    "gc_percent": gc * 100,
                    "message": f"GC content extremo: {gc * 100:.1f}%",
                }
            )

        # Check 3: Homopolímeros longos
        max_homopolymer = 0
        current_base = None
        current_count = 0

        for base in chunk.sequence:
            if base == current_base:
                current_count += 1
                max_homopolymer = max(max_homopolymer, current_count)
            else:
                current_base = base
                current_count = 1

        if max_homopolymer > 20:
            self.errors.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "type": "long_homopolymer",
                    "length": max_homopolymer,
                    "message": f"Homopolímero detectado: {max_homopolymer} bases",
                }
            )

        # Check 4: Qualidade baixa (FASTQ)
        if chunk.quality:
            mean_q = chunk.mean_quality()
            if mean_q < 20:
                self.errors.append(
                    {
                        "chunk_id": chunk.chunk_id,
                        "type": "low_quality",
                        "quality_score": mean_q,
                        "message": f"Qualidade baixa: Phred {mean_q:.1f}",
                    }
                )

        return is_valid

    def validate_stream(self, reader: GenomeStreamReader) -> tuple[bool, StreamingStats]:
        """Valida stream completo."""
        for chunk in reader:
            self.validate_chunk(chunk)

        # Normaliza stats
        if self.stats.gc_min > self.stats.gc_max:
            self.stats.gc_min = self.stats.gc_max = self.stats.gc_mean

        return len(self.errors) == 0, self.stats


class StreamingAnalyzer:
    """Analisador que coleta estatísticas sem buffer."""

    def __init__(self):
        self.stats = StreamingStats()
        self.gc_histogram: dict[int, int] = {}  # Bucket -> count
        self.base_composition: dict[str, int] = {b: 0 for b in "ATGCN"}

    def analyze_chunk(self, chunk: StreamChunk) -> None:
        """Analisa um chunk."""
        self.stats.update(chunk)

        # Histogram GC
        gc_bucket = int(chunk.gc_content() * 100) // 5  # Buckets de 5%
        self.gc_histogram[gc_bucket] = self.gc_histogram.get(gc_bucket, 0) + 1

        # Composição de bases
        for base in chunk.sequence.upper():
            if base in self.base_composition:
                self.base_composition[base] += 1

    def analyze_stream(self, reader: GenomeStreamReader) -> dict:
        """Analisa stream completo."""
        for chunk in reader:
            self.analyze_chunk(chunk)

        return self.get_report()

    def get_report(self) -> dict:
        """Retorna relatório de análise."""
        total_bases = self.stats.total_bp_read

        if total_bases == 0:
            return {"error": "Nenhuma sequência lida"}

        base_percent = {base: (count / total_bases * 100) for base, count in self.base_composition.items()}

        return {
            "total_bp": total_bases,
            "chunks": self.stats.chunks_processed,
            "gc_mean_percent": self.stats.gc_mean * 100,
            "gc_min_percent": self.stats.gc_min * 100,
            "gc_max_percent": self.stats.gc_max * 100,
            "base_composition": base_percent,
            "gc_histogram": dict(sorted(self.gc_histogram.items())),
            "quality_mean": self.stats.quality_mean,
            "invalid_bases": self.stats.invalid_bases,
        }


# ==================== UTILITÁRIOS ====================


def detect_file_format(file_path: str) -> str:
    """Detecta formato (FASTA ou FASTQ)."""
    with gzip.open(file_path, "rt") if file_path.endswith(".gz") else open(file_path) as f:
        first_line = f.readline()

    if first_line.startswith(">"):
        return "fasta"
    elif first_line.startswith("@"):
        return "fastq"
    else:
        return "unknown"


def create_reader(file_path: str, chunk_size: int = 100_000) -> GenomeStreamReader:
    """Factory para criar reader apropriado."""
    fmt = detect_file_format(file_path)

    if fmt == "fasta":
        return FastaStreamReader(file_path, chunk_size)
    elif fmt == "fastq":
        return FastqStreamReader(file_path, chunk_size)
    else:
        raise ValueError(f"Formato desconhecido: {file_path}")


# ==================== EXEMPLO ====================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("USO: python genome_streaming.py <fasta_ou_fastq>")
        print("\nExemplo:")
        print("  python genome_streaming.py genome.fasta")
        print("  python genome_streaming.py sequencers_output.fastq.gz")
        sys.exit(1)

    file_path = sys.argv[1]

    print(f"\n{'=' * 70}")
    print(f"Analisando: {file_path}")
    print(f"{'=' * 70}\n")

    # Detecta formato
    fmt = detect_file_format(file_path)
    print(f"Formato detectado: {fmt.upper()}")

    # Cria reader
    with create_reader(file_path, chunk_size=50_000) as reader:
        # Análise
        analyzer = StreamingAnalyzer()
        report = analyzer.analyze_stream(reader)

    # Imprime relatório
    print(f"\n{'=' * 70}")
    print("RELATÓRIO DE ANÁLISE")
    print(f"{'=' * 70}\n")

    print(f"Total de bp: {report['total_bp']:,}")
    print(f"Chunks processados: {report['chunks']:,}")
    print("\nComposição de bases:")
    for base, percent in report["base_composition"].items():
        print(f"  {base}: {percent:.2f}%")

    print("\nConteúdo GC:")
    print(f"  Média: {report['gc_mean_percent']:.2f}%")
    print(f"  Min: {report['gc_min_percent']:.2f}%")
    print(f"  Max: {report['gc_max_percent']:.2f}%")

    if report.get("quality_mean"):
        print("\nQualidade (FASTQ):")
        print(f"  Média Phred: {report['quality_mean']:.1f}")

    if report.get("invalid_bases"):
        print("\nErros:")
        print(f"  Bases inválidas: {report['invalid_bases']}")

    print(f"\n{'=' * 70}\n")
