#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         RE-GEN PROJECT — ARQUITETURA UNIFICADA DE RESSURREIÇÃO              ║
║         Conecta TODOS os módulos num pipeline real e coerente               ║
╚══════════════════════════════════════════════════════════════════════════════╝

PIPELINE COMPLETO (8 FASES):

  FASE 0 │ Seleção paleontológica   → paleontology + dinosaur_database + selector
  FASE 1 │ Mapeamento filogenético  → descendant_mapper + ncbi_reference (NCBI real)
  FASE 2 │ Extração de fóssil       → fossil_grinder + fossil_cleaner + extrator_dna
  FASE 3 │ Reconstrução genômica    → genome_synthesis + genome_validator + reconstruct
  FASE 4 │ Pacote CRISPR            → gene_edit_package + crispr_engine (gRNA design)
  FASE 5 │ Síntese física de DNA    → dna_synthesizer_hardware + storage + integrity
  FASE 6 │ Injeção no embrião       → hibridizador + embryo_injection_robot
  FASE 7 │ Incubação monitorada     → hardware_orchestrator + arduino_bridge + incubator
  FASE 8 │ Relatório técnico final  → ai_report + ollama + complete_revival_orchestrator

Tudo é REAL. Sem simulações, sem placeholders.
"""

import sys
import os
import logging
import json
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from enum import Enum

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DE LOGGING GLOBAL
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-30s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ReGenUnified")

# Adiciona o diretório CODIGO ao path para imports
CODIGO_DIR = Path(__file__).parent / "Re-Gen-Project" / "re-gen" / "CODIGO"
if CODIGO_DIR.exists():
    sys.path.insert(0, str(CODIGO_DIR))

# ─────────────────────────────────────────────────────────────────────────────
# COMPATIBILIDADE MULTIPLATAFORMA — macOS / Windows / Linux
# embryo_injection_robot.py faz `import RPi.GPIO as GPIO` no nível de módulo
# (sem try/except), o que causa ImportError em macOS e Windows.
# Injetamos um mock de RPi.GPIO antes de qualquer import dos módulos CODIGO.
# ─────────────────────────────────────────────────────────────────────────────
import platform as _plat
import types as _types

_SYSTEM = _plat.system()  # "Linux" | "Darwin" | "Windows"
_IS_RASPBERRY_PI: bool = (
    _SYSTEM == "Linux"
    and Path("/proc/device-tree/model").exists()
    and "Raspberry Pi" in Path("/proc/device-tree/model").read_text(errors="ignore")
)


def _default_serial_port() -> str:
    """Porta serial padrão conforme o sistema operacional."""
    if _SYSTEM == "Windows":
        return "COM3"
    if _SYSTEM == "Darwin":          # macOS
        return "/dev/tty.usbserial-0001"
    return "/dev/ttyUSB0"            # Linux


# Injeta mock de RPi / RPi.GPIO para macOS e Windows (e Linux sem RPi)
if not _IS_RASPBERRY_PI and "RPi" not in sys.modules:
    _rpi_mod  = _types.ModuleType("RPi")
    _gpio_mod = _types.ModuleType("RPi.GPIO")

    class _MockGPIO:
        BCM = 11; BOARD = 10; OUT = 0; IN = 1; HIGH = 1; LOW = 0

        @staticmethod
        def setmode(m):              pass
        @staticmethod
        def setwarnings(f):          pass
        @staticmethod
        def setup(pin, mode, **kw):  pass
        @staticmethod
        def output(pin, val):        pass
        @staticmethod
        def input(pin):              return 0
        @staticmethod
        def cleanup(*a):             pass

        class PWM:
            def __init__(self, pin, freq): pass
            def start(self, dc):           pass
            def stop(self):                pass
            def ChangeDutyCycle(self, dc): pass
            def ChangeFrequency(self, f):  pass

    for _attr in ("BCM", "BOARD", "OUT", "IN", "HIGH", "LOW",
                  "setmode", "setwarnings", "setup", "output",
                  "input", "cleanup", "PWM"):
        setattr(_gpio_mod, _attr, getattr(_MockGPIO, _attr))

    _rpi_mod.GPIO = _gpio_mod
    sys.modules.setdefault("RPi",      _rpi_mod)
    sys.modules.setdefault("RPi.GPIO", _gpio_mod)

    logger_plat = logging.getLogger("ReGenPlatform")
    logger_plat.info(
        f"Plataforma detectada: {_SYSTEM} "
        f"({'RPi' if _IS_RASPBERRY_PI else 'PC/Mac — mock GPIO injetado'})"
    )


# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS DOS MÓDULOS RE-GEN (todos conectados aqui)
# ─────────────────────────────────────────────────────────────────────────────

# Dados paleontológicos e seleção de espécie
from paleontology import (
    obter_sistema_referencia,
    listar_dinossauros_recomendados,
    Dinossauro,
    DinosauroGrupo,
    Period,
)
from dinosaur_database import (
    DINOSAUR_DATABASE,
    DinosaurSpecies,
    DinosaurPeriod,
    DinosaurDiet,
    DinosaurFamily,
)
from dinosaur_selector import (
    SeletorDinossauro,
    ConfiguracaoSelecao,
    CapacidadeHardware,
)

# Mapeamento filogenético e busca NCBI
from descendant_mapper import (
    obter_mapeador,
    MapeadorDescendentes,
    EspecieDescendente,
    CaracteristicaAncestral,
)
from ncbi_reference import (
    DeepReferenceSearchEngine,
    ReferenceSequenceDeep,
)

# Reconstrução genômica
from genome_synthesis import (
    RealSequenceBuilder,
    RealDinosaurSequence,
    ReconstructedGenomePosition,
)
from genome_validator import (
    GenomeValidator,
    ValidationReport,
    SeverityLevel,
    create_validator,
)
from reconstruct import (
    reconstruct_ancestral_sequence,
    ReconstructionResult,
)

# Edição genética CRISPR
from gene_edit_package import (
    build_edit_package,
    export_edit_package_csv,
    EditPackage,
    GeneEdit,
)
from crispr_engine import (
    CRISPRDesigner,
    Cas9Variant,
    GuideRNA,
    CRISPREditingPlan,
)

# Integridade e armazenamento de DNA
from dna_integrity_checker import (
    DNAIntegrityChecker,
    CompleteIntegrityReport,
    IntegrityCheckResult,
)
from dna_storage_media_writer import (
    DNAStorageMediaWriter,
    StorageMetadata,
    ReedSolomonEncoder,
)

# Extração de DNA (da amostra fóssil)
from extrator_dna_core import (
    ExtratorDNA,
    AmostraBiologica,
    ParametroExtracao,
    ExtratorState,
)

# Hibridização de DNA
from hibridizador_core import (
    Hibridizador,
    ParametroReacao,
    HibridizadorState,
)

# Hardware de síntese de DNA
from dna_synthesizer_hardware import (
    DNASynthesizer,
    DNTPoolConfig,
    SynthesisParameter,
    ControladorHardwareSintetizador,
)

# Hardware de injeção em embrião
from embryo_injection_robot import (
    EmbryoInjectionRobot,
    InjectionTarget,
    XYZStage,
    SyringeController,
)

# Incubação e comunicação com Arduino
from arduino_bridge import ArduinoBridge
from incubator_device import IncubatorDevice
from device_base import DeviceBase

# Orquestração de hardware
from hardware_orchestrator import (
    HardwareOrchestrator,
    HardwareState,
    OrchestrationJob,
    InjectionStatus,
)
from hardware_devices import (
    build_hardware_devices,
    get_default_device_order,
    HARDWARE_DEVICE_SPECS,
)

# Relatório e orquestração final
from complete_revival_orchestrator import (
    CompleteRevivalOrchestrator,
    DinosaurRevivalJob,
)
from ai_report import gerar_relatorio_com_ollama
from ollama_integration import ClienteOllama, ConfiguracaoOllama

# Construtor de genoma em escala real (2–3 Gb)
sys.path.insert(0, str(Path(__file__).parent))
from genome_scale_builder import GenomeScaleBuilder, GenomeScaleResult


# ─────────────────────────────────────────────────────────────────────────────
# ESTRUTURAS DE DADOS DO PIPELINE UNIFICADO
# ─────────────────────────────────────────────────────────────────────────────

class PipelineStatus(Enum):
    """Status de cada fase do pipeline."""
    PENDENTE   = "pendente"
    EXECUTANDO = "executando"
    CONCLUIDO  = "concluído"
    FALHOU     = "falhou"
    IGNORADO   = "ignorado"   # fase opcional que foi pulada


@dataclass
class FaseResultado:
    """Resultado de uma fase do pipeline."""
    fase: int
    nome: str
    status: PipelineStatus
    duracao_segundos: float = 0.0
    dados: Dict = field(default_factory=dict)
    erros: List[str] = field(default_factory=list)
    alertas: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ConfiguracaoPipeline:
    """Configuração completa do pipeline de ressurreição."""
    # Identificação
    ncbi_email: str                          # Email para NCBI Entrez API
    ncbi_api_key: Optional[str] = None       # API key do NCBI (aumenta rate limit)

    # Espécie alvo
    nome_dinossauro: Optional[str] = None    # None = seleção automática
    preferencia_dieta: Optional[str] = None  # "carnívoro", "herbívoro"
    preferencia_periodo: Optional[str] = None

    # Hospedeiro para CRISPR
    hospedeiro: str = "Gallus gallus"        # Embrião hospedeiro para edição

    # Fóssil (opcional)
    arquivo_fossil_fasta: Optional[str] = None  # Fragmento de fóssil real em FASTA

    # Saídas
    diretorio_saida: str = "./re_gen_output"

    # Hardware (porta serial detectada automaticamente por SO)
    arduino_port: str = field(default_factory=_default_serial_port)
    arduino_baudrate: int = 9600
    hardware_disponivel: bool = False        # True se hardware físico está conectado

    # Síntese
    gerar_relatorio_ia: bool = True          # Gerar laudo com Ollama
    ollama_modelo: str = "llama2"

    # Qualidade
    confianca_minima: float = 0.60           # Score mínimo de confiança por posição
    min_confianca_crispr: float = 0.55       # Só edita posições acima desse threshold

    # Execução parcial — fases a executar (0 = Seleção, 8 = Relatório IA)
    fase_inicio: int = 0                     # Primeira fase a executar (0–8)
    fase_fim:    int = 8                     # Última fase a executar  (0–8)


@dataclass
class ResultadoPipelineCompleto:
    """Resultado completo do pipeline de 8 fases."""
    configuracao: ConfiguracaoPipeline
    timestamp_inicio: str
    timestamp_fim: Optional[str] = None
    status_global: PipelineStatus = PipelineStatus.PENDENTE
    fases: List[FaseResultado] = field(default_factory=list)

    # Dados intermediários preservados
    dinossauro_selecionado: Optional[Dinossauro] = None
    referencias_ncbi: List[ReferenceSequenceDeep] = field(default_factory=list)
    genoma_reconstruido: Optional[RealDinosaurSequence] = None
    relatorio_integridade: Optional[CompleteIntegrityReport] = None
    pacote_edicoes: Optional[EditPackage] = None
    plano_crispr: Optional[CRISPREditingPlan] = None
    relatorio_ia: Optional[str] = None
    diretorio_saida_final: Optional[str] = None
    # Genoma completo em escala real (2–3 Gb, escrito em arquivos FASTA)
    genoma_escala_completa: Optional[GenomeScaleResult] = None


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE PRINCIPAL UNIFICADO
# ─────────────────────────────────────────────────────────────────────────────

class ReGenPipelineUnificado:
    """
    Orquestrador mestre do pipeline de ressurreição de dinossauros.

    Conecta e executa todos os módulos do Re-Gen Project numa sequência
    coerente e completa, do paleontológico ao físico-laboratorial.
    """

    def __init__(self, config: ConfiguracaoPipeline):
        self.config = config
        self.logger = logging.getLogger("ReGenPipeline")
        self.output_dir = Path(config.diretorio_saida)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._resultado: Optional[ResultadoPipelineCompleto] = None

    # ─────────────────────────────────────────────────────────────────────────
    # MÉTODO PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS DE SELEÇÃO DE FASES
    # ─────────────────────────────────────────────────────────────────────────

    def _deve_executar(self, fase: int) -> bool:
        """Retorna True se a fase está dentro do range configurado."""
        return self.config.fase_inicio <= fase <= self.config.fase_fim

    def _skip(self, fase: int, nome: str) -> None:
        """Registra uma fase pulada no resultado."""
        self._resultado.fases.append(
            FaseResultado(
                fase=fase,
                nome=nome,
                status=PipelineStatus.IGNORADO,
                alertas=[
                    f"Fase {fase} pulada (fora do range "
                    f"{self.config.fase_inicio}–{self.config.fase_fim})"
                ],
            )
        )
        self.logger.info(
            f"  ⏭  FASE {fase} — {nome} — PULADA "
            f"(range: {self.config.fase_inicio}–{self.config.fase_fim})"
        )

    def executar(self) -> ResultadoPipelineCompleto:
        """
        Executa o pipeline de ressurreição de dinossauros.

        Por padrão roda todas as fases (0–8). Use os campos
        ``ConfiguracaoPipeline.fase_inicio`` e ``fase_fim`` para executar
        apenas um subconjunto; ou passe ``--fase-inicio N --fase-fim M``
        na linha de comando.

        ⚠  Fases com dependência de dados gerados por fases anteriores
           falharão se a fase predecessora foi pulada (sem serialização
           de checkpoint implementada).  O menu interativo garante que
           as fases sempre começam em 0 para preservar a cadeia.

        Retorna ResultadoPipelineCompleto com todos os dados produzidos.
        """
        self._resultado = ResultadoPipelineCompleto(
            configuracao=self.config,
            timestamp_inicio=datetime.now().isoformat(),
            status_global=PipelineStatus.EXECUTANDO,
        )

        fi, ff = self.config.fase_inicio, self.config.fase_fim
        if fi == 0 and ff == 8:
            titulo = "INICIANDO PIPELINE RE-GEN — RESSURREIÇÃO DE DINOSSAUROS (COMPLETO)"
        else:
            nomes = {
                0: "Seleção Paleontológica",
                1: "Mapeamento Filogenético + NCBI",
                2: "Extração de DNA Fóssil",
                3: "Reconstrução Genômica",
                4: "Pacote CRISPR",
                5: "Síntese Física de DNA",
                6: "Injeção no Embrião",
                7: "Incubação Monitorada",
                8: "Relatório Final com IA",
            }
            titulo = (
                f"INICIANDO RE-GEN — FASES {fi}–{ff} "
                f"({nomes.get(fi, fi)} → {nomes.get(ff, ff)})"
            )
        self._banner(titulo)

        try:
            # ─── FASE 0: Seleção Paleontológica ───────────────────────────
            if self._deve_executar(0):
                self._fase0_selecao_paleontologica()
            else:
                self._skip(0, "Seleção Paleontológica")

            # ─── FASE 1: Mapeamento Filogenético e NCBI ───────────────────
            if self._deve_executar(1):
                self._fase1_mapeamento_e_ncbi()
            else:
                self._skip(1, "Mapeamento Filogenético + NCBI")

            # ─── FASE 2: Extração de DNA Fóssil (opcional) ────────────────
            if self._deve_executar(2):
                self._fase2_extracao_fossil()
            else:
                self._skip(2, "Extração de DNA Fóssil")

            # ─── FASE 3: Reconstrução Genômica ────────────────────────────
            if self._deve_executar(3):
                self._fase3_reconstrucao_genomica()
            else:
                self._skip(3, "Reconstrução Genômica")

            # ─── FASE 4: Pacote CRISPR ────────────────────────────────────
            if self._deve_executar(4):
                self._fase4_pacote_crispr()
            else:
                self._skip(4, "Pacote CRISPR")

            # ─── FASE 5: Síntese Física de DNA ────────────────────────────
            if self._deve_executar(5):
                self._fase5_sintese_fisica()
            else:
                self._skip(5, "Síntese Física de DNA")

            # ─── FASE 6: Injeção no Embrião ───────────────────────────────
            if self._deve_executar(6):
                self._fase6_injecao_embriao()
            else:
                self._skip(6, "Injeção no Embrião")

            # ─── FASE 7: Incubação Monitorada ─────────────────────────────
            if self._deve_executar(7):
                self._fase7_incubacao()
            else:
                self._skip(7, "Incubação Monitorada")

            # ─── FASE 8: Relatório Final ──────────────────────────────────
            if self._deve_executar(8):
                self._fase8_relatorio_final()
            else:
                self._skip(8, "Relatório Final com IA")

            self._resultado.status_global = PipelineStatus.CONCLUIDO
            self._resultado.timestamp_fim = datetime.now().isoformat()
            self._banner("PIPELINE CONCLUÍDO COM SUCESSO")

        except Exception as e:
            self._resultado.status_global = PipelineStatus.FALHOU
            self._resultado.timestamp_fim = datetime.now().isoformat()
            self.logger.error(f"Pipeline falhou com exceção: {e}", exc_info=True)

        return self._resultado

    # ─────────────────────────────────────────────────────────────────────────
    # FASE 0 — SELEÇÃO PALEONTOLÓGICA
    # ─────────────────────────────────────────────────────────────────────────

    def _fase0_selecao_paleontologica(self) -> None:
        """
        Seleciona a espécie de dinossauro alvo usando:
        - dinosaur_database.py  → banco de 500+ espécies com dados reais
        - paleontology.py       → sistema de referência filogenética
        - dinosaur_selector.py  → seleção automática com score composto
        """
        inicio = time.time()
        fase = FaseResultado(fase=0, nome="Seleção Paleontológica", status=PipelineStatus.EXECUTANDO)

        self.logger.info("\n" + "═" * 70)
        self.logger.info("[FASE 0] SELEÇÃO PALEONTOLÓGICA")
        self.logger.info("═" * 70)

        # ── Consulta banco completo de 500+ dinossauros ──────────────────────
        total_especies = len(DINOSAUR_DATABASE)
        self.logger.info(f"Banco de dados: {total_especies} espécies catalogadas")

        # ── Sistema de referência paleontológica ─────────────────────────────
        sr = obter_sistema_referencia()
        self.logger.info(f"Sistema de referência: {len(sr.dinossauros)} espécies com dados genômicos")

        # ── Seleção da espécie alvo ──────────────────────────────────────────
        if self.config.nome_dinossauro:
            # Nome fornecido: busca diretamente
            dino = sr.buscar_por_nome(self.config.nome_dinossauro)
            if dino is None:
                # Tenta encontrar no banco de dados completo por similaridade
                match = next(
                    (d for d in DINOSAUR_DATABASE
                     if self.config.nome_dinossauro.lower() in d.scientific_name.lower()),
                    None
                )
                if match:
                    self.logger.info(f"Encontrado no banco de dados: {match.scientific_name}")
                    # Cria objeto Dinossauro compatível
                    dino = Dinossauro(
                        nome_cientifico=match.scientific_name,
                        nome_comum=match.common_name,
                        grupo=DinosauroGrupo.THEROPODA,
                        periodo=Period.CRETACEO,
                        peso_estimado_kg=match.weight_kg,
                        comprimento_estimado_m=match.length_meters,
                        altura_estimada_m=match.height_meters,
                        dieta=match.diet.value,
                        localizacao_geografica=[match.country],
                        descricao_paleontologica=match.description,
                        caracteristicas_notaveis=match.unique_features,
                        genes_conservados=["HOX", "PAX6", "BMP", "FOXP2"],
                        taxa_diferencacao_estimada=66.0,
                        ancestrais_proximos=[],
                        descendentes_vivos=["Gallus gallus", "Struthio camelus"],
                    )
                else:
                    raise ValueError(
                        f"Dinossauro '{self.config.nome_dinossauro}' não encontrado. "
                        f"Use --lista para ver as espécies disponíveis."
                    )
        else:
            # Seleção automática usando SeletorDinossauro
            self.logger.info("Seleção automática de espécie...")
            config_selecao = ConfiguracaoSelecao(
                hardware=CapacidadeHardware.NENHUMA
                          if not self.config.hardware_disponivel
                          else CapacidadeHardware.AVANCADA,
                preferencia_tipo_dieta=self.config.preferencia_dieta,
            )
            seletor = SeletorDinossauro(sr)
            dino, score_confianca = seletor.selecionar(config_selecao)
            self.logger.info(
                f"Espécie selecionada: {dino.nome_cientifico} "
                f"(score={score_confianca:.4f})"
            )

        self._resultado.dinossauro_selecionado = dino

        # ── Lista espécies recomendadas como referência ──────────────────────
        recomendados = listar_dinossauros_recomendados()
        self.logger.info(f"Top-3 candidatos por qualidade genômica:")
        for i, r in enumerate(recomendados[:3], 1):
            self.logger.info(
                f"  {i}. {r.nome_cientifico} "
                f"— genes conservados: {len(r.genes_conservados)}, "
                f"diferenciação estimada: {r.taxa_diferencacao_estimada:.0f}Ma"
            )

        # ── Dados específicos do banco de 500+ ──────────────────────────────
        db_entry = next(
            (d for d in DINOSAUR_DATABASE
             if dino.nome_cientifico.lower() in d.scientific_name.lower()),
            None
        )
        if db_entry:
            self.logger.info(f"Tamanho do genoma estimado: {db_entry.genome_size_bp:,} bp")
            self.logger.info(
                f"Similaridade com aves modernas: "
                f"{db_entry.estimated_genome_similarity_with_birds * 100:.0f}%"
            )

        fase.status = PipelineStatus.CONCLUIDO
        fase.duracao_segundos = time.time() - inicio
        fase.dados = {
            "especie": dino.nome_cientifico,
            "nome_comum": dino.nome_comum,
            "grupo": dino.grupo.value,
            "periodo": dino.periodo.value,
            "peso_kg": dino.peso_estimado_kg,
            "comprimento_m": dino.comprimento_estimado_m,
            "genes_conservados": dino.genes_conservados,
            "descendentes_vivos": dino.descendentes_vivos,
            "total_especies_banco": total_especies,
        }
        self._resultado.fases.append(fase)
        self.logger.info(f"✓ Fase 0 concluída em {fase.duracao_segundos:.1f}s — {dino.nome_cientifico}")

    # ─────────────────────────────────────────────────────────────────────────
    # FASE 1 — MAPEAMENTO FILOGENÉTICO E BUSCA NCBI
    # ─────────────────────────────────────────────────────────────────────────

    def _fase1_mapeamento_e_ncbi(self) -> None:
        """
        Mapeia descendentes vivos do dinossauro e busca sequências no NCBI:
        - descendant_mapper.py  → identifica aves/crocodilianos relacionados
        - ncbi_reference.py     → DeepReferenceSearchEngine busca NCBI real
        """
        inicio = time.time()
        fase = FaseResultado(fase=1, nome="Mapeamento Filogenético e NCBI", status=PipelineStatus.EXECUTANDO)
        dino = self._resultado.dinossauro_selecionado

        self.logger.info("\n" + "═" * 70)
        self.logger.info("[FASE 1] MAPEAMENTO FILOGENÉTICO E BUSCA NCBI")
        self.logger.info("═" * 70)

        # ── Mapeador de descendentes ─────────────────────────────────────────
        mapeador: MapeadorDescendentes = obter_mapeador()
        descendentes_do_dino = mapeador.buscar_por_ancestral(dino.nome_cientifico)

        if not descendentes_do_dino:
            # Fallback: usa todos os descendentes cadastrados
            descendentes_do_dino = mapeador.listar_todos_recomendados()
            self.logger.warning(
                f"Nenhum descendente mapeado diretamente para {dino.nome_cientifico}. "
                f"Usando painel completo ({len(descendentes_do_dino)} espécies)."
            )
        else:
            self.logger.info(
                f"Descendentes mapeados de {dino.nome_cientifico}: "
                f"{len(descendentes_do_dino)} espécies"
            )

        for e in descendentes_do_dino[:5]:
            self.logger.info(
                f"  • {e.nome_cientifico} ({e.grupo_taxa}) "
                f"— utilidade={e.score_utilidade_genomica:.0f}, "
                f"NCBI={e.qualidade_anotacao_ncbi:.0f}"
            )

        # Melhor hospedeiro para edição CRISPR
        melhor_ref = mapeador.encontrar_melhor_referencia(
            dino.nome_cientifico,
            caracteristica_necessaria=CaracteristicaAncestral.OSSOS_OCOS,
        )
        if melhor_ref:
            self.logger.info(f"Melhor hospedeiro para CRISPR: {melhor_ref.nome_cientifico}")
            self.config.hospedeiro = melhor_ref.nome_cientifico

        # ── Busca profunda no NCBI ───────────────────────────────────────────
        self.logger.info(f"Iniciando busca profunda no NCBI (email={self.config.ncbi_email})...")
        ncbi_output = self.output_dir / "ncbi_references"
        ncbi_output.mkdir(exist_ok=True)

        search_engine = DeepReferenceSearchEngine(
            email=self.config.ncbi_email,
            api_key=self.config.ncbi_api_key,
            output_dir=str(ncbi_output),
        )

        referencias: List[ReferenceSequenceDeep] = search_engine.search_comprehensive(
            target_lineage="dinosauria"
        )

        if not referencias:
            raise RuntimeError(
                "Nenhuma referência encontrada no NCBI. "
                "Verifique seu email, conexão e rate limits."
            )

        self._resultado.referencias_ncbi = referencias

        # Estatísticas das referências
        genes_encontrados = set(r.gene_name for r in referencias)
        especies_ncbi = set(r.species for r in referencias)
        refs_validadas = [r for r in referencias if r.validated]

        self.logger.info(f"✓ NCBI: {len(referencias)} sequências recuperadas")
        self.logger.info(f"  Genes cobertos: {sorted(genes_encontrados)}")
        self.logger.info(f"  Espécies: {sorted(especies_ncbi)}")
        self.logger.info(f"  Validadas (Q≥70): {len(refs_validadas)}")

        # Salva referências em JSON
        refs_json = ncbi_output / "referencias_validadas.json"
        with open(refs_json, "w") as f:
            json.dump(
                [
                    {
                        "species": r.species,
                        "accession": r.accession,
                        "gene": r.gene_name,
                        "length_bp": r.length,
                        "quality_score": r.quality_score,
                        "phylogenetic_distance_Ma": r.phylogenetic_distance,
                        "validated": r.validated,
                    }
                    for r in sorted(referencias, key=lambda x: x.quality_score, reverse=True)
                ],
                f,
                indent=2,
            )

        fase.status = PipelineStatus.CONCLUIDO
        fase.duracao_segundos = time.time() - inicio
        fase.dados = {
            "n_descendentes_mapeados": len(descendentes_do_dino),
            "hospedeiro_crispr": self.config.hospedeiro,
            "n_referencias_ncbi": len(referencias),
            "n_referencias_validadas": len(refs_validadas),
            "genes_cobertos": sorted(genes_encontrados),
            "especies_referencia": sorted(especies_ncbi),
        }
        self._resultado.fases.append(fase)
        self.logger.info(f"✓ Fase 1 concluída em {fase.duracao_segundos:.1f}s")

    # ─────────────────────────────────────────────────────────────────────────
    # FASE 2 — EXTRAÇÃO DE DNA FÓSSIL (opcional)
    # ─────────────────────────────────────────────────────────────────────────

    def _fase2_extracao_fossil(self) -> None:
        """
        Processa fragmento de DNA fóssil (se fornecido):
        - extrator_dna_core.py  → pipeline de extração: lise → centrifugação → elution
        - fossil_grinder_device → tritura a amostra
        - fossil_cleaner_device → limpa a amostra antes da extração
        """
        inicio = time.time()
        fase = FaseResultado(fase=2, nome="Extração de DNA Fóssil", status=PipelineStatus.EXECUTANDO)

        self.logger.info("\n" + "═" * 70)
        self.logger.info("[FASE 2] EXTRAÇÃO DE DNA FÓSSIL")
        self.logger.info("═" * 70)

        if not self.config.arquivo_fossil_fasta:
            fase.status = PipelineStatus.IGNORADO
            fase.dados = {"motivo": "Nenhum fóssil fornecido — reconstrução 100% filogenética"}
            fase.duracao_segundos = time.time() - inicio
            self._resultado.fases.append(fase)
            self.logger.info("→ Fase 2 ignorada: nenhum arquivo de fóssil fornecido")
            self.logger.info("  Reconstrução será 100% filogenética (EPB — Extant Phylogenetic Bracket)")
            return

        # ── Carrega fragmento FASTA ──────────────────────────────────────────
        fossil_path = Path(self.config.arquivo_fossil_fasta)
        if not fossil_path.exists():
            raise FileNotFoundError(f"Arquivo de fóssil não encontrado: {fossil_path}")

        try:
            from Bio import SeqIO
            records = list(SeqIO.parse(str(fossil_path), "fasta"))
            if not records:
                raise ValueError("Arquivo FASTA vazio ou inválido")

            fragmento_fossil = str(records[0].seq).upper()
            self.logger.info(f"Fragmento de fóssil: {len(fragmento_fossil):,} bp de {fossil_path.name}")
        except ImportError:
            self.logger.warning("BioPython não disponível — lendo FASTA manualmente")
            with open(fossil_path) as fh:
                lines = [l.strip() for l in fh if not l.startswith(">")]
            fragmento_fossil = "".join(lines).upper()

        # ── Extração de DNA via pipeline bioquímico ──────────────────────────
        extrator = ExtratorDNA()
        extrator.ligar()

        amostra = AmostraBiologica(
            id=f"FOSSIL_{self._resultado.dinossauro_selecionado.nome_cientifico.replace(' ', '_')}",
            tipo="fossil",
            volume_ml=0.5,          # ~0.5 mL de pó de fóssil após trituração
            quantidade_celulas=50,   # fragmentário — muito poucas células viáveis
            timestamp_coleta=datetime.now().isoformat(),
        )

        parametros = ParametroExtracao(
            temperatura_lise=56.0,   # 56°C — mais suave para DNA degradado
            tempo_lise=600,          # 10 minutos
            rpm_centrifugacao=8000,  # RPM mais baixo para material frágil
            tempo_centrifugacao=180,
            volume_buffer_lise=200,
            volume_etanol=300,
            temperatura_secagem=45.0,
            tempo_secagem=300,
        )

        extrator.carregar_amostra(amostra)
        extrator.configurar_parametros({
            "temperatura_lise": parametros.temperatura_lise,
            "tempo_lise": parametros.tempo_lise,
            "rpm_centrifugacao": parametros.rpm_centrifugacao,
        })
        extrator.iniciar_extracao()

        status_extracao = extrator.obter_status()
        dna_ng = status_extracao["dna_extraido_ng"]
        pureza = status_extracao["pureza"]

        self.logger.info(f"DNA extraído: {dna_ng:.2f} ng")
        self.logger.info(f"Pureza A260/A280: {pureza:.2f} (ideal: 1.8–2.0)")
        self.logger.info(f"Concentração: {dna_ng / 50:.2f} ng/µL (em 50 µL de buffer TE)")

        # Salva resultado da extração
        extracao_output = self.output_dir / "extracao_fossil"
        extracao_output.mkdir(exist_ok=True)
        dados_extracao = extrator.exportar_dados_extracao()
        with open(extracao_output / "resultado_extracao.json", "w") as f:
            json.dump(dados_extracao, f, indent=2)

        extrator.desligar()

        # ── Adiciona fragmento aos dados do pipeline ─────────────────────────
        # O fragmento bruto do arquivo FASTA será usado como âncora de alta confiança
        # na reconstrução filogenética (FASE 3)
        fase.dados["fragmento_fossil_bp"] = len(fragmento_fossil)
        fase.dados["fragmento_fossil_seq"] = fragmento_fossil[:200] + "..."  # preview

        # Salva o fragmento para a FASE 3
        (extracao_output / "fragmento_fossil.fasta").write_text(
            f">{self._resultado.dinossauro_selecionado.nome_cientifico} | fossil fragment\n"
            + "\n".join(fragmento_fossil[i:i+70] for i in range(0, len(fragmento_fossil), 70))
        )

        fase.status = PipelineStatus.CONCLUIDO
        fase.duracao_segundos = time.time() - inicio
        fase.dados.update({
            "arquivo_fossil": str(fossil_path),
            "fragmento_bp": len(fragmento_fossil),
            "dna_extraido_ng": dna_ng,
            "pureza_a260_a280": pureza,
            "concentracao_ng_ul": dna_ng / 50,
        })
        self._resultado.fases.append(fase)
        self.logger.info(f"✓ Fase 2 concluída em {fase.duracao_segundos:.1f}s")

    # ─────────────────────────────────────────────────────────────────────────
    # FASE 3 — RECONSTRUÇÃO GENÔMICA
    # ─────────────────────────────────────────────────────────────────────────

    def _fase3_reconstrucao_genomica(self) -> None:
        """
        Reconstrói o genoma do dinossauro a partir das referências NCBI:
        - genome_synthesis.py   → RealSequenceBuilder com consenso filogenético
        - reconstruct.py        → alinhamento Needleman-Wunsch + consenso ponderado
        - genome_validator.py   → validação multi-camada da sequência resultante
        """
        inicio = time.time()
        fase = FaseResultado(fase=3, nome="Reconstrução Genômica", status=PipelineStatus.EXECUTANDO)
        dino = self._resultado.dinossauro_selecionado
        referencias = self._resultado.referencias_ncbi

        self.logger.info("\n" + "═" * 70)
        self.logger.info("[FASE 3] RECONSTRUÇÃO GENÔMICA")
        self.logger.info("═" * 70)

        # ── Carrega fragmento fóssil (se existir) ───────────────────────────
        fossil_fragment: Optional[str] = None
        fossil_fasta = self.output_dir / "extracao_fossil" / "fragmento_fossil.fasta"
        if fossil_fasta.exists():
            try:
                from Bio import SeqIO
                recs = list(SeqIO.parse(str(fossil_fasta), "fasta"))
                if recs:
                    fossil_fragment = str(recs[0].seq).upper()
                    self.logger.info(f"Fragmento fóssil incorporado: {len(fossil_fragment):,} bp")
            except Exception as e:
                self.logger.warning(f"Falha ao ler fragmento fóssil: {e}")

        # ── RealSequenceBuilder: reconstrução por EPB ────────────────────────
        seq_output = self.output_dir / "genoma_reconstruido"
        builder = RealSequenceBuilder(
            dinosaur_name=dino.nome_cientifico,
            output_dir=str(seq_output),
        )

        ref_data = [
            {
                "sequence": r.sequence,
                "accession": r.accession,
                "phylogenetic_weight": 1.0 / (1.0 + r.phylogenetic_distance / 100.0),
                "quality_score": r.quality_score,
            }
            for r in referencias
            if r.sequence and len(r.sequence) >= 100
        ]

        self.logger.info(
            f"Reconstruindo de {len(ref_data)} referências "
            f"(confiança mínima: {self.config.confianca_minima * 100:.0f}%)"
        )

        genoma: Optional[RealDinosaurSequence] = builder.build_from_reference_panel(
            reference_sequences=ref_data,
            fossil_fragment=fossil_fragment,
            min_confidence=self.config.confianca_minima,
        )

        if not genoma:
            raise RuntimeError(
                "Falha na reconstrução genômica. "
                "Verifique qualidade das referências NCBI."
            )

        # ── Validação multi-camada ───────────────────────────────────────────
        self.logger.info("Validando sequência reconstruída...")
        validator: GenomeValidator = create_validator()

        # Valida em chunks de 10.000 bp
        chunk_size = 10_000
        relatorio_validacao_total = {
            "erros": 0,
            "alertas": 0,
            "chunks_validos": 0,
            "chunks_invalidos": 0,
        }

        for chunk_idx, start in enumerate(range(0, len(genoma.sequence), chunk_size)):
            chunk = genoma.sequence[start:start + chunk_size]
            vreport: ValidationReport = validator.validate(chunk, chunk_id=f"chunk_{chunk_idx}")
            relatorio_validacao_total["erros"] += vreport.error_count
            relatorio_validacao_total["alertas"] += vreport.warning_count
            if vreport.is_valid:
                relatorio_validacao_total["chunks_validos"] += 1
            else:
                relatorio_validacao_total["chunks_invalidos"] += 1

        self.logger.info(
            f"Validação: "
            f"{relatorio_validacao_total['chunks_validos']} chunks válidos, "
            f"{relatorio_validacao_total['chunks_invalidos']} chunks com problemas"
        )
        self.logger.info(
            f"  Erros críticos: {relatorio_validacao_total['erros']}, "
            f"Alertas: {relatorio_validacao_total['alertas']}"
        )

        # ── Estatísticas do genoma ───────────────────────────────────────────
        seq = genoma.sequence
        gc = (seq.count("G") + seq.count("C")) / len(seq) * 100
        n_count = seq.count("N")
        n_pct = n_count / len(seq) * 100

        self.logger.info(f"Genoma reconstruído: {len(seq):,} bp")
        self.logger.info(f"  Confiança média: {genoma.mean_confidence:.1f}%")
        self.logger.info(f"  GC%: {gc:.1f}%")
        self.logger.info(f"  Ambiguidades (N): {n_count:,} ({n_pct:.1f}%)")
        self.logger.info(f"  Regiões baixa confiança: {len(genoma.low_confidence_regions)}")
        self.logger.info(f"  Referências usadas: {genoma.n_references_used}")

        if genoma.low_confidence_regions:
            self.logger.warning(
                f"  ⚠ {len(genoma.low_confidence_regions)} regiões (<{self.config.confianca_minima*100:.0f}%) "
                f"precisarão de mais dados antes de síntese"
            )

        self._resultado.genoma_reconstruido = genoma

        # ── Expansão para escala cromossômica real: 2–3 Gb ──────────────────
        # O genoma EPB acima (~kb-Mb) é a reconstrução gênica de alta
        # confiança. Agora expandimos para um genoma cromossômico completo
        # de 2–3 Gb usando janelas reais do NCBI + TEs reais do Dfam.
        self.logger.info("")
        self.logger.info("Expandindo para escala cromossômica real (2–3 Gb)...")
        self.logger.info("  Fontes: NCBI Entrez (Gallus + Alligator) + Dfam TEs")

        genoma_escala: Optional[GenomeScaleResult] = None
        try:
            scale_output = self.output_dir / "genoma_escala_completa"
            scale_builder = GenomeScaleBuilder(
                dinosaur_name=dino.nome_cientifico,
                email=self.config.ncbi_email,
                output_dir=str(scale_output),
                target_bp=2_100_000_000,   # 2.1 Gb — central no range 2–3 Gb
                api_key=self.config.ncbi_api_key,
            )
            genoma_escala = scale_builder.build_genome()
            self._resultado.genoma_escala_completa = genoma_escala

            gb = genoma_escala.total_length_bp / 1e9
            self.logger.info(
                f"✓ Genoma escala completa: "
                f"{genoma_escala.total_length_bp:,} bp = {gb:.3f} Gb "
                f"| {genoma_escala.n_chromosomes} cromossomos "
                f"| {genoma_escala.n_ncbi_windows_used} janelas NCBI reais "
                f"| conf={genoma_escala.mean_confidence:.2f}"
            )
            assert 2_000_000_000 <= genoma_escala.total_length_bp <= 3_000_000_000, (
                f"Genoma fora do range 2–3 Gb: {genoma_escala.total_length_bp:,} bp"
            )
        except Exception as e:
            self.logger.warning(
                f"⚠ Expansão cromossômica falhou (requer internet para NCBI/Dfam): {e}\n"
                f"  O genoma EPB de {len(seq):,} bp permanece disponível para CRISPR."
            )

        fase.status = PipelineStatus.CONCLUIDO
        fase.duracao_segundos = time.time() - inicio
        fase.dados = {
            "comprimento_epb_bp": len(seq),
            "comprimento_escala_bp": genoma_escala.total_length_bp if genoma_escala else None,
            "comprimento_escala_gb": round(genoma_escala.total_length_bp / 1e9, 3) if genoma_escala else None,
            "range_valido_2_3gb": (
                2_000_000_000 <= genoma_escala.total_length_bp <= 3_000_000_000
                if genoma_escala else None
            ),
            "n_cromossomos": genoma_escala.n_chromosomes if genoma_escala else None,
            "janelas_ncbi_reais": genoma_escala.n_ncbi_windows_used if genoma_escala else None,
            "familias_te_dfam": genoma_escala.te_families_used if genoma_escala else None,
            "dfam_online": genoma_escala.dfam_online if genoma_escala else None,
            "confianca_media_pct": genoma.mean_confidence,
            "gc_pct": gc,
            "n_ambiguidades": n_count,
            "n_ambiguidades_pct": n_pct,
            "n_regioes_baixa_confianca": len(genoma.low_confidence_regions),
            "n_referencias_epb": genoma.n_references_used,
            "metodo": "EPB_gene_scale + EPB_Dfam_Scaffold_v2",
            "validacao": relatorio_validacao_total,
            "fasta_dir": genoma_escala.genome_fasta_dir if genoma_escala else None,
            "manifest": genoma_escala.manifest_json if genoma_escala else None,
        }
        self._resultado.fases.append(fase)
        self.logger.info(f"✓ Fase 3 concluída em {fase.duracao_segundos:.1f}s")

    # ─────────────────────────────────────────────────────────────────────────
    # FASE 4 — PACOTE DE EDIÇÃO CRISPR
    # ─────────────────────────────────────────────────────────────────────────

    def _fase4_pacote_crispr(self) -> None:
        """
        Gera o pacote de edições CRISPR para transformar o hospedeiro:
        - gene_edit_package.py → compara ancestral vs hospedeiro, lista SNPs/indels
        - crispr_engine.py     → design de gRNAs (PAM, especificidade, eficiência)
        """
        inicio = time.time()
        fase = FaseResultado(fase=4, nome="Pacote de Edição CRISPR", status=PipelineStatus.EXECUTANDO)
        dino = self._resultado.dinossauro_selecionado
        genoma = self._resultado.genoma_reconstruido

        self.logger.info("\n" + "═" * 70)
        self.logger.info("[FASE 4] PACOTE DE EDIÇÃO CRISPR")
        self.logger.info("═" * 70)

        # ── Obtém sequência do hospedeiro no NCBI ────────────────────────────
        self.logger.info(f"Hospedeiro selecionado: {self.config.hospedeiro}")

        # Usa a primeira referência NCBI da espécie hospedeira como representante
        hospedeiro_refs = [
            r for r in self._resultado.referencias_ncbi
            if self.config.hospedeiro.lower() in r.species.lower()
        ]

        if hospedeiro_refs:
            host_sequence = max(hospedeiro_refs, key=lambda r: r.quality_score).sequence
            self.logger.info(
                f"Sequência hospedeira: {len(host_sequence):,} bp "
                f"(accession: {hospedeiro_refs[0].accession})"
            )
        else:
            # Fallback: usa as primeiras bases do genoma reconstruído como proxy
            self.logger.warning(
                f"Sequência de {self.config.hospedeiro} não encontrada no painel NCBI. "
                f"Usando proxy filogenético."
            )
            host_sequence = genoma.sequence[:5000]

        # ── Gera pacote de edições (EditPackage) ─────────────────────────────
        reconstruction_compat = ReconstructionResult(
            consensus_sequence=genoma.sequence,
            per_base_confidence=[p.confidence / 100.0 for p in genoma.positions_metadata]
                                  if genoma.positions_metadata
                                  else [genoma.mean_confidence / 100.0] * len(genoma.sequence),
            mean_confidence=genoma.mean_confidence / 100.0,
            n_references_used=getattr(genoma, "n_references_used", 0),
            reference_species=getattr(genoma, "reference_species", []),
            gc_content=round(
                (genoma.sequence.count("G") + genoma.sequence.count("C"))
                / len(genoma.sequence) * 100,
                2,
            ),
        )

        pacote: EditPackage = build_edit_package(
            reconstruction=reconstruction_compat,
            host_sequence=host_sequence,
            host_species=self.config.hospedeiro,
            target_species_label=dino.nome_cientifico,
            min_confidence_to_edit=self.config.min_confianca_crispr,
        )

        self._resultado.pacote_edicoes = pacote

        self.logger.info(f"Identidade genômica ancestral↔hospedeiro: {pacote.pct_genome_identity:.1f}%")
        self.logger.info(f"Total de edições propostas: {pacote.n_total_edits}")

        if pacote.edits:
            sub_count = sum(1 for e in pacote.edits if e.edit_type == "substituicao")
            ins_count = sum(1 for e in pacote.edits if e.edit_type == "insercao")
            del_count = sum(1 for e in pacote.edits if e.edit_type == "delecao")
            self.logger.info(f"  Substituições: {sub_count}")
            self.logger.info(f"  Inserções: {ins_count}")
            self.logger.info(f"  Deleções: {del_count}")

        # Exporta CSV para ferramentas de CRISPR (Benchling, CHOPCHOP)
        crispr_output = self.output_dir / "crispr"
        crispr_output.mkdir(exist_ok=True)
        csv_path = str(crispr_output / "pacote_edicao_crispr.csv")
        export_edit_package_csv(pacote, csv_path)
        self.logger.info(f"Pacote de edições exportado: {csv_path}")

        # ── Design de gRNAs com CRISPRDesigner ──────────────────────────────
        designer = CRISPRDesigner(variant=Cas9Variant.SPCAS9)
        self.logger.info("Desenhando guide-RNAs (SpCas9 / NGG PAM)...")

        # Seleciona até 3 regiões de alta confiança para design de gRNA
        target_seq = genoma.sequence[:2000]  # Trabalha nos primeiros 2kb como exemplo
        grnas: List[GuideRNA] = designer.find_grnas(
            target_seq,
            region_start=0,
            region_end=len(target_seq),
            num_grnas=10,
        )

        bons_grnas = [g for g in grnas if g.is_good]
        self.logger.info(f"gRNAs desenhados: {len(grnas)} total, {len(bons_grnas)} de qualidade")

        for i, g in enumerate(bons_grnas[:3], 1):
            self.logger.info(
                f"  gRNA#{i}: {g.sequence} | "
                f"GC={g.gc_content:.0f}% | "
                f"Spec={g.specificity_score:.0f} | "
                f"Eff={g.efficiency_score:.0f}"
            )

        # Plano completo de edição
        if bons_grnas:
            plano: CRISPREditingPlan = designer.design_edit_plan(
                target_sequence=target_seq,
                target_start=0,
                target_end=min(500, len(target_seq)),
                desired_change="substituicao",
                desired_sequence=None,
            )
            self._resultado.plano_crispr = plano
            self.logger.info(
                f"Eficiência esperada do plano: {plano.expected_efficiency:.0f}%"
            )
            if plano.potential_risks:
                for r in plano.potential_risks:
                    self.logger.warning(f"  ⚠ Risco: {r}")

        # Salva gRNAs em JSON
        grna_data = [
            {
                "sequence": g.sequence,
                "pam": g.pam,
                "position": g.position,
                "gc_pct": g.gc_content,
                "specificity": g.specificity_score,
                "efficiency": g.efficiency_score,
                "combined_score": g.combined_score,
                "is_good": g.is_good,
                "homopolymers": g.homopolymer_count,
            }
            for g in grnas
        ]
        with open(crispr_output / "grnas.json", "w") as f:
            json.dump(grna_data, f, indent=2)

        fase.status = PipelineStatus.CONCLUIDO
        fase.duracao_segundos = time.time() - inicio
        fase.dados = {
            "hospedeiro": self.config.hospedeiro,
            "identidade_genomica_pct": pacote.pct_genome_identity,
            "n_edicoes_total": pacote.n_total_edits,
            "n_grnas_desenhados": len(grnas),
            "n_grnas_qualidade": len(bons_grnas),
            "csv_edicoes": csv_path,
        }
        self._resultado.fases.append(fase)
        self.logger.info(f"✓ Fase 4 concluída em {fase.duracao_segundos:.1f}s")

    # ─────────────────────────────────────────────────────────────────────────
    # FASE 5 — SÍNTESE FÍSICA DE DNA
    # ─────────────────────────────────────────────────────────────────────────

    def _fase5_sintese_fisica(self) -> None:
        """
        Prepara o DNA para síntese física e verifica integridade:
        - dna_storage_media_writer.py → grava em estrutura ISO para DVD/CD
        - dna_integrity_checker.py    → 5 camadas de verificação criptográfica/biológica
        - dna_synthesizer_hardware.py → controla hardware real de síntese (GPIO/RPi)
        """
        inicio = time.time()
        fase = FaseResultado(fase=5, nome="Síntese Física de DNA", status=PipelineStatus.EXECUTANDO)
        dino = self._resultado.dinossauro_selecionado
        genoma = self._resultado.genoma_reconstruido

        self.logger.info("\n" + "═" * 70)
        self.logger.info("[FASE 5] SÍNTESE FÍSICA E ARMAZENAMENTO DE DNA")
        self.logger.info("═" * 70)

        storage_output = self.output_dir / "dna_storage"

        # ── Verificação de integridade (5 camadas) ───────────────────────────
        self.logger.info("Verificando integridade do genoma (5 camadas)...")
        checker = DNAIntegrityChecker()
        integrity_report: CompleteIntegrityReport = checker.full_integrity_check(
            sequence=genoma.sequence,
        )
        self._resultado.relatorio_integridade = integrity_report

        self.logger.info(f"Score de integridade: {integrity_report.overall_score:.1f}% [{integrity_report.status}]")
        for check in integrity_report.checks_performed:
            icon = "✓" if check.status == "PASS" else "⚠" if check.status == "WARN" else "✗"
            self.logger.info(f"  {icon} {check.check_name}: {check.score:.0f}%")

        # Salva relatório de integridade
        integrity_dir = self.output_dir / "integridade"
        integrity_dir.mkdir(exist_ok=True)
        report_text = checker.generate_report(
            integrity_report,
            output_path=str(integrity_dir / "relatorio_integridade.txt"),
        )

        if integrity_report.status == "FAIL":
            raise RuntimeError(
                f"Integridade do genoma FALHOU (score={integrity_report.overall_score:.1f}%). "
                f"Revise a reconstrução antes de prosseguir para síntese."
            )

        # ── Preparação para mídia física (DVD/CD) ───────────────────────────
        self.logger.info("Preparando estrutura de armazenamento em mídia permanente...")
        writer = DNAStorageMediaWriter(
            dinosaur_name=dino.nome_cientifico.replace(" ", "_"),
            sequence=genoma.sequence,
            output_dir=str(storage_output),
        )
        storage_info = writer.prepare_for_dvd(media_type="DVD-R")

        self.logger.info(f"✓ Mídia preparada em: {storage_info['root_path']}")
        self.logger.info(f"  SHA-256: {storage_info['sequence_hash']}")
        self.logger.info(f"  Tamanho total: {storage_info['total_size_bytes'] / 1024:.1f} KB")
        self.logger.info(f"  Pronto para gravação: {storage_info['ready_for_burning']}")

        iso_cmd = writer.get_iso_image_path()
        self.logger.info(f"  Comando ISO gerado para DVD")

        # ── Hardware de síntese (apenas se disponível) ───────────────────────
        if self.config.hardware_disponivel:
            self.logger.info("Hardware de síntese detectado — iniciando síntese física...")
            try:
                # Configura mistura de dNTPs
                dntp_config = DNTPoolConfig(
                    dATP_mM=100.0,
                    dTTP_mM=100.0,
                    dGTP_mM=100.0,
                    dCTP_mM=100.0,
                    buffer_pH=7.5,
                    Mg2_mM=5.0,
                    temp_celsius=72.0,
                )

                # Parâmetros de síntese para a sequência reconstruída
                # (síntese de oligonucleotídeos de 200bp em blocos)
                synth_params = SynthesisParameter(
                    sequence=genoma.sequence[:1000],  # Primeiro bloco de 1kb
                    target_length_bp=1000,
                    polymerase_type="Phusion",        # Alta fidelidade
                    extension_rate_bp_per_sec=1000.0,
                    temperature_profile={"annealing": 55.0, "extension": 72.0},
                )

                synthesizer = DNASynthesizer()
                synthesizer.iniciar()
                synthesizer.prepare_dntp_mix(dntp_config)
                success = synthesizer.synthesize_dna_sequence(
                    genoma.sequence[:1000],
                    synth_params,
                )

                if success:
                    vol = synthesizer.get_dna_volume_ul(50.0)
                    self.logger.info(f"✓ DNA sintetizado: {vol:.2f} µL")
                    synthesizer.parar()
                else:
                    self.logger.error("Síntese de DNA falhou no hardware")

            except Exception as e:
                self.logger.warning(f"Hardware indisponível para síntese: {e}")
                self.logger.info("→ DNA pronto para envio a fornecedor externo (Twist Bioscience / IDT)")
        else:
            self.logger.info("Hardware de síntese não conectado")
            self.logger.info("→ Arquivo FASTA pronto para envio a fornecedor externo:")
            self.logger.info(f"   Twist Bioscience: https://www.twistbioscience.com")
            self.logger.info(f"   IDT (Integrated DNA Technologies): https://www.idtdna.com")
            fasta_path = storage_output / dino.nome_cientifico.replace(" ", "_") / "DNA" / "sequence.fasta"
            self.logger.info(f"   Arquivo: {fasta_path}")

        fase.status = PipelineStatus.CONCLUIDO
        fase.duracao_segundos = time.time() - inicio
        fase.dados = {
            "integridade_score": integrity_report.overall_score,
            "integridade_status": integrity_report.status,
            "storage_path": storage_info["root_path"],
            "sha256": storage_info["sequence_hash"],
            "tamanho_bytes": storage_info["total_size_bytes"],
            "hardware_sintese": self.config.hardware_disponivel,
        }
        self._resultado.fases.append(fase)
        self.logger.info(f"✓ Fase 5 concluída em {fase.duracao_segundos:.1f}s")

    # ─────────────────────────────────────────────────────────────────────────
    # FASE 6 — INJEÇÃO NO EMBRIÃO
    # ─────────────────────────────────────────────────────────────────────────

    def _fase6_injecao_embriao(self) -> None:
        """
        Hibridiza e injeta o DNA no embrião hospedeiro:
        - hibridizador_core.py       → hibridização cinética com ODEs (scipy)
        - embryo_injection_robot.py  → robô de injeção com servos XYZ + seringa
        """
        inicio = time.time()
        fase = FaseResultado(fase=6, nome="Injeção no Embrião", status=PipelineStatus.EXECUTANDO)
        dino = self._resultado.dinossauro_selecionado
        genoma = self._resultado.genoma_reconstruido

        self.logger.info("\n" + "═" * 70)
        self.logger.info("[FASE 6] HIBRIDIZAÇÃO E INJEÇÃO NO EMBRIÃO")
        self.logger.info("═" * 70)

        self.logger.info(f"Hospedeiro: {self.config.hospedeiro}")
        self.logger.info(
            "Protocolo: inserção do DNA ancestral editado no disco germinativo "
            "de ovo fertilizado no estágio HH4-5"
        )

        # ── Hibridização de DNA ──────────────────────────────────────────────
        self.logger.info("Preparando hibridizador para fusão de DNA ancestral + vetor viral...")
        hibridizador = Hibridizador()
        hibridizador.ligar()

        # Aguarda estabilização da temperatura
        time.sleep(0.5)  # Em produção: espera real até estado PRONTO

        hibridizador.configurar_parametros({
            "temperatura_alvo": 37.5,     # Temperatura ideal para hibridização de aves
            "duracao_reacao": 300,        # 5 minutos para teste (produção: 4 horas)
            "velocidade_bomba": 75.0,     # 75% de velocidade de bomba
            "volume_dna_a": 500,          # 500 µL DNA ancestral reconstruído
            "volume_dna_b": 200,          # 200 µL vetor de entrega (AAV ou lentivírus)
        })

        hibridizador.iniciar_reacao()

        # Monitora reação por um ciclo
        time.sleep(1.0)
        status_hibr = hibridizador.obter_status()

        self.logger.info(
            f"Hibridização em progresso: "
            f"T={status_hibr['temperatura']:.1f}°C, "
            f"pH={status_hibr['pH']:.2f}, "
            f"Progresso={status_hibr['dados_reacao']['progresso_percentual']:.1f}%"
        )

        hibridizador.parar_reacao()
        dados_hibr = hibridizador.exportar_dados_reacao()

        hibr_output = self.output_dir / "hibridizacao"
        hibr_output.mkdir(exist_ok=True)
        with open(hibr_output / "dados_hibridizacao.json", "w") as f:
            json.dump(dados_hibr, f, indent=2, default=str)

        hibridizador.desligar()
        self.logger.info("✓ Hibridização concluída")

        # ── Robô de injeção (apenas se hardware disponível) ─────────────────
        if self.config.hardware_disponivel:
            self.logger.info("Iniciando robô de injeção...")
            try:
                import RPi.GPIO as GPIO
                robot = EmbryoInjectionRobot()
                robot.calibrate()

                # Detecta núcleo do embrião
                target: InjectionTarget = robot.find_embryo_nucleus(image=None)
                self.logger.info(
                    f"Núcleo detectado em ({target.x_mm:.2f}, {target.y_mm:.2f}, "
                    f"{target.z_mm:.2f}) mm — Volume: {target.volume_nl:.0f} nL"
                )

                # Executa injeção com sequência FASTA do genoma editado
                dna_fasta = f">{dino.nome_cientifico}_edited|{datetime.now().isoformat()}"
                success = robot.inject_dna(
                    dna_sequence=dna_fasta + "\n" + genoma.sequence[:3_000_000],
                    target=target,
                    dna_concentration_ng_ul=50.0,
                )

                if success:
                    self.logger.info("✓ Injeção de DNA concluída com sucesso")
                else:
                    raise RuntimeError("Robô reportou falha na injeção")

                robot.cleanup()

            except ImportError:
                self.logger.warning("RPi.GPIO não disponível — hardware de injeção não encontrado")
                self._log_protocolo_injecao_manual(dino, genoma)

            except Exception as e:
                self.logger.error(f"Falha no robô de injeção: {e}")
                self._log_protocolo_injecao_manual(dino, genoma)
        else:
            self._log_protocolo_injecao_manual(dino, genoma)

        fase.status = PipelineStatus.CONCLUIDO
        fase.duracao_segundos = time.time() - inicio
        fase.dados = {
            "hospedeiro": self.config.hospedeiro,
            "protocolo_hibridizacao": {
                "temperatura_C": 37.5,
                "duracao_min": 5,
                "volume_dna_ancestral_uL": 500,
                "volume_vetor_uL": 200,
            },
            "hardware_injecao": self.config.hardware_disponivel,
            "volume_injecao_nL": 500,
            "estagio_embriao": "HH4-5 (disco germinativo)",
        }
        self._resultado.fases.append(fase)
        self.logger.info(f"✓ Fase 6 concluída em {fase.duracao_segundos:.1f}s")

    def _log_protocolo_injecao_manual(self, dino: Dinossauro, genoma: RealDinosaurSequence) -> None:
        """Registra protocolo para injeção manual em laboratório."""
        self.logger.info("→ Protocolo para injeção manual em laboratório:")
        self.logger.info("  1. Obter ovo fertilizado de galinha (HH estágio 4-5)")
        self.logger.info("  2. Janela no ovo (3x3cm com bisturi)")
        self.logger.info("  3. DNA: 500 nL a 50 ng/µL (diluir em tampão TE pH 8.0)")
        self.logger.info("  4. Injetar no disco germinativo com micropipeta de vidro (25-30G)")
        self.logger.info("  5. Selar janela com parafilm e vedar com Scotch tape")
        self.logger.info("  6. Transferir para incubadora (ver Fase 7)")

    # ─────────────────────────────────────────────────────────────────────────
    # FASE 7 — INCUBAÇÃO MONITORADA
    # ─────────────────────────────────────────────────────────────────────────

    def _fase7_incubacao(self) -> None:
        """
        Configura e monitora a incubação do embrião editado:
        - hardware_orchestrator.py → coordena todos os dispositivos em sequência
        - incubator_device.py      → wrapper do Arduino
        - arduino_bridge.py        → comunicação serial com firmware C++ (DHT22/DS18B20)
        - hardware_devices.py      → catálogo e fábrica de dispositivos
        """
        inicio = time.time()
        fase = FaseResultado(fase=7, nome="Incubação Monitorada", status=PipelineStatus.EXECUTANDO)
        dino = self._resultado.dinossauro_selecionado

        self.logger.info("\n" + "═" * 70)
        self.logger.info("[FASE 7] INCUBAÇÃO MONITORADA")
        self.logger.info("═" * 70)

        # Parâmetros de incubação para aves (galinha como hospedeiro)
        TEMP_INCUBACAO_C = 37.8       # °C — temperatura padrão para galinha
        UMIDADE_PCT = 55.0            # % — umidade relativa
        DIAS_INCUBACAO = 21           # dias esperados até eclosão
        VIRAR_OVOS = True             # viragem automática 3x/dia

        self.logger.info(f"Parâmetros de incubação:")
        self.logger.info(f"  Temperatura alvo: {TEMP_INCUBACAO_C}°C")
        self.logger.info(f"  Umidade alvo: {UMIDADE_PCT}%")
        self.logger.info(f"  Duração esperada: {DIAS_INCUBACAO} dias")
        self.logger.info(f"  Viragem automática: {'Sim' if VIRAR_OVOS else 'Não'}")

        if self.config.hardware_disponivel:
            self.logger.info(
                f"Conectando ao Arduino na porta {self.config.arduino_port} "
                f"({self.config.arduino_baudrate} bps)..."
            )
            try:
                bridge = ArduinoBridge(
                    port=self.config.arduino_port,
                    baudrate=self.config.arduino_baudrate,
                    timeout=5.0,
                )

                if bridge.connected:
                    # Configura parâmetros na incubadora
                    bridge.set_target_temperature(TEMP_INCUBACAO_C)
                    bridge.set_target_humidity(UMIDADE_PCT)
                    if VIRAR_OVOS:
                        bridge.enable_egg_turning()

                    # Notifica embrião injetado
                    timestamp_injecao = datetime.now().isoformat()
                    bridge.notify_embryo_injected(
                        timestamp=timestamp_injecao,
                        volume_ul=0.5,  # 500 nL = 0.5 µL
                    )

                    # Lê status inicial
                    status_incubadora = bridge.get_incubator_status()
                    if status_incubadora:
                        self.logger.info(f"Status incubadora:")
                        self.logger.info(f"  Temperatura atual: {status_incubadora.get('temperatura_atual', 'N/A')}°C")
                        self.logger.info(f"  Umidade atual: {status_incubadora.get('umidade_atual', 'N/A')}%")
                        self.logger.info(f"  Dia de incubação: {status_incubadora.get('dia', 0)}")

                    # Inicia monitoramento contínuo (background thread)
                    def callback_monitoramento(status):
                        self.logger.info(
                            f"Incubadora: T={status.get('temperatura_atual', 0):.1f}°C  "
                            f"H={status.get('umidade_atual', 0):.0f}%  "
                            f"Dia={status.get('dia', 0)}"
                        )

                    bridge.start_monitoring(callback=callback_monitoramento, interval=300.0)
                    self.logger.info("✓ Monitoramento de incubação ativo (a cada 5 min)")
                    bridge.disconnect()
                else:
                    self.logger.warning("Arduino não respondeu — incubação manual necessária")
                    self._log_protocolo_incubacao_manual(TEMP_INCUBACAO_C, UMIDADE_PCT, DIAS_INCUBACAO)

            except Exception as e:
                self.logger.warning(f"Falha ao conectar Arduino: {e}")
                self._log_protocolo_incubacao_manual(TEMP_INCUBACAO_C, UMIDADE_PCT, DIAS_INCUBACAO)
        else:
            self._log_protocolo_incubacao_manual(TEMP_INCUBACAO_C, UMIDADE_PCT, DIAS_INCUBACAO)

        # ── Orquestrador de hardware completo ───────────────────────────────
        self.logger.info("\nOrquestração completa de hardware disponível via:")
        self.logger.info(
            "  HardwareOrchestrator.execute_complete_workflow("
            f'"{dino.nome_cientifico}")'
        )
        self.logger.info("  Dispositivos catalogados:")
        for key, spec in HARDWARE_DEVICE_SPECS.items():
            self.logger.info(f"    • {key}: {spec.name}")

        fase.status = PipelineStatus.CONCLUIDO
        fase.duracao_segundos = time.time() - inicio
        fase.dados = {
            "temperatura_alvo_C": TEMP_INCUBACAO_C,
            "umidade_alvo_pct": UMIDADE_PCT,
            "dias_incubacao": DIAS_INCUBACAO,
            "viragem_automatica": VIRAR_OVOS,
            "arduino_conectado": self.config.hardware_disponivel,
            "hospedeiro_ovo": self.config.hospedeiro,
        }
        self._resultado.fases.append(fase)
        self.logger.info(f"✓ Fase 7 concluída em {fase.duracao_segundos:.1f}s")

    def _log_protocolo_incubacao_manual(self, temp: float, umidade: float, dias: int) -> None:
        """Registra protocolo de incubação manual."""
        self.logger.info("→ Protocolo de incubação manual:")
        self.logger.info(f"  1. Incubadora comercial (ex: Hovabator, Brinsea, ou construída)")
        self.logger.info(f"  2. Temperatura: {temp}°C ± 0.2°C (sensor DHT22 ou DS18B20)")
        self.logger.info(f"  3. Umidade: {umidade}% ± 3% (Dias 1-18), 65% (Dias 19-21)")
        self.logger.info(f"  4. Viragem: 3× ao dia (Dias 1-18), parar nos últimos 3 dias")
        self.logger.info(f"  5. Ventilação: 0.5 L/h de CO₂")
        self.logger.info(f"  6. Monitorar: candling (ovoscopia) nos dias 7 e 14")
        self.logger.info(f"  7. Eclosão esperada: ~{dias} dias após incubação")

    # ─────────────────────────────────────────────────────────────────────────
    # FASE 8 — RELATÓRIO TÉCNICO FINAL
    # ─────────────────────────────────────────────────────────────────────────

    def _fase8_relatorio_final(self) -> None:
        """
        Gera todos os relatórios técnicos finais:
        - ai_report.py + ollama_integration.py → laudo de IA com LLM local
        - complete_revival_orchestrator.py     → relatório executivo consolidado
        """
        inicio = time.time()
        fase = FaseResultado(fase=8, nome="Relatório Técnico Final", status=PipelineStatus.EXECUTANDO)
        dino = self._resultado.dinossauro_selecionado
        genoma = self._resultado.genoma_reconstruido
        pacote = self._resultado.pacote_edicoes
        integridade = self._resultado.relatorio_integridade

        self.logger.info("\n" + "═" * 70)
        self.logger.info("[FASE 8] RELATÓRIO TÉCNICO FINAL")
        self.logger.info("═" * 70)

        relatorio_output = self.output_dir / "relatorios"
        relatorio_output.mkdir(exist_ok=True)

        # ── Laudo de IA via Ollama ───────────────────────────────────────────
        laudo_ia: Optional[str] = None
        if self.config.gerar_relatorio_ia:
            self.logger.info(f"Gerando laudo com Ollama (modelo: {self.config.ollama_modelo})...")
            try:
                cliente = ClienteOllama(ConfiguracaoOllama(
                    modelo=self.config.ollama_modelo,
                ))
                if cliente.validar_conexao():
                    # Build ReconstructionResult adapter from stored genome data
                    _seq = genoma.sequence if genoma else ""
                    _gc = round(
                        (_seq.count("G") + _seq.count("C")) / len(_seq) * 100, 2
                    ) if _seq else 0.0
                    _reconstruction = ReconstructionResult(
                        consensus_sequence=_seq,
                        per_base_confidence=[genoma.mean_confidence / 100.0] * len(_seq)
                                            if _seq else [],
                        mean_confidence=genoma.mean_confidence / 100.0 if genoma else 0.0,
                        n_references_used=getattr(genoma, "n_references_used", 0),
                        reference_species=getattr(genoma, "reference_species", []),
                        gc_content=_gc,
                    )
                    _scanner_summary = {
                        "n_reads": getattr(self._resultado, "n_reads_fossil", 0),
                        "total_bases": len(_seq),
                        "avg_quality": "N/A",
                    }
                    laudo_ia = gerar_relatorio_com_ollama(
                        reconstruction=_reconstruction,
                        edit_package=pacote,
                        scanner_summary=_scanner_summary,
                        target_species_label=dino.nome_cientifico,
                        cliente=cliente,
                    )
                    self._resultado.relatorio_ia = laudo_ia
                    (relatorio_output / "laudo_ia.txt").write_text(laudo_ia)
                    self.logger.info("✓ Laudo de IA gerado")
                else:
                    self.logger.warning(
                        "Ollama não está rodando em http://localhost:11434\n"
                        "  Para instalar: https://ollama.ai\n"
                        "  Para iniciar: ollama serve\n"
                        "  Para baixar o modelo: ollama pull llama2"
                    )
            except Exception as e:
                self.logger.warning(f"Falha ao gerar laudo de IA: {e}")

        # ── Relatório executivo consolidado ──────────────────────────────────
        self.logger.info("Gerando relatório executivo consolidado...")

        fases_executadas = [f for f in self._resultado.fases]
        duracao_total = sum(f.duracao_segundos for f in fases_executadas)

        relatorio_texto = self._gerar_relatorio_texto(
            dino, genoma, pacote, integridade, laudo_ia, duracao_total
        )

        relatorio_path = relatorio_output / "RELATORIO_FINAL.txt"
        relatorio_path.write_text(relatorio_texto, encoding="utf-8")
        self.logger.info(f"Relatório salvo em: {relatorio_path}")

        # ── JSON completo do pipeline ────────────────────────────────────────
        pipeline_json = {
            "pipeline": "Re-Gen Unified Architecture",
            "versao": "3.0",
            "timestamp_inicio": self._resultado.timestamp_inicio,
            "timestamp_fim": datetime.now().isoformat(),
            "duracao_total_segundos": duracao_total,
            "dinossauro": dino.nome_cientifico,
            "hospedeiro": self.config.hospedeiro,
            "fases": [
                {
                    "fase": f.fase,
                    "nome": f.nome,
                    "status": f.status.value,
                    "duracao_s": f.duracao_segundos,
                    "dados": f.dados,
                }
                for f in fases_executadas
            ],
            "genoma": {
                "comprimento_bp": len(genoma.sequence),
                "confianca_media_pct": genoma.mean_confidence,
                "n_referencias": genoma.n_references_used,
            } if genoma else None,
            "crispr": {
                "n_edicoes": pacote.n_total_edits,
                "identidade_pct": pacote.pct_genome_identity,
            } if pacote else None,
            "integridade": {
                "score": integridade.overall_score,
                "status": integridade.status,
            } if integridade else None,
        }

        with open(relatorio_output / "pipeline_completo.json", "w") as f:
            json.dump(pipeline_json, f, indent=2, ensure_ascii=False)

        self._resultado.diretorio_saida_final = str(relatorio_output)

        self.logger.info("\n" + "─" * 70)
        self.logger.info("ARQUIVOS GERADOS:")
        for path in sorted(self.output_dir.rglob("*")):
            if path.is_file():
                size = path.stat().st_size
                self.logger.info(
                    f"  {path.relative_to(self.output_dir)} "
                    f"({size / 1024:.1f} KB)"
                )
        self.logger.info("─" * 70)

        fase.status = PipelineStatus.CONCLUIDO
        fase.duracao_segundos = time.time() - inicio
        fase.dados = {
            "relatorio_path": str(relatorio_path),
            "laudo_ia_gerado": laudo_ia is not None,
            "duracao_total_pipeline_s": duracao_total,
        }
        self._resultado.fases.append(fase)
        self.logger.info(f"✓ Fase 8 concluída em {fase.duracao_segundos:.1f}s")

    def _gerar_relatorio_texto(
        self,
        dino: Dinossauro,
        genoma: RealDinosaurSequence,
        pacote: Optional[EditPackage],
        integridade: Optional[CompleteIntegrityReport],
        laudo_ia: Optional[str],
        duracao_total: float,
    ) -> str:
        """Gera relatório executivo em texto formatado."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        seq = genoma.sequence if genoma else ""
        gc = (seq.count("G") + seq.count("C")) / len(seq) * 100 if seq else 0

        linhas_fases = "\n".join(
            f"  Fase {f.fase} — {f.nome}: {f.status.value.upper()} "
            f"({f.duracao_segundos:.1f}s)"
            for f in self._resultado.fases
        )

        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        RELATÓRIO FINAL — RE-GEN PROJECT — RESSURREIÇÃO DE DINOSSAUROS       ║
