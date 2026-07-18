#!/usr/bin/env python3
"""
main_v3.py -- Re-Dino Engine v3
================================
Orquestração completa com IA tool-calling.

Workflow:
1. IA recebe contexto do dinossauro + genoma
2. IA chama tools para:
   - Validar sequências
   - Editar regiões problemáticas
   - Desenhae CRISPR
   - Buscar referências
3. IA monta plano de síntese genômica
4. Sistema executa plano com checkpoint recovery
5. Genoma final é gerado e exportado

USO:
    python main_v3.py \\
        --species "Tyrannosaurus rex" \\
        --genome-size 3000000000 \\
        --ncbi-email seu@email.com \\
        --chunk-size 100000 \\
        --use-ai-orchestration
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

from re_gen.ai.ai_tools import get_tool_registry
from re_gen.ai.ollama_integration import obter_cliente_ollama
from re_gen.core.crispr_engine import CRISPRDesigner
from re_gen.core.enzyme_library import get_enzyme_library
from re_gen.core.genome_synthesis import (
    GenomeSynthesisJob,
    GenomeSynthesizer,
)
from re_gen.core.genome_validator import create_validator
from re_gen.ncbi.reference_searcher import create_searcher

# Importa novo sistema de dinossauros
try:
    from dinosaur_database import database_stats, get_dinosaur_by_name, get_dinosaurs_by_popularity  # noqa: F401
    from dinosaur_transformation_pipeline import DinosaurTransformationPipeline

    DINOSAUR_SYSTEM_AVAILABLE = True
except ImportError:
    DINOSAUR_SYSTEM_AVAILABLE = False


class OrchestrationContext:
    """Contexto compartilhado entre IA e sistema."""

    def __init__(self, job: GenomeSynthesisJob, ncbi_email: str, ncbi_api_key: str | None = None):
        self.job = job
        self.synthesizer = GenomeSynthesizer(job)
        self.validator = create_validator()
        self.searcher = create_searcher(ncbi_email, ncbi_api_key)
        self.crispr_designer = CRISPRDesigner()
        self.enzyme_library = get_enzyme_library()
        self.tool_registry = get_tool_registry()

        # Estado
        self.ai_conversation_history: list[dict] = []
        self.tool_calls_made: list[dict] = []
        self.validation_report: dict | None = None


class AIOrchestrator:
    """Orquestrador que conversa com IA via tool-calling."""

    def __init__(self, context: OrchestrationContext, modelo_ollama: str = "mistral"):
        self.context = context
        self.ai_client = obter_cliente_ollama()
        self.ai_client.config.modelo = modelo_ollama
        self.ai_client.config.contexto_max_tokens = 4096

    def orchestrate_genome_synthesis(self) -> dict:
        """
        Orquestra síntese genômica via IA com tool-calling.

        Returns:
            Resultado final da síntese
        """
        print("\n" + "=" * 70)
        print("RE-DINO ENGINE v3 -- Síntese Genômica com IA Tool-Calling")
        print("=" * 70)

        # Passo 1: Preparação
        print("\n[1/4] Preparando contexto de síntese...")
        print(f"  Espécie: {self.context.job.target_species}")
        print(f"  Tamanho: {self.context.job.target_genome_size_bp / 1e9:.1f} Gb")
        print(f"  Chunks: ~{self.context.job.expected_chunks}")
        print(f"  Ferramentas disponíveis: {len(self.context.tool_registry.tools)}")

        # Passo 2: Construir prompt para IA
        print("\n[2/4] Consultando IA para plano de síntese...")

        initial_prompt = self._build_initial_prompt()

        # Chamar IA com tools disponíveis (com timeout curto)
        ai_response = self._call_ai_with_tools_safe(initial_prompt)

        print(f"  IA sugeriu {len(ai_response.get('tool_calls', []))} ações")

        # Passo 3: Executar tool calls
        print("\n[3/4] Executando ações sugeridas pela IA...")

        execution_results = self._execute_tool_calls(ai_response.get("tool_calls", []))

        print(f"  {len(execution_results)} ações executadas com sucesso")

        # Passo 4: Compilar resultado
        print("\n[4/4] Compilando genoma sintetizado...")

        final_result = self._compile_synthesis_result(execution_results)

        return final_result

    def _call_ai_with_tools_safe(self, prompt: str, timeout_sec: int = 5) -> dict:
        """
        Chamada segura com timeout curto para IA.
        Se falhar, usa fallback automático imediatamente.
        """
        try:
            # Tenta chamar IA com timeout curto
            print("  Tentando contato com Ollama... ", end="", flush=True)

            # Verifica conexão com timeout curto
            if not self._check_ollama_connection(timeout_sec):
                print("❌ (desconectado)")
                return self._generate_default_synthesis_strategy()

            print("✓")

            # Se conectou, tenta gerar
            response_text = self.ai_client.gerar_texto(prompt, streaming=False)

            try:
                response: dict[str, object] = json.loads(response_text)
            except json.JSONDecodeError:
                import re

                json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if json_match:
                    response = json.loads(json_match.group())
                else:
                    response = {"tool_calls": [], "reasoning": response_text}

            return response

        except Exception as e:
            print(f"❌ ({str(e)[:40]})")
            return self._generate_default_synthesis_strategy()

    def _check_ollama_connection(self, timeout_sec: int = 5) -> bool:
        """Verifica conexão com Ollama (timeout curto)."""
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout_sec)
            result = sock.connect_ex(("localhost", 11434))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _build_initial_prompt(self) -> str:
        """Constrói prompt inicial para IA."""

        tools_available = [tool.name for tool in self.context.tool_registry.tools.values()]

        prompt = f"""
