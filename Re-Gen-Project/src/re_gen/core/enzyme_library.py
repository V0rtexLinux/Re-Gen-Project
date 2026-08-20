"""
enzyme_library.py
-----------------
Biblioteca de enzimas para síntese genômica.

Inclui:
1. Enzimas de restrição (corte DNA em sítios específicos)
2. DNA ligases (une fragmentos DNA)
3. Polymerases (cópia DNA)
4. Helicases (desagrega DNA)
5. Topoisomerases (libera tensão)

Uso real: síntese de fragmentos grandes envolve múltiplas enzimas.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EnzymeClass(Enum):
    """Classe de enzima."""

    RESTRICTION = "restriction"  # Endonuclease de restrição
    LIGASE = "ligase"  # DNA ligase
    POLYMERASE = "polymerase"  # DNA polymerase
    HELICASE = "helicase"  # DNA helicase
    TOPOISOMERASE = "topoisomerase"  # Topoisomerase


@dataclass
class RestrictionSite:
    """Sítio de corte de enzima de restrição."""

    recognition_sequence: str  # Sequência de reconhecimento
    cut_position: int  # Onde corta (offset)
    sticky_overhang: tuple[int, int] | None = None  # (upstream, downstream) se sticky


@dataclass
class Enzyme:
    """Uma enzima para síntese genômica."""

    name: str  # Nome comercial (ex: "EcoRI")
    systematic_name: str  # Nome sistemático
    enzyme_class: EnzymeClass
    organism_source: str  # De qual organismo veio (ex: "E. coli")
    activity_unit: str  # Unidade de medida (ex: "U/µL")
    price_per_unit_usd: float  # Preço USD por unidade
    optimal_temperature_c: int  # Temperatura ótima
    optimal_ph: float  # pH ótimo
    buffer_composition: str  # Buffer recomendado
    description: str = ""

    # Para restriction enzymes
    recognition_site: RestrictionSite | None = None

    # Para ligases e polymerases
    processivity_bp: int | None = None  # Quantos bp consegue processar por ligação
    error_rate: float | None = None  # Taxa de erro (0.0-1.0)

    def __str__(self) -> str:
        return f"{self.name} ({self.enzyme_class.value})"


class EnzymeLibrary:
    """Banco de dados de enzimas disponíveis."""

    def __init__(self):
        self.enzymes: dict[str, Enzyme] = {}
        self._populate_default_enzymes()

    def _populate_default_enzymes(self) -> None:
        """Popula com enzimas comuns em síntese."""

        # ==================== RESTRICTION ENZYMES ====================

        # EcoRI - clássica, frequent em clonagem
        self.add_enzyme(
            Enzyme(
                name="EcoRI",
                systematic_name="EcoRI endonuclease",
                enzyme_class=EnzymeClass.RESTRICTION,
                organism_source="Escherichia coli RY13",
                activity_unit="U/µL",
                price_per_unit_usd=50,
                optimal_temperature_c=37,
                optimal_ph=7.5,
                buffer_composition="TE (Tris-EDTA) pH 7.5",
                description="Corta GAATTC produzindo extremidades pegajosas 5' AATT",
                recognition_site=RestrictionSite(
                    recognition_sequence="GAATTC",
                    cut_position=1,
                    sticky_overhang=(4, 2),  # Deixa 4bp upstream, 2bp downstream
                ),
            )
        )

        # BamHI
        self.add_enzyme(
            Enzyme(
                name="BamHI",
                systematic_name="BamHI endonuclease",
                enzyme_class=EnzymeClass.RESTRICTION,
                organism_source="Bacillus amyloliquefaciens H",
                activity_unit="U/µL",
                price_per_unit_usd=60,
                optimal_temperature_c=37,
                optimal_ph=7.5,
                buffer_composition="TE pH 7.5",
                description="Corta GGATCC produzindo extremidades pegajosas",
                recognition_site=RestrictionSite(
                    recognition_sequence="GGATCC",
                    cut_position=1,
                    sticky_overhang=(4, 2),
                ),
            )
        )

        # PstI - corta CTGCAG
        self.add_enzyme(
            Enzyme(
                name="PstI",
                systematic_name="PstI endonuclease",
                enzyme_class=EnzymeClass.RESTRICTION,
                organism_source="Providencia stuartii",
                activity_unit="U/µL",
                price_per_unit_usd=55,
                optimal_temperature_c=37,
                optimal_ph=7.5,
                buffer_composition="TE pH 7.5",
                recognition_site=RestrictionSite(
                    recognition_sequence="CTGCAG",
                    cut_position=3,
                    sticky_overhang=(3, 3),
                ),
            )
        )

        # HindIII
        self.add_enzyme(
            Enzyme(
                name="HindIII",
                systematic_name="HindIII endonuclease",
                enzyme_class=EnzymeClass.RESTRICTION,
                organism_source="Haemophilus influenzae Rd",
                activity_unit="U/µL",
                price_per_unit_usd=50,
                optimal_temperature_c=37,
                optimal_ph=7.5,
                buffer_composition="TE pH 7.5",
                recognition_site=RestrictionSite(
                    recognition_sequence="AAGCTT",
                    cut_position=1,
                    sticky_overhang=(4, 2),
                ),
            )
        )

        # ==================== LIGASES ====================

        # T4 DNA Ligase
        self.add_enzyme(
            Enzyme(
                name="T4 DNA Ligase",
                systematic_name="Bacteriophage T4 DNA ligase",
                enzyme_class=EnzymeClass.LIGASE,
                organism_source="Bacteriophage T4",
                activity_unit="Weiss units/µL",
                price_per_unit_usd=200,
                optimal_temperature_c=16,
                optimal_ph=7.5,
                buffer_composition="Ligase buffer (Tris, MgCl2, DTT, PEG)",
                description="Ligase de DNA de fita dupla; une fragmentos via ATP",
                processivity_bp=100000,
                error_rate=0.0001,
            )
        )

        # E. coli DNA Ligase
        self.add_enzyme(
            Enzyme(
                name="E. coli DNA Ligase",
                systematic_name="Escherichia coli DNA ligase",
                enzyme_class=EnzymeClass.LIGASE,
                organism_source="Escherichia coli",
                activity_unit="U/mL",
                price_per_unit_usd=150,
                optimal_temperature_c=20,
                optimal_ph=7.5,
                buffer_composition="Ligase buffer",
                description="Mais estável em temperatura ambiente que T4",
                processivity_bp=50000,
                error_rate=0.0002,
            )
        )

        # ==================== POLYMERASES ====================

        # Taq Polymerase
        self.add_enzyme(
            Enzyme(
                name="Taq Polymerase",
                systematic_name="Thermus aquaticus DNA polymerase",
                enzyme_class=EnzymeClass.POLYMERASE,
                organism_source="Thermus aquaticus",
                activity_unit="U/µL",
                price_per_unit_usd=100,
                optimal_temperature_c=72,
                optimal_ph=8.3,
                buffer_composition="PCR buffer (Tris, KCl, MgCl2)",
                description="Polymerase termotolerante; usa em PCR",
                processivity_bp=1000,
                error_rate=0.00001,
            )
        )

        # Pfu Polymerase (alta fidelidade)
        self.add_enzyme(
            Enzyme(
                name="Pfu Polymerase",
                systematic_name="Pyrococcus furiosus DNA polymerase",
                enzyme_class=EnzymeClass.POLYMERASE,
                organism_source="Pyrococcus furiosus",
                activity_unit="U/µL",
                price_per_unit_usd=250,
                optimal_temperature_c=74,
                optimal_ph=8.5,
                buffer_composition="Pfu buffer",
                description="Alta fidelidade (3-12 vezes melhor que Taq)",
                processivity_bp=1800,
                error_rate=0.000001,  # 10x melhor que Taq
            )
        )

        # Phusion Polymerase (ultra-alta fidelidade)
        self.add_enzyme(
            Enzyme(
                name="Phusion Polymerase",
                systematic_name="Thermus thermophilus DNA polymerase + binding protein",
                enzyme_class=EnzymeClass.POLYMERASE,
                organism_source="Thermus thermophilus / engineered",
                activity_unit="U/µL",
                price_per_unit_usd=300,
                optimal_temperature_c=72,
                optimal_ph=7.5,
                buffer_composition="Phusion HF buffer",
                description="Ultaalta fidelidade e velocidade (1kb/s)",
                processivity_bp=15000,
                error_rate=0.0000001,  # Melhor do mercado
            )
        )

        # ==================== HELICASES ====================

        # DnaB Helicase
        self.add_enzyme(
            Enzyme(
                name="DnaB Helicase",
                systematic_name="E. coli replication helicase",
                enzyme_class=EnzymeClass.HELICASE,
                organism_source="Escherichia coli",
                activity_unit="U/µL",
                price_per_unit_usd=350,
                optimal_temperature_c=37,
                optimal_ph=7.5,
                buffer_composition="Helicase buffer (Tris, NaCl, MgCl2, DTT)",
                description="Desagrega DNA de fita dupla; requer ATP",
            )
        )

        # ==================== TOPOISOMERASES ====================

        # Topoisomerase I
        self.add_enzyme(
            Enzyme(
                name="Topoisomerase I",
                systematic_name="Vacuolar topoisomerase I",
                enzyme_class=EnzymeClass.TOPOISOMERASE,
                organism_source="Vacc viral / engineered",
                activity_unit="U/µL",
                price_per_unit_usd=280,
                optimal_temperature_c=37,
                optimal_ph=7.5,
                buffer_composition="Top buffer (Tris, NaCl, MgCl2)",
                description="Remove tensão de DNA; essencial para síntese de grandes fragmentos",
            )
        )

    def add_enzyme(self, enzyme: Enzyme) -> None:
        """Adiciona uma enzima ao banco."""
        self.enzymes[enzyme.name] = enzyme

    def get_enzyme(self, name: str) -> Enzyme | None:
        """Obtém uma enzima pelo nome."""
        return self.enzymes.get(name)

    def get_restriction_enzymes(self) -> list[Enzyme]:
        """Retorna todas as enzimas de restrição."""
        return [e for e in self.enzymes.values() if e.enzyme_class == EnzymeClass.RESTRICTION]

    def get_ligases(self) -> list[Enzyme]:
        """Retorna todas as ligases."""
        return [e for e in self.enzymes.values() if e.enzyme_class == EnzymeClass.LIGASE]

    def get_polymerases(self) -> list[Enzyme]:
        """Retorna todas as polymerases."""
        return [e for e in self.enzymes.values() if e.enzyme_class == EnzymeClass.POLYMERASE]

    def find_restriction_enzyme_for_sequence(
        self,
        sequence: str,
    ) -> list[tuple[str, int]]:
        """
        Encontra enzimas de restrição que cortam em uma sequência.

        Returns:
            Lista de (nome_enzima, posição_corte)
        """
        results = []
        seq_upper = sequence.upper()

        for enzyme in self.get_restriction_enzymes():
            if enzyme.recognition_site:
                pattern = enzyme.recognition_site.recognition_sequence

                # Busca padrão (exato, ignorando 'N')
                import re

                pattern_regex = pattern.replace("N", "[ATCG]")

                for match in re.finditer(pattern_regex, seq_upper):
                    results.append((enzyme.name, match.start()))

        return results

    def get_synthesis_recipe(self, fragment_size_bp: int) -> dict:
        """
        Recomenda enzimas para síntese de um fragmento.

        Args:
            fragment_size_bp: Tamanho do fragmento

        Returns:
            Dicionário com receita recomendada
        """
        recipe = {
            "fragment_size_bp": fragment_size_bp,
            "recommended_enzymes": [],
            "total_cost_usd": 0.0,
        }

        # PCR: use polymerase de alta fidelidade
        polymerase = self.get_enzyme("Phusion Polymerase")
        if polymerase:
            recipe["recommended_enzymes"].append(
                {
                    "step": "PCR amplification",
                    "enzyme": polymerase.name,
                    "quantity": 1,  # units
                    "cost": polymerase.price_per_unit_usd * 1,
                }
            )
            recipe["total_cost_usd"] += polymerase.price_per_unit_usd

        # Digestão: restriction enzyme (se relevante)
        restriction = self.get_enzyme("EcoRI")
        if restriction:
            recipe["recommended_enzymes"].append(
                {
                    "step": "Digestion (optional)",
                    "enzyme": restriction.name,
                    "quantity": 2,  # 2 enzimas diferentes para clonar
                    "cost": restriction.price_per_unit_usd * 2,
                }
            )
            recipe["total_cost_usd"] += restriction.price_per_unit_usd * 2

        # Ligation
        ligase = self.get_enzyme("T4 DNA Ligase")
        if ligase:
            recipe["recommended_enzymes"].append(
                {
                    "step": "Ligation",
                    "enzyme": ligase.name,
                    "quantity": 1,
                    "cost": ligase.price_per_unit_usd,
                }
            )
            recipe["total_cost_usd"] += ligase.price_per_unit_usd

        return recipe


# Instância global
_LIBRARY = None


def get_enzyme_library() -> EnzymeLibrary:
    """Retorna a biblioteca singleton."""
    global _LIBRARY
    if _LIBRARY is None:
        _LIBRARY = EnzymeLibrary()
    return _LIBRARY


# Exemplo de uso
if __name__ == "__main__":
    lib = get_enzyme_library()

    print("ENZYME LIBRARY")
    print("=" * 60)

    print("\nRestriction Enzymes:")
    for enzyme in lib.get_restriction_enzymes():
        print(f"  {enzyme.name}: {enzyme.description}")

    print("\nLigases:")
    for enzyme in lib.get_ligases():
        print(f"  {enzyme.name}: {enzyme.optimal_temperature_c}°C")

    print("\nPolymerases:")
    for enzyme in lib.get_polymerases():
        print(f"  {enzyme.name}: error rate {enzyme.error_rate:.2e}")

    # Receita para síntese de 10kb
    recipe = lib.get_synthesis_recipe(10000)
    print("\n\nSynthesis Recipe (10kb fragment):")
    print(f"Total estimated cost: ${recipe['total_cost_usd']:.2f}")