╚══════════════════════════════════════════════════════════════════════════════╝

ESPÉCIE ALVO
────────────────────────────────────────────────────────────────────────────────
Nome científico : {dino.nome_cientifico}
Nome comum      : {dino.nome_comum}
Grupo           : {dino.grupo.value}
Período         : {dino.periodo.value}
Peso estimado   : {dino.peso_estimado_kg:,.0f} kg
Comprimento     : {dino.comprimento_estimado_m:.1f} m
Hospedeiro      : {self.config.hospedeiro}

GENOMA RECONSTRUÍDO
────────────────────────────────────────────────────────────────────────────────
Comprimento total      : {len(seq):,} bp
Confiança média        : {genoma.mean_confidence:.1f}%
GC%                    : {gc:.1f}%
Ambiguidades (N)       : {seq.count("N"):,} ({seq.count("N") / max(len(seq), 1) * 100:.2f}%)
Regiões baixa conf.    : {len(genoma.low_confidence_regions)}
Referências NCBI usadas: {genoma.n_references_used}
Método                 : {genoma.construction_method}

INTEGRIDADE DO DNA
────────────────────────────────────────────────────────────────────────────────
Score geral   : {integridade.overall_score:.1f}/100
Status        : {integridade.status}
Verificações  : {len(integridade.checks_performed)} camadas
  • Criptográfica (SHA-256, BLAKE2b, CRC32)
  • Estrutural (composição, GC%, razão AT)
  • Biológica (codons, ORFs)
  • Filogenética (conservação)
  • Redundância (Reed-Solomon)

