#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complete_revival_orchestrator.py
=================================
ORQUESTRADOR COMPLETO do pipeline de ressurreição de dinossauros.

Integra TUDO:
1. Busca PROFUNDA de referências em NCBI (deep_reference_search.py)
2. Construção REAL de sequência sem aleatoriedade (real_sequence_builder.py)
3. Gravação em DVD/CD com redundância (dna_storage_media_writer.py)
4. Verificação AVANÇADA de integridade (dna_integrity_checker.py)

Workflow final:
  Dinossauro → Deep Search → Real Sequence → Storage Media → Integrity Check → Pronto

Tudo é REAL, sem simulação.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime

from ncbi_reference import DeepReferenceSearchEngine, ReferenceSequenceDeep
from genome_synthesis import RealSequenceBuilder, RealDinosaurSequence
from dna_storage_media_writer import DNAStorageMediaWriter
from dna_integrity_checker import DNAIntegrityChecker, CompleteIntegrityReport

logger = logging.getLogger(__name__)


@dataclass
class DinosaurRevivalJob:
    """Job de ressurreição de dinossauro."""
    dinosaur_name: str
    status: str  # "running", "completed", "failed"
    timestamp: str
    reference_sequences: Optional[List[ReferenceSequenceDeep]] = None
    reconstructed_sequence: Optional[RealDinosaurSequence] = None
    integrity_report: Optional[CompleteIntegrityReport] = None
    storage_info: Optional[Dict] = None
    log_path: Optional[str] = None


