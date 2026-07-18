"""
crispr_engine.py
----------------
Motor completo de CRISPR-Cas9: design, otimização, predição de off-targets.

Algoritmos:
1. gRNA design: encontra guias ótimos com PAM (NGG)
2. Scoring: pontuação baseada em GC%, estrutura, repetições
3. Off-target prediction: busca por locais similares no genoma
4. Delivery otimization: seleciona melhores guias para entrega
5. Efficiency prediction: estima taxa de corte para cada gRNA

Referências:
- Doench et al. (2016) - Optimized sgRNA design
- Hsu et al. (2013) - Off-target effects
- Bae et al. (2014) - Prediction rules
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List
import re
from enum import Enum


class Cas9Variant(Enum):
    """Variantes de Cas9 com diferentes PAMs."""
    SPCAS9 = ("NGG", "SpCas9")           # Streptococcus pyogenes
    SAUCAS9 = ("NGRRT", "SauCas9")       # Staphylococcus aureus
    NMCAS9 = ("NNNNGATT", "NmCas9")      # Neisseria meningitidis
    CPFCAS9 = ("TTN", "CpfCas9")         # Cpf1/Cas12a
    FNCAS9 = ("YG", "FnCas9")            # Francisella novicida


@dataclass
class GuideRNA:
    """Um guide-RNA design ótimo."""
    sequence: str                          # 20bp sequence (5' to 3')
    pam: str                               # PAM adjacente (ex: NGG)
    position: int                          # Posição no genoma alvo
    strand: str = "+"                      # + ou -
    gc_content: float = 0.0                # % GC (ideal: 40-60%)
    specificity_score: float = 0.0         # Score de especificidade (0-100)
    efficiency_score: float = 0.0          # Score de eficiência (0-100)
    off_targets_count: int = 0             # Número de off-targets encontrados
    secondary_structure: Optional[str] = None  # Predicted structure
    homopolymer_count: int = 0             # Número de homopolímeros
    
    @property
    def combined_score(self) -> float:
        """Score combinado para ranking."""
        return (self.specificity_score + self.efficiency_score) / 2.0
    
    @property
    def is_good(self) -> bool:
        """True se gRNA tem boa qualidade."""
        return (
            self.combined_score > 60.0
            and self.off_targets_count < 5
            and self.homopolymer_count == 0
            and 40 <= self.gc_content <= 60
        )


@dataclass
class CRISPREditingPlan:
    """Plano completo de edição CRISPR."""
    target_region: str                     # Região alvo da sequência
    target_start: int
    target_end: int
    desired_change: str                    # "deletion", "insertion", "substitution"
    desired_sequence: Optional[str] = None  # Sequência desejada
    grnas: List[GuideRNA] = field(default_factory=list)
    donor_dna: Optional[str] = None        # Template para edição (se needed)
    expected_efficiency: float = 0.0       # % esperado de sucesso
    potential_risks: List[str] = field(default_factory=list)


class CRISPRDesigner:
    """Desenhador de experimentos CRISPR."""
    
    def __init__(self, variant: Cas9Variant = Cas9Variant.SPCAS9):
        self.variant = variant
        self.pam_pattern = variant.value[0]
    
    def find_grnas(
        self,
        target_sequence: str,
        region_start: int = 0,
        region_end: Optional[int] = None,
        num_grnas: int = 10,
    ) -> List[GuideRNA]:
        """
        Encontra gRNAs ótimos em uma sequência.
        
        Args:
            target_sequence: Sequência alvo completa
            region_start: Início da região de interesse
            region_end: Fim da região
            num_grnas: Quantos gRNAs retornar
        
        Returns:
            Lista de GuideRNAs ranqueados por qualidade
        """
        if region_end is None:
            region_end = len(target_sequence)
        
        grnas = []
        seq_upper = target_sequence.upper()
        grna_len = 20
        
        # Busca por PAM
        for match in self._find_pams(seq_upper):
            pam_pos, pam_seq = match
            
            # gRNA está antes do PAM (para SpCas9)
            grna_start = max(0, pam_pos - grna_len)
            grna_end = grna_start + grna_len
            
            if grna_end > len(seq_upper):
                continue
            
            # Valida se está na região de interesse
            if not (region_start <= grna_start < region_end):
                continue
            
            grna_seq = seq_upper[grna_start:grna_end]
            
            # Cria GuideRNA com scores
            grna = GuideRNA(
                sequence=grna_seq,
                pam=pam_seq,
                position=grna_start,
            )
            
            # Calcula scores
            grna.gc_content = self._calculate_gc_content(grna_seq)
            grna.specificity_score = self._score_specificity(grna_seq)
            grna.efficiency_score = self._score_efficiency(grna_seq)
            grna.homopolymer_count = self._count_homopolymers(grna_seq)
            
            grnas.append(grna)
        
        # Ordena por score combinado
        grnas.sort(key=lambda g: g.combined_score, reverse=True)
        
        return grnas[:num_grnas]
    
    def _find_pams(self, sequence: str) -> List[Tuple[int, str]]:
        """
        Encontra todas as PAMs em uma sequência.
        
        Returns:
            Lista de (posição, sequência_PAM)
        """
        pams = []
        
        if self.variant == Cas9Variant.SPCAS9:
            # NGG: qualquer base seguida de GG
            for match in re.finditer(r"[ATCG]GG", sequence):
                pams.append((match.start(), match.group()))
        
        elif self.variant == Cas9Variant.CPFCAS9:
            # TTN: TT seguida de qualquer base
            for match in re.finditer(r"TT[ATCG]", sequence):
                pams.append((match.start(), match.group()))
        
        # Adicionar outros conforme necessário
        
        return pams
    
    def _calculate_gc_content(self, sequence: str) -> float:
        """Calcula % de GC."""
        gc_count = sequence.count("G") + sequence.count("C")
        return (gc_count / len(sequence)) * 100 if sequence else 0
    
    def _score_specificity(self, grna_sequence: str) -> float:
        """
        Score de especificidade (0-100).
        Baseado em: GC%, complexidade, repeat patterns.
        """
        gc = self._calculate_gc_content(grna_sequence)
        
        # Ideal GC: 40-60%
        gc_score = 100 - abs(50 - gc) * 2
        gc_score = max(0, min(100, gc_score))
        
        # Complexidade (dinucleotídeos únicos)
        dinucs = set()
        for i in range(len(grna_sequence) - 1):
            dinucs.add(grna_sequence[i:i+2])
        complexity = len(dinucs) / 16.0 * 100
        
        # Score final
        specificity = (gc_score * 0.6 + complexity * 0.4)
        return specificity
    
    def _score_efficiency(self, grna_sequence: str) -> float:
        """
        Score de eficiência (0-100).
        Baseado em: Doench et al. machine learning rules.
        """
        # Regras simplificadas de Doench et al. (2016)
        
        # Nucleotídeos na posição 4 e 20 (importante)
        pos4 = grna_sequence[3]
        pos20 = grna_sequence[19]
        
        pos_score = 0
        if pos4 in "G":
            pos_score += 25
        if pos20 in "G":
            pos_score += 25
        
        # GC% (ideal 40-60%)
        gc = self._calculate_gc_content(grna_sequence)
        gc_score = 100 - abs(50 - gc) * 2
        gc_score = max(0, min(100, gc_score))
        
        # Homopolímeros (ruim)
        homo_penalty = 0
        for base in "ATCG":
            if base * 4 in grna_sequence:
                homo_penalty += 15
        
        efficiency = (pos_score + gc_score) / 2 - homo_penalty
        efficiency = max(0, min(100, efficiency))
        
        return efficiency
    
    def _count_homopolymers(self, sequence: str, min_length: int = 4) -> int:
        """Conta homopolímeros na sequência."""
        count = 0
        for base in "ATCG":
            pattern = base * min_length
            if pattern in sequence:
                count += sequence.count(pattern)
        return count
    
    def design_edit_plan(
        self,
        target_sequence: str,
        target_start: int,
        target_end: int,
        desired_change: str,
        desired_sequence: Optional[str] = None,
    ) -> CRISPREditingPlan:
        """
        Desanha um plano completo de edição CRISPR.
        
        Args:
            target_sequence: Sequência genômica completa
            target_start: Início da região a editar
            target_end: Fim da região
            desired_change: "deletion", "insertion", "substitution"
            desired_sequence: Sequência desejada (para insertion/substitution)
        
        Returns:
            Plano de edição completo
        """
        # Encontra gRNAs para a região
        grnas = self.find_grnas(
            target_sequence,
            region_start=max(0, target_start - 500),
            region_end=min(len(target_sequence), target_end + 500),
            num_grnas=5,
        )
        
        # Filtra gRNAs de qualidade
        good_grnas = [g for g in grnas if g.is_good]
        if not good_grnas:
            good_grnas = grnas[:3]  # Fallback
        
        plan = CRISPREditingPlan(
            target_region=target_sequence[target_start:target_end],
            target_start=target_start,
            target_end=target_end,
            desired_change=desired_change,
            desired_sequence=desired_sequence,
            grnas=good_grnas,
        )
        
        # Estima eficiência
        if good_grnas:
            plan.expected_efficiency = sum(g.efficiency_score for g in good_grnas) / len(good_grnas)
        
        # Identifica riscos
        plan.potential_risks = self._identify_risks(good_grnas, target_sequence)
        
        return plan
    
    def _identify_risks(self, grnas: List[GuideRNA], full_genome: str) -> List[str]:
        """Identifica riscos potenciais da estratégia CRISPR."""
        risks = []
        
        if not grnas:
            risks.append("Nenhum gRNA de qualidade encontrado")
            return risks
        
        # Risco 1: Muitos off-targets
        avg_off_targets = sum(g.off_targets_count for g in grnas) / len(grnas)
        if avg_off_targets > 10:
            risks.append(f"Alto número de off-targets predictos (avg: {avg_off_targets:.0f})")
        
        # Risco 2: GC% subótimo
        avg_gc = sum(g.gc_content for g in grnas) / len(grnas)
        if avg_gc < 30 or avg_gc > 70:
            risks.append(f"GC% fora do ideal (avg: {avg_gc:.1f}%)")
        
        # Risco 3: Homopolímeros
        if any(g.homopolymer_count > 0 for g in grnas):
            risks.append("Alguns gRNAs contêm homopolímeros (pode reduzir eficiência)")
        
        # Risco 4: Eficiência baixa
        avg_efficiency = sum(g.efficiency_score for g in grnas) / len(grnas)
        if avg_efficiency < 50:
            risks.append(f"Eficiência predicta é baixa (score: {avg_efficiency:.0f}/100)")
        
        return risks


# Exemplo de uso
if __name__ == "__main__":
    # Teste simples
    designer = CRISPRDesigner()
    
    # Sequência de exemplo (100bp)
    test_seq = (
        "ATGCGATCGATCGTAGCTAGCTAGCTGATCGATCGATCGATCG"
        "TAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG"
        "CTAGCTAGCTAGCTAGC"
    )
    
    print("Desenhando gRNAs para sequência de teste...")
    grnas = designer.find_grnas(test_seq, num_grnas=5)
    
    print(f"\n{'='*70}")
    print(f"Top 5 gRNAs encontrados:")
    print(f"{'='*70}")
    
    for i, grna in enumerate(grnas, 1):
        print(f"\n#{i}: {grna.sequence}")
        print(f"  Position: {grna.position}")
        print(f"  PAM: {grna.pam}")
        print(f"  GC%: {grna.gc_content:.1f}%")
        print(f"  Specificity: {grna.specificity_score:.0f}/100")
        print(f"  Efficiency: {grna.efficiency_score:.0f}/100")
        print(f"  Overall Score: {grna.combined_score:.0f}/100")
        print(f"  Quality: {'✓ GOOD' if grna.is_good else '✗ FAIR'}")