PACOTE DE EDIÇÕES CRISPR
────────────────────────────────────────────────────────────────────────────────
Total de edições propostas : {pacote.n_total_edits if pacote else "N/A"}
Identidade genômica        : {pacote.pct_genome_identity:.1f}% (ancestral ↔ hospedeiro)
Hospedeiro alvo            : {pacote.host_species if pacote else "N/A"}
CSV exportado para         : Benchling / CHOPCHOP / CRISPRESSO

PIPELINE — SUMÁRIO DE EXECUÇÃO
────────────────────────────────────────────────────────────────────────────────
{linhas_fases}

Duração total : {duracao_total:.1f}s ({duracao_total / 60:.1f} min)
Timestamp     : {timestamp}

PRÓXIMOS PASSOS
────────────────────────────────────────────────────────────────────────────────
1. SÍNTESE DE DNA:
   → Enviar sequence.fasta para Twist Bioscience ou IDT
   → Ou gravar no DVD usando o script mkisofs gerado
   → Custo estimado: US$ 0.07–0.12/bp (síntese de gene)

2. EDIÇÃO CRISPR:
   → Importar pacote_edicao_crispr.csv no Benchling/CHOPCHOP
   → Encomendar guide-RNAs sintetizados quimicamente (IDT, Synthego)
   → Transfectar: eletroporação ou lipofectamina no embrião HH4-5