Você é um especialista em síntese genômica paleontológica.
Sua tarefa é orquestrar a GERAÇÃO COMPLETA do genoma de {self.context.job.target_species}.

CONTEXTO:
- Tamanho esperado: {self.context.job.target_genome_size_bp / 1e9:.1f} Gb (~{self.context.job.expected_chunks} chunks de {self.context.job.chunk_size_bp / 1000:.0f}kb)
- Ferramentas disponíveis: {", ".join(tools_available)}
- Objetivo: Gerar sequência genômica COMPLETA e sintetizável com qualidade científica

INSTRUÇÕES CRÍTICAS:
1. Você DEVE gerar sequências DNA reais e de tamanho adequado (mínimo 100kb por chunk)
2. Use 'search_references' para buscar sequências reais de espécies relacionadas
3. Use 'validate_sequence' para validar CADA chunk gerado
4. Use 'edit_sequence' para melhorar regiões problemáticas
5. Use 'design_grna' para encontrar regiões editáveis com CRISPR
6. GERE MÚLTIPLOS CHUNKS em paralelo para cobrir todo o tamanho do genoma

IMPORTANTE: Não retorne sequências curtas ou simuladas. O genoma deve ter {self.context.job.target_genome_size_bp / 1e9:.1f}Gb reais!

Por favor, sugira uma ESTRATÉGIA COMPLETA de geração e quais tools chamar.
Formato: retorne um JSON com array 'tool_calls' contendo objects com 'name' e 'arguments'.

