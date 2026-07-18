#!/usr/bin/env python3
"""
main.py -- Re-Dino Engine v2
=============================
Pipeline NOVO com:
  1. Seleção automática de dinossauro (se sem hardware)
  2. Busca inteligente de descendentes vivos (genealogia paleontológica)
  3. Ollama local (sem APIs externas)
  4. Integração com paleontologia real

USO - Modo Padrão (seleção automática):
    python main.py \\
        --gene "cytochrome b" \\
        --host-species "Struthio camelus" \\
        --ncbi-email seu.email@dominio.com

USO - Modo com Hardware Especificado:
    python main.py \\
        --scanner-file caminho/para/leituras.fastq \\
        --gene "cytochrome b" \\
        --host-species "Struthio camelus" \\
        --dinosaur "Tyrannosaurus rex" \\
        --ncbi-email seu.email@dominio.com

USO - Modo Seletor com Preferências:
    python main.py \\
        --gene "cytochrome b" \\
        --preferencia-tamanho-min 8000 \\
        --preferencia-dieta "carnívoro" \\
        --ncbi-email seu.email@dominio.com

REQUISITOS NOVOS:
  - Ollama rodando localmente: `ollama serve`
  - Modelo baixado: `ollama pull llama2` (ou seu preferido)
  - NCBI email sempre necessário (para descendentes vivos)

OPCIONAL:
  - --ncbi-api-key: Sua API key do NCBI (aumenta rate limit)
  - --gerar-relatorio-ia: Gera laudo com Ollama
"""

import argparse
import sys
from pathlib import Path