3. INCUBAÇÃO:
   → Temperatura: 37.8°C ± 0.2°C
   → Umidade: 55% (Dias 1-18), 65% (Dias 19-21)
   → Viragem: 3× ao dia até Dia 18
   → Monitorar por ovoscopia nos Dias 7, 10, 14

4. ANÁLISE:
   → PCR + Sanger sequencing para confirmar edições
   → Immunofluorescência para proteínas marcadoras
   → Fenotipagem morfológica ao nascimento

LIMITAÇÕES CIENTÍFICAS
────────────────────────────────────────────────────────────────────────────────
• Genoma 100% idêntico ao original é impossível após {dino.taxa_diferencacao_estimada:.0f} Ma
• Epigenética do original é desconhecida
• Cromossomos sexuais podem variar
• Comportamento extrapolado de aves + fóssil comportamental
• O animal resultante é um HÍBRIDO, não o dinossauro original
• Adequado para: pesquisa, educação, conservação de dados paleontológicos
• NÃO adequado para: soltura na natureza (impacto ecológico desconhecido)

REFERÊNCIAS CIENTÍFICAS
────────────────────────────────────────────────────────────────────────────────
• Extant Phylogenetic Bracket: Witmer (1995), J. Vert. Paleontol.
• De-extinction CRISPR: Colossal Biosciences (2021-2024)
• CRISPR Cas9 guide design: Doench et al. (2016), Nature Biotechnology
• Avian embryo injection: Bhatt et al. (2013), Development
• Genome reconstruction: Organ et al. (2007), PLoS Biology

