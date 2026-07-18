"""
dinosaur_selector.py
--------------------
Seleção automática de qual dinossauro reconstruir baseado em:
1. Hardware disponível (se fornecido)
2. Características paleontológicas (genes conservados, tamanho)
3. Dados genômicos bem documentados

O sistema escolhe o dinossauro mais viável dado o contexto, sem
precisação do usuário fornecer qual quer reconstruir.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from re_gen.data.paleontology import (
    DinosauroGrupo,
    Dinossauro,
    SistemaReferencia,
    obter_sistema_referencia,
)


class CapacidadeHardware(Enum):
    """Classificação de capacidade computacional disponível."""

    NENHUMA = "nenhuma"  # Sem hardware de sequenciamento
    BASICA = "basica"  # Miniaturizado (ex: Oxford Nanopore MinION)
    INTERMEDIARIA = "intermediaria"  # Illumina MiSeq
    AVANCADA = "avancada"  # Illumina NextSeq/HiSeq, PacBio


@dataclass
class ConfiguracaoSelecao:
    """Configurações para seleção automática de dinossauro."""

    hardware: CapacidadeHardware = CapacidadeHardware.NENHUMA
    preferencia_tipo_dieta: str | None = None  # "carnívoro", "herbívoro"
    preferencia_tamanho_min_kg: float | None = None  # Tamanho mínimo preferido
    preferencia_tamanho_max_kg: float | None = None  # Tamanho máximo preferido
    preferencia_periodo: str | None = None  # "Triássico", "Jurássico", "Cretáceo"
    preferencia_grupo: DinosauroGrupo | None = None


class SeletorDinossauro:
    """
    Motor de seleção automática: dado(s) um contexto de hardware e preferências,
    recomenda qual dinossauro reconstruir.
    """

    def __init__(self, sistema_ref: SistemaReferencia | None = None):
        self.sistema_ref = sistema_ref or obter_sistema_referencia()

    def _score_compatibilidade_hardware(
        self,
        dino: Dinossauro,
        hardware: CapacidadeHardware,
    ) -> float:
        """
        Score de compatibilidade entre características do dinossauro e
        hardware disponível. Hardware limitado precisa de espécies com
        genoma mais conservado (menos diferenciado do presente).

        Retorna: 0.0 (incompatível) a 1.0 (ótima compatibilidade)
        """
        # Taxa de diferenciação: quanto menor, melhor para hardware limitado
        # (menos mudanças genômicas = menos ambiguidade na reconstrução)
        taxa_norm = 1.0 - (dino.taxa_diferencacao_estimada / 200.0)  # normaliza em ~200 Ma
        taxa_norm = max(0.0, min(1.0, taxa_norm))

        # Hardware sem sequenciador: prefere genomas bem conservados
        if hardware == CapacidadeHardware.NENHUMA:
            # Genomas mais preservados = reconstrução mais confiável sem dados reais
            return taxa_norm * 0.8 + (len(dino.genes_conservados) / 20.0) * 0.2

        # Hardware básico (Nanopore): precisa de reads longos, genes bem mapeados
        elif hardware == CapacidadeHardware.BASICA:
            # Favorece espécies com muitos genes bem caracterizados em descendentes
            return taxa_norm * 0.5 + (len(dino.genes_conservados) / 20.0) * 0.5

        # Hardware intermediário (Illumina): oferece cobertura alta, reads curtas
        # Pode reconstruir genomas maiores
        elif hardware == CapacidadeHardware.INTERMEDIARIA:
            return taxa_norm * 0.4 + (len(dino.genes_conservados) / 20.0) * 0.6

        # Hardware avançado: qualquer espécie é viável
        else:  # AVANCADA
            return taxa_norm * 0.3 + (len(dino.genes_conservados) / 20.0) * 0.7

    def _score_preferencias(
        self,
        dino: Dinossauro,
        config: ConfiguracaoSelecao,
    ) -> float:
        """
        Score de aderência às preferências do usuário.

        Retorna: 0.0 (não atende) a 1.0 (atende perfeitamente)
        """
        score = 1.0

        # Dieta
        if config.preferencia_tipo_dieta is not None:
            if dino.dieta.lower() == config.preferencia_tipo_dieta.lower():
                score *= 1.2  # bônus
            else:
                score *= 0.5  # penalidade

        # Tamanho
        if dino.peso_estimado_kg is not None:
            if config.preferencia_tamanho_min_kg is not None:
                if dino.peso_estimado_kg >= config.preferencia_tamanho_min_kg:
                    score *= 1.0
                else:
                    score *= 0.3
            if config.preferencia_tamanho_max_kg is not None:
                if dino.peso_estimado_kg <= config.preferencia_tamanho_max_kg:
                    score *= 1.0
                else:
                    score *= 0.3

        # Período
        if config.preferencia_periodo is not None:
            if config.preferencia_periodo in dino.periodo.value:
                score *= 1.1
            else:
                score *= 0.7

        # Grupo filogenético
        if config.preferencia_grupo is not None:
            if dino.grupo == config.preferencia_grupo:
                score *= 1.3
            else:
                score *= 0.6

        return score

    def selecionar(self, config: ConfiguracaoSelecao) -> tuple[Dinossauro, float]:
        """
        Seleciona o melhor dinossauro para reconstrução.

        Retorna: (dinossauro_selecionado, score_confianca)
        """
        if not self.sistema_ref.dinossauros:
            raise ValueError("Sistema de referência vazio: nenhum dinossauro disponível.")

        scores: dict[str, float] = {}

        for nome, dino in self.sistema_ref.dinossauros.items():
            score_hw = self._score_compatibilidade_hardware(dino, config.hardware)
            score_pref = self._score_preferencias(dino, config)
            score_final = score_hw * score_pref

            # Bônus por tamanho (dinossauros maiores deixam mais restos)
            if dino.peso_estimado_kg is not None:
                score_final *= 1.0 + 0.1 * (dino.peso_estimado_kg / 70000.0)

            scores[nome] = score_final

        melhor_nome = max(scores, key=scores.get)
        melhor_dino = self.sistema_ref.dinossauros[melhor_nome]
        confianca = scores[melhor_nome]

        return melhor_dino, confianca

    def recomendar_multiplos(
        self,
        config: ConfiguracaoSelecao,
        n: int = 3,
    ) -> list[tuple[Dinossauro, float]]:
        """
        Retorna os N melhores dinossauros para reconstrução, ordenados por score.

        Retorna: Lista de (dinossauro, score_confianca)
        """
        scores: dict[str, float] = {}

        for nome, dino in self.sistema_ref.dinossauros.items():
            score_hw = self._score_compatibilidade_hardware(dino, config.hardware)
            score_pref = self._score_preferencias(dino, config)
            score_final = score_hw * score_pref

            if dino.peso_estimado_kg is not None:
                score_final *= 1.0 + 0.1 * (dino.peso_estimado_kg / 70000.0)

            scores[nome] = score_final

        top_n = sorted(
            ((self.sistema_ref.dinossauros[nome], score) for nome, score in scores.items()),
            key=lambda x: x[1],
            reverse=True,
        )[:n]

        return top_n


def selecionador_adaptativo(hardware: CapacidadeHardware) -> SeletorDinossauro:
    """
    Factory: cria um seletor com recomendações pré-ajustadas para cada
    nível de hardware.
    """
    return SeletorDinossauro()


# Descrições em linguagem natural para cada recomendação
DESCRICOES_SELECAO = {
    "Tyrannosaurus rex": (
        "T-Rex: O predador de topo do Cretáceo Superior. Genoma bem conservado "
        "em aves modernas (gavião, falcão). Ótimo para validação: é o dinossauro "
        "mais estudado de todos."
    ),
    "Velociraptor mongoliensis": (
        "Velociraptor: Maniraptor pequeno com ossos ocos (similar a aves modernas). "
        "Genes de desenvolvimento de asa parcialmente preservados. Excelente para "
        "estudos de transição para voo."
    ),
    "Archaeopteryx lithographica": (
        "Archaeopteryx: Transição viva entre dinossauros e aves. Fóssil com penas "
        "preservadas. Permite validação direta contra aves modernas."
    ),
    "Triceratops horridus": (
        "Triceratops: Ceratopsiano herbívoro com crânio especializado. Descendentes "
        "vivos (crocodilianos) bem documentados. Ótimo para estudos de diversidade."
    ),
    "Brachiosaurus altithorax": (
        "Brachiosaurus: Saurópode gigante do Jurássico. Ossos pneumáticos (similar "
        "a aves modernas). Desafia modelos de genômica de grandes organismos."
    ),
}
