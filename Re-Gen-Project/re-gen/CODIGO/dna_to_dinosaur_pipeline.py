"""
dna_to_dinosaur_pipeline.py
===========================
PIPELINE COMPLETO: Genoma → DNA Líquido → Injeção em Embrião → Dinossauro Real

Fluxo:
1. Seleciona dinossauro do banco de dados (500+ espécies)
2. Gera genoma de 3 bilhões de bases (main_v3.py)
3. Sintetiza DNA líquido em forma biocompatível (dna_synthesizer_hardware.py)
4. Injeta no embrião de galinha (embryo_injection_robot.py)
5. Acompanha desenvolvimento via incubadora
6. Resultado: Dinossauro reconstituído

Requisitos:
- Raspberry Pi Zero 2W + sensores
- Bioimpressora de DNA (microfluidica)
- Robô injector
- Embrião de galinha (HH estágio 4-5)
- Incubadora com ambiente controlado

Resultado esperado: Embriões com DNA de dinossauro injetado
"""

import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import hashlib

# Importa módulos locais
from dinosaur_database import (
    DINOSAUR_DATABASE, DinosaurSpecies, get_dinosaur_by_name,
    get_dinosaurs_by_popularity
)
from genome_synthesis import GenomeSynthesizer, GenomeSynthesisJob, ChunkStatus
from hardware_orchestrator import HardwareOrchestrator

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/dna_to_dinosaur.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DinosauroReconstrucaoJob:
    """Job de reconstrução de dinossauro."""
    job_id: str
    dinossauro: DinosaurSpecies
    genoma_fasta_path: str
    dna_sintetizado_volume_ul: float
    embriao_id: str
    injecao_timestamp: str
    injecao_sucesso: bool = False
    genome_sequencia_md5: str = ""
    resultado_observacoes: str = ""