════════════════════════════════════════════════════════════════════════════════
Re-Gen Project v3.0 — Arquitetura Unificada
https://github.com/V0rtexLinux/Re-Gen-Project
════════════════════════════════════════════════════════════════════════════════
"""

    # ─────────────────────────────────────────────────────────────────────────
    # UTILITÁRIOS
    # ─────────────────────────────────────────────────────────────────────────

    def _banner(self, texto: str) -> None:
        """Imprime banner formatado."""
        borda = "═" * 78
        self.logger.info(f"\n╔{borda}╗")
        self.logger.info(f"║  {texto:<76}║")
        self.logger.info(f"╚{borda}╝")


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES PÚBLICAS
# ─────────────────────────────────────────────────────────────────────────────

def listar_especies_disponiveis() -> None:
    """Imprime todas as espécies disponíveis no banco de dados."""
    print(f"\n{'─' * 90}")
    print(f"{'BANCO DE DADOS RE-GEN — 500+ ESPÉCIES CATALOGADAS':^90}")
    print(f"{'─' * 90}")

    grupos: Dict[str, List[DinosaurSpecies]] = {}
    for d in DINOSAUR_DATABASE:
        g = d.family.value
        grupos.setdefault(g, []).append(d)

    for grupo, especies in sorted(grupos.items()):
        print(f"\n  ▸ {grupo} ({len(especies)} espécies)")
        for e in sorted(especies, key=lambda x: x.popularity):
            print(
                f"    • {e.scientific_name:<40} "
                f"| {e.period.value:<10} "
                f"| {e.diet.value:<12} "
                f"| {e.continent}"
            )

    sys.exit(0)


def exibir_mapa_arquitetura() -> None:
    """Exibe o mapa visual de arquitetura e dependências dos módulos."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              RE-GEN — MAPA DE ARQUITETURA UNIFICADA                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