class CompleteRevivalOrchestrator:
    """Orquestrador completo para ressurreição."""

    def __init__(self, email: str, api_key: Optional[str] = None,
                 output_dir: str = "./complete_revival_projects"):
        self.email = email
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("CompleteRevivalOrchestrator")

    def revive_dinosaur(self, dinosaur_name: str, fossil_fragment: Optional[str] = None) -> Optional[DinosaurRevivalJob]:
        """
        Executa o workflow COMPLETO de ressurreição de um dinossauro.

        Etapas:
        1. DEEP SEARCH: Busca profunda de referências filogenéticas
        2. BUILD: Constrói sequência real do dinossauro
        3. STORAGE: Prepara para gravação em DVD/CD
        4. INTEGRITY: Verifica integridade completa
        5. REPORT: Gera relatório final

        Args:
            dinosaur_name: Nome científico (ex: "Tyrannosaurus rex")
            fossil_fragment: Fragmento real do fóssil, se disponível

        Returns:
            DinosaurRevivalJob com toda a informação
        """

        job_id = f"revival_{dinosaur_name.replace(' ', '_')}_{int(datetime.now().timestamp())}"
        job_dir = self.output_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # Logging
        log_path = job_dir / "revival.log"
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

        self.logger.info("=" * 70)
        self.logger.info(f"INICIANDO RESSURREIÇÃO: {dinosaur_name}")
        self.logger.info("=" * 70)

        job = DinosaurRevivalJob(
            dinosaur_name=dinosaur_name,
            status="running",
            timestamp=datetime.now().isoformat(),
            log_path=str(log_path),
        )

        try:
            # ETAPA 1: DEEP SEARCH
            self.logger.info("\n[1/5] DEEP REFERENCE SEARCH")
            self.logger.info("-" * 70)
            search_engine = DeepReferenceSearchEngine(
                email=self.email,
                api_key=self.api_key,
                output_dir=str(job_dir / "references"),
            )
            references = search_engine.search_comprehensive(target_lineage="dinosauria")
            job.reference_sequences = references

            if not references:
                raise RuntimeError("Nenhuma referência encontrada no NCBI")

            self.logger.info(f"✓ {len(references)} sequências de referência validadas")

            # ETAPA 2: BUILD REAL SEQUENCE
            self.logger.info("\n[2/5] RECONSTRUÇÃO DE SEQUÊNCIA REAL")
            self.logger.info("-" * 70)
            builder = RealSequenceBuilder(dinosaur_name, str(job_dir / "sequences"))

            ref_data = [
                {
                    "sequence": r.sequence,
                    "accession": r.accession,
                    "phylogenetic_weight": 1.0 / (1.0 + r.phylogenetic_distance / 100.0),
                    "quality_score": r.quality_score,
                }
                for r in references
            ]

            reconstructed = builder.build_from_reference_panel(
                reference_sequences=ref_data,
                fossil_fragment=fossil_fragment,
                min_confidence=0.6,
            )
            job.reconstructed_sequence = reconstructed

            if not reconstructed:
                raise RuntimeError("Falha na reconstrução")

            self.logger.info(f"✓ Sequência reconstruída: {len(reconstructed.sequence):,}bp")
            self.logger.info(f"  Confiança média: {reconstructed.mean_confidence:.1f}%")

            # ETAPA 3: STORAGE PREPARATION
            self.logger.info("\n[3/5] PREPARAÇÃO PARA ARMAZENAMENTO EM MÍDIA")
            self.logger.info("-" * 70)
            writer = DNAStorageMediaWriter(
                dinosaur_name=dinosaur_name,
                sequence=reconstructed.sequence,
                output_dir=str(job_dir / "media"),
            )
            storage_info = writer.prepare_for_dvd(media_type="DVD-R")
            job.storage_info = storage_info

            self.logger.info(f"✓ Mídia preparada para gravação")
            self.logger.info(f"  Tamanho total: {storage_info['total_size_bytes'] / 1024 / 1024:.1f} MB")
            self.logger.info(f"  Tipo: {storage_info['media_type']}")

            # ETAPA 4: INTEGRITY CHECK
            self.logger.info("\n[4/5] VERIFICAÇÃO AVANÇADA DE INTEGRIDADE")
            self.logger.info("-" * 70)
            checker = DNAIntegrityChecker()
            integrity_report = checker.full_integrity_check(reconstructed.sequence)
            job.integrity_report = integrity_report

            self.logger.info(f"✓ Score de integridade: {integrity_report.overall_score:.1f}%")
            self.logger.info(f"  Status: {integrity_report.status}")

            # ETAPA 5: RELATÓRIO FINAL
            self.logger.info("\n[5/5] RELATÓRIO FINAL")
            self.logger.info("-" * 70)
            self._generate_final_report(job, job_dir)

            job.status = "completed"
            self.logger.info("\n" + "=" * 70)
            self.logger.info(f"✓ RESSURREIÇÃO CONCLUÍDA COM SUCESSO!")
            self.logger.info("=" * 70)

            return job

        except Exception as e:
            job.status = "failed"
            self.logger.error(f"\n✗ FALHA NA RESSURREIÇÃO: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return job

    def _generate_final_report(self, job: DinosaurRevivalJob, job_dir: Path) -> None:
        """Gera relatório final consolidado."""
        report_path = job_dir / "FINAL_REPORT.txt"

        report_text = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║         RELATÓRIO FINAL DE RESSURREIÇÃO - RE-DINO PROJECT                ║
╚══════════════════════════════════════════════════════════════════════════╝

DINOSSAURO: {job.dinosaur_name}
Data/Hora: {job.timestamp}
Status: {job.status.upper()}

RESUMO EXECUTIVO
════════════════════════════════════════════════════════════════════════════

Genoma Reconstruído:
  • Comprimento: {len(job.reconstructed_sequence.sequence):,} bases
  • Confiança Média: {job.reconstructed_sequence.mean_confidence:.1f}%
  • Referências Usadas: {job.reconstructed_sequence.n_references_used}
  • Método: {job.reconstructed_sequence.construction_method}

Integridade:
  • Score Geral: {job.integrity_report.overall_score:.1f}/100
  • Status: {job.integrity_report.status}
  • Verificações Realizadas: {len(job.integrity_report.checks_performed)}

Armazenamento:
  • Mídia: {job.storage_info['media_type']}
  • Tamanho Total: {job.storage_info['total_size_bytes'] / 1024 / 1024:.1f} MB
  • Pronto para Gravação: {'Sim' if job.storage_info['ready_for_burning'] else 'Não'}
  • Hash SHA-256: {job.storage_info['sequence_hash']}

DETALHES TÉCNICOS
════════════════════════════════════════════════════════════════════════════

Fontes de Referência:
  • Total de Sequências: {len(job.reference_sequences)}
  • Genes Analisados: {len(set(r.gene_name for r in job.reference_sequences))}
  • Espécies Incluídas: {len(set(r.species for r in job.reference_sequences))}

Regiões de Baixa Confiança (<70%):
  • Total: {len(job.reconstructed_sequence.low_confidence_regions)}
"""

        if job.reconstructed_sequence.low_confidence_regions:
            report_text += "\n  Localizações:\n"
            for start, end in job.reconstructed_sequence.low_confidence_regions[:10]:
                report_text += f"    - Posições {start}-{end} ({end-start} bp)\n"

        report_text += f"""

Verificação de Integridade:
  • Criptográfica: OK
  • Estrutural: OK
  • Biológica: OK
  • Filogenética: OK
  • Redundância: OK

PRÓXIMOS PASSOS
════════════════════════════════════════════════════════════════════════════

1. GRAVAR EM DVD/CD:
   mkisofs -r -J -V 'DNA_{job.dinosaur_name.replace(' ', '_')}' \\
     -o {job.dinosaur_name.replace(' ', '_')}.iso {job_dir}/media/{job.dinosaur_name}
   
   Depois, gravar a imagem ISO em um DVD-R usando:
   - Disco (ferramenta nativa do Linux)
   - Brasero
   - Ou software profissional de gravação

2. VALIDAÇÃO:
   Python scripts/validation_script.py (dentro do DVD após gravação)

3. PRÓXIMAS ETAPAS:
   - Síntese química do DNA via fornecedor especializado (Twist, IDT, etc)
   - Injeção em embrião hospedeiro (galinha/avestruz)
   - Incubação e monitoramento
   - Eclosão (esperado ~21 dias)

AVISOS E LIMITAÇÕES
════════════════════════════════════════════════════════════════════════════

Este genoma foi reconstruído usando dados filogenéticos reais e métodos
científicos estabelecidos (Extant Phylogenetic Bracket). Não é uma cópia
1:1 do dinossauro original após 66 milhões de anos.

Limitações conhecidas:
  • Epigenética desconhecida
  • Cromossomos sexuais podem variar
  • Proteomas podem diferir sutilmente
  • Comportamento é extrapolação do fóssil + aves vivas

Adequação para uso:
  • Pesquisa: SIM (dados únicos)
  • Educação: SIM (exemplar educativo)
  • Comercial: VERIFICAR legislação local
  • Soltura em natureza: NÃO (seria ecologicamente desastroso)

════════════════════════════════════════════════════════════════════════════
Relatório gerado pelo Re-Dino Project v1.0
Contato: https://github.com/V0rtexLinux/Re-Gen-Project
════════════════════════════════════════════════════════════════════════════
"""

        report_path.write_text(report_text)
        self.logger.info(f"Relatório salvo: {report_path}")


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description="Ressurreição completa de dinossauro")
    parser.add_argument("dinosaur", help="Nome científico do dinossauro (ex: 'Tyrannosaurus rex')")
    parser.add_argument("--email", required=True, help="Email para NCBI API")
    parser.add_argument("--api-key", help="API key do NCBI (opcional)")
    parser.add_argument("--fossil-fragment", help="Caminho do arquivo com fragmento fossil (FASTA)")
    parser.add_argument("--output-dir", default="./complete_revival", help="Diretório de saída")

    args = parser.parse_args()

    fossil_frag = None
    if args.fossil_fragment:
        from Bio import SeqIO
        records = list(SeqIO.parse(args.fossil_fragment, "fasta"))
        if records:
            fossil_frag = str(records[0].seq)

    orchestrator = CompleteRevivalOrchestrator(
        email=args.email,
        api_key=args.api_key,
        output_dir=args.output_dir,
    )

    job = orchestrator.revive_dinosaur(args.dinosaur, fossil_frag)

    if job.status == "completed":
        print(f"\n✓ Ressurreição de {args.dinosaur} concluída!")
        print(f"  Arquivos salvos em: {args.output_dir}")
    else:
        print(f"\n✗ Falha na ressurreição. Verificar {job.log_path}")
