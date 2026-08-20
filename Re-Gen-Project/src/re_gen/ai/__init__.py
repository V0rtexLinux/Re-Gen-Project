"""AI integration modules (Ollama tool-calling)."""

__all__ = [
    "PROMPT_TEMPLATE_RELATORIO",
    "PROMPT_TEMPLATE_VALIDACAO",
    # ai_report
    "AIReportError",
    "ClienteOllama",
    "ConfiguracaoOllama",
    # ollama_integration
    "OllamaModeloRecomendado",
    "Tool",
    "ToolParameter",
    "ToolRegistry",
    # ai_tools
    "ToolType",
    "create_default_registry",
    "criar_cliente_padrao",
    "design_grna",
    "edit_sequence",
    "generate_lab_report",
    "gerar_relatorio_com_ollama",
    "get_tool_registry",
    "obter_cliente_ollama",
    "predict_off_targets",
    "search_references",
    "validate_sequence",
]