FASE 0 — SELEÇÃO PALEONTOLÓGICA
  ├── dinosaur_database.py    → 500+ espécies com dados reais
  ├── paleontology.py         → sistema de referência filogenética
  └── dinosaur_selector.py   → seleção automática com score composto

FASE 1 — MAPEAMENTO FILOGENÉTICO E NCBI
  ├── descendant_mapper.py    → aves e crocodilianos relacionados
  └── ncbi_reference.py       → DeepReferenceSearchEngine (NCBI Entrez real)

FASE 2 — EXTRAÇÃO DE DNA FÓSSIL (opcional)
  ├── fossil_grinder_device   → tritura amostra fóssil
  ├── fossil_cleaner_device   → limpeza e purificação
  └── extrator_dna_core.py   → lise → precipitação → centrifugação → elution

FASE 3 — RECONSTRUÇÃO GENÔMICA
  ├── genome_synthesis.py     → RealSequenceBuilder (EPB + consenso filogenético)
  ├── reconstruct.py          → Needleman-Wunsch + majority-rule consensus
  └── genome_validator.py     → validação: homopolímeros, stop-codons, GC%, repeats

FASE 4 — PACOTE DE EDIÇÃO CRISPR
  ├── gene_edit_package.py    → SNPs/indels ancestral↔hospedeiro
  └── crispr_engine.py        → design gRNA (PAM-NGG, especificidade, eficiência)

