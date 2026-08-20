"""Tests for re_gen.monitoring.tech_watch."""

import json
from unittest.mock import MagicMock, patch

import pytest

from re_gen.monitoring import tech_watch


class TestMarcos:
    def test_marcos_nao_vazio(self):
        assert len(tech_watch.MARCOS) >= 1

    def test_cada_marco_tem_query_pubmed(self):
        for marco in tech_watch.MARCOS:
            assert marco.pubmed_query.strip()
            assert marco.id
            assert marco.titulo

    def test_ids_sao_unicos(self):
        ids = [m.id for m in tech_watch.MARCOS]
        assert len(ids) == len(set(ids))


class TestContarPublicacoesPubmed:
    def test_conta_resultado_real_da_api_mockada(self):
        fake_handle = MagicMock()
        with patch("Bio.Entrez.esearch", return_value=fake_handle) as mock_esearch, \
             patch("Bio.Entrez.read", return_value={"Count": "7"}):
            n = tech_watch.contar_publicacoes_pubmed(
                "artificial womb", email="test@example.com", dias=30
            )
        assert n == 7
        mock_esearch.assert_called_once()

    def test_query_inclui_filtro_de_data(self):
        fake_handle = MagicMock()
        captured = {}

        def _fake_esearch(**kwargs):
            captured.update(kwargs)
            return fake_handle

        with patch("Bio.Entrez.esearch", side_effect=_fake_esearch), \
             patch("Bio.Entrez.read", return_value={"Count": "0"}):
            tech_watch.contar_publicacoes_pubmed(
                "synthetic genome", email="test@example.com", dias=30
            )
        assert "PDAT" in captured["term"]


class TestMotorDeRegrasDeterministico:
    """Testa o motor de decisão 100% baseado em regex (sem IA)."""

    def test_confirma_quando_frase_de_resultado_presente(self):
        marco = tech_watch.MARCOS[0]
        texto = (
            "Artificial ectogenesis device for reptile embryos. The hatchlings "
            "hatched successfully and survived to term without a living surrogate."
        )
        confirmado, motivo = tech_watch._decidir_por_regras(texto, [], marco)
        assert confirmado is True
        assert "confirmação" in motivo

    def test_exclui_por_tipo_de_publicacao_review(self):
        marco = tech_watch.MARCOS[0]
        texto = "Chicks were born successfully in this review of the field."
        confirmado, motivo = tech_watch._decidir_por_regras(texto, ["Review"], marco)
        assert confirmado is False
        assert "Review" in motivo

    def test_exclui_por_frase_de_ressalva_mesmo_sem_tipo_review(self):
        marco = tech_watch.MARCOS[0]
        texto = "In principle, chicks were born successfully, but this remains theoretical."
        confirmado, motivo = tech_watch._decidir_por_regras(texto, [], marco)
        assert confirmado is False

    def test_nao_confirma_sem_nenhuma_frase_relevante(self):
        marco = tech_watch.MARCOS[0]
        texto = "Discussion of incubator temperature control systems for poultry farms."
        confirmado, motivo = tech_watch._decidir_por_regras(texto, [], marco)
        assert confirmado is False
        assert motivo == "nenhuma frase de confirmação encontrada (ou todas estavam negadas pelo contexto)"

    def test_decisao_e_reproduzivel_mesmo_texto_mesmo_resultado(self):
        marco = tech_watch.MARCOS[1]
        texto = "The synthetic genome was fully functional in a living cell after transplantation."
        r1 = tech_watch._decidir_por_regras(texto, [], marco)
        r2 = tech_watch._decidir_por_regras(texto, [], marco)
        assert r1 == r2  # determinístico: mesma entrada, mesma saída, sempre


class TestBuscarELerArtigos:
    def test_le_titulo_resumo_e_classifica_via_regras(self, monkeypatch):
        marco = tech_watch.MARCOS[0]

        fake_esearch_handle = MagicMock()
        fake_efetch_handle = MagicMock()

        registro_confirmado = {
            "MedlineCitation": {
                "PMID": "11111111",
                "Article": {
                    "ArticleTitle": "Ectogenesis in reptiles",
                    "Abstract": {"AbstractText": ["The eggs hatched successfully."]},
                    "PublicationTypeList": ["Journal Article"],
                },
            }
        }
        registro_review = {
            "MedlineCitation": {
                "PMID": "22222222",
                "Article": {
                    "ArticleTitle": "A review of ectogenesis",
                    "Abstract": {"AbstractText": ["Chicks were born in past studies."]},
                    "PublicationTypeList": ["Review"],
                },
            }
        }

        def _fake_read(handle):
            if handle is fake_esearch_handle:
                return {"IdList": ["11111111", "22222222"]}
            return {"PubmedArticle": [registro_confirmado, registro_review]}

        with patch("Bio.Entrez.esearch", return_value=fake_esearch_handle), \
             patch("Bio.Entrez.efetch", return_value=fake_efetch_handle), \
             patch("Bio.Entrez.read", side_effect=_fake_read):
            evidencias = tech_watch.buscar_e_ler_artigos(
                marco, email="test@example.com", dias=30
            )

        assert len(evidencias) == 2
        confirmados = [e for e in evidencias if e.confirmado]
        assert len(confirmados) == 1
        assert confirmados[0].pmid == "11111111"

    def test_retorna_lista_vazia_sem_resultados(self):
        marco = tech_watch.MARCOS[0]
        fake_handle = MagicMock()
        with patch("Bio.Entrez.esearch", return_value=fake_handle), \
             patch("Bio.Entrez.read", return_value={"IdList": []}):
            evidencias = tech_watch.buscar_e_ler_artigos(
                marco, email="test@example.com", dias=30
            )
        assert evidencias == []


