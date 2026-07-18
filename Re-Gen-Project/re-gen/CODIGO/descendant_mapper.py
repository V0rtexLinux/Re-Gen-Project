"""
descendant_mapper.py
--------------------
Mapeamento de descendentes vivos (aves atuais e crocodilianos) para
características ancestrais de dinossauros.

Converte dados filogenéticos em referências práticas para busca NCBI:
dada uma característica paleontológica (ex: "ossos ocos", "penas"),
encontra aves/crocodilianos modernos que a preservam e sugere qual
usar como referência genômica.

Referências:
- Chiappe, L. M. (2007). Glorified Dinosaurs: The Origin and Early Evolution of Birds.
- Organ, C. L., et al. (2007). Origin of avian genome size and structure in non-avian dinosaurs.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class CaracteristicaAncestral(Enum):
    """Características paleontológicas preservadas em descendentes."""
    OSSOS_OCOS = "ossos_ocos"  # Ossos pneumáticos
    PENAS = "penas"  # Estrutura de penas
    GARRA_SICLE = "garra_sicle"  # Garras especializadas
    VISAO_BINOCULAR = "visao_binocular"  # Órbitas frontais
    ESTRUTURA_MANDIBULAR = "estrutura_mandibular"  # Bico/mandíbula
    ESCAMA_AVANCADA = "escama_avancada"  # Escamas modificadas
    DIMORFISMO_SEXUAL = "dimorfismo_sexual"  # Diferenças sexuais marcadas


@dataclass
class EspecieDescendente:
    """Uma espécie viva que preserva características ancestrais de dinossauro."""
    nome_cientifico: str
    nome_comum: str
    grupo_taxa: str  # "Aves", "Crocodilia", etc.
    
    # Mapeamento: qual característica ancestral ela preserva
    caracteristicas_preservadas: list[CaracteristicaAncestral]
    
    # Gene ortólogos: genes que essa espécie compartilha com o dinossauro ancestral
    genes_ortologos: list[str]
    
    # Genes-chave para essa característica
    genes_notaveis: dict[CaracteristicaAncestral, list[str]]
    
    # Qual dinossauro essa espécie é descendente?
    ancestral_direto: str  # ex: "Tyrannosaurus rex" ou "Archaeopteryx"
    
    # Distância evolutiva (anos desde divergência)
    anos_divergencia_estimados: float
    
    # Score de utilidade para reconstrução genômica (0-100)
    score_utilidade_genomica: float
    
    # Qualidade de anotação no NCBI (0-100)
    qualidade_anotacao_ncbi: float


@dataclass
class MapeadorDescendentes:
    """
    Mapeamento centralizado: dado um dinossauro e características,
    encontra os melhores descendentes vivos para referência genômica.
    """
    descendentes: dict[str, EspecieDescendente] = field(default_factory=dict)
    
    # Índice reverso: característica -> espécies que a preservam
    _indice_caracteristicas: dict[CaracteristicaAncestral, list[str]] = field(
        default_factory=dict
    )
    
    # Índice: dinossauro ancestral -> espécies descendentes
    _indice_ancestrais: dict[str, list[str]] = field(default_factory=dict)

    def registrar(self, especie: EspecieDescendente) -> None:
        """Registra uma espécie descendente no mapeador."""
        self.descendentes[especie.nome_cientifico] = especie
        
        # Atualiza índices
        for carac in especie.caracteristicas_preservadas:
            if carac not in self._indice_caracteristicas:
                self._indice_caracteristicas[carac] = []
            self._indice_caracteristicas[carac].append(especie.nome_cientifico)
        
        anc = especie.ancestral_direto
        if anc not in self._indice_ancestrais:
            self._indice_ancestrais[anc] = []
        self._indice_ancestrais[anc].append(especie.nome_cientifico)

    def buscar_por_ancestral(self, nome_dinossauro: str) -> list[EspecieDescendente]:
        """
        Retorna todas as espécies vivas descendentes de um dinossauro.
        Ordenado por score de utilidade genômica.
        """
        nomes = self._indice_ancestrais.get(nome_dinossauro, [])
        especies = [self.descendentes[n] for n in nomes if n in self.descendentes]
        return sorted(especies, key=lambda e: e.score_utilidade_genomica, reverse=True)

    def buscar_por_caracteristica(
        self,
        carac: CaracteristicaAncestral,
    ) -> list[EspecieDescendente]:
        """
        Retorna espécies que preservam uma característica ancestral específica.
        Ordenado por anotação NCBI (melhor qualidade = mais genes sequenciados).
        """
        nomes = self._indice_caracteristicas.get(carac, [])
        especies = [self.descendentes[n] for n in nomes if n in self.descendentes]
        return sorted(especies, key=lambda e: e.qualidade_anotacao_ncbi, reverse=True)

    def encontrar_melhor_referencia(
        self,
        nome_dinossauro: str,
        caracteristica_necessaria: Optional[CaracteristicaAncestral] = None,
    ) -> Optional[EspecieDescendente]:
        """
        Encontra a espécie descendente mais útil para reconstrução genômica.
        
        Se `caracteristica_necessaria` for especificada, filtra apenas
        espécies que a preservam.
        """
        candidatos = self.buscar_por_ancestral(nome_dinossauro)
        
        if caracteristica_necessaria is not None:
            candidatos = [
                e for e in candidatos
                if caracteristica_necessaria in e.caracteristicas_preservadas
            ]
        
        if not candidatos:
            return None
        
        # Seleciona: maior score genômico + melhor anotação NCBI
        return max(
            candidatos,
            key=lambda e: (e.score_utilidade_genomica + e.qualidade_anotacao_ncbi) / 2.0,
        )

    def listar_todos_recomendados(self) -> list[EspecieDescendente]:
        """
        Lista todas as espécies ordenadas por utilidade genômica total.
        """
        return sorted(
            self.descendentes.values(),
            key=lambda e: (e.score_utilidade_genomica + e.qualidade_anotacao_ncbi) / 2.0,
            reverse=True,
        )


def criar_mapeador_padrao() -> MapeadorDescendentes:
    """
    Cria e popula o mapeador padrão com espécies descendentes bem documentadas.
    Dados baseados em sequências de genoma publicadas no NCBI.
    """
    mapeador = MapeadorDescendentes()

    # ==================== AVES MODERNAS ====================

    # Galinha-selvagem (Gallus gallus) - genoma de referência bem anotado
    gallus = EspecieDescendente(
        nome_cientifico="Gallus gallus",
        nome_comum="Galinha-selvagem",
        grupo_taxa="Aves",
        caracteristicas_preservadas=[
            CaracteristicaAncestral.OSSOS_OCOS,
            CaracteristicaAncestral.PENAS,
            CaracteristicaAncestral.ESTRUTURA_MANDIBULAR,
            CaracteristicaAncestral.VISAO_BINOCULAR,
        ],
        genes_ortologos=[
            "FOXP2",
            "PAX6",
            "HOXA", "HOXC",
            "BMP4", "BMP2",
            "LMBR1",
            "HAND2",
        ],
        genes_notaveis={
            CaracteristicaAncestral.OSSOS_OCOS: ["FGFR3", "PTCH1"],
            CaracteristicaAncestral.PENAS: ["LMBR1", "SOX6"],
            CaracteristicaAncestral.ESTRUTURA_MANDIBULAR: ["PAX9", "BARX1"],
        },
        ancestral_direto="Tyrannosaurus rex",
        anos_divergencia_estimados=66e6,  # 66 milhões de anos
        score_utilidade_genomica=95.0,
        qualidade_anotacao_ncbi=98.0,
    )
    mapeador.registrar(gallus)

    # Avestruz (Struthio camelus) - genoma grande, estrutura primitiva
    struthio = EspecieDescendente(
        nome_cientifico="Struthio camelus",
        nome_comum="Avestruz",
        grupo_taxa="Aves",
        caracteristicas_preservadas=[
            CaracteristicaAncestral.OSSOS_OCOS,
            CaracteristicaAncestral.PENAS,
            CaracteristicaAncestral.ESTRUTURA_MANDIBULAR,
            CaracteristicaAncestral.DIMORFISMO_SEXUAL,
        ],
        genes_ortologos=[
            "FOXP2", "PAX6", "HOXA", "HOXC",
            "BMP2", "BMP4", "FGFR3",
        ],
        genes_notaveis={
            CaracteristicaAncestral.OSSOS_OCOS: ["FGFR3", "PTCH1", "GLI1"],
            CaracteristicaAncestral.PENAS: ["LMBR1", "SOX6", "HOXA"],
        },
        ancestral_direto="Tyrannosaurus rex",
        anos_divergencia_estimados=66e6,
        score_utilidade_genomica=88.0,
        qualidade_anotacao_ncbi=85.0,
    )
    mapeador.registrar(struthio)

    # Falcão-peregrino (Falco peregrinus) - visão binocular/aguda preservada
    falco = EspecieDescendente(
        nome_cientifico="Falco peregrinus",
        nome_comum="Falcão-peregrino",
        grupo_taxa="Aves",
        caracteristicas_preservadas=[
            CaracteristicaAncestral.OSSOS_OCOS,
            CaracteristicaAncestral.PENAS,
            CaracteristicaAncestral.VISAO_BINOCULAR,
            CaracteristicaAncestral.GARRA_SICLE,  # garras de caça
        ],
        genes_ortologos=[
            "FOXP2", "PAX6", "OPN1SW", "OPN1LW",  # genes de visão
            "HOXA", "HOXC", "HAND2",
        ],
        genes_notaveis={
            CaracteristicaAncestral.VISAO_BINOCULAR: ["PAX6", "OPN1SW", "OPN1LW", "RH1"],
            CaracteristicaAncestral.GARRA_SICLE: ["HAND2", "BMP2", "HOXA"],
        },
        ancestral_direto="Velociraptor mongoliensis",
        anos_divergencia_estimados=75e6,
        score_utilidade_genomica=82.0,
        qualidade_anotacao_ncbi=78.0,
    )
    mapeador.registrar(falco)

    # Gavião-pequeno (Accipiter nisus) - também predador com características similares
    accipiter = EspecieDescendente(
        nome_cientifico="Accipiter nisus",
        nome_comum="Gavião-pequeno",
        grupo_taxa="Aves",
        caracteristicas_preservadas=[
            CaracteristicaAncestral.OSSOS_OCOS,
            CaracteristicaAncestral.PENAS,
            CaracteristicaAncestral.VISAO_BINOCULAR,
            CaracteristicaAncestral.GARRA_SICLE,
        ],
        genes_ortologos=[
            "FOXP2", "PAX6", "OPN1SW", "OPN1LW",
            "HOXA", "HOXC", "HAND2",
        ],
        genes_notaveis={
            CaracteristicaAncestral.VISAO_BINOCULAR: ["PAX6", "OPN1SW", "OPN1LW"],
            CaracteristicaAncestral.GARRA_SICLE: ["HAND2", "BMP2"],
        },
        ancestral_direto="Velociraptor mongoliensis",
        anos_divergencia_estimados=75e6,
        score_utilidade_genomica=78.0,
        qualidade_anotacao_ncbi=72.0,
    )
    mapeador.registrar(accipiter)

    # ==================== CROCODILIANOS ====================

    # Jacaré-do-nilo (Crocodylus niloticus) - genoma bem sequenciado, parente vivo de TODOS dinossauros
    crocodylus = EspecieDescendente(
        nome_cientifico="Crocodylus niloticus",
        nome_comum="Jacaré-do-nilo",
        grupo_taxa="Crocodilia",
        caracteristicas_preservadas=[
            CaracteristicaAncestral.ESTRUTURA_MANDIBULAR,
            CaracteristicaAncestral.ESCAMA_AVANCADA,
            CaracteristicaAncestral.VISAO_BINOCULAR,
            CaracteristicaAncestral.DIMORFISMO_SEXUAL,
        ],
        genes_ortologos=[
            "FOXP2", "PAX6", "HOX", "BMP",
            "GREM1",  # crescimento de membros (importante para saurópodes)
        ],
        genes_notaveis={
            CaracteristicaAncestral.ESTRUTURA_MANDIBULAR: ["JAG1", "NOTCH1", "DLX"],
            CaracteristicaAncestral.ESCAMA_AVANCADA: ["EDA", "EDAR"],
        },
        ancestral_direto="Triceratops horridus",  # Crocodilianos: parentes de todos os dinossauros
        anos_divergencia_estimados=250e6,  # ~250 Ma: ancestral comum com dinossauros
        score_utilidade_genomica=92.0,  # Genoma bem conservado
        qualidade_anotacao_ncbi=96.0,  # Genoma completamente sequenciado
    )
    mapeador.registrar(crocodylus)

    # Crocodilo-americano (Crocodylus acutus) - genoma também anotado
    croc_americano = EspecieDescendente(
        nome_cientifico="Crocodylus acutus",
        nome_comum="Crocodilo-americano",
        grupo_taxa="Crocodilia",
        caracteristicas_preservadas=[
            CaracteristicaAncestral.ESTRUTURA_MANDIBULAR,
            CaracteristicaAncestral.ESCAMA_AVANCADA,
            CaracteristicaAncestral.VISAO_BINOCULAR,
        ],
        genes_ortologos=[
            "FOXP2", "PAX6", "HOX", "BMP",
            "GREM1",
        ],
        genes_notaveis={
            CaracteristicaAncestral.ESTRUTURA_MANDIBULAR: ["JAG1", "NOTCH1"],
            CaracteristicaAncestral.ESCAMA_AVANCADA: ["EDA", "EDAR", "BMP"],
        },
        ancestral_direto="Brachiosaurus altithorax",
        anos_divergencia_estimados=250e6,
        score_utilidade_genomica=85.0,
        qualidade_anotacao_ncbi=88.0,
    )
    mapeador.registrar(croc_americano)

    return mapeador


# Instância global
_MAPEADOR_PADRAO = None


def obter_mapeador() -> MapeadorDescendentes:
    """Retorna a instância singleton do mapeador de descendentes."""
    global _MAPEADOR_PADRAO
    if _MAPEADOR_PADRAO is None:
        _MAPEADOR_PADRAO = criar_mapeador_padrao()
    return _MAPEADOR_PADRAO