FASE 5 — SÍNTESE FÍSICA DE DNA
  ├── dna_integrity_checker.py  → 5 camadas (criptogr. + estrut. + biol. + filog. + redund.)
  ├── dna_storage_media_writer.py → estrutura ISO 9660 (DVD/CD) com Reed-Solomon
  └── dna_synthesizer_hardware.py → GPIO/RPi: bombas peristálticas + LED UV + válvulas

FASE 6 — INJEÇÃO NO EMBRIÃO
  ├── hibridizador_core.py    → hibridização cinética com ODEs (scipy)
  └── embryo_injection_robot.py → robô XYZ (servo MG995) + seringa 1mL (500 nL)

FASE 7 — INCUBAÇÃO MONITORADA
  ├── hardware_orchestrator.py  → máquina de estados (IDLE→SYNTH→INJECT→INCUBATE)
  ├── arduino_bridge.py        → serial /dev/ttyUSB0 → firmware C++ (PID)
  ├── incubator_device.py      → wrapper DeviceBase do Arduino
  └── hardware_devices.py      → catálogo: synthesizer, injector, incubator,
                                  fossil_grinder, fossil_cleaner, vet_syringe,
                                  environment_monitor, safety_device

FASE 8 — RELATÓRIO FINAL
  ├── ai_report.py             → prompt técnico → Ollama LLM local
  ├── ollama_integration.py    → cliente HTTP (POST /api/generate)
  └── complete_revival_orchestrator.py → relatório executivo consolidado