from re_gen.ai.ollama_integration import obter_cliente_ollama
from re_gen.core.gene_edit_package import build_edit_package, export_edit_package_csv
from re_gen.core.reconstruct import low_confidence_regions, reconstruct_ancestral_sequence
from re_gen.data.descendant_mapper import obter_mapeador
from re_gen.data.dinosaur_selector import (
    CapacidadeHardware,
    ConfiguracaoSelecao,
    SeletorDinossauro,
)
from re_gen.data.paleontology import Dinossauro, obter_sistema_referencia
from re_gen.hardware.scanner_input import ScannerInputError, load_scanner_output, summarize_reads
from re_gen.ncbi.ncbi_reference import (
    NCBIQueryError,
    buscar_painel_referencia_por_paleontologia,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Re-Dino Engine v2: Reconstrução genômica com seleção automática e Ollama local.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # ==================== Entrada ====================
    p.add_argument(
        "--scanner-file",
        default=None,
        help="Caminho do FASTQ/FASTA exportado do sequenciador real (opcional se sem hardware).",
    )

    # ==================== Dinossauro ====================
    p.add_argument(
        "--dinosaur",
        default=None,
        help="Nome científico do dinossauro a reconstruir (ex: 'Tyrannosaurus rex'). "
        "Se omitido, seleciona automaticamente.",
    )
    p.add_argument(
        "--preferencia-dieta",
        choices=["carnívoro", "herbívoro"],
        default=None,
        help="Se seleção automática, preferência por dieta.",
    )
    p.add_argument(
        "--preferencia-tamanho-min",
        type=float,
        default=None,
        help="Se seleção automática, tamanho mínimo em kg.",
    )
    p.add_argument(
        "--preferencia-tamanho-max",
        type=float,
        default=None,
        help="Se seleção automática, tamanho máximo em kg.",
    )
    p.add_argument(
        "--hardware",
        choices=["nenhuma", "basica", "intermediaria", "avancada"],
        default="nenhuma",
        help="Capacidade de hardware disponível (afeta seleção automática).",
    )

    # ==================== Gene e Referências ====================
    p.add_argument(
        "--gene",
        required=True,
        help="Nome do gene de referência a buscar (ex: 'cytochrome b', 'COI').",
    )
    p.add_argument(
        "--host-species",
        required=True,
        help="Espécie hospedeira para o pacote de edição (ex: 'Struthio camelus').",
    )

    # ==================== NCBI ====================
    p.add_argument(
        "--ncbi-email",
        required=True,
        help="Seu e-mail real (exigido pelo NCBI).",
    )
    p.add_argument(
        "--ncbi-api-key",
        default=None,
        help="Sua API key do NCBI (opcional, aumenta rate limit).",
    )

    # ==================== Filtros de Entrada ====================
    p.add_argument(
        "--min-length",
        type=int,
        default=50,
        help="Tamanho mínimo de leitura aceita (padrão: 50).",
    )
    p.add_argument(
        "--min-quality",
        type=float,
        default=7.0,
        help="Qualidade Phred média mínima aceita (padrão: 7.0).",
    )

    # ==================== Saída ====================
    p.add_argument(
        "--output-dir",
        default="./re_dino_output",
        help="Pasta de saída (padrão: ./re_dino_output).",
    )

    # ==================== IA ====================
    p.add_argument(
        "--gerar-relatorio-ia",
        action="store_true",
        help="Gera laudo técnico com Ollama (requer servidor Ollama rodando).",
    )
    p.add_argument(
        "--modelo-ollama",
        default="llama2",
        help="Nome do modelo Ollama a usar (padrão: llama2). Tente 'mistral' se quiser mais rápido.",
    )

    return p.parse_args()


def selecionar_dinossauro_automaticamente(
    hardware: str,
    preferencia_dieta: str | None = None,
    preferencia_tamanho_min: float | None = None,
    preferencia_tamanho_max: float | None = None,
) -> tuple[Dinossauro, float]:
    """
    Seleciona automaticamente qual dinossauro reconstruir.

    Retorna: (dinossauro, score_confiança)
    """
    mapa_hardware = {
        "nenhuma": CapacidadeHardware.NENHUMA,
        "basica": CapacidadeHardware.BASICA,
        "intermediaria": CapacidadeHardware.INTERMEDIARIA,
        "avancada": CapacidadeHardware.AVANCADA,
    }

    config = ConfiguracaoSelecao(
        hardware=mapa_hardware[hardware],
        preferencia_tipo_dieta=preferencia_dieta,
        preferencia_tamanho_min_kg=preferencia_tamanho_min,
        preferencia_tamanho_max_kg=preferencia_tamanho_max,
    )

    seletor = SeletorDinossauro()
    return seletor.selecionar(config)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("RE-DINO ENGINE v2 -- Reconstrução Genômica Paleontológica")
    print("=" * 70)

    # ==================== [1/6] Seleção de Dinossauro ====================
    print("\n[1/6] Selecionando dinossauro para reconstrução...")

    if args.dinosaur:
        # Usuário especificou
        sr = obter_sistema_referencia()
        dinossauro = sr.buscar_por_nome(args.dinosaur)
        if dinossauro is None:
            print(f"ERRO: Dinossauro '{args.dinosaur}' não encontrado no sistema.", file=sys.stderr)
            return 1
        score_selecao = 1.0
        print(f"  Seleção manual: {dinossauro.nome_cientifico}")
    else:
        # Seleção automática
        dinossauro, score_selecao = selecionar_dinossauro_automaticamente(
            hardware=args.hardware,
            preferencia_dieta=args.preferencia_dieta,
            preferencia_tamanho_min=args.preferencia_tamanho_min,
            preferencia_tamanho_max=args.preferencia_tamanho_max,
        )
        print(f"  Seleção automática: {dinossauro.nome_cientifico}")
        print(f"  Score de confiança: {score_selecao:.1%}")
        print(f"  Tamanho estimado: {dinossauro.peso_estimado_kg}kg")
        print(f"  Período: {dinossauro.periodo.value}")

    # ==================== [2/6] Leitura de Scanner (opcional) ====================
    print("\n[2/6] Lendo entrada do sequenciador...")

    if args.scanner_file:
        try:
            reads = load_scanner_output(args.scanner_file, args.min_length, args.min_quality)
            scanner_summary = summarize_reads(reads)
            print(f"  Leituras válidas: {scanner_summary['n_reads']}")
            print(f"  Bases totais: {scanner_summary['total_bases']}")
            print(f"  Qualidade média: {scanner_summary['avg_quality']}")
            best_read = max(reads, key=lambda r: r.length)
            print(f"  Âncora selecionada: {best_read.read_id} ({best_read.length} bases)")
            dna_ancora = best_read.sequence
        except ScannerInputError as e:
            print(f"ERRO no scanner: {e}", file=sys.stderr)
            return 1
    else:
        # Sem hardware: usa sequência consenso sintética de descendentes
        print("  Sem hardware: usaremos descendentes vivos como referência direta")
        mapeador = obter_mapeador()
        descendentes = mapeador.buscar_por_ancestral(dinossauro.nome_cientifico)
        if descendentes:
            print(f"  Descendentes vivos encontrados: {len(descendentes)}")
            for d in descendentes[:3]:
                print(f"    - {d.nome_cientifico} ({d.grupo_taxa})")

        # Simulação: âncora vem do primeira descendente
        # TODO: Replace with actual sequence from extant descendant (FASTA download)
        dna_ancora = "ATGCATGCATGCATGCATGC"  # placeholder curto
        scanner_summary = {
            "n_reads": 0,
            "total_bases": len(dna_ancora),
            "avg_quality": "simulada",
        }

    # ==================== [3/6] Busca de Referências ====================
    print(f"\n[3/6] Buscando referências NCBI para '{args.gene}'...")
    print(f"       Descendentes de: {dinossauro.nome_cientifico}")

    try:
        panel = buscar_painel_referencia_por_paleontologia(
            dinossauro=dinossauro,
            gene=args.gene,
            email=args.ncbi_email,
            api_key=args.ncbi_api_key,
        )
        print(f"  Referências encontradas: {len(panel)}")
        for ref in panel[:5]:
            print(f"    - {ref.species}: {ref.accession} ({ref.length} bases)")
            if ref.fonte_genealogica:
                print(f"      Caminho: {ref.fonte_genealogica}")
    except NCBIQueryError as e:
        print(f"ERRO no NCBI: {e}", file=sys.stderr)
        return 1

    # ==================== [4/6] Reconstrução Ancestral ====================
    print("\n[4/6] Reconstruindo sequência ancestral...")

    try:
        reconstruction = reconstruct_ancestral_sequence(dna_ancora, panel)
        print(f"  Comprimento consenso: {len(reconstruction.consensus_sequence)} bases")
        print(f"  Confiança média: {reconstruction.mean_confidence * 100:.1f}%")
        print(f"  Conteúdo GC: {reconstruction.gc_content}%")

        low_conf = low_confidence_regions(reconstruction)
        if low_conf:
            print(f"  Atenção: {len(low_conf)} região(ões) de baixa confiança")
    except Exception as e:
        print(f"ERRO na reconstrução: {e}", file=sys.stderr)
        return 1

    # Salva FASTA
    consensus_fasta = out_dir / "sequencia_reconstruida.fasta"
    with open(consensus_fasta, "w") as f:
        f.write(
            f">Re-Dino_{dinossauro.nome_cientifico.replace(' ', '_')}|confianca={reconstruction.mean_confidence:.3f}\n"
        )
        seq = reconstruction.consensus_sequence
        for i in range(0, len(seq), 70):
            f.write(seq[i : i + 70] + "\n")
    print(f"  Salvo: {consensus_fasta}")

    # ==================== [5/6] Pacote de Edição Genética ====================
    print(f"\n[5/6] Gerando pacote de edição para hospedeiro '{args.host_species}'...")

    # Busca referência do hospedeiro
    try:
        host_panel = buscar_painel_referencia_por_paleontologia(
            dinossauro=dinossauro,
            gene=args.gene,
            email=args.ncbi_email,
            api_key=args.ncbi_api_key,
        )
        host_ref = next((r for r in host_panel if args.host_species in r.species), None)
        if host_ref is None:
            print(f"  Hospedeiro '{args.host_species}' não está no painel, usando primeira referência.")
            host_ref = host_panel[0]
    except NCBIQueryError:
        print(f"  Aviso: não consegui buscar hospedeiro '{args.host_species}' novamente")
        host_ref = panel[0]  # fallback

    try:
        edit_package = build_edit_package(
            reconstruction=reconstruction,
            host_sequence=host_ref.sequence,
            host_species=args.host_species,
            target_species_label=dinossauro.nome_cientifico,
        )
        print(f"  Identidade genômica: {edit_package.pct_genome_identity}%")
        print(f"  Edições propostas: {edit_package.n_total_edits}")

        edit_csv = out_dir / "pacote_edicao_re_dino.csv"
        export_edit_package_csv(edit_package, str(edit_csv))
        print(f"  Salvo: {edit_csv}")
    except Exception as e:
        print(f"ERRO ao gerar pacote de edição: {e}", file=sys.stderr)
        return 1

    # ==================== [6/6] Relatório com IA (opcional) ====================
    if args.gerar_relatorio_ia:
        print("\n[6/6] Gerando laudo com Ollama local...")

        try:
            from ai_report import gerar_relatorio_com_ollama

            cliente = obter_cliente_ollama()
            cliente.config.modelo = args.modelo_ollama

            if not cliente.validar_conexao():
                print(f"  AVISO: Ollama não está acessível em {cliente.config.endpoint}")
                print("  Inicie com: ollama serve")
                print(f"  E baixe um modelo: ollama pull {args.modelo_ollama}")
            else:
                print(f"  Usando modelo: {args.modelo_ollama}")
                relatorio = gerar_relatorio_com_ollama(
                    reconstruction=reconstruction,
                    edit_package=edit_package,
                    scanner_summary=scanner_summary,
                    target_species_label=dinossauro.nome_cientifico,
                    cliente=cliente,
                )

                relatorio_path = out_dir / "laudo_ia.txt"
                relatorio_path.write_text(relatorio)
                print(f"  Salvo: {relatorio_path}")
                print("\n--- LAUDO ---\n")
                print(relatorio)
        except Exception as e:
            print(f"  Aviso: não consegui gerar laudo com Ollama: {e}")
    else:
        print("\n[6/6] Relatório IA não solicitado (use --gerar-relatorio-ia)")

    # ==================== Resumo Final ====================
    print("\n" + "=" * 70)
    print("✓ Pipeline concluído com sucesso!")
    print("=" * 70)
    print("\nArquivos gerados:")
    print(f"  1. Sequência reconstruída: {consensus_fasta.name}")
    print("     → Envie para fornecedor de síntese (Twist Bioscience, IDT)")
    print(f"\n  2. Pacote de edição genética: {edit_csv.name}")
    print("     → Importe em ferramenta de CRISPR (Benchling, CHOPCHOP)")

    if (out_dir / "laudo_ia.txt").exists():
        print("\n  3. Laudo técnico: laudo_ia.txt")
        print("     → Documentação para laboratório")

    print(f"\nTodos os arquivos em: {out_dir.absolute()}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
