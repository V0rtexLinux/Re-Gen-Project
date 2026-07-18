#!/usr/bin/env python3
"""
test_v3_integration.py -- Teste Integrado Re-Dino v3
====================================================

Valida funcionamento de todos os módulos v3:
✓ genome_streaming.py - Leitura eficiente em memória
✓ ai_tools.py - Framework tool-calling
✓ genome_validator.py - Validação genética
✓ reference_searcher.py - Busca de referências
✓ crispr_engine.py - Design CRISPR
✓ enzyme_library.py - Enzimas disponíveis
✓ main_v3.py - Orquestração com IA

USO:
    python test_v3_integration.py
    python test_v3_integration.py --fast (testa rápido)
    python test_v3_integration.py --verbose (saída detalhada)
"""

import sys
from pathlib import Path

# ==================== TEST SUITE ====================

def test_genome_streaming():
    """Test 1: genome_streaming - Leitura de FASTQ em chunks."""
    print("\n" + "="*70)
    print("[TEST 1] genome_streaming.py - Leitura FASTQ em Streaming")
    print("="*70)
    
    try:
        from genome_streaming import (
            create_reader,
            StreamingValidator,
            StreamingAnalyzer,
        )
        
        fastq_file = Path("/home/v0rtex/Documents/re-gen/leitura.fastq")
        
        if not fastq_file.exists():
            print("⚠ Arquivo FASTQ não encontrado, pulando")
            return True
        
        print(f"\nAnalisando: {fastq_file}")
        
        # Test streaming read
        with create_reader(str(fastq_file), chunk_size=50_000) as reader:
            analyzer = StreamingAnalyzer()
            report = analyzer.analyze_stream(reader)
        
        print(f"✓ Leitura bem-sucedida:")
        print(f"  Total bp: {report['total_bp']:,}")
        print(f"  Chunks: {report['chunks']}")
        print(f"  GC médio: {report['gc_mean_percent']:.2f}%")
        print(f"  Qualidade: {report['quality_mean']:.1f} Phred")
        
        # Test validation
        with create_reader(str(fastq_file), chunk_size=50_000) as reader:
            validator = StreamingValidator()
            is_valid, stats = validator.validate_stream(reader)
        
        print(f"✓ Validação:")
        print(f"  Válido: {is_valid}")
        print(f"  Chunks validados: {stats.chunks_processed}")
        print(f"  Erros encontrados: {len(validator.errors)}")
        
        return True
    
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_tools():
    """Test 2: ai_tools - Framework tool-calling."""
    print("\n" + "="*70)
    print("[TEST 2] ai_tools.py - Framework Tool-Calling")
    print("="*70)
    
    try:
        from ai_tools import get_tool_registry, Tool
        
        registry = get_tool_registry()
        
        print(f"\n✓ Registry carregado com {len(registry.tools)} tools:")
        for tool_name, tool in registry.tools.items():
            print(f"  - {tool_name}: {tool.description[:50]}...")
        
        # Test tool execution
        print(f"\nTestando execução de tools:")
        
        result = registry.execute_tool(
            "validate_sequence",
            sequence="ATGCATGC" * 100,
            check_type="all"
        )
        
        print(f"✓ validate_sequence executada:")
        print(f"  Sucesso: {result['success']}")
        print(f"  Result: {str(result.get('result', ''))[:60]}...")
        
        return True
    
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_genome_validator():
    """Test 3: genome_validator - Validação genética."""
    print("\n" + "="*70)
    print("[TEST 3] genome_validator.py - Validação Genética")
    print("="*70)
    
    try:
        from genome_validator import create_validator
        
        validator = create_validator()
        
        print(f"\n✓ Validador criado")
        
        # Test com sequência válida
        report = validator.validate("ATGCATGCATGC" * 100, "test_chunk_1")
        print(f"\n✓ Validação sequência boa:")
        print(f"  Problemas encontrados: {len(report.issues)}")
        print(f"  Comprimento: {report.sequence_length} bp")
        
        # Test com sequência problemática
        bad_sequence = "AAAAAAAAAA" * 50  # Homopolímero longo
        report = validator.validate(bad_sequence, "test_chunk_bad")
        print(f"\n✓ Validação sequência ruim:")
        print(f"  Problemas encontrados: {len(report.issues)}")
        for issue in report.issues[:3]:
            print(f"    - {issue.issue_type}: {issue.description[:40]}...")
        
        return True
    
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crispr_engine():
    """Test 4: crispr_engine - Design CRISPR."""
    print("\n" + "="*70)
    print("[TEST 4] crispr_engine.py - Design CRISPR")
    print("="*70)
    
    try:
        from crispr_engine import CRISPRDesigner, Cas9Variant
        
        designer = CRISPRDesigner()
        
        print(f"\n✓ Designer CRISPR criado")
        print(f"  Variantes Cas9 disponíveis: {len(Cas9Variant.__members__)}")
        for variant_name in list(Cas9Variant.__members__.keys())[:3]:
            print(f"    - {variant_name}")
        
        # Test gRNA design
        target_sequence = "ATGCATGCATGCATGCATGC" * 10
        grnas = designer.find_grnas(target_sequence)
        
        print(f"\n✓ Design de gRNAs:")
        print(f"  gRNAs encontradas: {len(grnas)}")
        if grnas:
            best = grnas[0]
            print(f"  Melhor gRNA: {best.sequence[:20]}...")
            print(f"  Score: {best.combined_score():.2f}")
        
        return True
    
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enzyme_library():
    """Test 5: enzyme_library - Catálogo de enzimas."""
    print("\n" + "="*70)
    print("[TEST 5] enzyme_library.py - Catálogo de Enzimas")
    print("="*70)
    
    try:
        from enzyme_library import get_enzyme_library
        
        library = get_enzyme_library()
        
        print(f"\n✓ Biblioteca carregada com {len(library.enzymes)} enzimas:")
        for enzyme_name in list(library.enzymes.keys())[:5]:
            enzyme = library.enzymes[enzyme_name]
            print(f"  - {enzyme_name}: {enzyme.recognition_site}")
        
        # Test restriction site search
        dna = "GAATTCATGCGAATTC"  # EcoRI sites
        sites = library.find_restriction_enzyme_for_sequence(dna)
        print(f"\n✓ Busca de restriction sites:")
        print(f"  Sites encontrados: {len(sites)}")
        if sites:
            for enzyme_name, position in sites[:3]:
                print(f"    - {enzyme_name} at {position}")
        
        return True
    
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reference_searcher():
    """Test 6: reference_searcher - Busca de referências (SKIP em tests rápidos)."""
    print("\n" + "="*70)
    print("[TEST 6] reference_searcher.py - Busca de Referências")
    print("="*70)
    
    try:
        from reference_searcher import create_searcher
        
        searcher = create_searcher("test@example.com")
        
        print(f"\n✓ Searcher criado")
        print(f"  NCBI Searcher: {searcher.ncbi is not None}")
        print(f"  UniProt Searcher: {searcher.uniprot is not None}")
        print(f"  CrossRef Searcher: {searcher.crossref is not None}")
        
        # Não executar busca real (requer internet)
        print(f"  ⚠ Busca real requer internet, pulando")
        
        return True
    
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_v3_imports():
    """Test 7: main_v3 - Verificar imports e orquestração."""
    print("\n" + "="*70)
    print("[TEST 7] main_v3.py - Orquestração IA Tool-Calling")
    print("="*70)
    
    try:
        from main_v3 import (
            AIOrchestrator,
            OrchestrationContext,
        )
        from genome_synthesis import GenomeSynthesisJob
        from pathlib import Path
        
        print(f"\n✓ Imports bem-sucedidos")
        
        # Criar job de teste
        job = GenomeSynthesisJob(
            job_id="test_job",
            target_species="Test Species",
            target_genome_size_bp=1_000_000,
            chunk_size_bp=100_000,
            output_dir=Path("/tmp"),
        )
        
        context = OrchestrationContext(job, "test@example.com")
        
        print(f"✓ Contexto de orquestração criado:")
        print(f"  Job ID: {context.job.job_id}")
        print(f"  Espécie: {context.job.target_species}")
        print(f"  Tamanho genoma: {context.job.target_genome_size_bp:,} bp")
        print(f"  Tools disponíveis: {len(context.tool_registry.tools)}")
        
        return True
    
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ollama_integration():
    """Test 8: Ollama - Verificar conectividade."""
    print("\n" + "="*70)
    print("[TEST 8] Ollama Integration - IA Tool-Calling Backend")
    print("="*70)
    
    try:
        from ollama_integration import obter_cliente_ollama
        
        client = obter_cliente_ollama()
        
        if client.validar_conexao():
            print(f"✓ Conectado ao Ollama em {client.config.endpoint}")
            
            models = client.listar_modelos_disponiveis()
            print(f"  Modelos disponíveis: {models}")
            
            # Test simple generation
            response = client.gerar_texto("Diga 'OK' se estiver funcionando.", streaming=False)
            print(f"✓ Geração de texto testada")
            print(f"  Resposta: {response[:50]}...")
            
            return True
        else:
            print(f"✗ Ollama não acessível em {client.config.endpoint}")
            print(f"  Inicie com: ollama serve")
            return False
    
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa suite de testes."""
    
    print("\n" + "="*70)
    print("RE-DINO v3 -- SUITE DE TESTES INTEGRADA")
    print("="*70)
    
    tests = [
        ("genome_streaming", test_genome_streaming),
        ("ai_tools", test_ai_tools),
        ("genome_validator", test_genome_validator),
        ("crispr_engine", test_crispr_engine),
        ("enzyme_library", test_enzyme_library),
        ("reference_searcher", test_reference_searcher),
        ("main_v3", test_main_v3_imports),
        ("ollama_integration", test_ollama_integration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Erro não tratado em {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! Re-Dino v3 está pronto.")
        return 0
    else:
        print(f"\n⚠ {total - passed} teste(s) falharam.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
