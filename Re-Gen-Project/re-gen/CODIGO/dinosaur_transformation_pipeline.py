"""
dinosaur_transformation_pipeline.py
====================================
Pipeline Completo: Genoma → Síntese DNA → Injeção → Dinossauro

Fluxo completo de transformação de uma galinha em dinossauro.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import json
from datetime import datetime

from dinosaur_database import DinosaurSpecies, get_dinosaur_by_name
from dna_synthesis_robot import DNASynthesisRobot, SynthesisOutput, create_robot
from embryo_injection_system import EmbryoInjectionSystem, DNASolution, MultiEmbryoInjectionBatch


@dataclass
class TransformationStatus:
    """Status da transformação."""
    phase: str  # "genoma", "síntese", "injeção", "incubação", "desenvolvimento"
    progress_percent: float
    timestamp: str
    notes: str


class DinosaurTransformationPipeline:
    """
    Pipeline Completo de Transformação Dinossauro.
    
    Fases:
    1. Seleção do genoma (DinoDatabase)
    2. Síntese de DNA (Robot)
    3. Injeção em embrião (EmbryoSystem)
    4. Incubação (37.8°C)
    5. Eclosão e desenvolvimento
    6. Crescimento e maturação
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.target_species: Optional[DinosaurSpecies] = None
        self.dna_robot: Optional[DNASynthesisRobot] = None
        self.embryo_batch: Optional[MultiEmbryoInjectionBatch] = None
        self.status_history: List[TransformationStatus] = []
        self.final_result: Optional[Dict] = None
    
    def select_dinosaur_species(self, species_name: str) -> DinosaurSpecies:
        """Seleciona a espécie de dinossauro."""
        print(f"\n🦖 Selecionando espécie: {species_name}")
        
        dino = get_dinosaur_by_name(species_name)
        if not dino:
            print(f"❌ Espécie não encontrada!")
            return None
        
        self.target_species = dino
        
        print(f"   ✓ Nome científico: {dino.scientific_name}")
        print(f"   ✓ Tamanho: {dino.length_meters}m × {dino.height_meters}m")
        print(f"   ✓ Peso: {dino.weight_kg:,} kg")
        print(f"   ✓ Genoma: {dino.genome_size_bp/1e9:.2f} Gb")
        print(f"   ✓ Características: {', '.join(dino.unique_features[:2])}")
        
        self._update_status("seleção_dinossauro", 5, 
                           f"Espécie selecionada: {dino.scientific_name}")
        
        return dino
    
    def synthesize_genome(self) -> SynthesisOutput:
        """Sintetiza o genoma completo."""
        if not self.target_species:
            print("❌ Nenhuma espécie selecionada!")
            return None
        
        print(f"\n🤖 Iniciando síntese de DNA...")
        
        # Cria robô
        self.dna_robot = create_robot()
        
        # Gera genoma (simulado para demonstração)
        import random
        import numpy as np
        
        bases = 'ATGC'
        genome_length = min(
            self.target_species.genome_size_bp,
            100_000  # Usar 100k bp como demo (reduzido)
        )
        
        print(f"   Tamanho de genoma a sintetizar: {genome_length/1e6:.1f} Mb")
        print(f"   (Genoma completo seria {self.target_species.genome_size_bp/1e9:.2f} Gb)")
        
        # Simula síntese
        synthetic_genome = ''.join(random.choice(bases) for _ in range(genome_length))
        
        result = self.dna_robot.synthesize_sequence(synthetic_genome)
        
        print(f"\n✅ SÍNTESE CONCLUÍDA!")
        print(f"   Sequência sintetizada: {genome_length:,} bp")
        print(f"   Pureza: {result.purity_percent}%")
        print(f"   Rendimento: {result.yield_percent}%")
        print(f"   Tempo total: {result.synthesis_time_minutes:.1f} minutos")
        
        self._update_status("síntese_dna", 25, 
                           f"DNA sintetizado: {genome_length:,} bp")
        
        return result
    
    def prepare_dna_solution(self, synthesis_result: SynthesisOutput) -> DNASolution:
        """Prepara solução de DNA para injeção."""
        print(f"\n💧 Preparando solução de DNA para injeção...")
        
        dna_solution = DNASolution(
            sequence=synthesis_result.sequence,
            concentration_ng_ul=synthesis_result.concentration_ng_ul,
            volume_ul=synthesis_result.volume_ul,
            purity_percent=synthesis_result.purity_percent,
            dino_species=self.target_species.scientific_name
        )
        
        print(f"   ✓ Concentração: {dna_solution.concentration_ng_ul} ng/μL")
        print(f"   ✓ Volume: {dna_solution.volume_ul} μL")
        print(f"   ✓ Pureza: {dna_solution.purity_percent}%")
        print(f"   ✓ Pronto para injeção!")
        
        self._update_status("preparação_dna", 35,
                           "Solução de DNA preparada")
        
        return dna_solution
    
    def inject_embryos(self, num_embryos: int = 10) -> MultiEmbryoInjectionBatch:
        """Injeta DNA em embriões de galinha."""
        print(f"\n🥚 Preparando injeção em {num_embryos} embriões...")
        
        # Cria lote de embriões
        self.embryo_batch = MultiEmbryoInjectionBatch(
            f"{self.project_id}_batch",
            num_embryos
        )
        
        # Prepara solução de DNA
        if not self.dna_robot or not self.dna_robot.synthesis_results:
            print("❌ Nenhum DNA sintetizado!")
            return None
        
        synthesis_result = self.dna_robot.get_last_synthesis_result()
        dna_solution = self.prepare_dna_solution(synthesis_result)
        
        # Injeta em lote
        self.embryo_batch.inject_batch([dna_solution] * num_embryos)
        
        self._update_status("injeção_embriões", 55,
                           f"{num_embryos} embriões injetados")
        
        return self.embryo_batch
    
    def incubate_and_monitor(self, days: int = 21) -> Dict:
        """Incuba embriões e monitora desenvolvimento."""
        if not self.embryo_batch:
            print("❌ Nenhum embrião para incubar!")
            return None
        
        print(f"\n🔥 Iniciando incubação por {days} dias...")
        print(f"   Temperatura: 37.8°C")
        print(f"   Umidade: 60-65%")
        print(f"   Embriões: {len(self.embryo_batch.embryos)}")
        
        # Simula desenvolvimento
        development_log = []
        
        milestones = {
            1: "Integração de DNA",
            3: "Primeiras divisões celulares",
            7: "Organogênese begin",
            10: "Penas começam a se formar",
            14: "Características dinossauro evidentes",
            18: "Desenvolvimento completo",
            20: "Pronto para eclosão",
            21: "Eclosão esperada"
        }
        
        for day in range(1, days + 1):
            if day in milestones:
                event = milestones[day]
                print(f"   [{day:2d}d] {event}")
                development_log.append({"day": day, "event": event})
            
            if day % 5 == 0:
                self._update_status("incubação", 55 + (day/days) * 35,
                                   f"Dia {day} de {days}")
        
        print(f"\n✅ Incubação concluída!")
        
        batch_stats = self.embryo_batch.get_batch_statistics()
        print(f"   Taxa de integração: {batch_stats['average_integration']:.1f}%")
        print(f"   Taxa de sobrevivência: {batch_stats['average_survival']:.1f}%")
        
        self._update_status("eclosão", 85,
                           "Embriões prontos para eclosão")
        
        return {
            "total_days": days,
            "development_log": development_log,
            "batch_statistics": batch_stats,
            "ready_to_hatch": True
        }
    
    def hatch_dinosaurs(self) -> Dict:
        """Simula eclosão dos dinossauros."""
        if not self.embryo_batch:
            print("❌ Nenhum embrião!")
            return None
        
        print(f"\n🐣 ECLOSÃO DE DINOSSAUROS!")
        print(f"   Espécie: {self.target_species.scientific_name}")
        print(f"   Embriões prontos: {len(self.embryo_batch.embryos)}")
        
        hatched = []
        for embryo in self.embryo_batch.embryos:
            status = embryo.get_transformation_status()
            hatched.append(status)
            print(f"   ✓ {embryo.embryo_id}: 100% dinossauro!")
        
        self._update_status("eclosão_completa", 95,
                           f"{len(hatched)} dinossauros eclodidos!")
        
        return {
            "total_hatched": len(hatched),
            "species": self.target_species.scientific_name,
            "hatched_organisms": hatched
        }
    
    def monitor_growth(self, weeks: int = 4) -> Dict:
        """Monitora crescimento dos dinossauros."""
        print(f"\n📈 Monitorando crescimento por {weeks} semanas...")
        
        growth_data = []
        for week in range(1, weeks + 1):
            size_percent = (week / weeks) * 100
            print(f"   Semana {week}: {size_percent:.0f}% do tamanho adulto")
            growth_data.append({
                "week": week,
                "growth_percent": size_percent,
                "status": "Saudável"
            })
        
        self._update_status("crescimento", 95 + (weeks/4) * 5,
                           f"Dinossauros em crescimento")
        
        return {
            "species": self.target_species.scientific_name,
            "monitoring_weeks": weeks,
            "growth_data": growth_data,
            "status": "Crescimento normal"
        }
    
    def complete_pipeline(self, num_embryos: int = 10):
        """Executa o pipeline completo."""
        print("\n" + "="*70)
        print("🦖 PIPELINE COMPLETO: GALINHA → DINOSSAURO")
        print("="*70)
        
        # Fase 1: Seleção
        self.select_dinosaur_species("Tyrannosaurus rex")
        
        # Fase 2: Síntese
        synthesis = self.synthesize_genome()
        
        # Fase 3: Injeção
        self.inject_embryos(num_embryos)
        
        # Fase 4: Incubação
        incubation = self.incubate_and_monitor(21)
        
        # Fase 5: Eclosão
        hatching = self.hatch_dinosaurs()
        
        # Fase 6: Crescimento
        growth = self.monitor_growth(4)
        
        self._update_status("completo", 100,
                           "Pipeline finalizado com sucesso!")
        
        # Resultado final
        self.final_result = {
            "project_id": self.project_id,
            "target_species": self.target_species.scientific_name,
            "dna_synthesized_bp": len(synthesis.sequence),
            "embryos_injected": num_embryos,
            "embryos_hatched": hatching["total_hatched"],
            "success_rate_percent": 100.0,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n" + "="*70)
        print("✅ SUCESSO! DINOSSAUROS CRIADOS!")
        print("="*70)
        print(json.dumps(self.final_result, indent=2, ensure_ascii=False))
        
        return self.final_result
    
    def _update_status(self, phase: str, progress: float, notes: str):
        """Atualiza status do pipeline."""
        status = TransformationStatus(
            phase=phase,
            progress_percent=progress,
            timestamp=datetime.now().isoformat(),
            notes=notes
        )
        self.status_history.append(status)
        
        bar_length = 50
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\n   [{bar}] {progress:.0f}%")
        print(f"   Fase: {phase} - {notes}")
    
    def get_status_report(self) -> str:
        """Retorna relatório de status."""
        report = f"Projeto: {self.project_id}\n"
        report += f"Alvo: {self.target_species.scientific_name if self.target_species else 'Não selecionado'}\n"
        report += f"Status: {self.status_history[-1].phase if self.status_history else 'Não iniciado'}\n"
        return report
    
    def save_report(self, filepath: str):
        """Salva relatório do pipeline."""
        report = {
            "project_id": self.project_id,
            "target_species": self.target_species.scientific_name if self.target_species else None,
            "status_history": [
                {
                    "phase": s.phase,
                    "progress": s.progress_percent,
                    "timestamp": s.timestamp,
                    "notes": s.notes
                }
                for s in self.status_history
            ],
            "final_result": self.final_result
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Relatório salvo: {filepath}")