class TestResumoExtrativoLuhn:
    """Testa o algoritmo de resumo extrativo por frequência de palavras
    (H. P. Luhn, 1958) — determinístico, sem IA."""

    def test_retorna_texto_original_se_poucas_sentencas(self):
        texto = "Uma única sentença aqui."
        assert tech_watch.resumir_por_frequencia_luhn(texto, n_sentencas=2) == texto

    def test_seleciona_sentencas_com_palavras_mais_frequentes(self):
        texto = (
            "The bioreactor system monitors gas exchange. "
            "A completely unrelated sentence about weather patterns today. "
            "The bioreactor system also monitors nutrient delivery in real time. "
            "Another unrelated sentence about traffic conditions downtown."
        )
        resumo = tech_watch.resumir_por_frequencia_luhn(texto, n_sentencas=2)
        assert "bioreactor" in resumo.lower()

    def test_e_deterministico_mesma_entrada_mesma_saida(self):
        texto = (
            "First sentence about synthetic genomes. "
            "Second sentence about synthetic genome synthesis in detail. "
            "Third sentence about something else entirely unrelated."
        )
        r1 = tech_watch.resumir_por_frequencia_luhn(texto, n_sentencas=1)
        r2 = tech_watch.resumir_por_frequencia_luhn(texto, n_sentencas=1)
        assert r1 == r2

    def test_preserva_ordem_original_das_sentencas_selecionadas(self):
        texto = (
            "Zebra sentence with rare words zzqx. "
            "Common important topic words repeated topic topic topic. "
            "Another sentence with topic topic words. "
            "Final sentence zzqx zzqx unrelated."
        )
        resumo = tech_watch.resumir_por_frequencia_luhn(texto, n_sentencas=2)
        # As duas sentenças de maior pontuação ("topic") devem aparecer na
        # ordem em que estavam no texto original, não em ordem de pontuação.
        pos_1 = resumo.find("Common important")
        pos_2 = resumo.find("Another sentence")
        assert pos_1 != -1 and pos_2 != -1
        assert pos_1 < pos_2


class TestDeteccaoDeNegacao:
    """Testa a detecção de negação por janela de contexto — regra fixa,
    sem IA, que evita falsos positivos como 'did not hatch successfully'."""

    def test_confirma_quando_frase_positiva_sem_negacao(self):
        marco = tech_watch.MARCOS[0]
        texto = "The eggs hatched successfully after 60 days of incubation."
        confirmado, _ = tech_watch._decidir_por_regras(texto, [], marco)
        assert confirmado is True

    def test_nao_confirma_quando_frase_esta_negada(self):
        marco = tech_watch.MARCOS[0]
        texto = "Unfortunately, the eggs did not hatch successfully in this trial."
        confirmado, motivo = tech_watch._decidir_por_regras(texto, [], marco)
        assert confirmado is False

    def test_nao_confirma_com_failed_to_antes_da_frase(self):
        marco = tech_watch.MARCOS[0]
        texto = "The embryos failed to survive to term despite optimal conditions."
        confirmado, _ = tech_watch._decidir_por_regras(texto, [], marco)
        assert confirmado is False

    def test_negacao_distante_nao_invalida_confirmacao(self):
        """Negação fora da janela de contexto (muito longe da frase) não
        deve invalidar uma confirmação real em outra parte do texto."""
        marco = tech_watch.MARCOS[0]
        texto = (
            "Unrelated earlier finding did not replicate in a separate unrelated "
            "control experiment using a totally different animal model species. "
            "In our main trial, the eggs hatched successfully and chicks were born."
        )
        confirmado, _ = tech_watch._decidir_por_regras(texto, [], marco)
        assert confirmado is True


class TestVerificarNewsroomColossal:
    def test_retorna_vazio_se_requests_falhar(self):
        import requests

        with patch("requests.get", side_effect=requests.RequestException("network down")):
            resultado = tech_watch.verificar_newsroom_colossal(["artificial womb"])
        assert resultado == []

    def test_encontra_palavra_chave_presente(self):
        resp = MagicMock()
        resp.text = "A Colossal announced progress on its Artificial Womb project."
        resp.raise_for_status = MagicMock()
        with patch("requests.get", return_value=resp):
            resultado = tech_watch.verificar_newsroom_colossal(["artificial womb", "não presente"])
        assert resultado == ["artificial womb"]


