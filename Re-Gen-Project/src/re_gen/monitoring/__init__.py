"""Monitoramento periódico de marcos tecnológicos reais para o Re-Gen.

Veja `tech_watch.py` para detalhes e limitações honestas do que este
monitor pode e não pode fazer. A decisão sobre se um artigo confirma um
marco usa dois algoritmos deterministicos clássicos (sem IA/modelo treinado):
  - resumo extrativo por frequência de palavras (Luhn, 1958)
  - detecção de negação por janela de contexto
"""

from re_gen.monitoring.tech_watch import (
    MARCOS,
    Evidencia,
    Marco,
    buscar_e_ler_artigos,
    executar_ciclo,
    resumir_por_frequencia_luhn,
    main,
)

__all__ = [
    "MARCOS",
    "Evidencia",
    "Marco",
    "buscar_e_ler_artigos",
    "executar_ciclo",
    "resumir_por_frequencia_luhn",
    "main",
]
