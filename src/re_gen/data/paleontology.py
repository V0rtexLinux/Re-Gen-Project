"""
paleontology.py
---------------
Base de dados paleontológica de dinossauros e suas características filogenéticas.

Dados consolidados de pesquisas recentes em paleontologia:
- Relações filogenéticas entre táxons de dinossauros
- Características osteológicas/genômicas compartilhadas
- Descendentes vivos (aves = dinossauros avianos; crocodilianos = parentes vivos mais próximos)
- Períodos geológicos e distribuição geográfica

Referências:
- Sereno, P. C., et al. Phylogeny of Dinosauria. University of Chicago Press.
- Barsbold, R., & Osmólska, H. (1999). The skull of Velociraptor and the evolution
  of theropod cranial mechanisms. Palaeontologia Polonica, 55, 103-126.
- Benton, M. J. (2015). Vertebrate Palaeontology: Biology and Evolution (4th ed.).
  Blackwell Publishing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DinosauroGrupo(Enum):
    """Classificação filogenética dos dinossauros."""

    THEROPODA = "Theropoda"  # Bípedes carnívoros (T-rex, velociraptores, aves)
    SAUROPODOMORPHA = "Sauropodomorpha"  # Saurópodes, herbívoros gigantes
    ORNITHISCHIA = "Ornithischia"  # Ornitísquios, herbívoros diversos


class Period(Enum):
    """Períodos geológicos."""

    TRIASSICO = "Triássico (252-201 Ma)"
    JURASSICO = "Jurássico (201-145 Ma)"
    CRETACEO = "Cretáceo (145-66 Ma)"


@dataclass
class CaracteristicaGenomica:
    """Uma característica genômica/osteológica compartilhada entre táxons."""

    nome: str
    descricao: str
    presente_em: list[str]  # lista de nomes de espécies que possuem essa característica


@dataclass
class Dinossauro:
    """Representa uma espécie de dinossauro com suas características paleontológicas."""

    nome_cientifico: str
    nome_comum: str
    grupo: DinosauroGrupo
    periodo: Period
    peso_estimado_kg: float | None  # None = desconhecido
    comprimento_estimado_m: float | None
    altura_estimada_m: float | None
    dieta: str  # "carnívoro", "herbívoro", "onívoro"
    localizacao_geografica: list[str]  # ex: ["América do Norte", "Ásia"]
    descricao_paleontologica: str
    caracteristicas_notaveis: list[str]
    genes_conservados: list[str]  # Genes que ainda existem em descendentes vivos
    taxa_diferencacao_estimada: float  # Diferença genômica estimada vs descendentes vivos (0-100%)
    ancestrais_proximos: list[str]  # Nomes de possíveis ancestrais no painel de referência
    descendentes_vivos: list[str]  # Nomes científicos de aves/crocodilianos relacionados


@dataclass
class SistemaReferencia:
    """
    Base de dados de dinossauros conhecidos e seus descendentes vivos.
    Usada para seleção automática quando não há hardware específico.
    """

    dinossauros: dict[str, Dinossauro] = field(default_factory=dict)
    grupos_por_tipo: dict[DinosauroGrupo, list[str]] = field(default_factory=dict)

    def registrar(self, dino: Dinossauro) -> None:
        """Registra um dinossauro na base de dados."""
        self.dinossauros[dino.nome_cientifico] = dino
        if dino.grupo not in self.grupos_por_tipo:
            self.grupos_por_tipo[dino.grupo] = []
        self.grupos_por_tipo[dino.grupo].append(dino.nome_cientifico)

    def buscar_por_nome(self, nome: str) -> Dinossauro | None:
        """Busca um dinossauro pelo nome científico."""
        return self.dinossauros.get(nome)

    def listar_por_grupo(self, grupo: DinosauroGrupo) -> list[Dinossauro]:
        """Lista todos os dinossauros de um grupo específico."""
        nomes = self.grupos_por_tipo.get(grupo, [])
        return [self.dinossauros[n] for n in nomes if n in self.dinossauros]

    def listar_por_periodo(self, periodo: Period) -> list[Dinossauro]:
        """Lista todos os dinossauros de um período específico."""
        return [d for d in self.dinossauros.values() if d.periodo == periodo]


def criar_sistema_referencia_padrao() -> SistemaReferencia:
    """
    Cria e popula a base de dados paleontológica padrão com espécies bem
    documentadas e seus descendentes vivos.
    """
    sr = SistemaReferencia()

    # ==================== THEROPODA ====================

    # Tyrannosaurus rex - o mais icônico
    t_rex = Dinossauro(
        nome_cientifico="Tyrannosaurus rex",
        nome_comum="T-Rex",
        grupo=DinosauroGrupo.THEROPODA,
        periodo=Period.CRETACEO,
        peso_estimado_kg=9000,
        comprimento_estimado_m=12.3,
        altura_estimada_m=4.0,
        dieta="carnívoro",
        localizacao_geografica=["América do Norte (USA, Canadá)"],
        descricao_paleontologica=(
            "Tiranosaurídeo de topo da cadeia alimentar do Cretáceo Superior. "
            "Ossos e marcas de musculatura preservados indicam predador ativo de grande porte. "
            "Ancestral filogenético próximo às aves modernas através de maniraptoráuros."
        ),
        caracteristicas_notaveis=[
            "Mandíbula extremamente robusta",
            "Visão binocular (órbitas frontais)",
            "Estruturas ósseas de crista/carúncula na cabeça",
            "Garras reduzidas nos membros anteriores (precursor de asas)",
        ],
        genes_conservados=[
            "FOXP2",  # linguagem/vocalização
            "PAX6",  # desenvolvimento ocular
            "HOX",  # desenvolvimento corporal
        ],
        taxa_diferencacao_estimada=66.0,  # 66 milhões de anos
        ancestrais_proximos=["Allosaurus", "Proceratosaurus"],
        descendentes_vivos=[
            "Gallus gallus",  # galinha-selvagem
            "Struthio camelus",  # avestruz
            "Crocodylus niloticus",  # jacaré-do-nilo
        ],
    )
    sr.registrar(t_rex)

    # Velociraptor - célebre maniraptor
    velociraptor = Dinossauro(
        nome_cientifico="Velociraptor mongoliensis",
        nome_comum="Velociraptor",
        grupo=DinosauroGrupo.THEROPODA,
        periodo=Period.CRETACEO,
        peso_estimado_kg=10,  # Bem menor que T-rex
        comprimento_estimado_m=1.8,
        altura_estimada_m=0.5,
        dieta="carnívoro",
        localizacao_geografica=["Ásia (Mongólia)"],
        descricao_paleontologica=(
            "Maniraptor pequeno do Cretáceo Inferior. Ossos ocos e estruturas "
            "de penas preservadas indicam voo ativo ou planador. Garras "
            "sicle-forma em membros posteriores sugerem predação especializada."
        ),
        caracteristicas_notaveis=[
            "Ossos ocos (reduções de densidade similares a aves)",
            "Penas preservadas em fósseis",
            "Garra em forma de sicle em pé posterior",
            "Cauda ossuda com estruturas de sustentação",
        ],
        genes_conservados=[
            "HOXA",  # estrutura de membros (precursor de asa)
            "HAND2",  # desenvolvimento digital
            "PAX6",  # visão
        ],
        taxa_diferencacao_estimada=75.0,
        ancestrais_proximos=["Deinonychus", "Microraptor"],
        descendentes_vivos=[
            "Accipiter nisus",  # gavião-pequeno
            "Falco peregrinus",  # falcão-peregrino
            "Crocodylus niloticus",
        ],
    )
    sr.registrar(velociraptor)

    # Archaeopteryx - ancestral direto das aves
    archaeopteryx = Dinossauro(
        nome_cientifico="Archaeopteryx lithographica",
        nome_comum="Archaeopteryx",
        grupo=DinosauroGrupo.THEROPODA,
        periodo=Period.JURASSICO,
        peso_estimado_kg=1,
        comprimento_estimado_m=0.5,
        altura_estimada_m=0.2,
        dieta="carnívoro",
        localizacao_geografica=["Europa (Alemanha)"],
        descricao_paleontologica=(
            "Fóssil transitório entre dinossauros não-avianos e aves modernas. "
            "Preserva penas primárias e asas, mas ainda retém cauda óssea de dinossauro. "
            "Voo possivelmente planador ou explosivo em curtas distâncias."
        ),
        caracteristicas_notaveis=[
            "Penas primárias bem preservadas",
            "Asas com estrutura de pena simétrica",
            "Cauda óssea ainda presente",
            "Garras em membros anteriores",
        ],
        genes_conservados=[
            "HOXA",
            "HOXC",  # estruturas de asa
            "LMBR1",  # desenvolvimento de dígitos
            "BMP",  # sinalização embrionária
        ],
        taxa_diferencacao_estimada=150.0,
        ancestrais_proximos=["Microraptor", "Deinonychus"],
        descendentes_vivos=["Aves modernas (toda a classe Aves)"],
    )
    sr.registrar(archaeopteryx)

    # Triceratops - de Ceratopsia, grupo de ornitísquios herbívoros
    triceratops = Dinossauro(
        nome_cientifico="Triceratops horridus",
        nome_comum="Triceratops",
        grupo=DinosauroGrupo.ORNITHISCHIA,
        periodo=Period.CRETACEO,
        peso_estimado_kg=6000,
        comprimento_estimado_m=9.0,
        altura_estimada_m=3.0,
        dieta="herbívoro",
        localizacao_geografica=["América do Norte (USA, Canadá)"],
        descricao_paleontologica=(
            "Ceratopsiano do Cretáceo Superior com crânio massivo e três chifres. "
            "Fossas lacrimais e estrutura mandibular sugerem herbivoria especializada. "
            "Osso em rede (nasal/frontal) indica possível sinalização visual ou termorregulação."
        ),
        caracteristicas_notaveis=[
            "Três chifres distintos",
            "Gola óssea de proteção cervical",
            "Bico de papagaio para herbivoria",
            "Estrutura craniana robusta",
        ],
        genes_conservados=[
            "HOX",
            "BMP",  # desenvolvimento de crânio
            "PTCH1",  # sinalização hedgehog
        ],
        taxa_diferencacao_estimada=66.0,
        ancestrais_proximos=["Protoceratops", "Pentaceratops"],
        descendentes_vivos=[
            "Crocodylus niloticus",  # crocodilianos são o parente mais vivo próximo de todos os dinossauros
        ],
    )
    sr.registrar(triceratops)

    # ==================== SAUROPODOMORPHA ====================

    # Brachiosaurus - saurópode gigante
    brachiosaurus = Dinossauro(
        nome_cientifico="Brachiosaurus altithorax",
        nome_comum="Brachiosaurus",
        grupo=DinosauroGrupo.SAUROPODOMORPHA,
        periodo=Period.JURASSICO,
        peso_estimado_kg=60000,
        comprimento_estimado_m=25.0,
        altura_estimada_m=13.0,
        dieta="herbívoro",
        localizacao_geografica=["América do Norte (USA)"],
        descricao_paleontologica=(
            "Saurópode gigante com pescoço alongado e membros anteriores mais altos. "
            "Ossos pneumáticos (ocos) e estrutura vertebral especializada sugerem "
            "redução de peso apesar do tamanho extremo. Estratégia de alimentação em altura."
        ),
        caracteristicas_notaveis=[
            "Pescoço extremamente alongado",
            "Ossos pneumáticos (câmaras de ar)",
            "Membros anteriores mais altos que posteriores",
            "Dentes pequenos para colher folhas",
        ],
        genes_conservados=[
            "HOX",  # alongamento vertebral
            "GREM1",  # desenvolvimento de membros
        ],
        taxa_diferencacao_estimada=145.0,
        ancestrais_proximos=["Diplodocus", "Mamenchisaurus"],
        descendentes_vivos=[
            "Crocodylus niloticus",  # crocodilianos
        ],
    )
    sr.registrar(brachiosaurus)

    return sr


# Instância global do sistema de referência
_SISTEMA_PADRAO = None


def obter_sistema_referencia() -> SistemaReferencia:
    """Retorna a instância singleton do sistema de referência paleontológica."""
    global _SISTEMA_PADRAO
    if _SISTEMA_PADRAO is None:
        _SISTEMA_PADRAO = criar_sistema_referencia_padrao()
    return _SISTEMA_PADRAO


def listar_dinossauros_recomendados() -> list[Dinossauro]:
    """
    Retorna lista de dinossauros recomendados para reconstrução,
    ordenados por:
    1. Disponibilidade de dados genômicos (genes conservados)
    2. Tamanho (preferência por espécies grandes = mais DNA preservável)
    3. Dados fósseis bem documentados
    """
    sr = obter_sistema_referencia()
    recomendados = sorted(
        sr.dinossauros.values(),
        key=lambda d: (
            -len(d.genes_conservados),  # mais genes conservados = melhor
            -(d.peso_estimado_kg or 0),  # tamanho maior = mais DNA
            d.taxa_diferencacao_estimada,  # menor diferença = genoma mais preservado
        ),
    )
    return recomendados
