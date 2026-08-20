"""Pipeline unificado de ressurreição de dinossauros (Re-Gen).

Este pacote expõe um único pipeline coerente, `unified`, que substitui as
antigas pipelines paralelas e desconectadas (main.py / main_v3.py). Todas
as fases -- da seleção paleontológica ao relatório final -- são executadas
através de `ReGenPipelineUnificado`, que por sua vez usa apenas módulos
reais do pacote `re_gen` (sem dados sintéticos ou placeholders).
"""

from re_gen.pipeline.unified import (
    ReGenPipelineUnificado,
    ConfiguracaoPipeline,
    ResultadoPipelineCompleto,
    PipelineStatus,
    FaseResultado,
    main,
)

__all__ = [
    "ReGenPipelineUnificado",
    "ConfiguracaoPipeline",
    "ResultadoPipelineCompleto",
    "PipelineStatus",
    "FaseResultado",
    "main",
]
