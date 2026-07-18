#!/usr/bin/env python3
"""
demo_full_transformation.py
============================
Demo completa: Do genoma ao dinossauro nascido!

Executa o pipeline completo de transformação.
"""

import sys
from dinosaur_database import database_stats, get_dinosaurs_by_popularity
from dinosaur_transformation_pipeline import DinosaurTransformationPipeline


def print_header():
    """Imprime cabeçalho."""
    print("\n" + "="*70)
    print("🦖 RE-DINO: PROJETO DE RESSURREIÇÃO DE DINOSSAUROS 🦖")
    print("="*70)
    print()
    print("Tecnologia: Síntese de DNA + Injeção em Embriões")
    print("Objetivo: Trazer dinossauros de volta à vida")
    print()


def show_database_overview():
    """Mostra visão geral do banco de dados."""
    print("\n" + "─"*70)
    print("📊 BANCO DE DADOS DE DINOSSAUROS")
    print("─"*70)
    
    stats = database_stats()
    print(f"\nTotal de espécies: {stats['total_species']}")
    print(f"  • Populares: {stats['populares']}")
    print(f"  • Impopulares: {stats['impopulares']}")
    print(f"  • Desconhecidos: {stats['desconhecidos']}")
    
    print(f"\nDistribuição por período:")
    print(f"  • Triássico: {stats['periodos']['triassico']}")
    print(f"  • Jurássico: {stats['periodos']['jurassico']}")
    print(f"  • Cretáceo: {stats['periodos']['cretaceo']}")
    
    # Mostra alguns desconhecidos ao público
    print("\n🔍 Alguns dinossauros DESCONHECIDOS ao público:")
    unknown = get_dinosaurs_by_popularity("desconhecido")
    for dino in unknown[:3]:
        print(f"   • {dino.scientific_name} ({dino.common_name})")
        print(f"     └─ {dino.description[:60]}...")


def run_single_transformation():
    """Executa transformação de um único dinossauro."""
    print("\n" + "─"*70)
    print("🧬 TRANSFORMAÇÃO: GALINHA → TIRANOSSAURO")
    print("─"*70)
    
    # Cria pipeline
    pipeline = DinosaurTransformationPipeline("TREX-001")
    
    # Executa
    result = pipeline.complete_pipeline(num_embryos=5)
    
    # Salva relatório
    pipeline.save_report("re_dino_output/transformation_report.json")
    
    return pipeline


def run_multi_species_transformation():
    """Executa transformação de múltiplas espécies."""
    print("\n" + "─"*70)
    print("🦖 TRANSFORMAÇÃO MÚLTIPLA: VÁRIAS ESPÉCIES")
    print("─"*70)
    
    species_list = [
        "Tyrannosaurus rex",
        "Triceratops horridus",
        "Stegosaurus stenops",
        "Velociraptor mongoliensis"
    ]
    
    pipelines = []
    for i, species in enumerate(species_list, 1):
        print(f"\n[{i}/{len(species_list)}] Iniciando transformação de {species}...")
        
        pipeline = DinosaurTransformationPipeline(f"MULTI-{i:03d}")
        pipeline.select_dinosaur_species(species)
        pipeline.synthesize_genome()
        pipeline.inject_embryos(num_embryos=3)
        pipeline.incubate_and_monitor(days=21)
        pipeline.hatch_dinosaurs()
        
        pipelines.append(pipeline)
        print(f"✅ {species} criado com sucesso!")
    
    return pipelines


def generate_full_report(pipelines):
    """Gera relatório completo."""
    print("\n" + "─"*70)
    print("📋 RELATÓRIO FINAL")
    print("─"*70)
    
    total_hatched = 0
    for pipeline in pipelines:
        if pipeline.final_result:
            total_hatched += pipeline.final_result.get("embryos_hatched", 0)
            print(f"\n✓ {pipeline.final_result['target_species']}")
            print(f"  Embriões eclodidos: {pipeline.final_result['embryos_hatched']}")
    
    print(f"\n{'='*70}")
    print(f"TOTAL DE DINOSSAUROS CRIADOS: {total_hatched}")
    print(f"{'='*70}")


def main():
    """Função principal."""
    print_header()
    
    print("\n🚀 Iniciando demo completa...\n")
    
    # 1. Visão geral do banco de dados
    show_database_overview()
    
    # 2. Transformação simples
    print("\n\n" + "▓"*70)
    print("▓ FASE 1: TRANSFORMAÇÃO SIMPLES")
    print("▓"*70)
    pipeline1 = run_single_transformation()
    
    # 3. Transformação múltipla
    print("\n\n" + "▓"*70)
    print("▓ FASE 2: TRANSFORMAÇÃO MÚLTIPLA")
    print("▓"*70)
    pipelines_multi = run_multi_species_transformation()
    
    # 4. Relatório final
    generate_full_report([pipeline1] + pipelines_multi)
    
    # 5. Instruções para construção real
    print("\n\n" + "="*70)
    print("🛠️  PRÓXIMOS PASSOS: CONSTRUIR A MÁQUINA NA VIDA REAL")
    print("="*70)
    print_construction_guide()
    
    print("\n✅ DEMO CONCLUÍDA!\n")