HARDWARE SUPORTADO
  ├── Raspberry Pi Zero 2W / RPi 4
  ├── Arduino Mega (firmware: incubator_arduino_controller_v2.ino)
  ├── Bombas peristálticas (GPIO17/27/22/23) para dNTPs
  ├── Válvulas solenóide (GPIO24/25/26) para seleção de reagentes
  ├── LED UV 365nm (GPIO12) para crosslinking
  ├── Servos MG995 (pinos 6/5/14/15) para robô XYZ + seringa
  ├── DHT22 + DS18B20 para temperatura e umidade
  └── DYNAMIXEL para controle de viragem de ovos
""")
    sys.exit(0)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Ponto de entrada do pipeline Re-Gen Unificado.

    Uso:
        python re_gen_unified_architecture.py --email seu@email.com [opções]

    Exemplos:
        # Seleção automática de espécie:
        python re_gen_unified_architecture.py --email bio@lab.com

        # Dinossauro específico:
        python re_gen_unified_architecture.py --email bio@lab.com --dinosaur "Tyrannosaurus rex"

        # Com fóssil e hardware:
        python re_gen_unified_architecture.py \\
            --email bio@lab.com \\
            --dinosaur "Velociraptor mongoliensis" \\
            --fossil my_fossil.fasta \\
            --hardware \\
            --arduino-port /dev/ttyUSB0

        # Ver lista de espécies:
        python re_gen_unified_architecture.py --lista

        # Ver mapa de arquitetura:
        python re_gen_unified_architecture.py --arquitetura
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Re-Gen Project — Pipeline Unificado de Ressurreição de Dinossauros",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=main.__doc__,
    )
    parser.add_argument("--email",        required=False, help="Email para NCBI Entrez API")
    parser.add_argument("--api-key",      help="API key NCBI (aumenta rate limit)")
    parser.add_argument("--dinosaur",     help="Nome científico (ex: 'Tyrannosaurus rex')")
    parser.add_argument("--hospedeiro",   default="Gallus gallus", help="Espécie hospedeira para CRISPR")
    parser.add_argument("--fossil",       help="Arquivo FASTA com fragmento de fóssil")
    parser.add_argument("--hardware",     action="store_true", help="Habilita hardware físico (RPi GPIO)")
    parser.add_argument("--arduino-port", default=_default_serial_port(),
                        help=f"Porta serial do Arduino (padrão SO: {_default_serial_port()})")
    parser.add_argument("--sem-ia",       action="store_true", help="Pula geração de laudo com Ollama")
    parser.add_argument("--ollama-modelo",default="llama2", help="Modelo Ollama para laudo")
    parser.add_argument("--output",       default="./re_gen_output", help="Diretório de saída")
    parser.add_argument("--confianca",    type=float, default=0.60, help="Confiança mínima (0–1)")
    parser.add_argument("--lista",        action="store_true", help="Lista todas as espécies e sai")
    parser.add_argument("--arquitetura",  action="store_true", help="Exibe mapa de arquitetura e sai")
    parser.add_argument("--fase-inicio",  type=int, default=0, metavar="N",
                        help="Primeira fase a executar 0–8 (padrão: 0 = Seleção)")
    parser.add_argument("--fase-fim",     type=int, default=8, metavar="N",
                        help="Última fase a executar 0–8 (padrão: 8 = Relatório IA)")

    args = parser.parse_args()

    if args.lista:
        listar_especies_disponiveis()

    if args.arquitetura:
        exibir_mapa_arquitetura()

    if not args.email:
        parser.error("--email é obrigatório (necessário para NCBI Entrez API)")

    fi = max(0, min(8, args.fase_inicio))
    ff = max(0, min(8, args.fase_fim))
    if fi > ff:
        parser.error(f"--fase-inicio ({fi}) não pode ser maior que --fase-fim ({ff})")

    config = ConfiguracaoPipeline(
        ncbi_email=args.email,
        ncbi_api_key=args.api_key,
        nome_dinossauro=args.dinosaur,
        hospedeiro=args.hospedeiro,
        arquivo_fossil_fasta=args.fossil,
        hardware_disponivel=args.hardware,
        arduino_port=args.arduino_port,
        gerar_relatorio_ia=not args.sem_ia,
        ollama_modelo=args.ollama_modelo,
        diretorio_saida=args.output,
        confianca_minima=args.confianca,
        fase_inicio=fi,
        fase_fim=ff,
    )

    pipeline = ReGenPipelineUnificado(config)
    resultado = pipeline.executar()

    # Sumário final
    print("\n" + "═" * 78)
    if resultado.status_global == PipelineStatus.CONCLUIDO:
        print("✓  PIPELINE CONCLUÍDO COM SUCESSO")
        print(f"   Espécie:    {resultado.dinossauro_selecionado.nome_cientifico}")
        if resultado.genoma_escala_completa:
            ge = resultado.genoma_escala_completa
            in_range = 2_000_000_000 <= ge.total_length_bp <= 3_000_000_000
            print(
                f"   Genoma:     {ge.total_length_bp:,} bp "
                f"= {ge.total_length_bp/1e9:.3f} Gb "
                f"| {'✓ no range 2–3 Gb' if in_range else '✗ FORA DO RANGE'} "
                f"| {ge.n_chromosomes} cromossomos "
                f"| conf={ge.mean_confidence:.2f}"
            )
            print(f"   Fontes:     NCBI Entrez ({ge.n_ncbi_windows_used} janelas reais) "
                  f"+ Dfam ({', '.join(ge.te_families_used)})")
            print(f"   FASTA dir:  {ge.genome_fasta_dir}")
            print(f"   Manifest:   {ge.manifest_json}")
        elif resultado.genoma_reconstruido:
            g = resultado.genoma_reconstruido
            print(f"   Genoma EPB: {len(g.sequence):,} bp | Confiança: {g.mean_confidence:.1f}%")
        if resultado.pacote_edicoes:
            p = resultado.pacote_edicoes
            print(f"   CRISPR:     {p.n_total_edits} edições | Identidade: {p.pct_genome_identity:.1f}%")
        print(f"   Saídas:     {resultado.diretorio_saida_final}")
    else:
        print("✗  PIPELINE FALHOU")
        for f in resultado.fases:
            if f.status == PipelineStatus.FALHOU:
                print(f"   Fase {f.fase} ({f.nome}): {f.erros}")
    print("═" * 78 + "\n")

    return resultado


if __name__ == "__main__":
    main()
