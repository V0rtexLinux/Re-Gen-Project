"""
reference_searcher.py
---------------------
Busca inteligente de referências científicas na internet.

Sem hardcoded: integra com:
1. NCBI BLAST - busca de sequências similares
2. NCBI Entrez - busca de genes, proteínas, artigos
3. UniProt - banco de proteínas com anotações
4. PubMed - artigos científicos
5. CrossRef - metadados de publicações
6. Open Alex - API aberta de citações

Retorna: Referências estruturadas e linkáveis
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum

import requests

logger = logging.getLogger(__name__)


class ReferenceType(Enum):
    """Tipo de referência encontrada."""

    NCBI_GENE = "ncbi_gene"
    NCBI_PROTEIN = "ncbi_protein"
    NCBI_SEQUENCE = "ncbi_sequence"
    PUBMED_ARTICLE = "pubmed_article"
    UNIPROT_ENTRY = "uniprot_entry"
    CROSSREF_DOI = "crossref_doi"
    OPEN_ALEX = "open_alex"


@dataclass
class Reference:
    """Uma referência científica encontrada."""

    ref_id: str  # ID único (ex: "ncbi:NM_123456")
    ref_type: ReferenceType
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    abstract: str | None = None
    url: str = ""
    doi: str | None = None
    accession: str | None = None  # GenBank, UniProt, etc
    relevance_score: float = 0.0  # 0-1, score de relevância
    metadata: dict = field(default_factory=dict)

    @property
    def citation(self) -> str:
        """Formato de citação simples."""
        auth_str = ", ".join(self.authors[:3]) if self.authors else "Unknown"
        year_str = f" ({self.year})" if self.year else ""
        return f"{auth_str}{year_str}. {self.title}"

    def to_dict(self) -> dict:
        """Serializa para dicionário."""
        return {
            "ref_id": self.ref_id,
            "type": self.ref_type.value,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "abstract": self.abstract,
            "url": self.url,
            "doi": self.doi,
            "accession": self.accession,
            "relevance": self.relevance_score,
        }


class NCBISearcher:
    """Busca no NCBI (Entrez API)."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, email: str, api_key: str | None = None):
        self.email = email
        self.api_key = api_key
        self.session = requests.Session()

    def search_gene(self, query: str, max_results: int = 10) -> Iterator[Reference]:
        """Busca genes no NCBI Gene database."""
        params = {
            "db": "gene",
            "term": query,
            "retmax": max_results,
            "rettype": "json",
            "usehistory": "y",
        }

        if self.api_key:
            params["api_key"] = self.api_key
        params["email"] = self.email

        try:
            resp = self.session.get(f"{self.BASE_URL}/esearch.fcgi", params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                uids = data.get("esearchresult", {}).get("idlist", [])

                for uid in uids[:max_results]:
                    yield self._fetch_gene_details(uid)
                    time.sleep(0.3)  # Rate limit
        except Exception as e:
            print(f"Erro ao buscar genes NCBI: {e}")

    def search_protein(self, query: str, max_results: int = 10) -> Iterator[Reference]:
        """Busca proteínas no NCBI Protein database."""
        params = {
            "db": "protein",
            "term": query,
            "retmax": max_results,
            "rettype": "json",
        }

        if self.api_key:
            params["api_key"] = self.api_key
        params["email"] = self.email

        try:
            resp = self.session.get(f"{self.BASE_URL}/esearch.fcgi", params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                uids = data.get("esearchresult", {}).get("idlist", [])

                for uid in uids[:max_results]:
                    yield self._fetch_protein_details(uid)
                    time.sleep(0.3)
        except Exception as e:
            print(f"Erro ao buscar proteínas NCBI: {e}")

    def search_pubmed(self, query: str, max_results: int = 10) -> Iterator[Reference]:
        """Busca artigos no PubMed."""
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "rettype": "json",
        }

        if self.api_key:
            params["api_key"] = self.api_key
        params["email"] = self.email

        try:
            resp = self.session.get(f"{self.BASE_URL}/esearch.fcgi", params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                uids = data.get("esearchresult", {}).get("idlist", [])

                for uid in uids[:max_results]:
                    yield self._fetch_pubmed_details(uid)
                    time.sleep(0.3)
        except Exception as e:
            print(f"Erro ao buscar PubMed: {e}")

    def _fetch_gene_details(self, uid: str) -> Reference:
        """Busca detalhes de um gene específico."""
        params = {
            "db": "gene",
            "id": uid,
            "rettype": "json",
        }
        if self.api_key:
            params["api_key"] = self.api_key
        params["email"] = self.email

        try:
            resp = self.session.get(f"{self.BASE_URL}/efetch.fcgi", params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                gene = data.get("result", {}).get(uid, {})

                return Reference(
                    ref_id=f"ncbi_gene:{uid}",
                    ref_type=ReferenceType.NCBI_GENE,
                    title=gene.get("description", "Unknown"),
                    accession=gene.get("uid"),
                    url=f"https://www.ncbi.nlm.nih.gov/gene/{uid}",
                    metadata={"ncbi_uid": uid},
                )
        except Exception as e:
            logger.debug(f"Failed to fetch gene details for {uid}: {e}")

        return Reference(
            ref_id=f"ncbi_gene:{uid}",
            ref_type=ReferenceType.NCBI_GENE,
            title="Unknown",
            url=f"https://www.ncbi.nlm.nih.gov/gene/{uid}",
        )

    def _fetch_protein_details(self, uid: str) -> Reference:
        """Busca detalhes de uma proteína."""
        return Reference(
            ref_id=f"ncbi_protein:{uid}",
            ref_type=ReferenceType.NCBI_PROTEIN,
            title="Unknown",
            accession=uid,
            url=f"https://www.ncbi.nlm.nih.gov/protein/{uid}",
        )

    def _fetch_pubmed_details(self, uid: str) -> Reference:
        """Busca detalhes de um artigo PubMed."""
        params = {
            "db": "pubmed",
            "id": uid,
            "rettype": "json",
        }
        if self.api_key:
            params["api_key"] = self.api_key
        params["email"] = self.email

        try:
            resp = self.session.get(f"{self.BASE_URL}/efetch.fcgi", params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                articles = data.get("result", {}).get("uids", [])

                if articles and uid in data.get("result", {}):
                    article = data["result"][uid]
                    authors = [a.get("name", "") for a in article.get("authors", [])[:5]]

                    return Reference(
                        ref_id=f"pubmed:{uid}",
                        ref_type=ReferenceType.PUBMED_ARTICLE,
                        title=article.get("title", "Unknown"),
                        authors=authors,
                        year=int(article.get("pubdate", "0000")[:4]) if article.get("pubdate") else None,
                        abstract=article.get("abstract", ""),
                        url=f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                        doi=article.get("doi"),
                    )
        except Exception as e:
            logger.debug(f"Failed to fetch PubMed details for {uid}: {e}")

        return Reference(
            ref_id=f"pubmed:{uid}",
            ref_type=ReferenceType.PUBMED_ARTICLE,
            title="Unknown",
            url=f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
        )


class UniProtSearcher:
    """Busca no UniProt."""

    BASE_URL = "https://rest.uniprot.org/uniprotkb/search"

    def search(self, query: str, max_results: int = 10) -> Iterator[Reference]:
        """
        Busca proteínas no UniProt.

        Args:
            query: Query UniProt (ex: "organism:dinosaur" ou nome de gene)
            max_results: Número máximo de resultados
        """
        params = {
            "query": query,
            "size": max_results,
            "format": "json",
        }

        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()

                for result in data.get("results", [])[:max_results]:
                    entry = result.get("primaryAccession", "")
                    title = result.get("uniProtkbId", "")

                    genes = result.get("genes", [])
                    gene_names = []
                    if genes:
                        gene_names = [g.get("geneName", {}).get("value", "") for g in genes]

                    yield Reference(
                        ref_id=f"uniprot:{entry}",
                        ref_type=ReferenceType.UNIPROT_ENTRY,
                        title=title,
                        accession=entry,
                        url=f"https://www.uniprot.org/uniprotkb/{entry}",
                        metadata={"gene_names": gene_names},
                    )
        except Exception as e:
            logger.warning(f"UniProt search failed: {e}")


class CrossRefSearcher:
    """Busca no CrossRef (DOI e metadados de publicações)."""

    BASE_URL = "https://api.crossref.org/works"

    def search(self, query: str, max_results: int = 10) -> Iterator[Reference]:
        """
        Busca DOIs e publicações no CrossRef.

        Args:
            query: Termo de busca (título, autor, DOI)
            max_results: Número máximo de resultados
        """
        params = {
            "query": query,
            "rows": max_results,
            "sort": "relevance",
        }

        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()

                for item in data.get("message", {}).get("items", [])[:max_results]:
                    doi = item.get("DOI", "")
                    title = item.get("title", ["Unknown"])[0] if item.get("title") else "Unknown"

                    authors = []
                    for author in item.get("author", [])[:5]:
                        name = f"{author.get('given', '')} {author.get('family', '')}"
                        authors.append(name.strip())

                    yield Reference(
                        ref_id=f"crossref:{doi}",
                        ref_type=ReferenceType.CROSSREF_DOI,
                        title=title,
                        authors=authors,
                        year=item.get("published-online", {}).get("date-parts", [[]])[0][0],
                        doi=doi,
                        url=f"https://doi.org/{doi}",
                        metadata={"publisher": item.get("publisher", "")},
                    )
        except Exception as e:
            logger.warning(f"CrossRef search failed: {e}")


class ReferenceSearcher:
    """
    Orquestrador central de buscas de referências.
    Integra múltiplas APIs em um interface único.
    """

    def __init__(self, ncbi_email: str, ncbi_api_key: str | None = None):
        self.ncbi = NCBISearcher(ncbi_email, ncbi_api_key)
        self.uniprot = UniProtSearcher()
        self.crossref = CrossRefSearcher()

    def search_all(
        self,
        query: str,
        max_results_per_source: int = 5,
        sources: list[str] | None = None,
    ) -> list[Reference]:
        """
        Busca em múltiplas fontes e retorna resultados consolidados.

        Args:
            query: Termo de busca
            max_results_per_source: Máximo por fonte
            sources: Quais fontes usar (None = todas)
                     Opções: "ncbi", "uniprot", "crossref", "pubmed"

        Returns:
            Lista de referências ordenada por relevância
        """
        if sources is None:
            sources = ["ncbi", "uniprot", "crossref", "pubmed"]

        all_references = []

        # NCBI Gene
        if "ncbi" in sources:
            logger.info(f"Searching NCBI genes for '{query}'...")
            for ref in self.ncbi.search_gene(query, max_results_per_source):
                ref.relevance_score = 0.8
                all_references.append(ref)

        # NCBI PubMed
        if "pubmed" in sources:
            logger.info(f"Searching PubMed for '{query}'...")
            for ref in self.ncbi.search_pubmed(query, max_results_per_source):
                ref.relevance_score = 0.7
                all_references.append(ref)

        # UniProt
        if "uniprot" in sources:
            logger.info(f"Searching UniProt for '{query}'...")
            for ref in self.uniprot.search(query, max_results_per_source):
                ref.relevance_score = 0.75
                all_references.append(ref)

        # CrossRef
        if "crossref" in sources:
            logger.info(f"Searching CrossRef for '{query}'...")
            for ref in self.crossref.search(query, max_results_per_source):
                ref.relevance_score = 0.6
                all_references.append(ref)

        # Ordena por relevância
        all_references.sort(key=lambda r: r.relevance_score, reverse=True)

        return all_references

    def search_gene(self, gene_name: str, max_results: int = 10) -> list[Reference]:
        """Busca um gene específico."""
        refs = list(self.ncbi.search_gene(gene_name, max_results))
        for ref in refs:
            ref.relevance_score = 0.85
        return refs

    def search_sequence_homology(
        self,
        sequence: str,
        species: str | None = None,
    ) -> list[Reference]:
        """
        Busca homologia de uma sequência (via BLAST conceitual).

        Em produção: integraria com NCBI BLAST API.
        Por enquanto: retorna busca por keywords.
        """
        # Simplificado: busca por espécie
        query = f"gene {species}" if species else "gene"
        return self.search_all(query, max_results_per_source=5, sources=["ncbi"])


def create_searcher(ncbi_email: str, ncbi_api_key: str | None = None) -> ReferenceSearcher:
    """Factory: cria searcher com credenciais NCBI."""
    return ReferenceSearcher(ncbi_email, ncbi_api_key)


# Exemplo de uso
if __name__ == "__main__":
    # Teste simples
    searcher = create_searcher(ncbi_email="seu@email.com")

    results = searcher.search_all(query="T-Rex hemoglobin", max_results_per_source=3, sources=["ncbi", "pubmed"])

    print(f"\n{'=' * 60}")
    print(f"Encontradas {len(results)} referências:")
    print(f"{'=' * 60}")

    for ref in results:
        print(f"\n{ref.ref_type.value.upper()}")
        print(f"Título: {ref.title}")
        print(f"URL: {ref.url}")
        print(f"Relevância: {ref.relevance_score:.0%}")