def print_construction_guide():
    """Imprime guia de construção da máquina robótica."""
    guide = """
╔════════════════════════════════════════════════════════════════════╗
║                  GUIA DE CONSTRUÇÃO - MÁQUINA ROBÓTICA             ║
║                   Para Síntese de DNA em Escala                    ║
╚════════════════════════════════════════════════════════════════════╝

📋 LISTA DE MATERIAIS E COMPONENTES:

1️⃣  NÚCLEO DE SÍNTESE
   ├─ Coluna de síntese (vidro borosilicato, 1mL)
   ├─ Filtro de vidro sinterizado (5-10 μm)
   ├─ Suporte universal de laboratório
   └─ Clamp para coluna

2️⃣  SISTEMA DE BOMBEAMENTO
   ├─ Bomba peristáltica (Gilson Minipuls 3 ou equivalente)
   ├─ Tubing: Teflon/silicone, vários diâmetros
   ├─ Adaptadores L e T de PTFE
   └─ Válvulas de bola (PTFE, Swagelok)

3️⃣  SISTEMA DE VÁLVULAS
   ├─ Válvulas solenóide (16 canais, 12V DC)
   ├─ Manifold de distribuição (PTFE ou aço inox)
   ├─ Relés para controle
   └─ Fonte de alimentação 12V

4️⃣  REAGENTES QUÍMICOS (Custos indicativos)
   ├─ dA amidite: $300
   ├─ dT amidite: $250
   ├─ dG amidite: $350
   ├─ dC amidite: $280
   ├─ Acetonitrila: $50/L
   ├─ TCA 3%: $30/L
   ├─ Iodo 0.02M: $100/50mL
   └─ Cap A: $60/20mL
   
   TOTAL: ~$1,500/kit

5️⃣  SISTEMA DE CONTROLE
   ├─ Arduino Mega 2560 ou PLC industrial
   ├─ Módulo relé 16 canais
   ├─ Sensor de temperatura (NTC 10k)
   ├─ Sensor de pressão (0-100 psi)
   ├─ Display LCD 16x2
   └─ Botões de controle (iniciar, parar, manual)

6️⃣  PERIFÉRICOS
   ├─ Aquecedor resistivo (200W, 12V)
   ├─ Termostato (±0.5°C)
   ├─ Detector UV (260nm, opcional)
   ├─ Coletor de frações automático (12 posições)
   └─ Gabinete de segurança (fume hood)

💰 ORÇAMENTO TOTAL: ~$3,000 - $5,000

⚙️  PROTOCOLO DE CONSTRUÇÃO:

1. Montar estrutura base em alumínio 40x40mm
2. Instalar coluna de síntese no centro
3. Conectar bomba peristáltica com tubing
4. Montar manifold de válvulas solenóide
5. Integrar controle eletrônico com Arduino
6. Testar cada válvula individualmente
7. Calibrar bomba (volume/tempo)
8. Testar com reagentes dummy
9. Fazer síntese teste com oligonucleotídeos curtos
10. Validar com HPLC ou espectrometria

📚 REFERÊNCIAS CIENTÍFICAS:

[1] Beaucage & Iyer (1992) - "Synthesis of oligonucleotides by the 
    phosphoramidite method" - Tetrahedron 48(12)

[2] Glenn Research - "Oligonucleotide Synthesis Protocols"
    https://www.glenresearch.com

[3] Hogrefe et al. (1993) - "Optimization of automated DNA synthesis"
    - Methods in Molecular Biology

[4] Matteucci & Caruthers (1981) - "Synthesis of deoxyoligonucleotides 
    on a polymer support" - JACS 103(11)

🔗 SUPPLIERS (Equipamento):
   • Glen Research: Reagentes e colunas
   • Gilson: Bombas peristálticas
   • Swagelok: Válvulas e conexões
   • Sigma-Aldrich: Solventes e reagentes
   • Amazon/AliExpress: Arduino, sensores, relés

⚠️  MEDIDAS DE SEGURANÇA:
   • Use respirador ao trabalhar com acetonitrila
   • Use luvas de nitrilo descartáveis
   • Trabalhe em fume hood sempre
   • Dispose TCA e acetonitrila corretamente
   • Mantenha iodo em frasco lacrado
   • Tenha extintor de incêndio próximo
"""
    print(guide)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
