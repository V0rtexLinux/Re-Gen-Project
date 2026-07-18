#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arduino_bridge.py
=================
Bridge de Comunicação com Arduino

Estabelece comunicação serial com incubadora Arduino para:
- Enviar comandos (embrião injetado, etc)
- Receber status (temperatura, umidade, dia)
- Sincronização de estado

Protocolo Serial:
- Baudrate: 9600
- Formato: Texto ASCII com delimitador '\n'
- Respostas: "OK" ou JSON para status
"""

import logging
import json
import time
from typing import Optional, Dict
import threading

logger = logging.getLogger(__name__)


class ArduinoBridge:
    """Bridge de comunicação com Arduino/Incubadora."""
    
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 9600, 
                 timeout: float = 5.0):
        """Inicializa bridge."""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        
        self.serial = None
        self.connected = False
        self.logger = logging.getLogger("ArduinoBridge")
        
        # Conectar
        self._connect()
    
    def _connect(self) -> bool:
        """Conecta ao Arduino."""
        try:
            import serial
            
            self.logger.info(f"Conectando ao Arduino em {self.port} ({self.baudrate} bps)...")
            
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout
            )
            
            # Aguardar inicialização do Arduino
            time.sleep(2)
            self.connected = True

            # Testar conexão com ping
            if self.ping():
                self.logger.info("✓ Arduino conectado")
                return True
            else:
                self.logger.error("✗ Arduino não respondeu ao ping")
                self.connected = False
                return False

        except ImportError:
            self.logger.error("Módulo 'serial' não encontrado. Instale: pip install pyserial")
            self.connected = False
            return False
        except Exception as e:
            self.logger.error(f"Erro ao conectar: {e}")
            self.connected = False
            return False

    def ping(self) -> bool:
        """Testa conexão com Arduino."""
        try:
            response = self.send_command("PING", timeout=2)
            return response == "OK"
        except:
            return False
    
    def send_command(self, command: str, timeout: Optional[float] = None) -> Optional[str]:
        """
        Envia comando e aguarda resposta.
        
        Args:
            command: Comando a enviar (ex: "PING", "STATUS", "EMBRYO_INJECTED|...")
            timeout: Timeout em segundos (padrão: self.timeout)
        
        Returns:
            Resposta do Arduino ou None se timeout
        """
        if self.serial is None or not getattr(self.serial, 'is_open', True):
            self.logger.error("Arduino não conectado")
            self.connected = False
            return None
        
        if timeout is None:
            timeout = self.timeout
        
        try:
            # Enviar comando
            self.logger.debug(f"Enviando: {command}")
            self.serial.write(f"{command}\n".encode())
            self.serial.flush()
            
            # Aguardar resposta
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    response = self.serial.readline().decode().strip()
                    self.logger.debug(f"Recebido: {response}")
                    return response
                time.sleep(0.1)
            
            self.logger.warning(f"Timeout ao enviar comando: {command}")
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar comando: {e}")
            self.connected = False
            return None
    
    def notify_embryo_injected(self, timestamp: str, volume_ul: float) -> bool:
        """
        Notifica Arduino que embrião foi injetado.
        
        Comando: EMBRYO_INJECTED|<timestamp>|<volume>
        
        Arduino vai:
        - Registrar timestamp em EEPROM
        - Iniciar contagem de dias de incubação
        - Fazer logging
        """
        try:
            command = f"EMBRYO_INJECTED|{timestamp}|{volume_ul}"
            response = self.send_command(command)
            
            if response == "OK":
                self.logger.info(f"✓ Arduino notificado: embrião injetado")
                return True
            else:
                self.logger.error(f"✗ Arduino não confirmou: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao notificar embrião: {e}")
            return False
    
    def get_incubator_status(self) -> Optional[Dict]:
        """
        Obtém status completo da incubadora.
        
        Comando: STATUS
        
        Resposta JSON com:
        - temperatura_atual
        - temperatura_alvo
        - umidade_atual
        - umidade_alvo
        - dia
        - hora
        - minuto
        - estado
        - alarme_ativo
        - viragens_count
        """
        try:
            response = self.send_command("STATUS", timeout=3)
            
            if not response:
                self.logger.warning("Timeout ao obter status")
                return None
            
            # Tentar parse JSON
            try:
                status = json.loads(response)
                return status
            except json.JSONDecodeError:
                self.logger.error(f"Resposta não é JSON válido: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao obter status: {e}")
            return None
    
    def get_temperature(self) -> Optional[float]:
        """Obtém temperatura atual."""
        status = self.get_incubator_status()
        if status:
            return status.get('temperatura_atual')
        return None
    
    def get_humidity(self) -> Optional[float]:
        """Obtém umidade atual."""
        status = self.get_incubator_status()
        if status:
            return status.get('umidade_atual')
        return None
    
    def get_incubation_day(self) -> Optional[int]:
        """Obtém dia de incubação atual."""
        status = self.get_incubator_status()
        if status:
            return status.get('dia')
        return None
    
    def set_target_temperature(self, temp_c: float) -> bool:
        """Define temperatura alvo."""
        try:
            command = f"SET_TEMP|{temp_c}"
            response = self.send_command(command)
            return response == "OK"
        except Exception as e:
            self.logger.error(f"Erro ao definir temperatura: {e}")
            return False
    
    def set_target_humidity(self, humidity_percent: float) -> bool:
        """Define umidade alvo."""
        try:
            command = f"SET_HUMIDITY|{humidity_percent}"
            response = self.send_command(command)
            return response == "OK"
        except Exception as e:
            self.logger.error(f"Erro ao definir umidade: {e}")
            return False
    
    def enable_egg_turning(self) -> bool:
        """Ativa viragem automática de ovos."""
        try:
            response = self.send_command("TURN_EGGS_ON")
            return response == "OK"
        except Exception as e:
            self.logger.error(f"Erro ao ativar viragem: {e}")
            return False
    
    def disable_egg_turning(self) -> bool:
        """Desativa viragem automática de ovos."""
        try:
            response = self.send_command("TURN_EGGS_OFF")
            return response == "OK"
        except Exception as e:
            self.logger.error(f"Erro ao desativar viragem: {e}")
            return False
    
    def trigger_alarm(self) -> bool:
        """Aciona alarme."""
        try:
            response = self.send_command("ALARM")
            return response == "OK"
        except Exception as e:
            self.logger.error(f"Erro ao acionar alarme: {e}")
            return False
    
    def get_full_logs(self) -> Optional[Dict]:
        """Obtém logs completos do Arduino."""
        try:
            response = self.send_command("GET_LOGS", timeout=5)
            
            if not response:
                return None
            
            try:
                logs = json.loads(response)
                return logs
            except json.JSONDecodeError:
                self.logger.error(f"Logs não são JSON: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao obter logs: {e}")
            return None
    
    def reset_arduino(self) -> bool:
        """Reseta Arduino."""
        try:
            response = self.send_command("RESET")
            time.sleep(2)  # Aguardar reboot
            return self.ping()
        except Exception as e:
            self.logger.error(f"Erro ao resetar Arduino: {e}")
            return False
    
    def start_monitoring(self, callback=None, interval: float = 60.0):
        """
        Inicia thread de monitoramento contínuo.
        
        Args:
            callback: Função chamada com status a cada interval
            interval: Intervalo em segundos
        """
        def monitor():
            while self.connected:
                try:
                    status = self.get_incubator_status()
                    if status and callback:
                        callback(status)
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Erro no monitoramento: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    def disconnect(self):
        """Desconecta do Arduino."""
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
            self.connected = False
            self.logger.info("Arduino desconectado")
        except Exception as e:
            self.logger.error(f"Erro ao desconectar: {e}")
    
    def __enter__(self):
        """Context manager: enter."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: exit."""
        self.disconnect()


# ============================================================================
# TESTE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
    )
    
    # Testar com context manager
    with ArduinoBridge(port='/dev/ttyUSB0') as bridge:
        
        # 1. Ping
        print("\n[TEST] Ping...")
        print(f"  Conectado: {bridge.connected}")
        
        # 2. Status
        print("\n[TEST] Status...")
        status = bridge.get_incubator_status()
        if status:
            print(f"  Temperatura: {status.get('temperatura_atual', 'N/A')}°C")
            print(f"  Umidade: {status.get('umidade_atual', 'N/A')}%")
            print(f"  Dia: {status.get('dia', 'N/A')}")
        
        # 3. Notificar embrião injetado
        print("\n[TEST] Notificando embrião injetado...")
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        success = bridge.notify_embryo_injected(timestamp, 50.0)
        print(f"  Sucesso: {success}")
        
        # 4. Novo status
        print("\n[TEST] Novo status...")
        status = bridge.get_incubator_status()
        if status:
            print(f"  Dia: {status.get('dia', 'N/A')}")
        
        print("\n✓ Testes concluídos")
