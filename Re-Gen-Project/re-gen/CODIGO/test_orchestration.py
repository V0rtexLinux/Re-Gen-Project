#!/usr/bin/env python3
"""
test_orchestration.py -- Teste da Orquestração com IA
====================================================

Testa o fluxo completo:
1. IA recebe contexto do dinossauro
2. IA chama tools para validar/editar/buscar referências
3. Sistema executa o plano de síntese genômica

USO:
    python test_orchestration.py
"""

import sys
from pathlib import Path

def test_orchestration_workflow():
    """Testa workflow completo de orquestração."""
    
    print("\n" + "="*70)
    print("RE-DINO v3 -- TESTE DE ORQUESTRAÇÃO COM IA")
    print("="*70)
    
    # Imports
    from main_v3 import AIOrchestrator, OrchestrationContext
    from genome_synthesis import GenomeSynthesisJob
    
    # Setup
    print("\n[1/3] Configurando contexto de síntese...")
    
    job = GenomeSynthesisJob(
        job_id="test_trex",
        target_species="Tyrannosaurus rex",
        target_genome_size_bp=5_000_000,  # 5Mb para teste rápido
        chunk_size_bp=100_000,
        output_dir=Path("/tmp/redino_test"),
    )
    
    context = OrchestrationContext(job, "test@example.com")
    
    print(f"✓ Job criado:")
    print(f"  Espécie: {job.target_species}")
    print(f"  Tamanho: {job.target_genome_size_bp/1e6:.1f} Mb")
    print(f"  Chunks: ~{job.expected_chunks}")
    
    # Orquestração
    print(f"\n[2/3] Inicializando orquestrador IA...")
    
    orchestrator = AIOrchestrator(context, modelo_ollama="mistral")
    
    print(f"✓ Orquestrador pronto")
    print(f"  Modelo: mistral")
    print(f"  Tools disponíveis: {len(context.tool_registry.tools)}")
    
    # Executa
    print(f"\n[3/3] Executando síntese com IA tool-calling...")
    
    result = orchestrator.orchestrate_genome_synthesis()
    
    # Resultado
    print("\n" + "="*70)
    print("✓ SÍNTESE CONCLUÍDA COM SUCESSO")
    print("="*70)
    
    print(f"\nResultado:")
    print(f"  Sucesso: {result.get('success', False)}")
    print(f"  Espécie: {result.get('species')}")
    print(f"  Tamanho: {result.get('genome_size_bp', 0):,} bp")
    
    if "tools_executed" in result:
        print(f"\n  AI Tool-Calling:")
        print(f"    Tools executadas: {result['tools_executed']}")
        print(f"    Bem-sucedidas: {result['tools_successful']}")
        print(f"    Falhadas: {result['tools_failed']}")
    
    if "output_files" in result:
        print(f"\n  Arquivos gerados:")
        for file_type, file_path in result["output_files"].items():
            exists = Path(file_path).exists() if file_path else False
            status = "✓" if exists else "⚠"
            print(f"    {status} {file_type}: {file_path}")
    
    print("\n" + "="*70)
    
    return 0 if result.get("success", False) else 1


if __name__ == "__main__":
    try:
        sys.exit(test_orchestration_workflow())
    except KeyboardInterrupt:
        print("\n⚠ Interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