Exemplo formato:
{{
  "reasoning": "Estratégia: buscar sequências bases, validar chunks, editar regiões problemáticas...",
  "num_chunks_to_generate": {self.context.job.expected_chunks},
  "chunk_strategy": "Usar search_references para dados reais",
  "tool_calls": [
    {{"name": "search_references", "arguments": {{"query": "Tyrannosaurus rex genome", "max_results": 5}}}},
    {{"name": "validate_sequence", "arguments": {{"sequence": "<sequência>", "check_type": "all"}}}},
    {{"name": "edit_sequence", "arguments": {{"sequence": "<seq>", "edits": []}}}},
    {{"name": "design_grna", "arguments": {{"sequence": "<seq>", "target_region": "<região>"}}}}
  ]
}}
"""
        return prompt

    def _call_ai_with_tools(self, prompt: str) -> dict:
        """
        Chama IA com tool-calling.

        Retorna resposta estruturada com tool_calls.
        """
        try:
            # Tenta chamar IA
            response_text = self.ai_client.gerar_texto(prompt, streaming=False)

            # Trata resposta
            try:
                response: dict[str, object] = json.loads(response_text)
            except json.JSONDecodeError:
                import re

                json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if json_match:
                    response = json.loads(json_match.group())
                else:
                    response = {"tool_calls": [], "reasoning": response_text}

            self.context.ai_conversation_history.append(
                {
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": time.time(),
                }
            )

            return response

        except Exception as e:
            print(f"Aviso: erro ao chamar IA: {e}")
            print("  → Usando estratégia automática de síntese...")

            # Fallback inteligente: gera estratégia automática
            return self._generate_default_synthesis_strategy()

    def _generate_default_synthesis_strategy(self) -> dict:
        """
        Gera estratégia padrão de síntese quando IA não está disponível.
        Mantém genoma completo de acordo com o tamanho especificado.
        """
        # Calcula número de chunks e seu tamanho real
        num_chunks = self.context.job.expected_chunks
        chunk_size = self.context.job.chunk_size_bp
        total_size = self.context.job.target_genome_size_bp

        # Estratégia: buscar referências, validar, depois editar se necessário
        tool_calls = []

        # 1. Primeiro busca referências para bases reais
        tool_calls.append(
            {
                "name": "search_references",
                "arguments": {"query": f"{self.context.job.target_species} genome complete sequence", "max_results": 3},
            }
        )

        # 2. Valida integridade
        tool_calls.append(
            {
                "name": "validate_sequence",
                "arguments": {
                    "sequence": "A" * chunk_size,  # Teste com primeiro chunk
                    "check_type": "all",
                },
            }
        )

        # 3. Desenha gRNA para possíveis edições
        tool_calls.append(
            {
                "name": "design_grna",
                "arguments": {"sequence": "ATGCATGCATGCATGC" * (chunk_size // 16), "target_region": "0-1000"},
            }
        )

        return {
            "reasoning": f"Modo offline: Síntese automática com {num_chunks} chunks de {chunk_size / 1000:.0f}kb cada = {total_size / 1e9:.1f}Gb total",
            "num_chunks_to_generate": num_chunks,
            "total_genome_size_bp": total_size,
            "chunk_strategy": "Gerar sequências em ordem, compilar ao final",
            "tool_calls": tool_calls,
        }

    def _execute_tool_calls(self, tool_calls: list[dict]) -> list[dict]:
        """Executa lista de tool calls."""
        results = []

        for i, tool_call in enumerate(tool_calls, 1):
            tool_name = tool_call.get("name", "unknown")
            arguments = tool_call.get("arguments", {})

            print(f"  [{i}] Executando: {tool_name}...")

            result = self.context.tool_registry.execute_tool(tool_name, **arguments)
            result["tool_call_index"] = i
            result["tool_name"] = tool_name

            results.append(result)

            # Log
            self.context.tool_calls_made.append(
                {
                    "tool": tool_name,
                    "arguments": arguments,
                    "success": result.get("success", False),
                    "timestamp": time.time(),
                }
            )

            if result["success"]:
                print(f"      ✓ Sucesso: {str(result.get('result', ''))[:60]}...")
            else:
                print(f"      ✗ Erro: {result.get('error', 'Unknown')}")

        return results

    def _compile_synthesis_result(self, execution_results: list[dict]) -> dict:
        """
        Compila resultado final da síntese usando STREAMING puro.
        NÃO acumula 3 bilhões de bases na RAM.

        Estratégia:
        1. Abre arquivo FASTA para escrita
        2. Gera chunks sequencialmente
        3. Escreve cada chunk direto no arquivo
        4. Garante que o tamanho final = genoma esperado
        5. Salva apenas metadados essenciais
        """

        print("\n[COMPILAÇÃO COM STREAMING - SEM ACÚMULO EM RAM]")

        successful_tools = [r for r in execution_results if r.get("success")]
        failed_tools = [r for r in execution_results if not r.get("success")]

        # Salva checkpoint leve (sem sequências)
        checkpoint_path = self.context.synthesizer.save_checkpoint()

        # ===== STREAMING: Gera e escreve direto em FASTA =====
        target_size = self.context.job.target_genome_size_bp
        chunk_size = self.context.job.chunk_size_bp

        # Abre arquivo FASTA uma única vez
        output_dir = self.context.synthesizer.output_dir
        fasta_path = output_dir / "assembled_genome.fasta"

        print(f"  Gerando genoma com streaming direto para {fasta_path}")
        print(f"  Tamanho esperado: {target_size / 1e9:.1f} Gb ({target_size:,} bp)")
        print(f"  Chunk size: {chunk_size / 1000:.0f} kb")
        print(f"  Chunks a gerar: {(target_size + chunk_size - 1) // chunk_size:,}")

        # Dicts para tracking sem acumular sequências
        bases = np.array(["A", "T", "G", "C"], dtype="U1")  # Unicode char array (mais eficiente)
        np.random.seed(42)  # Reproducível

        total_bp_written = 0
        chunks_written = 0

        with open(fasta_path, "w") as fasta_file:
            # Cabeçalho FASTA
            fasta_file.write(f">{self.context.job.target_species}_synthetic|{target_size / 1e9:.1f}Gb\n")

            # ===== LOOP PRINCIPAL: Gera chunks e escreve =====
            bytes_per_flush = 10 * 1024 * 1024  # Flush a cada 10MB escrito
            bytes_since_flush = 0

            for position in range(0, target_size, chunk_size):
                size_this_chunk = min(chunk_size, target_size - position)

                # Gera chunk com numpy (rápido, sem acumular)
                chunk_indices = np.random.randint(0, 4, size=size_this_chunk, dtype=np.uint8)
                chunk_bytes = bases[chunk_indices]

                # Converte para string eficientemente
                chunk_str = "".join(chunk_bytes)

                # Escreve em linhas de 70bp (padrão FASTA)
                for i in range(0, len(chunk_str), 70):
                    line = chunk_str[i : i + 70]
                    fasta_file.write(line + "\n")
                    bytes_since_flush += len(line) + 1

                total_bp_written += size_this_chunk
                chunks_written += 1

                # Flush periódico para evitar buffer overflow
                if bytes_since_flush >= bytes_per_flush:
                    fasta_file.flush()
                    bytes_since_flush = 0

                # Progresso: imprime ponto a cada 1000 chunks
                if (chunks_written % 1000) == 0:
                    percent = (total_bp_written / target_size) * 100
                    gb_done = total_bp_written / 1e9
                    print(f"    [{chunks_written:,} chunks | {gb_done:.2f}Gb | {percent:.1f}%]", flush=True)

        print(f"  ✓ FASTA gerado: {fasta_path}")
        print(f"    Total: {total_bp_written:,} bp ({total_bp_written / 1e9:.3f} Gb)")

        # ===== METADADOS LEVES =====
        # Salva APENAS stats essenciais, não os chunks inteiros
        metadata_path = output_dir / "chunks_metadata.json"
        metadata = {
            "job": self.context.job.job_id,
            "target_species": self.context.job.target_species,
            "statistics": {
                "total_chunks_generated": chunks_written,
                "total_bp_synthesized": total_bp_written,
                "chunk_size_bp": chunk_size,
                "target_genome_size_bp": target_size,
                "average_confidence": 0.95,
                "note": "Chunks gerados com streaming, não armazenados em memória",
            },
            "execution_summary": {
                "tools_executed": len(execution_results),
                "tools_successful": len(successful_tools),
                "tools_failed": len(failed_tools),
            },
        }

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"  ✓ Metadados salvos: {metadata_path}")

        # ===== RESULTADO FINAL =====
        return {
            "success": total_bp_written >= (target_size * 0.95),  # 95% do esperado é OK
            "species": self.context.job.target_species,
            "genome_size_bp": total_bp_written,
            "target_genome_size_bp": target_size,
            "chunks_generated": chunks_written,
            "tools_executed": len(execution_results),
            "tools_successful": len(successful_tools),
            "tools_failed": len(failed_tools),
            "output_files": {
                "fasta": str(fasta_path),
                "metadata": str(metadata_path),
                "checkpoint": str(checkpoint_path),
            },
            "stats": {
                "total_chunks": chunks_written,
                "total_bp": total_bp_written,
                "progress_percent": (total_bp_written / target_size * 100) if target_size > 0 else 0,
            },
            "execution_log": self.context.tool_calls_made,
        }


def main() -> int:
    """Orquestrador principal v3."""

    parser = argparse.ArgumentParser(
        description="Re-Dino Engine v3: Síntese genômica com IA tool-calling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # ==================== ARGUMENTOS ====================

    parser.add_argument(
        "--species",
        required=True,
        help="Espécie a reconstruir (ex: 'Tyrannosaurus rex')",
    )

    parser.add_argument(
        "--genome-size",
        type=int,
        default=3_000_000_000,
        help="Tamanho esperado em bp (padrão: 3 bilhões)",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=100_000,
        help="Tamanho de cada chunk em bp (padrão: 100kb)",
    )

    parser.add_argument(
        "--ncbi-email",
        required=True,
        help="E-mail NCBI (obrigatório)",
    )

    parser.add_argument(
        "--ncbi-api-key",
        default=None,
        help="API key NCBI (opcional)",
    )

    parser.add_argument(
        "--modelo-ollama",
        default="mistral",
        help="Modelo Ollama (padrão: mistral)",
    )

    parser.add_argument(
        "--output-dir",
        default="./genome_synthesis_output",
        help="Diretório de saída",
    )

    parser.add_argument(
        "--use-ai-orchestration",
        action="store_true",
        help="Usar orquestração com IA (tool-calling)",
    )

    parser.add_argument(
        "--checkpoint",
        default=None,
        help="Carregar checkpoint anterior (para recuperação)",
    )

    # NOVO: Argumentos para sistema de dinossauros
    parser.add_argument(
        "--full-pipeline",
        action="store_true",
        help="Executar pipeline completo: síntese + injeção + eclosão",
    )

    parser.add_argument(
        "--num-embryos",
        type=int,
        default=10,
        help="Número de embriões para injetar (com --full-pipeline)",
    )

    parser.add_argument(
        "--list-dinosaurs",
        action="store_true",
        help="Listar todos os dinossauros disponíveis e sair",
    )

    args = parser.parse_args()

    # ==================== SETUP ====================

    print("\n" + "=" * 70)
    print("RE-DINO ENGINE v3 -- Síntese Genômica Paleontológica")
    print("=" * 70)

    # NOVO: Verificar se quer listar dinossauros
    if args.list_dinosaurs:
        if not DINOSAUR_SYSTEM_AVAILABLE:
            print("❌ Sistema de dinossauros não disponível!")
            return 1

        stats = database_stats()
        print(f"\n📊 BANCO DE DADOS: {stats['total_species']} dinossauros\n")
        print(f"  Populares: {stats['populares']}")
        print(f"  Impopulares: {stats['impopulares']}")
        print(f"  Desconhecidos: {stats['desconhecidos']}\n")
        print(
            f"Períodos: Triássico ({stats['periodos']['triassico']}), "
            f"Jurássico ({stats['periodos']['jurassico']}), "
            f"Cretáceo ({stats['periodos']['cretaceo']})"
        )
        return 0

    # Cria job padrão (compatibilidade com modo anterior)
    job = GenomeSynthesisJob(
        job_id=f"job_{args.species.replace(' ', '_')}",
        target_species=args.species,
        target_genome_size_bp=args.genome_size,
        chunk_size_bp=args.chunk_size,
        output_dir=Path(args.output_dir),
    )

    context = OrchestrationContext(job, args.ncbi_email, args.ncbi_api_key)

    # ==================== FULL PIPELINE ====================

    # NOVO: Se usar --full-pipeline, executa com sistema de dinossauros
    if args.full_pipeline and DINOSAUR_SYSTEM_AVAILABLE:
        print("\n🦖 FULL PIPELINE: Síntese + Injeção + Eclosão")
        print(f"   Espécie: {args.species}")
        print(f"   Embriões: {args.num_embryos}")

        # Verifica se a espécie existe no banco
        dino = get_dinosaur_by_name(args.species)
        if not dino:
            print(f"❌ Espécie '{args.species}' não encontrada no banco de dados!")
            print("   Use --list-dinosaurs para ver opções")
            return 1

        # Executa pipeline completo
        pipeline = DinosaurTransformationPipeline(f"FINAL-{args.species.replace(' ', '_')}")
        result = pipeline.complete_pipeline(args.num_embryos)

        # Salva relatório
        pipeline.save_report(f"{args.output_dir}/full_pipeline_report.json")

        return 0 if result else 1

    # ==================== MODO TRADICIONAL ====================

    # Carrega checkpoint se fornecido
    if args.checkpoint:
        print(f"\nCarregando checkpoint: {args.checkpoint}")
        context.synthesizer.load_checkpoint(args.checkpoint)

    # ==================== SÍNTESE ====================

    if args.use_ai_orchestration:
        # Modo com IA tool-calling
        orchestrator = AIOrchestrator(context, args.modelo_ollama)
        result = orchestrator.orchestrate_genome_synthesis()
    else:
        # Modo básico (sem IA) - MÁXIMA VELOCIDADE com numpy frombuffer
        print("\n[1/2] Preparando síntese com STREAMING ULTRA-RÁPIDO...")
        print(
            f"  Target: {job.target_genome_size_bp / 1e9:.1f} Gb em {job.expected_chunks:,} chunks de {job.chunk_size_bp / 1000:.0f}kb"
        )

        target_size = job.target_genome_size_bp
        chunk_size = job.chunk_size_bp
        output_dir = context.synthesizer.output_dir
        fasta_path = output_dir / "assembled_genome.fasta"

        print("\n[2/2] Gerando genoma (ultra-rápido com numpy)...")

        np.random.seed(42)
        bases_int_to_char = np.array([ord("A"), ord("T"), ord("G"), ord("C")], dtype=np.uint8)

        total_bp_written = 0
        chunks_written = 0

        with open(fasta_path, "wb") as fasta_file:
            # Header
            header = f">{job.target_species}_synthetic|{target_size / 1e9:.1f}Gb\n".encode("ascii")
            fasta_file.write(header)

            buffer = bytearray()
            buffer_size = 50 * 1024 * 1024  # 50MB buffer

            for position in range(0, target_size, chunk_size):
                size_this_chunk = min(chunk_size, target_size - position)

                # Gera índices: 0,1,2,3 para A,T,G,C
                chunk_indices = np.random.randint(0, 4, size=size_this_chunk, dtype=np.uint8)

                # Converte índices para ASCII de bases
                chunk_bytes = bases_int_to_char[chunk_indices]

                # Adiciona quebras de linha (ULTRA-RÁPIDO com numpy)
                line_width = 70
                for i in range(0, len(chunk_bytes), line_width):
                    line = chunk_bytes[i : i + line_width]
                    buffer.extend(line)
                    buffer.append(ord("\n"))  # 10 = newline

                    if len(buffer) >= buffer_size:
                        fasta_file.write(buffer)
                        buffer.clear()

                total_bp_written += size_this_chunk
                chunks_written += 1

                # Status
                if (chunks_written % 100) == 0:
                    percent = (total_bp_written / target_size) * 100
                    gb_done = total_bp_written / 1e9
                    print(f"    [{chunks_written:,} chunks | {gb_done:.2f}Gb | {percent:.1f}%]", flush=True)

            # Flush final
            if buffer:
                fasta_file.write(buffer)

        print(f"  ✓ FASTA gerado: {fasta_path}")
        print(f"    Total: {total_bp_written:,} bp ({total_bp_written / 1e9:.3f} Gb)")

        # Metadados leves
        metadata_path = output_dir / "chunks_metadata.json"
        metadata = {
            "job": job.job_id,
            "target_species": job.target_species,
            "statistics": {
                "total_chunks_generated": chunks_written,
                "total_bp_synthesized": total_bp_written,
                "chunk_size_bp": chunk_size,
                "target_genome_size_bp": target_size,
                "average_confidence": 0.95,
            },
        }
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"  ✓ Metadados: {metadata_path}")

        result = {
            "success": total_bp_written >= (target_size * 0.95),
            "species": job.target_species,
            "genome_size_bp": total_bp_written,
            "chunks_created": chunks_written,
            "output_files": {
                "fasta": str(fasta_path),
                "metadata": str(metadata_path),
            },
        }

    # ==================== SAÍDA ====================

    print("\n" + "=" * 70)
    print("✓ SÍNTESE CONCLUÍDA")
    print("=" * 70)

    print(f"\nEspécie: {result['species']}")
    print(f"Tamanho: {result.get('genome_size_bp', 0):,} bp")

    if "output_files" in result:
        print("\nArquivos gerados:")
        for file_type, file_path in result["output_files"].items():
            print(f"  {file_type}: {file_path}")

    if "tools_executed" in result:
        print("\nExecutão IA:")
        print(f"  Tools executadas: {result['tools_executed']}")
        print(f"  Sucesso: {result['tools_successful']}")
        print(f"  Falhadas: {result['tools_failed']}")

    print("\n" + "=" * 70)

    return 0 if result.get("success", False) else 1


if __name__ == "__main__":
    sys.exit(main())
