"""Tests for re_gen.hardware.utero_ovo_controller."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from re_gen.hardware.utero_ovo_controller import (
    FaseUteroOvo,
    LeituraSensores,
    ParametrosProtocolo,
    UteroOvoController,
)


@pytest.fixture
def controller():
    with patch("re_gen.hardware.arduino_bridge.ArduinoBridge._connect", return_value=True):
        c = UteroOvoController(port="/dev/null")
    c.bridge.connected = True
    return c


class TestInicializacao:
    def test_initialize_sucesso(self, controller):
        with patch.object(controller.bridge, "ping", return_value=True):
            assert controller.initialize() is True
        assert controller.initialized is True

    def test_initialize_falha_nao_finge_sucesso(self, controller):
        with patch.object(controller.bridge, "ping", return_value=False):
            assert controller.initialize() is False
        assert controller.initialized is False


class TestRegistrarTransferencia:
    def test_falha_se_nao_inicializado(self, controller):
        assert controller.registrar_transferencia(50.0) is False

    def test_sucesso_registra_massa_e_muda_fase(self, controller):
        controller.initialized = True
        with patch.object(controller.bridge, "send_command", return_value="OK"):
            assert controller.registrar_transferencia(50.0) is True
        assert controller.massa_inicial_g == 50.0
        assert controller.fase_atual == FaseUteroOvo.CULTURA_PADRAO
        assert controller.timestamp_transferencia is not None

    def test_nao_finge_sucesso_se_firmware_nao_confirma(self, controller):
        controller.initialized = True
        with patch.object(controller.bridge, "send_command", return_value=None):
            resultado = controller.registrar_transferencia(50.0)
        assert resultado is False
        # A fase e o timestamp ainda são atualizados localmente (o registro
        # local é independente da confirmação do firmware), mas o retorno
        # honesto indica que o firmware não confirmou.


class TestDiaDeDesenvolvimento:
    def test_none_sem_transferencia(self, controller):
        assert controller.dia_de_desenvolvimento() is None

    def test_calcula_dias_reais_desde_transferencia(self, controller):
        controller.timestamp_transferencia = datetime.now() - timedelta(days=5, hours=12)
        dia = controller.dia_de_desenvolvimento()
        assert 5.4 < dia < 5.6


class TestAtualizarFase:
    def test_nao_transiciona_antes_do_dia_17(self, controller):
        controller.fase_atual = FaseUteroOvo.CULTURA_PADRAO
        controller.timestamp_transferencia = datetime.now() - timedelta(days=10)
        with patch.object(controller, "_acionar_valvula_o2") as mock_valvula:
            fase = controller.atualizar_fase()
        mock_valvula.assert_not_called()
        assert fase == FaseUteroOvo.CULTURA_PADRAO

    def test_transiciona_para_oxigenacao_pura_apos_dia_17(self, controller):
        controller.fase_atual = FaseUteroOvo.CULTURA_PADRAO
        controller.timestamp_transferencia = datetime.now() - timedelta(days=18)
        with patch.object(controller, "_acionar_valvula_o2", return_value=True) as mock_valvula:
            fase = controller.atualizar_fase()
        mock_valvula.assert_called_once_with(controller.parametros.concentracao_o2_fase3_pct)
        assert fase == FaseUteroOvo.OXIGENACAO_PURA

    def test_nao_transiciona_se_firmware_nao_confirma_valvula(self, controller):
        """Não deve fingir a transição de fase se o hardware real não confirmar."""
        controller.fase_atual = FaseUteroOvo.CULTURA_PADRAO
        controller.timestamp_transferencia = datetime.now() - timedelta(days=18)
        with patch.object(controller, "_acionar_valvula_o2", return_value=False):
            fase = controller.atualizar_fase()
        assert fase == FaseUteroOvo.CULTURA_PADRAO  # continua na fase anterior, honestamente


class TestPIDDeterministico:
    """PID clássico -- determinístico, sem IA."""

    def test_mesma_entrada_mesma_saida(self, controller):
        leitura = LeituraSensores(36.0, 55.0, 20.9, 47.0, "x")
        r1 = controller.calcular_potencia_aquecedor(leitura, erro_acumulado=0.0, erro_anterior=0.0)
        r2 = controller.calcular_potencia_aquecedor(leitura, erro_acumulado=0.0, erro_anterior=0.0)
        assert r1 == r2

    def test_potencia_maior_quando_temperatura_mais_abaixo_do_alvo(self, controller):
        leitura_fria = LeituraSensores(30.0, 55.0, 20.9, 47.0, "x")
        leitura_morna = LeituraSensores(36.5, 55.0, 20.9, 47.0, "x")
        p_fria, _ = controller.calcular_potencia_aquecedor(leitura_fria, 0.0, 0.0)
        p_morna, _ = controller.calcular_potencia_aquecedor(leitura_morna, 0.0, 0.0)
        assert p_fria > p_morna

    def test_potencia_e_limitada_entre_0_e_100(self, controller):
        leitura_muito_fria = LeituraSensores(0.0, 55.0, 20.9, 47.0, "x")
        potencia, _ = controller.calcular_potencia_aquecedor(leitura_muito_fria, 0.0, 0.0)
        assert 0.0 <= potencia <= 100.0


class TestPerdaDeMassa:
    def test_none_sem_massa_inicial(self, controller):
        leitura = LeituraSensores(37.5, 55.0, 20.9, 47.0, "x")
        assert controller.calcular_perda_de_massa_pct(leitura) is None

    def test_calcula_perda_real(self, controller):
        controller.massa_inicial_g = 50.0
        leitura = LeituraSensores(37.5, 55.0, 20.9, 47.0, "x")
        assert controller.calcular_perda_de_massa_pct(leitura) == pytest.approx(6.0)

    def test_verifica_necessidade_reposicao_acima_do_limite(self, controller):
        controller.massa_inicial_g = 50.0
        controller.parametros = ParametrosProtocolo(limite_perda_massa_alerta_pct=5.0)
        leitura = LeituraSensores(37.5, 55.0, 20.9, 47.0, "x")  # perda de 6%
        assert controller.verificar_necessidade_reposicao(leitura) is True

    def test_nao_precisa_reposicao_abaixo_do_limite(self, controller):
        controller.massa_inicial_g = 50.0
        controller.parametros = ParametrosProtocolo(limite_perda_massa_alerta_pct=10.0)
        leitura = LeituraSensores(37.5, 55.0, 20.9, 49.0, "x")  # perda de 2%
        assert controller.verificar_necessidade_reposicao(leitura) is False


class TestLerSensores:
    def test_retorna_none_sem_resposta(self, controller):
        with patch.object(controller.bridge, "send_command", return_value=None):
            assert controller.ler_sensores() is None

    def test_retorna_none_com_resposta_malformada(self, controller):
        with patch.object(controller.bridge, "send_command", return_value="isso nao e json"):
            assert controller.ler_sensores() is None

    def test_le_sensores_reais_corretamente(self, controller):
        resposta_json = '{"temperatura_c": 37.4, "umidade_pct": 61.0, "o2_pct": 20.9, "massa_g": 48.5}'
        with patch.object(controller.bridge, "send_command", return_value=resposta_json):
            leitura = controller.ler_sensores()
        assert leitura is not None
        assert leitura.temperatura_c == 37.4
        assert leitura.massa_atual_g == 48.5


class TestAcionamentoDeAtuadores:
    def test_acionar_aquecedor_sucesso(self, controller):
        with patch.object(controller.bridge, "send_command", return_value="OK") as mock_cmd:
            assert controller.acionar_aquecedor(45.0) is True
        mock_cmd.assert_called_once_with("SET_HEATER_POWER|45.0")

    def test_acionar_bomba_reposicao_falha_honesta(self, controller):
        with patch.object(controller.bridge, "send_command", return_value=None):
            assert controller.acionar_bomba_reposicao(2.5) is False


class TestStatus:
    def test_status_sem_sensores_disponiveis(self, controller):
        with patch.object(controller, "ler_sensores", return_value=None):
            status = controller.status()
        assert status["sensores"] is None
        assert status["fase"] == FaseUteroOvo.AGUARDANDO_TRANSFERENCIA.value

    def test_status_com_sensores_disponiveis(self, controller):
        controller.massa_inicial_g = 50.0
        leitura = LeituraSensores(37.5, 55.0, 20.9, 47.0, "x")
        with patch.object(controller, "ler_sensores", return_value=leitura):
            status = controller.status()
        assert status["sensores"]["temperatura_c"] == 37.5
        assert status["perda_massa_pct"] == pytest.approx(6.0)