class TestExecutarCiclo:
    def test_ciclo_completo_sem_alarme_quando_sem_salto(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tech_watch, "STATE_DIR", tmp_path)
        monkeypatch.setattr(tech_watch, "STATE_FILE", tmp_path / "state.json")
        monkeypatch.setattr(tech_watch, "ALERT_DIR", tmp_path / "alertas")

        with patch.object(tech_watch, "contar_publicacoes_pubmed", return_value=0), \
             patch.object(tech_watch, "buscar_e_ler_artigos", return_value=[]), \
             patch.object(tech_watch, "disparar_alarme") as mock_alarme:
            resumo = tech_watch.executar_ciclo(
                email="test@example.com", verificar_newsroom=False
            )

        mock_alarme.assert_not_called()
        assert len(resumo["marcos"]) == len(tech_watch.MARCOS)
        assert (tmp_path / "state.json").exists()

    def test_ciclo_dispara_alarme_quando_ha_salto(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tech_watch, "STATE_DIR", tmp_path)
        monkeypatch.setattr(tech_watch, "STATE_FILE", tmp_path / "state.json")
        monkeypatch.setattr(tech_watch, "ALERT_DIR", tmp_path / "alertas")

        with patch.object(tech_watch, "contar_publicacoes_pubmed", return_value=50), \
             patch.object(tech_watch, "buscar_e_ler_artigos", return_value=[]), \
             patch.object(tech_watch, "disparar_alarme") as mock_alarme:
            resumo = tech_watch.executar_ciclo(
                email="test@example.com", verificar_newsroom=False
            )

        assert mock_alarme.called
        # Sem evidência confirmada pelo motor de regras -> alarme de nível SINAL
        _, kwargs = mock_alarme.call_args
        assert mock_alarme.call_args.kwargs.get("nivel", "SINAL") == "SINAL"
        assert any(m["alerta_disparado"] for m in resumo["marcos"].values())

    def test_ciclo_dispara_confirmacao_quando_regras_confirmam_artigo(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tech_watch, "STATE_DIR", tmp_path)
        monkeypatch.setattr(tech_watch, "STATE_FILE", tmp_path / "state.json")
        monkeypatch.setattr(tech_watch, "ALERT_DIR", tmp_path / "alertas")

        evidencia_confirmada = tech_watch.Evidencia(
            pmid="12345", titulo="Hatched successfully in artificial incubator",
            texto_completo="Hatched successfully in artificial incubator. The hatchlings survived to term.",
            resumo_extrativo="The hatchlings survived to term.",
            tipos_publicacao=["Journal Article"], confirmado=True,
            motivo="contém frase de confirmação de resultado (não negada): 'hatched successfully'",
        )

        with patch.object(tech_watch, "contar_publicacoes_pubmed", return_value=5), \
             patch.object(tech_watch, "buscar_e_ler_artigos", return_value=[evidencia_confirmada]), \
             patch.object(tech_watch, "disparar_alarme") as mock_alarme:
            resumo = tech_watch.executar_ciclo(
                email="test@example.com", verificar_newsroom=False
            )

        assert mock_alarme.called
        assert mock_alarme.call_args.kwargs.get("nivel") == "CONFIRMACAO"
        primeiro_marco_id = tech_watch.MARCOS[0].id
        assert len(resumo["marcos"][primeiro_marco_id]["artigos_confirmados_por_regras"]) == 1

    def test_estado_persiste_historico_entre_ciclos(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tech_watch, "STATE_DIR", tmp_path)
        monkeypatch.setattr(tech_watch, "STATE_FILE", tmp_path / "state.json")
        monkeypatch.setattr(tech_watch, "ALERT_DIR", tmp_path / "alertas")

        with patch.object(tech_watch, "contar_publicacoes_pubmed", return_value=1), \
             patch.object(tech_watch, "buscar_e_ler_artigos", return_value=[]), \
             patch.object(tech_watch, "disparar_alarme"):
            tech_watch.executar_ciclo(email="test@example.com", verificar_newsroom=False)
            tech_watch.executar_ciclo(email="test@example.com", verificar_newsroom=False)

        estado = json.loads((tmp_path / "state.json").read_text())
        primeiro_marco_id = tech_watch.MARCOS[0].id
        assert len(estado["marcos"][primeiro_marco_id]["historico"]) == 2


class TestDispararAlarme:
    def test_grava_arquivo_de_alerta(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tech_watch, "ALERT_DIR", tmp_path / "alertas")
        with patch("subprocess.run"), patch("sys.stdout"):
            tech_watch.disparar_alarme(tech_watch.MARCOS[0], "detalhes de teste")
        arquivos = list((tmp_path / "alertas").glob("ALERTA_*.txt"))
        assert len(arquivos) == 1
        conteudo = arquivos[0].read_text(encoding="utf-8")
        assert "detalhes de teste" in conteudo
        assert tech_watch.MARCOS[0].titulo in conteudo


class TestCLI:
    def test_instalar_cron_nao_requer_rede(self, capsys):
        with patch("sys.argv", ["re-gen-watch", "--email", "a@b.com", "--instalar-cron"]):
            ret = tech_watch.main()
        assert ret == 0
        out = capsys.readouterr().out
        assert "crontab" in out
        assert "a@b.com" in out