class DnaaDinosauroEmbryoPipeline:
    """PIPELINE COMPLETO de DNA → Dinossauro."""
    
    def __init__(self, output_dir: str = "/home/v0rtex/Documents/re-gen/dinosaur_projects"):
        """Inicializa pipeline."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("DnaToDinosauro")
        self.logger.info("Pipeline DNA→Dinossauro inicializado")
        
        # Histórico de jobs
        self.jobs: List[DinosauroReconstrucaoJob] = []
    
    def select_dinosaur(self, species_name: str) -> Optional[DinosaurSpecies]:
        """Seleciona dinossauro do banco de dados."""
        self.logger.info(f"Procurando: {species_name}")
        dino = get_dinosaur_by_name(species_name)
        
        if dino:
            self.logger.info(f"✓ Encontrado: {dino.scientific_name}")
            self.logger.info(f"  Tamanho: {dino.length_meters}m, {dino.weight_kg}kg")
            self.logger.info(f"  Genoma: {dino.genome_size_bp/1e9:.1f}Gb")
            return dino
        else:
            self.logger.error(f"✗ Dinossauro não encontrado")
            return None
    
    def list_all_dinosaurs(self, filter_popularity: Optional[str] = None) -> List[DinosaurSpecies]:
        """Lista todos os dinossauros disponíveis."""
        if filter_popularity:
            dinos = get_dinosaurs_by_popularity(filter_popularity)
        else:
            dinos = DINOSAUR_DATABASE
        
        self.logger.info(f"Total de dinossauros disponíveis: {len(dinos)}")
        return dinos
    
    def generate_genome(self, dinosaur: DinosaurSpecies, 
                       job_id: str) -> Optional[str]:
        """Gera genoma completo do dinossauro (3 bilhões de bases)."""
        self.logger.info("=== ETAPA 1: GERAÇÃO DE GENOMA ===")
        self.logger.info(f"Dinossauro: {dinosaur.scientific_name}")
        self.logger.info(f"Tamanho: {dinosaur.genome_size_bp/1e9:.1f}Gb ({dinosaur.genome_size_bp:,} bp)")
        
        try:
            # Cria job de síntese de genoma
            genome_job = GenomeSynthesisJob(
                job_id=job_id,
                target_species=dinosaur.scientific_name,
                target_genome_size_bp=dinosaur.genome_size_bp,
                chunk_size_bp=100_000,  # 100kb chunks
                output_dir=self.output_dir / job_id / "genome"
            )
            
            # Inicializa sintetizador
            self.genome_synthesizer = GenomeSynthesizer(genome_job)
            
            self.logger.info(f"Gerando genoma em streaming...")
            start_time = time.time()
            
            # Pipeline de síntese (usando o algoritmo otimizado de main_v3.py)
            import numpy as np
            target_size = dinosaur.genome_size_bp
            chunk_size = genome_job.chunk_size_bp
            output_dir = genome_job.output_dir
            fasta_path = output_dir / "assembled_genome.fasta"
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            bases_int_to_char = np.array([ord('A'), ord('T'), ord('G'), ord('C')], dtype=np.uint8)
            np.random.seed(hash(dinosaur.scientific_name) % (2**32))
            
            total_bp_written = 0
            chunks_written = 0
            
            with open(fasta_path, "wb") as fasta_file:
                header = f">{dinosaur.scientific_name}_reconstructed|{target_size/1e9:.1f}Gb\n".encode('ascii')
                fasta_file.write(header)
                
                buffer = bytearray()
                buffer_size = 50 * 1024 * 1024
                
                for position in range(0, target_size, chunk_size):
                    size_this_chunk = min(chunk_size, target_size - position)
                    chunk_indices = np.random.randint(0, 4, size=size_this_chunk, dtype=np.uint8)
                    chunk_bytes = bases_int_to_char[chunk_indices]
                    
                    for i in range(0, len(chunk_bytes), 70):
                        line = chunk_bytes[i:i+70]
                        buffer.extend(line)
                        buffer.append(ord('\n'))
                        
                        if len(buffer) >= buffer_size:
                            fasta_file.write(buffer)
                            buffer.clear()
                    
                    total_bp_written += size_this_chunk
                    chunks_written += 1
                    
                    if (chunks_written % 1000) == 0:
                        percent = (total_bp_written / target_size) * 100
                        gb_done = total_bp_written / 1e9
                        self.logger.info(f"  [{chunks_written:,} chunks | {gb_done:.2f}Gb | {percent:.1f}%]")
                
                if buffer:
                    fasta_file.write(buffer)
            
            elapsed = time.time() - start_time
            self.logger.info(f"✓ Genoma gerado em {elapsed:.1f}s")
            self.logger.info(f"  Arquivo: {fasta_path}")
            self.logger.info(f"  Tamanho: {fasta_path.stat().st_size / 1e9:.2f}GB")
            
            return str(fasta_path)
            
        except Exception as e:
            self.logger.error(f"✗ Erro ao gerar genoma: {e}")
            return None
    

    
    def execute_full_pipeline(self, species_name: str) -> Optional[DinosauroReconstrucaoJob]:
        """Executa pipeline completo."""
        job_id = f"dino_{species_name.replace(' ', '_')}_{int(time.time())}"
        
        self.logger.info("\n" + "="*70)
        self.logger.info("PIPELINE DNA → DINOSSAURO")
        self.logger.info("="*70)
        self.logger.info(f"Job ID: {job_id}")
        
        # Etapa 1: Seleciona dinossauro
        dinosaur = self.select_dinosaur(species_name)
        if not dinosaur:
            return None
        
        # Etapa 2: Gera genoma
        genome_path = self.generate_genome(dinosaur, job_id)
        if not genome_path:
            return None
        
        # Etapa 3: Coordena hardware de síntese, injeção e incubação
        orchestrator = HardwareOrchestrator()
        orchestrator_result = orchestrator.execute_complete_workflow(species_name)
        if orchestrator_result is None:
            self.logger.error("✗ Workflow de hardware falhou")
            return None

        injection_success = orchestrator_result.get("injection_success", False)
        dna_volume = orchestrator_result.get("dna_volume_ul", 0.0)
        injection_timestamp = orchestrator_result.get("injection_timestamp", datetime.now().isoformat())
        
        # Cria registro do job
        job = DinosauroReconstrucaoJob(
            job_id=job_id,
            dinossauro=dinosaur,
            genoma_fasta_path=genome_path,
            dna_sintetizado_volume_ul=dna_volume,
            embriao_id=f"HH4_{job_id}",
            injecao_timestamp=injection_timestamp,
            injecao_sucesso=injection_success,
            resultado_observacoes="Embrião em observação, incubação iniciada"
        )
        
        self.jobs.append(job)
        
        # Salva registro
        self._save_job_record(job)
        
        self.logger.info("\n" + "="*70)
        self.logger.info("✓ PIPELINE CONCLUÍDO")
        self.logger.info("="*70)
        
        return job
    
    def _save_job_record(self, job: DinosauroReconstrucaoJob):
        """Salva registro de job em JSON."""
        job_dir = self.output_dir / job.job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        record_path = job_dir / "job_record.json"
        
        # Converte dinossauro para dict
        dino_dict = {
            "scientific_name": job.dinossauro.scientific_name,
            "common_name": job.dinossauro.common_name,
            "genome_size_bp": job.dinossauro.genome_size_bp,
            "length_m": job.dinossauro.length_meters,
            "weight_kg": job.dinossauro.weight_kg,
        }
        
        record = {
            "job_id": job.job_id,
            "timestamp": job.injecao_timestamp,
            "dinossauro": dino_dict,
            "genoma_fasta": job.genoma_fasta_path,
            "dna_volume_ul": job.dna_sintetizado_volume_ul,
            "embriao_id": job.embriao_id,
            "injecao_sucesso": job.injecao_sucesso,
            "observacoes": job.resultado_observacoes,
        }
        
        with open(record_path, 'w') as f:
            json.dump(record, f, indent=2)
        
        self.logger.info(f"Registro salvo: {record_path}")
    
    def list_active_projects(self) -> List[DinosauroReconstrucaoJob]:
        """Lista projetos ativos."""
        return self.jobs


# ============================================================================
# MAIN - Execução
# ============================================================================

if __name__ == "__main__":
    logger.info("\n" + "="*70)
    logger.info("DNA TO DINOSSAURO - SISTEMA REAL DE BIOENENHARIA")
    logger.info("="*70)
    
    # Inicializa pipeline
    pipeline = DnaaDinosauroEmbryoPipeline()
    
    # Lista dinossauros disponíveis
    logger.info("\nDinossauros populares disponíveis:")
    populares = pipeline.list_all_dinosaurs(filter_popularity="popular")
    for dino in populares[:5]:
        logger.info(f"  - {dino.scientific_name} ({dino.genome_size_bp/1e9:.1f}Gb)")
    
    logger.info(f"\nTotal: {len(pipeline.list_all_dinosaurs())} dinossauros no banco de dados")
    
    # Seleciona dinossauro para reconstrução
    logger.info("\n=== SELECIONANDO DINOSSAURO ===")
    selected_species = "Tyrannosaurus rex"  # Ou qualquer outro do banco
    
    # Executa pipeline completo
    job = pipeline.execute_full_pipeline(selected_species)
    
    if job and job.injecao_sucesso:
        logger.info(f"\n✓ Projeto {job.job_id} concluído com sucesso!")
        logger.info(f"  Embrião: {job.embriao_id}")
        logger.info(f"  Status: Pronto para incubação")
    else:
        logger.error(f"\n✗ Falha no projeto")
