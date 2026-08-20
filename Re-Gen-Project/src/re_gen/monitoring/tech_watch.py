"""
Re-Gen Tech Watch
==================

Monitor real e periódico de marcos tecnológicos que, se atingidos, tornariam
as Fases 5-7 do pipeline (síntese física de DNA em escala, útero artificial
para espécie ovípara, incubação monitorada) fisicamente executáveis com
hardware real — e não apenas simuladas/bloqueadas como hoje.

O QUE ESTE SCRIPT REALMENTE FAZ
--------------------------------
- Consulta a API pública e real do PubMed/NCBI (Bio.Entrez) por publicações
  recentes que combinem os termos de cada marco tecnológico.
- BUSCA E LÊ O CONTEÚDO REAL dos artigos encontrados (título + resumo,
  via Entrez.efetch) e aplica um MOTOR DE DECISÃO DETERMINÍSTICO baseado em
  regras fixas de texto (regex) — SEM nenhum modelo de IA envolvido:
    1. Exclui o artigo se o tipo de publicação real (campo PublicationType do
       PubMed) for Review/Editorial/Comment/Retracted Publication.
    2. Exclui o artigo se o título+resumo contiver frases de ressalva
       (ex.: "proof of concept", "did not survive", "theoretical", "review").
    3. Só classifica como EVIDÊNCIA FORTE se o título+resumo contiver uma das
       frases de confirmação de resultado real (ex.: "hatched successfully",
       "born alive", "survived to term") — definidas manualmente por marco.
  Essa é uma decisão 100% baseada em regras fixas (if/regex), reproduzível e
  auditável: qualquer pessoa pode ler as mesmas 15-20 linhas de regex e saber
  exatamente por que o script decidiu o que decidiu.
- Opcionalmente verifica a newsroom pública da Colossal Biosciences (fonte
  real, sem chave de API) por palavras-chave.
- Registra o histórico de contagens e das decisões em um arquivo de estado
  local.
- Quando o motor de regras classifica um artigo como EVIDÊNCIA FORTE, dispara
  um alarme sonoro local (via `paplay`/`aplay`/sino de terminal) com nível
  "CONFIRMAÇÃO"; quando há apenas um salto de volume de publicações sem
  evidência forte, dispara um alarme de nível "SINAL" (mais fraco).

LIMITAÇÕES HONESTAS DO MOTOR DE REGRAS (leia isso)
----------------------------------------------------
Um motor de regex não "entende" o artigo — ele casa padrões de texto. Isso
significa que:
- FALSOS POSITIVOS são possíveis: um artigo pode usar a frase "hatched
  successfully" num contexto que não é o marco monitorado (ex.: um estudo
  sobre técnicas de incubação convencional, não um útero artificial).
- FALSOS NEGATIVOS são possíveis: um resultado real pode ser descrito com
  palavras diferentes das previstas nas regras e passar despercebido.
Por isso, mesmo uma classificação de "EVIDÊNCIA FORTE" deve ser lida por
você antes de qualquer mudança de configuração no pipeline. O script reduz
o volume de leitura manual (de milhares de artigos por ano para um punhado
de alertas), mas não substitui o julgamento humano final — nenhuma regra
fixa consegue substituir compreensão real de um texto científico.

O QUE ESTE SCRIPT *NÃO* FAZ
----------------------------
- NÃO usa nenhum modelo de linguagem/IA para ler ou resumir os artigos — a
  decisão é 100% se/então sobre texto e metadados reais retornados pela API
  do PubMed.
- NÃO roda continuamente por 20-40 anos dentro de um processo do Claude —
  isso não existe tecnicamente. Ele é feito para ser agendado no SEU sistema
  operacional (cron/systemd timer), rodando periodicamente por conta própria,
  independente de qualquer conversa com o Claude.
- NÃO ativa ou "libera" nenhuma fase de hardware sozinho. Ele apenas escreve
  a decisão em `tech_watch_state.json`; mudar `hardware_disponivel` no
  pipeline continua manual e deliberada.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("ReGenTechWatch")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-16s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

STATE_DIR = Path(os.environ.get("RE_GEN_HOME", Path.home() / ".re_gen"))
STATE_FILE = STATE_DIR / "tech_watch_state.json"
ALERT_DIR = STATE_DIR / "alertas"

COLOSSAL_NEWSROOM_URL = "https://colossal.com/newsroom/"
NCBI_MIN_INTERVAL_SECONDS = 0.4  # respeita o limite de requisições do NCBI sem API key


@dataclass
class Marco:
    """Um marco tecnológico monitorável, com sua consulta ao PubMed e as
    regras fixas (regex) que decidem se um artigo encontrado é evidência
    real do marco, sem nenhum modelo de IA envolvido."""

    id: str
    titulo: str
    fase_relacionada: str  # ex.: "Fase 5 (síntese física de DNA)"
    pubmed_query: str
    limiar_salto: int = 3  # aumento mínimo de hits/mês para disparar alerta de SINAL
    palavras_chave_newsroom: list = field(default_factory=list)
    nota_para_humano: str = ""

    # Regras determinísticas de decisão (regex, case-insensitive).
    # Um artigo só vira "EVIDÊNCIA FORTE" se casar >=1 padrão de
    # `frases_confirmacao` E não casar nenhum de `frases_exclusao` E seu
    # tipo de publicação real não estiver em `tipos_publicacao_excluidos`.
    frases_confirmacao: list = field(default_factory=list)
    frases_exclusao: list = field(default_factory=list)
    tipos_publicacao_excluidos: list = field(default_factory=lambda: [
        "Review", "Editorial", "Comment", "Retracted Publication",
        "Retraction of Publication", "News", "Congress",
    ])


MARCOS: list[Marco] = [
    Marco(
        id="utero_artificial_oviparo",
        titulo="Útero/incubadora artificial funcional para espécie ovípara "
               "(ave ou réptil) gerando descendente vivo a termo",
        fase_relacionada="Fase 6/7 (injeção em embrião + incubação)",
        pubmed_query=(
            '("artificial womb"[tiab] OR "ectogenesis"[tiab] OR '
            '"ex-utero"[tiab] OR "artificial egg"[tiab]) AND '
            '(avian[tiab] OR reptile[tiab] OR oviparous[tiab] OR bird[tiab])'
        ),
        limiar_salto=2,
        palavras_chave_newsroom=["artificial womb", "ectogenesis", "synthetic egg"],
        nota_para_humano=(
            "Confirme se o experimento produziu um animal vivo e viável até o "
            "fim da gestação/incubação, não apenas até um estágio parcial."
        ),
        frases_confirmacao=[
            r"hatched successfully",
            r"live young",
            r"born alive",
            r"survived to (hatching|term)",
            r"full[- ]term",
            r"viable hatchling",
            r"(healthy )?chicks? (were |was )?born",
            r"delivered [a-z ]{0,20}healthy",
            r"successfully raised to (adulthood|maturity)",
        ],
        frases_exclusao=[
            r"\breview\b",
            r"\bperspective\b",
            r"proof[- ]of[- ]concept",
            r"\btheoretical\b",
            r"\bproposed\b",
            r"feasibility study",
            r"did not survive",
            r"failed to (survive|hatch|develop)",
            r"\bpreliminary\b",
            r"in principle",
        ],
    ),
    Marco(
        id="sintese_genoma_completo_complexo",
        titulo="Síntese de novo de genoma completo (escala Gb) de organismo complexo",
        fase_relacionada="Fase 5 (síntese física de DNA)",
        pubmed_query=(
            '("de novo genome synthesis"[tiab] OR "whole genome synthesis"[tiab] OR '
            '"synthetic genome"[tiab]) AND (eukaryote[tiab] OR vertebrate[tiab] '
            'OR chromosome[tiab])'
        ),
        limiar_salto=2,
        nota_para_humano=(
            "Confirme a escala real (Gb, não apenas genes isolados) e se o "
            "genoma sintetizado foi funcional em uma célula viva."
        ),
        frases_confirmacao=[
            r"functional in (a )?living cell",
            r"viable (synthetic )?cell",
            r"successfully synthesi[sz]ed the (entire|complete|whole) genome",
            r"chromosome[- ]scale synthesis achieved",
            r"fully functional synthetic genome",
            r"gigabase[- ]scale synthesis",
        ],
        frases_exclusao=[
            r"\breview\b",
            r"\bperspective\b",
            r"\broadmap\b",
            r"proposed strategy",
            r"partial synthesis",
            r"\bin silico\b",
            r"\btheoretical\b",
        ],
    ),
    Marco(
        id="utero_artificial_humano_funcional",
        titulo="Primeira gestação humana (parcial ou total) bem-sucedida em útero artificial",
        fase_relacionada="Indicador de maturidade geral da tecnologia de suporte de vida embrionário",
        pubmed_query=(
            '("artificial womb"[tiab] OR "ectogenesis"[tiab]) AND '
            '(human[tiab] OR clinical[tiab]) AND (trial[tiab] OR neonate[tiab])'
        ),
        limiar_salto=3,
        frases_confirmacao=[
            r"first human (infant|baby)[a-z ]{0,20}born",
            r"successfully gestated",
            r"survived [a-z ]{0,20}artificial womb",
            r"clinical trial [a-z ]{0,20}successful",
        ],
        frases_exclusao=[
            r"\breview\b", r"\bethical\b", r"no human", r"not yet",
            r"animal model only", r"\btheoretical\b",
        ],
    ),
    Marco(
        id="sintetizador_dna_comercial_escala_genoma",
        titulo="Sintetizador de DNA de bancada comercialmente disponível em escala de genoma completo",
        fase_relacionada="Fase 5 (síntese física de DNA)",
        pubmed_query=(
            '("benchtop DNA synthesizer"[tiab] OR "DNA printer"[tiab]) AND '
            '(commercial[tiab] OR "gigabase"[tiab])'
        ),
        limiar_salto=2,
        frases_confirmacao=[
            r"commercially available",
            r"now on the market",
            r"FDA[- ]cleared",
            r"launched [a-z ]{0,20}synthesizer",
        ],
        frases_exclusao=[
            r"\breview\b", r"\bprototype\b", r"proof[- ]of[- ]concept",
            r"in development", r"\btheoretical\b",
        ],
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# ESTADO PERSISTENTE
# ─────────────────────────────────────────────────────────────────────────────

def _carregar_estado() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Estado corrompido (%s); recriando do zero.", exc)
    return {"marcos": {}, "criado_em": datetime.now(timezone.utc).isoformat()}


def _salvar_estado(estado: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# CONSULTA REAL AO PUBMED (NCBI Entrez) — mesma API já usada no pipeline
# ─────────────────────────────────────────────────────────────────────────────

def contar_publicacoes_pubmed(query: str, email: str, dias: int = 30,
                               api_key: Optional[str] = None) -> int:
    """Retorna o número real de artigos indexados no PubMed nos últimos `dias`."""
    try:
        from Bio import Entrez
    except ImportError as exc:
        raise RuntimeError(
            "biopython não instalado — rode: pip install biopython"
        ) from exc

    Entrez.email = email
    if api_key:
        Entrez.api_key = api_key

    data_fim = datetime.now(timezone.utc)
    data_inicio = data_fim - timedelta(days=dias)
    query_com_data = (
        f"({query}) AND "
        f'("{data_inicio:%Y/%m/%d}"[PDAT] : "{data_fim:%Y/%m/%d}"[PDAT])'
    )

    handle = Entrez.esearch(db="pubmed", term=query_com_data, retmax=0)
    resultado = Entrez.read(handle)
    handle.close()
    time.sleep(NCBI_MIN_INTERVAL_SECONDS)
    return int(resultado.get("Count", 0))


@dataclass
class Evidencia:
    """Resultado da leitura real de um artigo e da decisão determinística
    (sem IA) sobre se ele confirma o marco monitorado."""

    pmid: str
    titulo: str
    texto_completo: str       # título + resumo real extraído do PubMed, na íntegra
    resumo_extrativo: str      # resumo gerado pelo algoritmo de Luhn (sem IA)
    tipos_publicacao: list
    confirmado: bool
    motivo: str


def _extrair_texto_artigo(registro: dict) -> tuple[str, str, str, list[str]]:
    """Extrai (pmid, titulo, resumo, tipos_publicacao) de um registro real
    retornado por Entrez.efetch (formato MedlineCitation XML)."""
    citacao = registro["MedlineCitation"]
    pmid = str(citacao["PMID"])
    artigo = citacao["Article"]
    titulo = str(artigo.get("ArticleTitle", ""))

    resumo_partes = []
    abstract = artigo.get("Abstract", {})
    for trecho in abstract.get("AbstractText", []):
        resumo_partes.append(str(trecho))
    resumo = " ".join(resumo_partes)

    tipos = [str(t) for t in artigo.get("PublicationTypeList", [])]

    return pmid, titulo, resumo, tipos


# ─────────────────────────────────────────────────────────────────────────────
# ALGORITMO 1: RESUMO EXTRATIVO POR FREQUÊNCIA DE PALAVRAS (LUHN, 1958)
#
# Este é um algoritmo clássico de processamento de texto, puramente
# matemático (contagem de frequência + soma de pesos por sentença) — não é
# um modelo treinado, não tem parâmetros aprendidos, não é uma rede neural.
# Referência: H. P. Luhn, "The Automatic Creation of Literature Abstracts",
# IBM Journal of Research and Development, 1958.
# ─────────────────────────────────────────────────────────────────────────────

_STOPWORDS_EN = frozenset("""
a an the of in on at to for and or but is are was were be been being
this that these those it its their his her they we you i as by with
from into about not no can could may might will would should shall
""".split())


def _tokenizar_sentencas(texto: str) -> list[str]:
    """Divide o texto em sentenças usando pontuação como delimitador.
    Regra fixa, sem nenhum modelo de segmentação treinado."""
    partes = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", texto.strip())
    return [p.strip() for p in partes if p.strip()]


def _tokenizar_palavras(sentenca: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", sentenca.lower())


def resumir_por_frequencia_luhn(texto: str, n_sentencas: int = 2) -> str:
    """Resumo extrativo determinístico (algoritmo de Luhn, 1958).

    Passo a passo (100% matemático, sem IA):
      1. Divide o texto em sentenças.
      2. Conta a frequência de cada palavra significativa (exclui stopwords).
      3. Pontua cada sentença somando a frequência das suas palavras.
      4. Seleciona as `n_sentencas` de maior pontuação, na ORDEM ORIGINAL
         em que aparecem no texto (preserva a lógica do argumento).

    Isso não "entende" semântica — mede importância estatística de palavras.
    Ainda assim, para resumos científicos curtos (resumos de artigo), é uma
    técnica clássica e eficaz para destacar as sentenças mais informativas.
    """
    sentencas = _tokenizar_sentencas(texto)
    if len(sentencas) <= n_sentencas:
        return texto.strip()

    frequencia: dict[str, int] = {}
    for sentenca in sentencas:
        for palavra in _tokenizar_palavras(sentenca):
            if palavra in _STOPWORDS_EN or len(palavra) <= 2:
                continue
            frequencia[palavra] = frequencia.get(palavra, 0) + 1

    if not frequencia:
        return texto.strip()

    pontuacoes = []
    for indice, sentenca in enumerate(sentencas):
        palavras = _tokenizar_palavras(sentenca)
        if not palavras:
            pontuacao = 0.0
        else:
            pontuacao = sum(frequencia.get(p, 0) for p in palavras) / len(palavras)
        pontuacoes.append((indice, pontuacao))

    top_indices = {i for i, _ in sorted(pontuacoes, key=lambda x: x[1], reverse=True)[:n_sentencas]}
    resumo = " ".join(sentencas[i] for i in sorted(top_indices))
    return resumo


# ─────────────────────────────────────────────────────────────────────────────
# ALGORITMO 2: DETECÇÃO DE NEGAÇÃO POR JANELA DE CONTEXTO
#
# Técnica clássica de PLN baseada em regras (não estatística, não treinada):
# olha as N palavras imediatamente ANTES do trecho que casou com a regex de
# confirmação. Se alguma delas for um marcador de negação, o "match" é
# invalidado — porque "did NOT hatch successfully" não pode contar como
# confirmação, mesmo contendo literalmente "hatch successfully".
# ─────────────────────────────────────────────────────────────────────────────

_MARCADORES_NEGACAO = frozenset({
    "not", "no", "never", "n't", "without", "fail", "failed", "fails",
    "failing", "unable", "unsuccessful", "unsuccessfully", "lack",
    "lacked", "lacking", "absence", "cannot", "can't", "couldn't",
    "didn't", "doesn't", "unfortunately",
})

_JANELA_NEGACAO_PALAVRAS = 6


def _match_esta_negado(texto_lower: str, match: re.Match, janela: int = _JANELA_NEGACAO_PALAVRAS) -> bool:
    """Verifica se as `janela` palavras antes do match contêm um marcador de
    negação. Retorna True se o match estiver negado (deve ser descartado)."""
    inicio = match.start()
    contexto_antes = texto_lower[max(0, inicio - 80):inicio]  # ~80 chars ~ janela de palavras
    palavras_antes = re.findall(r"[a-zA-Z']+", contexto_antes)[-janela:]
    return any(p in _MARCADORES_NEGACAO for p in palavras_antes)


def _decidir_por_regras(texto: str, tipos_publicacao: list[str], marco: Marco) -> tuple[bool, str]:
    """Motor de decisão determinístico (regex + detecção de negação por
    janela de contexto), sem nenhum modelo de IA. Retorna (confirmado, motivo)."""
    texto_lower = texto.lower()

    for tipo_excluido in marco.tipos_publicacao_excluidos:
        if tipo_excluido in tipos_publicacao:
            return False, f"tipo de publicação excluído: '{tipo_excluido}'"

    for padrao in marco.frases_exclusao:
        if re.search(padrao, texto_lower):
            return False, f"contém frase de ressalva/exclusão: '{padrao}'"

    for padrao in marco.frases_confirmacao:
        match = re.search(padrao, texto_lower)
        if not match:
            continue
        if _match_esta_negado(texto_lower, match):
            # Achou a frase, mas está negada no contexto (ex.: "did not hatch
            # successfully") — continua procurando outras frases de confirmação
            # em vez de aceitar este match.
            continue
        return True, f"contém frase de confirmação de resultado (não negada): '{padrao}'"

    return False, "nenhuma frase de confirmação encontrada (ou todas estavam negadas pelo contexto)"


def buscar_e_ler_artigos(marco: Marco, email: str, dias: int = 30,
                          api_key: Optional[str] = None,
                          max_artigos: int = 20) -> list[Evidencia]:
    """Busca os artigos reais do PubMed para este marco, LÊ o título+resumo de
    cada um (via Entrez.efetch) e aplica o motor de regras determinístico.

    Nenhuma etapa aqui usa IA: a busca é uma chamada de API real ao NCBI, e a
    decisão é regex fixo sobre o texto retornado.
    """
    try:
        from Bio import Entrez
    except ImportError as exc:
        raise RuntimeError(
            "biopython não instalado — rode: pip install biopython"
        ) from exc

    Entrez.email = email
    if api_key:
        Entrez.api_key = api_key

    data_fim = datetime.now(timezone.utc)
    data_inicio = data_fim - timedelta(days=dias)
    query_com_data = (
        f"({marco.pubmed_query}) AND "
        f'("{data_inicio:%Y/%m/%d}"[PDAT] : "{data_fim:%Y/%m/%d}"[PDAT])'
    )

    handle = Entrez.esearch(db="pubmed", term=query_com_data, retmax=max_artigos)
    busca = Entrez.read(handle)
    handle.close()
    time.sleep(NCBI_MIN_INTERVAL_SECONDS)

    ids = busca.get("IdList", [])
    if not ids:
        return []

    handle = Entrez.efetch(db="pubmed", id=ids, rettype="abstract", retmode="xml")
    registros = Entrez.read(handle)
    handle.close()
    time.sleep(NCBI_MIN_INTERVAL_SECONDS)

    evidencias: list[Evidencia] = []
    for registro in registros.get("PubmedArticle", []):
        try:
            pmid, titulo, resumo, tipos = _extrair_texto_artigo(registro)
        except (KeyError, TypeError) as exc:
            logger.debug("Registro do PubMed sem campos esperados: %s", exc)
            continue

        texto_completo = f"{titulo} {resumo}".strip()
        confirmado, motivo = _decidir_por_regras(texto_completo, tipos, marco)
        resumo_extrativo = resumir_por_frequencia_luhn(resumo or titulo, n_sentencas=2)

        evidencias.append(Evidencia(
            pmid=pmid,
            titulo=titulo,
            texto_completo=texto_completo,
            resumo_extrativo=resumo_extrativo,
            tipos_publicacao=tipos,
            confirmado=confirmado,
            motivo=motivo,
        ))

    return evidencias


def verificar_newsroom_colossal(palavras_chave: list[str], timeout: int = 15) -> list[str]:
    """Verifica a newsroom pública da Colossal Biosciences por palavras-chave reais.

    Retorna a lista de palavras-chave encontradas. Falha graciosamente (lista
    vazia) se a página não puder ser acessada — isso não derruba o monitor.
    """
    try:
        import requests
    except ImportError:
        logger.warning("`requests` não instalado — pulando verificação de newsroom.")
        return []

    try:
        resp = requests.get(COLOSSAL_NEWSROOM_URL, timeout=timeout,
                             headers={"User-Agent": "re-gen-tech-watch/1.0"})
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Não foi possível acessar a newsroom da Colossal: %s", exc)
        return []

    texto = resp.text.lower()
    return [kw for kw in palavras_chave if kw.lower() in texto]


# ─────────────────────────────────────────────────────────────────────────────
# ALARME LOCAL
# ─────────────────────────────────────────────────────────────────────────────

def disparar_alarme(marco: Marco, detalhes: str, nivel: str = "SINAL",
                     evidencias: Optional[list["Evidencia"]] = None) -> None:
    """Dispara um alarme sonoro real na máquina local e grava o alerta em disco,
    incluindo o TEXTO COMPLETO extraído de cada artigo (título + resumo real do
    PubMed) e o resumo extrativo gerado pelo algoritmo de Luhn — para que você
    consiga ler tudo direto no arquivo de alerta, sem precisar abrir a URL.

    nivel="SINAL"       -> salto no volume de publicações, sem confirmação por regras.
    nivel="CONFIRMACAO" -> o motor de regras determinístico achou pelo menos um
                           artigo real com evidência textual do marco.
    """
    ALERT_DIR.mkdir(parents=True, exist_ok=True)
    arquivo_alerta = ALERT_DIR / f"ALERTA_{nivel}_{marco.id}_{datetime.now():%Y%m%d_%H%M%S}.txt"
    conteudo = (
        f"RE-GEN TECH WATCH — [{nivel}]\n"
        f"{'=' * 70}\n"
        f"Marco:            {marco.titulo}\n"
        f"Fase relacionada: {marco.fase_relacionada}\n"
        f"Detectado em:     {datetime.now().isoformat()}\n"
        f"Detalhes:         {detalhes}\n\n"
    )
    if nivel == "CONFIRMACAO":
        conteudo += (
            "O motor de regras determinístico (regex + detecção de negação por\n"
            "janela de contexto, sem IA) encontrou pelo menos um artigo real cujo\n"
            "título/resumo casa com as frases de confirmação definidas para este\n"
            "marco, sem estar negado no contexto, e que NÃO é um review/editorial.\n"
            "Ainda assim, LEIA o texto abaixo com atenção antes de mudar qualquer\n"
            "configuração de hardware — regras fixas podem produzir falsos\n"
            "positivos.\n"
        )
    else:
        conteudo += (
            "Isto é apenas um SALTO NO VOLUME de publicações — nenhum artigo foi\n"
            "confirmado pelo motor de regras ainda. Pode ser ruído (um evento não\n"
            "relacionado, uma conferência, etc.). Revise o texto abaixo.\n"
        )
    if marco.nota_para_humano:
        conteudo += f"\nNota para revisão humana: {marco.nota_para_humano}\n"

    if evidencias:
        conteudo += f"\n{'─' * 70}\nARTIGOS — TEXTO EXTRAÍDO (sem precisar abrir a URL)\n{'─' * 70}\n"
        for i, ev in enumerate(evidencias, start=1):
            conteudo += (
                f"\n[{i}] PMID {ev.pmid}  "
                f"(https://pubmed.ncbi.nlm.nih.gov/{ev.pmid}/)\n"
                f"Tipo(s) de publicação: {', '.join(ev.tipos_publicacao) or 'não informado'}\n"
                f"Decisão do motor de regras: "
                f"{'CONFIRMADO' if ev.confirmado else 'não confirmado'} — {ev.motivo}\n\n"
                f"RESUMO EXTRATIVO (algoritmo de Luhn, 2 sentenças mais relevantes):\n"
                f"{ev.resumo_extrativo}\n\n"
                f"TEXTO COMPLETO (título + resumo real extraído do PubMed):\n"
                f"{ev.texto_completo}\n"
                f"{'-' * 50}\n"
            )

    arquivo_alerta.write_text(conteudo, encoding="utf-8")
    logger.warning("!!! [%s] %s — ver %s", nivel, marco.titulo, arquivo_alerta)

    # Exibe o texto completo também no terminal (stdout), para leitura imediata
    # sem precisar abrir o arquivo ou qualquer URL.
    print("\n" + conteudo)

    # Tenta tocar um som real via utilitários comuns do Linux (Kali inclui pulseaudio/alsa).
    tocou = False
    for comando in (["paplay", "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"],
                    ["aplay", "/usr/share/sounds/alsa/Front_Center.wav"],
                    ["speaker-test", "-t", "sine", "-f", "1000", "-l", "1"]):
        try:
            subprocess.run(comando, check=True, timeout=5,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            tocou = True
            break
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue

    if not tocou:
        # Sino ASCII do terminal como último recurso (funciona na maioria dos terminais)
        sys.stdout.write("\a" * 5)
        sys.stdout.flush()

    # Notificação de desktop, se disponível (opcional, não falha se ausente)
    try:
        urgencia = "critical" if nivel == "CONFIRMACAO" else "normal"
        subprocess.run(
            ["notify-send", "-u", urgencia, f"Re-Gen Tech Watch [{nivel}]",
             marco.titulo],
            check=False, timeout=5,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# CICLO PRINCIPAL DE VERIFICAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def executar_ciclo(email: str, api_key: Optional[str] = None,
                    janela_dias: int = 30, verificar_newsroom: bool = True,
                    max_artigos_por_marco: int = 20) -> dict:
    """Executa uma verificação de todos os marcos: conta publicações, LÊ o
    conteúdo real das mais recentes e aplica o motor de decisão determinístico
    (regex fixo, sem IA) sobre cada uma. Retorna um resumo com a decisão."""
    estado = _carregar_estado()
    resumo = {"executado_em": datetime.now(timezone.utc).isoformat(), "marcos": {}}

    for marco in MARCOS:
        registro_anterior = estado["marcos"].get(marco.id, {"historico": []})
        try:
            contagem = contar_publicacoes_pubmed(
                marco.pubmed_query, email=email, dias=janela_dias, api_key=api_key
            )
        except RuntimeError as exc:
            logger.error("Falha ao consultar PubMed para '%s': %s", marco.id, exc)
            continue

        historico = registro_anterior.get("historico", [])
        media_anterior = (
            sum(h["contagem"] for h in historico[-6:]) / len(historico[-6:])
            if historico else 0
        )
        historico.append({
            "data": datetime.now(timezone.utc).isoformat(),
            "contagem": contagem,
        })
        historico = historico[-60:]  # mantém só os últimos 60 ciclos (histórico razoável)

        salto = contagem - media_anterior
        alerta_disparado = False
        evidencias_confirmadas: list[Evidencia] = []

        if contagem > 0:
            try:
                evidencias = buscar_e_ler_artigos(
                    marco, email=email, dias=janela_dias, api_key=api_key,
                    max_artigos=max_artigos_por_marco,
                )
            except RuntimeError as exc:
                logger.error("Falha ao ler artigos do PubMed para '%s': %s", marco.id, exc)
                evidencias = []

            evidencias_confirmadas = [e for e in evidencias if e.confirmado]

            if evidencias_confirmadas:
                citacoes = "; ".join(
                    f"PMID {e.pmid}: {e.titulo[:120]}" for e in evidencias_confirmadas[:3]
                )
                disparar_alarme(
                    marco,
                    detalhes=(
                        f"{len(evidencias_confirmadas)} artigo(s) real(is) confirmado(s) "
                        f"pelo motor de regras. {citacoes}"
                    ),
                    nivel="CONFIRMACAO",
                    evidencias=evidencias_confirmadas,
                )
                alerta_disparado = True
            elif salto >= marco.limiar_salto:
                disparar_alarme(
                    marco,
                    detalhes=(
                        f"{contagem} publicações no PubMed nos últimos {janela_dias} dias "
                        f"(média anterior: {media_anterior:.1f}), mas nenhuma confirmada "
                        f"pelo motor de regras ainda."
                    ),
                    nivel="SINAL",
                    evidencias=[e for e in evidencias if not e.confirmado][:3],
                )
                alerta_disparado = True

        if verificar_newsroom and marco.palavras_chave_newsroom:
            encontradas = verificar_newsroom_colossal(marco.palavras_chave_newsroom)
            if encontradas:
                disparar_alarme(
                    marco,
                    detalhes=f"Newsroom da Colossal Biosciences menciona: {', '.join(encontradas)}.",
                    nivel="SINAL",
                )
                alerta_disparado = True

        estado["marcos"][marco.id] = {"historico": historico}
        resumo["marcos"][marco.id] = {
            "titulo": marco.titulo,
            "contagem_atual": contagem,
            "media_anterior": round(media_anterior, 1),
            "artigos_confirmados_por_regras": [
                {
                    "pmid": e.pmid,
                    "titulo": e.titulo,
                    "motivo": e.motivo,
                    "resumo_extrativo": e.resumo_extrativo,
                    "texto_completo": e.texto_completo,
                }
                for e in evidencias_confirmadas
            ],
            "alerta_disparado": alerta_disparado,
        }
        logger.info(
            "[%s] contagem=%d média_anterior=%.1f confirmados=%d alerta=%s",
            marco.id, contagem, media_anterior, len(evidencias_confirmadas), alerta_disparado,
        )

    _salvar_estado(estado)
    return resumo


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="re-gen-watch",
        description=(
            "Verifica sinais reais (PubMed + newsroom pública) de marcos "
            "tecnológicos necessários para revival de dinossauros com hardware "
            "real. Feito para ser agendado via cron/systemd, rodando por conta "
            "própria durante anos, sem depender de nenhuma conversa com o Claude."
        ),
    )
    parser.add_argument("--email", required=True,
                         help="Email para a API do NCBI Entrez (exigido pela política do NCBI)")
    parser.add_argument("--api-key", default=None, help="Chave de API do NCBI (opcional, aumenta o limite de requisições)")
    parser.add_argument("--janela-dias", type=int, default=30,
                         help="Janela de dias para contar publicações recentes (padrão: 30)")
    parser.add_argument("--sem-newsroom", action="store_true",
                         help="Não verificar a newsroom da Colossal Biosciences")
    parser.add_argument("--instalar-cron", action="store_true",
                         help="Imprime a linha de crontab pronta para copiar (não instala sozinho)")
    args = parser.parse_args()

    if args.instalar_cron:
        script_path = Path(sys.argv[0]).resolve()
        print("Adicione esta linha ao seu crontab (rode: crontab -e) para checar 1x por mês:\n")
        print(f"0 9 1 * *  re-gen-watch --email {args.email} >> "
              f"{STATE_DIR}/tech_watch.log 2>&1\n")
        print("Isso faz o monitor rodar sozinho, todo dia 1 às 9h, por quantos anos "
              "o seu sistema continuar existindo — sem depender de nenhuma conversa "
              "com o Claude.")
        return 0

    resumo = executar_ciclo(
        email=args.email,
        api_key=args.api_key,
        janela_dias=args.janela_dias,
        verificar_newsroom=not args.sem_newsroom,
    )

    print(json.dumps(resumo, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
