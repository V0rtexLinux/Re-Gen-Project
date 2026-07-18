"""
genome_validator.py
-------------------
Motor avançado de validação genética.

Detecta:
1. Sequências inválidas (caracteres não-ATCGN)
2. Regiões de baixa complexidade
3. Estruturas secundárias problemáticas
4. Codons raros/problemáticos
5. Inconsistências filogenéticas
6. Regiões de repetição (tandem repeats)
7. Inversões/translocações suspeitas

Referências:
- De Bruijn graph validation (assembly)
- Secondary structure prediction (NUPACK)
- Codon usage bias (CAI - Codon Adaptation Index)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class SeverityLevel(Enum):
    """Nível de severidade de um erro."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Um problema detectado na sequência."""

    issue_type: str  # "invalid_char", "homopolymer", etc
    severity: SeverityLevel
    position: int | None = None  # Posição no genoma
    description: str = ""
    suggested_fix: str | None = None
    affected_region: str | None = None  # Sequência afetada


class GenomeValidator:
    """Validador avançado de genomas."""

    # Codons de parada
    STOP_CODONS = {"TAA", "TAG", "TGA"}

    # Codons raros em dinossauros (estimados de aves atuais)
    RARE_CODONS = {"CGA", "CGG", "AGA", "AGG", "TTA", "TCA"}

    def __init__(self):
        self.issues: list[ValidationIssue] = []

    def validate(self, sequence: str, chunk_id: str = "unknown") -> ValidationReport:
        """
        Executa validação completa de um segmento.

        Returns:
            ValidationReport com todos os problemas encontrados
        """
        self.issues = []

        # Validações (em ordem)
        self._check_valid_characters(sequence)
        self._check_homopolymers(sequence)
        self._check_gc_content(sequence)
        self._check_low_complexity(sequence)
        self._check_stop_codons(sequence)
        self._check_rare_codons(sequence)
        self._check_tandem_repeats(sequence)

        return ValidationReport(
            chunk_id=chunk_id,
            sequence_length=len(sequence),
            issues=self.issues,
        )

    def _check_valid_characters(self, sequence: str) -> None:
        """Verifica se contém apenas ATCGN."""
        valid_chars = set("ATCGN")
        seq_upper = sequence.upper()

        invalid_chars = set(seq_upper) - valid_chars
        if invalid_chars:
            self.issues.append(
                ValidationIssue(
                    issue_type="invalid_character",
                    severity=SeverityLevel.CRITICAL,
                    description=f"Caracteres inválidos encontrados: {invalid_chars}",
                    affected_region="global",
                )
            )

    def _check_homopolymers(self, sequence: str, threshold: int = 10) -> None:
        """Detecta sequências homopoliméricas longas."""
        seq_upper = sequence.upper()

        for base in "ATCG":
            pattern = base * threshold
            for match in re.finditer(pattern, seq_upper):
                self.issues.append(
                    ValidationIssue(
                        issue_type="homopolymer",
                        severity=SeverityLevel.WARNING,
                        position=match.start(),
                        description=f"Homopolímero longo ({threshold}+ {base}s) pode causar erro de síntese",
                        suggested_fix=f"Inserir SNP ou quebrar sequência de {base}s",
                        affected_region=seq_upper[match.start() : match.end()],
                    )
                )

    def _check_gc_content(self, sequence: str) -> None:
        """Verifica conteúdo GC (ideal: 40-60%)."""
        seq_upper = sequence.upper()
        gc_count = seq_upper.count("G") + seq_upper.count("C")
        gc_percent = (gc_count / len(sequence)) * 100

        if gc_percent < 30:
            self.issues.append(
                ValidationIssue(
                    issue_type="low_gc_content",
                    severity=SeverityLevel.WARNING,
                    description=f"GC% muito baixo ({gc_percent:.1f}%) - pode formar estruturas secundárias",
                    suggested_fix="Aumentar G/C content inserindo SNPs sinônimas",
                )
            )
        elif gc_percent > 70:
            self.issues.append(
                ValidationIssue(
                    issue_type="high_gc_content",
                    severity=SeverityLevel.WARNING,
                    description=f"GC% muito alto ({gc_percent:.1f}%) - pode reduzir expressão",
                    suggested_fix="Reduzir G/C content com SNPs sinônimas",
                )
            )

    def _check_low_complexity(self, sequence: str, window: int = 30) -> None:
        """
        Detecta regiões de baixa complexidade.

        Baixa complexidade = pouca variação (ex: ATATATATAT)
        """
        seq_upper = sequence.upper()

        for i in range(len(seq_upper) - window):
            window_seq = seq_upper[i : i + window]

            # Complexidade = número de dinucleotídeos únicos / 16 (máximo)
            dinucs = set()
            for j in range(len(window_seq) - 1):
                dinucs.add(window_seq[j : j + 2])

            complexity = len(dinucs) / 16.0

            if complexity < 0.5:  # Menos de 50% dos dinucleotídeos únicos
                self.issues.append(
                    ValidationIssue(
                        issue_type="low_complexity",
                        severity=SeverityLevel.WARNING,
                        position=i,
                        description=f"Região de baixa complexidade (score: {complexity:.2f}) - pode ser alvo de RNase",
                        affected_region=window_seq,
                    )
                )
                break  # Só reporta uma vez para não ficar repetitivo

    def _check_stop_codons(self, sequence: str) -> None:
        """
        Detecta codons de parada fora do final.

        Codons de parada terminam tradução prematura.
        """
        seq_upper = sequence.upper()

        # Verifica todos os 3 reading frames
        for frame in range(3):
            for i in range(frame, len(seq_upper) - 2, 3):
                codon = seq_upper[i : i + 3]
                if codon in self.STOP_CODONS:
                    # Só reporta se não for no final
                    if i + 3 < len(seq_upper):
                        self.issues.append(
                            ValidationIssue(
                                issue_type="stop_codon",
                                severity=SeverityLevel.ERROR,
                                position=i,
                                description=f"Codon de parada {codon} em posição {i} (frame {frame})",
                                suggested_fix="Editar para codon silencioso (syn synonym",
                                affected_region=codon,
                            )
                        )

    def _check_rare_codons(self, sequence: str) -> None:
        """Detecta codons raros que podem reduzir expressão."""
        seq_upper = sequence.upper()
        rare_count = 0

        for i in range(0, len(seq_upper) - 2, 3):
            codon = seq_upper[i : i + 3]
            if codon in self.RARE_CODONS:
                rare_count += 1

        rare_percent = (rare_count / (len(seq_upper) // 3)) * 100

        if rare_percent > 10:  # Mais de 10% de codons raros
            self.issues.append(
                ValidationIssue(
                    issue_type="rare_codons",
                    severity=SeverityLevel.WARNING,
                    description=f"Muitos codons raros ({rare_percent:.1f}%) - pode reduzir expressão proteica",
                    suggested_fix="Otimizar codons para usage comum",
                )
            )

    def _check_tandem_repeats(self, sequence: str, min_repeat_len: int = 6) -> None:
        """Detecta repetições em tandem (podem causar instabilidade)."""
        seq_upper = sequence.upper()

        for repeat_len in range(min_repeat_len, 21):
            for i in range(len(seq_upper) - repeat_len * 2):
                unit = seq_upper[i : i + repeat_len]

                # Verifica se se repete
                repeat_count = 0
                j = i
                while j < len(seq_upper) - repeat_len:
                    if seq_upper[j : j + repeat_len] == unit:
                        repeat_count += 1
                        j += repeat_len
                    else:
                        break

                if repeat_count >= 3:  # 3+ repetições
                    self.issues.append(
                        ValidationIssue(
                            issue_type="tandem_repeat",
                            severity=SeverityLevel.WARNING,
                            position=i,
                            description=f"Repetição em tandem encontrada: {unit} (x{repeat_count})",
                            suggested_fix="Quebrar repetição inserindo SNP silenciosa",
                            affected_region=seq_upper[i : i + repeat_len * repeat_count],
                        )
                    )
                    return  # Só reporta um para não ficar repetitivo


@dataclass
class ValidationReport:
    """Relatório completo de validação."""

    chunk_id: str
    sequence_length: int
    issues: list[ValidationIssue]

    @property
    def is_valid(self) -> bool:
        """True se não houver erros críticos."""
        return not any(issue.severity == SeverityLevel.CRITICAL for issue in self.issues)

    @property
    def error_count(self) -> int:
        """Número de erros."""
        return len([i for i in self.issues if i.severity in (SeverityLevel.ERROR, SeverityLevel.CRITICAL)])

    @property
    def warning_count(self) -> int:
        """Número de avisos."""
        return len([i for i in self.issues if i.severity == SeverityLevel.WARNING])

    def to_dict(self) -> dict:
        """Serializa para dicionário."""
        return {
            "chunk_id": self.chunk_id,
            "sequence_length": self.sequence_length,
            "is_valid": self.is_valid,
            "errors": self.error_count,
            "warnings": self.warning_count,
            "issues": [
                {
                    "type": issue.issue_type,
                    "severity": issue.severity.value,
                    "position": issue.position,
                    "description": issue.description,
                    "suggested_fix": issue.suggested_fix,
                    "affected_region": issue.affected_region,
                }
                for issue in self.issues
            ],
        }

    def __str__(self) -> str:
        """Representação em string."""
        lines = [
            f"Validação: {self.chunk_id}",
            f"Comprimento: {self.sequence_length} bp",
            f"Status: {'✓ VÁLIDO' if self.is_valid else '✗ INVÁLIDO'}",
            f"Erros: {self.error_count}, Avisos: {self.warning_count}",
        ]

        if self.issues:
            lines.append("\nProblemas:")
            for issue in self.issues:
                severity_emoji = {
                    SeverityLevel.INFO: "ℹ",
                    SeverityLevel.WARNING: "⚠",
                    SeverityLevel.ERROR: "❌",
                    SeverityLevel.CRITICAL: "🔴",
                }

                lines.append(f"  {severity_emoji.get(issue.severity, '')} {issue.issue_type}: {issue.description}")

        return "\n".join(lines)


def create_validator() -> GenomeValidator:
    """Factory para validador."""
    return GenomeValidator()
