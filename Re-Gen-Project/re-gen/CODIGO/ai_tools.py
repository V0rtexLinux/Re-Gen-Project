"""
ai_tools.py
-----------
Framework de tool-calling para IA (Ollama com Claude-style tools).

A IA pode chamar funções para:
1. Validar segmentos genômicos
2. Sugerir edições/correções
3. Executar CRISPR design
4. Buscar referências
5. Verificar off-targets

Padrão: Tool Calling (similar a Claude / GPT-4 function calling)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any, Optional
from enum import Enum
import json


class ToolType(Enum):
    """Tipos de ferramentas disponíveis para IA."""
    VALIDATOR = "validator"           # Validação genética
    EDITOR = "editor"                 # Edição/correção
    CRISPR = "crispr"                 # Design CRISPR
    SEARCHER = "searcher"             # Busca de referências
    ANALYZER = "analyzer"             # Análise de sequência
    PREDICTOR = "predictor"           # Predição (off-targets, etc)


@dataclass
class ToolParameter:
    """Parâmetro de uma ferramenta."""
    name: str
    type: str                         # "string", "integer", "array", etc
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum_values: Optional[list[str]] = None


@dataclass
class Tool:
    """Definição de uma ferramenta disponível para IA."""
    name: str
    tool_type: ToolType
    description: str
    parameters: list[ToolParameter]
    callable_fn: Callable                # Função Python a executar
    
    def to_schema(self) -> dict:
        """
        Converte para schema JSON (estilo Claude).
        """
        required_params = [p.name for p in self.parameters if p.required]
        
        properties = {}
        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum_values:
                prop["enum"] = param.enum_values
            if param.default is not None:
                prop["default"] = param.default
            properties[param.name] = prop
        
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required_params,
            }
        }
    
    def execute(self, **kwargs) -> Any:
        """Executa a ferramenta com argumentos."""
        return self.callable_fn(**kwargs)


class ToolRegistry:
    """Registro centralizado de ferramentas disponíveis para IA."""
    
    def __init__(self):
        self.tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Registra uma ferramenta."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Obtém uma ferramenta pelo nome."""
        return self.tools.get(name)
    
    def get_tools_by_type(self, tool_type: ToolType) -> list[Tool]:
        """Retorna todas as ferramentas de um tipo específico."""
        return [t for t in self.tools.values() if t.tool_type == tool_type]
    
    def get_all_schemas(self) -> list[dict]:
        """Retorna schemas de todas as ferramentas (para enviar para IA)."""
        return [tool.to_schema() for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, **kwargs) -> dict:
        """
        Executa uma ferramenta e retorna resultado estruturado.
        
        Returns:
            {"success": bool, "result": Any, "error": Optional[str]}
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "result": None,
                "error": f"Ferramenta '{tool_name}' não encontrada",
            }
        
        try:
            result = tool.execute(**kwargs)
            return {
                "success": True,
                "result": result,
                "error": None,
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": f"Erro ao executar '{tool_name}': {str(e)}",
            }


# ==================== FERRAMENTAS CONCRETAS ====================

def validate_sequence(
    sequence: str,
    check_type: str = "all",
) -> dict:
    """
    Valida um segmento DNA.
    
    Args:
        sequence: Sequência DNA
        check_type: "all", "codons", "gc_content", "homopolymers"
    
    Returns:
        Dicionário com resultados de validação
    """
    issues = []
    
    # Check 1: Caracteres válidos
    valid_chars = set("ATCGN")
    invalid = set(sequence.upper()) - valid_chars
    if invalid:
        issues.append(f"Caracteres inválidos: {invalid}")
    
    # Check 2: Sequências homopoliméricas (problemas de síntese)
    seq_upper = sequence.upper()
    for base in "ATCG":
        if base * 10 in seq_upper:  # >10 bases iguais seguidas
            issues.append(f"Homopolímero longo encontrado: {base*10}")
    
    # Check 3: Conteúdo GC
    gc_count = seq_upper.count("G") + seq_upper.count("C")
    gc_percent = (gc_count / len(sequence)) * 100
    if gc_percent < 30 or gc_percent > 70:
        issues.append(f"GC% fora do intervalo ideal (30-70%): {gc_percent:.1f}%")
    
    # Check 4: Codons de parada (se aplicável)
    stop_codons = ["TAA", "TAG", "TGA"]
    stop_count = sum(seq_upper.count(codon) for codon in stop_codons)
    if stop_count > 0:
        issues.append(f"Codons de parada encontrados: {stop_count}")
    
    return {
        "valid": len(issues) == 0,
        "sequence_length": len(sequence),
        "gc_content": gc_percent,
        "issues": issues,
        "severity": "critical" if len(issues) > 2 else ("warning" if issues else "ok"),
    }


def edit_sequence(
    sequence: str,
    edit_type: str,
    position: int,
    new_base: Optional[str] = None,
) -> dict:
    """
    Edita um segmento DNA.
    
    Args:
        sequence: Sequência original
        edit_type: "substitute", "insert", "delete"
        position: Posição (0-indexed)
        new_base: Base nova (para substitute/insert)
    
    Returns:
        Sequência editada
    """
    seq_list = list(sequence)
    
    if edit_type == "substitute":
        if position >= len(seq_list):
            return {"success": False, "error": "Posição fora do intervalo"}
        seq_list[position] = new_base
    
    elif edit_type == "insert":
        seq_list.insert(position, new_base)
    
    elif edit_type == "delete":
        if position >= len(seq_list):
            return {"success": False, "error": "Posição fora do intervalo"}
        seq_list.pop(position)
    
    else:
        return {"success": False, "error": f"Tipo de edição desconhecido: {edit_type}"}
    
    edited = "".join(seq_list)
    return {
        "success": True,
        "edited_sequence": edited,
        "changes": 1,
    }


def design_grna(
    target_sequence: str,
    pam_type: str = "NGG",  # SpCas9 default
    grna_length: int = 20,
) -> dict:
    """
    Desanha guide-RNAs para CRISPR.
    
    Args:
        target_sequence: Sequência alvo
        pam_type: Tipo de PAM ("NGG" para SpCas9)
        grna_length: Comprimento do gRNA (típico: 20)
    
    Returns:
        Lista de gRNAs candidatos
    """
    import re
    
    grnas = []
    seq_upper = target_sequence.upper()
    
    # Encontra PAMs
    # NGG = qualquer base seguida de GG
    pam_pattern = r"[ATCG]GG" if pam_type == "NGG" else pam_type
    
    for match in re.finditer(pam_pattern, seq_upper):
        pam_pos = match.start()
        
        # gRNA é 20bp antes do PAM
        grna_start = max(0, pam_pos - grna_length)
        grna_end = grna_start + grna_length
        
        if grna_end <= len(seq_upper):
            grna_seq = seq_upper[grna_start:grna_end]
            
            # Calcula GC%
            gc = (grna_seq.count("G") + grna_seq.count("C")) / len(grna_seq) * 100
            
            # Score simples (GC% ideal ~50%)
            gc_score = 100 - abs(50 - gc)
            
            grnas.append({
                "grna_sequence": grna_seq,
                "pam_sequence": match.group(),
                "position": grna_start,
                "gc_content": gc,
                "score": gc_score,
            })
    
    # Ordena por score
    grnas.sort(key=lambda g: g["score"], reverse=True)
    
    return {
        "success": True,
        "grnas": grnas[:10],  # Top 10
        "total_found": len(grnas),
    }


def predict_off_targets(
    grna_sequence: str,
    reference_genome: str,
    max_mismatches: int = 3,
) -> dict:
    """
    Prediz off-targets de um gRNA.
    
    Args:
        grna_sequence: Sequência do gRNA
        reference_genome: Genoma de referência
        max_mismatches: Máximo de mismatches tolerados
    
    Returns:
        Lista de potenciais off-targets
    """
    from difflib import SequenceMatcher
    
    off_targets = []
    grna_len = len(grna_sequence)
    
    # Busca por substrings similares
    for i in range(len(reference_genome) - grna_len):
        candidate = reference_genome[i:i+grna_len]
        
        # Calcula similaridade
        matcher = SequenceMatcher(None, grna_sequence, candidate)
        ratio = matcher.ratio()
        mismatches = int((1 - ratio) * grna_len)
        
        if mismatches <= max_mismatches and mismatches > 0:  # Ignora match perfeito
            off_targets.append({
                "position": i,
                "sequence": candidate,
                "mismatches": mismatches,
                "similarity": ratio * 100,
            })
    
    return {
        "success": True,
        "off_targets": off_targets[:20],  # Top 20
        "total_found": len(off_targets),
    }


def search_references(
    query: str,
    num_results: int = 5,
) -> dict:
    """
    Busca referências na internet (sem hardcoded).
    
    Args:
        query: Consulta (gene name, protein, sequence, etc)
        num_results: Número de resultados
    
    Returns:
        Lista de referências com links NCBI/UniProt
    """
    # Esta função será expandida com busca real via APIs
    # Por enquanto, retorna estrutura
    
    return {
        "query": query,
        "results": [],
        "note": "Implementar busca via NCBI API / UniProt / PubMed em ai_reference_fetcher",
    }


# ==================== REGISTRY SETUP ====================

def create_default_registry() -> ToolRegistry:
    """Cria registro com ferramentas padrão."""
    registry = ToolRegistry()
    
    # Tool 1: Validador de sequência
    registry.register(Tool(
        name="validate_sequence",
        tool_type=ToolType.VALIDATOR,
        description="Valida um segmento DNA verificando caracteres válidos, GC%, homopolímeros e codons de parada",
        parameters=[
            ToolParameter(
                name="sequence",
                type="string",
                description="Sequência DNA a validar (apenas ATCGN)",
                required=True,
            ),
            ToolParameter(
                name="check_type",
                type="string",
                description="Tipo de validação",
                required=False,
                enum_values=["all", "codons", "gc_content", "homopolymers"],
                default="all",
            ),
        ],
        callable_fn=validate_sequence,
    ))
    
    # Tool 2: Editor de sequência
    registry.register(Tool(
        name="edit_sequence",
        tool_type=ToolType.EDITOR,
        description="Edita um segmento DNA (substituição, inserção, deleção)",
        parameters=[
            ToolParameter(
                name="sequence",
                type="string",
                description="Sequência original",
                required=True,
            ),
            ToolParameter(
                name="edit_type",
                type="string",
                description="Tipo de edição",
                required=True,
                enum_values=["substitute", "insert", "delete"],
            ),
            ToolParameter(
                name="position",
                type="integer",
                description="Posição no genoma",
                required=True,
            ),
            ToolParameter(
                name="new_base",
                type="string",
                description="Base nova (para substitute/insert)",
                required=False,
            ),
        ],
        callable_fn=edit_sequence,
    ))
    
    # Tool 3: Design de gRNA
    registry.register(Tool(
        name="design_grna",
        tool_type=ToolType.CRISPR,
        description="Desanha guide-RNAs ótimos para CRISPR-Cas9",
        parameters=[
            ToolParameter(
                name="target_sequence",
                type="string",
                description="Sequência alvo",
                required=True,
            ),
            ToolParameter(
                name="pam_type",
                type="string",
                description="Tipo de PAM",
                required=False,
                default="NGG",
            ),
            ToolParameter(
                name="grna_length",
                type="integer",
                description="Comprimento do gRNA",
                required=False,
                default=20,
            ),
        ],
        callable_fn=design_grna,
    ))
    
    # Tool 4: Predição de off-targets
    registry.register(Tool(
        name="predict_off_targets",
        tool_type=ToolType.PREDICTOR,
        description="Prediz off-targets potenciais de um gRNA",
        parameters=[
            ToolParameter(
                name="grna_sequence",
                type="string",
                description="Sequência do gRNA",
                required=True,
            ),
            ToolParameter(
                name="reference_genome",
                type="string",
                description="Genoma de referência",
                required=True,
            ),
            ToolParameter(
                name="max_mismatches",
                type="integer",
                description="Máximo de mismatches",
                required=False,
                default=3,
            ),
        ],
        callable_fn=predict_off_targets,
    ))
    
    # Tool 5: Busca de referências
    registry.register(Tool(
        name="search_references",
        tool_type=ToolType.SEARCHER,
        description="Busca referências científicas na internet (NCBI, UniProt, PubMed)",
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Consulta (gene name, protein, sequence)",
                required=True,
            ),
            ToolParameter(
                name="num_results",
                type="integer",
                description="Número de resultados",
                required=False,
                default=5,
            ),
        ],
        callable_fn=search_references,
    ))
    
    return registry


# Instância global
_REGISTRY = None


def get_tool_registry() -> ToolRegistry:
    """Retorna o registry singleton."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = create_default_registry()
    return _REGISTRY
