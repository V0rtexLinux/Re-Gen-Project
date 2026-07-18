#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hardware_orchestrator.py
=========================
ORQUESTRADOR DE HARDWARE - Coordena 3 subsistemas

Sincroniza:
1. DNA Synthesizer (GPIO)
2. Embryo Injector (Servo motors)
3. Incubator (Arduino + DYNAMIXEL)

Garante que todo o fluxo: DNA → Injeção → Incubação funcione
de forma coerente e sincronizada.
"""

import logging
import json
import time
import threading
from typing import Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from device_base import DeviceBase
from hardware_devices import build_hardware_devices, get_default_device_order

logger = logging.getLogger(__name__)


class HardwareState(Enum):
    """Estados possíveis do sistema de hardware."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    SYNTHESIZING = "synthesizing"
    SYNTHESIS_COMPLETE = "synthesis_complete"
    PREPARING_INJECTOR = "preparing_injector"
    INJECTOR_READY = "injector_ready"
    INJECTING = "injecting"
    INJECTION_COMPLETE = "injection_complete"
    NOTIFYING_INCUBATOR = "notifying_incubator"
    INCUBATING = "incubating"
    ERROR = "error"
    EMERGENCY_STOP = "emergency_stop"


class InjectionStatus(Enum):
    """Status da injeção."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class OrchestrationJob:
    """Job de orquestração."""
    job_id: str
    species_name: str
    start_time: float = field(default_factory=time.time)
    state: HardwareState = HardwareState.IDLE
    dna_synthesized: bool = False
    dna_volume_ul: float = 0.0
    injection_status: InjectionStatus = InjectionStatus.PENDING
    injection_timestamp: Optional[str] = None
    error_message: Optional[str] = None
    events: list = field(default_factory=list)
    
    def log_event(self, event_type: str, message: str):
        """Registra evento."""
        timestamp = datetime.now().isoformat()
        event = {
            "timestamp": timestamp,
            "type": event_type,
            "message": message
        }
        self.events.append(event)
        logger.info(f"[{event_type}] {message}")


class HardwareOrchestrator:
    """Orquestrador principal de hardware."""
    
    def __init__(self, 
                 arduino_port: str = '/dev/ttyUSB0',
                 arduino_baudrate: int = 9600):
        """Inicializa orquestrador."""
        self.logger = logging.getLogger("HardwareOrchestrator")
        
        # Estado global
        self.state = HardwareState.IDLE
        self.current_job: Optional[OrchestrationJob] = None
        self.last_error: Optional[str] = None
        
        # Componentes
        self.devices: Dict[str, DeviceBase] = {}
        self.device_order = get_default_device_order()
        
        # Configuração
        self.arduino_port = arduino_port
        self.arduino_baudrate = arduino_baudrate
        
        # Timeouts
        self.SYNTHESIS_TIMEOUT = 120  # segundos
        self.INJECTION_TIMEOUT = 300  # segundos
        self.ARDUINO_RESPONSE_TIMEOUT = 5  # segundos
        
        # Hardware ready flags
        self.synthesizer_ready = False
        self.injector_ready = False
        self.incubator_ready = False
        
        self.logger.info("HardwareOrchestrator inicializado")
    
    def get_device(self, name: str) -> Optional[DeviceBase]:
        return self.devices.get(name)

    def initialize_hardware(self) -> bool:
        """Inicializa todos os subsistemas de hardware."""
        self.logger.info("=== INICIALIZANDO HARDWARE ===")
        self.state = HardwareState.INITIALIZING
        self.current_job.log_event("INIT_START", "Inicializando hardware")

        self.devices = build_hardware_devices(self.arduino_port, self.arduino_baudrate)
        initialized_devices = []

        try:
            for index, device_name in enumerate(self.device_order, start=1):
                device = self.devices.get(device_name)
                if device is None:
                    self.logger.warning(f"Dispositivo não encontrado: {device_name}")
                    continue

                self.logger.info(f"{index}. Inicializando {device.name}...")
                if not device.initialize():
                    raise RuntimeError(f"Falha ao inicializar {device.name}")

                initialized_devices.append(device_name)
                self.current_job.log_event("DEVICE_INIT", f"{device.name} inicializado")
                time.sleep(0.2)

            self.synthesizer_ready = bool(self.devices.get("synthesizer") and self.devices["synthesizer"].initialized)
            self.injector_ready = bool(self.devices.get("injector") and self.devices["injector"].initialized)
            self.incubator_ready = bool(self.devices.get("incubator") and self.devices["incubator"].initialized)

            self.state = HardwareState.READY
            self.logger.info("✓ HARDWARE PRONTO PARA OPERAÇÃO")
            self.current_job.log_event("INIT_COMPLETE", "Hardware totalmente inicializado")
            return True

        except Exception as e:
            self.logger.error(f"✗ Erro ao inicializar hardware: {e}")
            self.state = HardwareState.ERROR
            self.last_error = str(e)
            self.current_job.log_event("INIT_ERROR", f"Erro: {e}")
            self._shutdown_initialized_devices(initialized_devices)
            self._emergency_stop()
            return False

    def _shutdown_initialized_devices(self, initialized_device_names):
        for device_name in reversed(initialized_device_names):
            device = self.devices.get(device_name)
            if device and getattr(device, "initialized", False):
                try:
                    self.logger.info(f"Desligando {device.name}...")
                    device.shutdown()
                except Exception as e:
                    self.logger.warning(f"Erro ao desligar {device.name}: {e}")

    def shutdown(self):
        """Desliga todos os dispositivos de forma ordenada."""
        self.logger.info("Desligando todos os dispositivos...")
        self.state = HardwareState.IDLE
        self._shutdown_initialized_devices(self.device_order)
        self.logger.info("Todos os dispositivos foram desligados")
    
    def execute_complete_workflow(self, species_name: str) -> Optional[Dict]:
        """Executa workflow completo: DNA → Injeção → Incubação."""
        
        job_id = f"orch_{species_name.replace(' ', '_')}_{int(time.time())}"
        self.current_job = OrchestrationJob(
            job_id=job_id,
            species_name=species_name
        )
        
        self.logger.info("\n" + "="*70)
        self.logger.info("ORQUESTRADOR: INICIANDO WORKFLOW COMPLETO")
        self.logger.info("="*70)
        self.current_job.log_event("WORKFLOW_START", f"Iniciando workflow para {species_name}")
        
        try:
            # 1. Inicializar hardware
            if not self.initialize_hardware():
                return None
            
            # 2. Sintetizar DNA
            self.logger.info("\n[1/4] SÍNTESE DE DNA")
            self.state = HardwareState.SYNTHESIZING
            dna_volume = self._execute_synthesis(species_name)
            if dna_volume is None:
                self.logger.error("✗ Síntese de DNA falhou")
                raise Exception("DNA synthesis failed")
            
            self.current_job.dna_synthesized = True
            self.current_job.dna_volume_ul = dna_volume
            self.state = HardwareState.SYNTHESIS_COMPLETE
            
            # 2.5 Validar DNA
            if not self._validate_dna(dna_volume):
                raise Exception("DNA validation failed")
            
            # 3. Preparar Injector
            self.logger.info("\n[2/4] PREPARANDO INJECTOR")
            self.state = HardwareState.PREPARING_INJECTOR
            if not self._prepare_injector():
                raise Exception("Injector preparation failed")
            
            self.state = HardwareState.INJECTOR_READY
            
            # 4. Executar Injeção
            self.logger.info("\n[3/4] INJETANDO DNA")
            self.state = HardwareState.INJECTING
            
            injection_timestamp = datetime.now().isoformat()
            success = self._execute_injection(species_name, injection_timestamp, dna_volume)
            
            if not success:
                raise Exception("Injection failed")
            
            self.current_job.injection_status = InjectionStatus.SUCCESS
            self.current_job.injection_timestamp = injection_timestamp
            self.state = HardwareState.INJECTION_COMPLETE
            
            # 5. Notificar Incubadora
            self.logger.info("\n[4/4] NOTIFICANDO INCUBADORA")
            self.state = HardwareState.NOTIFYING_INCUBATOR
            
            if not self._notify_incubator(injection_timestamp, dna_volume):
                self.logger.warning("⚠ Falha ao notificar incubadora (continuando)")
            
            # 6. Iniciar Monitoramento
            self.state = HardwareState.INCUBATING
            self._start_incubation_monitoring()
            
            # Sucesso!
            self.logger.info("\n" + "="*70)
            self.logger.info("✓ WORKFLOW COMPLETO COM SUCESSO")
            self.logger.info("="*70)
            self.current_job.log_event("WORKFLOW_SUCCESS", "Workflow completado")
            
            return self._get_job_summary()
            
        except Exception as e:
            self.logger.error(f"\n✗ ERRO NO WORKFLOW: {e}")
            self.state = HardwareState.ERROR
            self.last_error = str(e)
            self.current_job.state = HardwareState.ERROR
            self.current_job.error_message = str(e)
            self.current_job.log_event("WORKFLOW_ERROR", f"Erro: {e}")
            
            # Emergency stop
            self._emergency_stop()
            
            return None
    
    def _execute_synthesis(self, species_name: str) -> Optional[float]:
        """Executa síntese de DNA."""
        self.logger.info("Iniciando síntese de DNA...")
        self.current_job.log_event("SYNTH_START", "Iniciando síntese")

        try:
            from dna_synthesizer_hardware import DNTPoolConfig, SynthesisParameter

            synthesizer = self.get_device("synthesizer")
            if synthesizer is None:
                raise RuntimeError("DNA Synthesizer não está disponível")

            dntp_config = DNTPoolConfig(
                dATP_mM=100.0,
                dTTP_mM=100.0,
                dGTP_mM=100.0,
                dCTP_mM=100.0,
                buffer_pH=7.5,
                Mg2_mM=5.0,
                temp_celsius=72.0
            )

            self.logger.info("Preparando dNTPs...")
            synthesizer.prepare_mix(dntp_config)
            time.sleep(1)

            sequence = ("ATG" + species_name.replace(" ", "") + "ATGC" * 250)[:1000]
            synthesis_params = SynthesisParameter(
                sequence=sequence,
                target_length_bp=len(sequence),
                polymerase_type="Phusion",
                extension_rate_bp_per_sec=1000.0,
                temperature_profile={"annealing": 50.0, "extension": 72.0}
            )

            self.logger.info("Iniciando síntese no hardware...")
            volume = synthesizer.synthesize(sequence, synthesis_params)
            if volume is None:
                raise RuntimeError("Falha ao sintetizar DNA no dispositivo")

            self.logger.info("Síntese em progresso...")
            start_time = time.time()
            while time.time() - start_time < 60:
                status = synthesizer.status()
                self.logger.info(f"  Síntese: {status.get('dna_progress', 0)}%")
                if status.get('dna_complete', False):
                    break
                time.sleep(5)

            dna_volume = synthesizer.last_volume_ul
            self.logger.info(f"✓ DNA sintetizado: {dna_volume:.2f}µL")
            self.current_job.log_event("SYNTH_COMPLETE", f"DNA: {dna_volume:.2f}µL")
            return dna_volume

        except Exception as e:
            self.logger.error(f"✗ Erro na síntese: {e}")
            self.current_job.log_event("SYNTH_ERROR", f"Erro: {e}")
            return None
    
    def _validate_dna(self, volume_ul: float) -> bool:
        """Valida DNA sintetizado."""
        self.logger.info("Validando DNA...")
        
        # Validações básicas
        if volume_ul < 10:
            self.logger.error(f"✗ Volume insuficiente: {volume_ul}µL (mínimo: 10µL)")
            return False
        
        if volume_ul > 1000:
            self.logger.warning(f"⚠ Volume muito alto: {volume_ul}µL")
        
        self.logger.info(f"✓ DNA validado: {volume_ul:.2f}µL")
        return True
    
    def _prepare_injector(self) -> bool:
        """Prepara injector para injeção."""
        self.logger.info("Preparando injector...")

        try:
            injector = self.get_device("injector")
            if injector is None:
                raise RuntimeError("Injector device is not initialized")

            injector.prepare_injection()
            self.current_job.log_event("INJECT_PREP", "Injector preparado")
            return True

        except Exception as e:
            self.logger.error(f"✗ Erro ao preparar injector: {e}")
            if self.current_job:
                self.current_job.log_event("INJECT_PREP_ERROR", f"Erro: {e}")
            return False
    
    def _execute_injection(self, species_name: str, timestamp: str, 
                          dna_volume: float) -> bool:
        """Executa injeção de DNA."""
        self.logger.info(f"Executando injeção de DNA ({dna_volume}µL)...")
        self.current_job.log_event("INJECT_START", f"Iniciando injeção")

        try:
            injector = self.get_device("injector")
            if injector is None:
                raise RuntimeError("Injector device is not initialized")

            self.logger.info("  Detectando núcleo do embrião...")
            target = injector.detect_embryo_target(None)
            if not target:
                raise RuntimeError("Núcleo não detectado")

            self.logger.info(f"  Injetando {target.volume_nl}nL...")
            success = injector.inject_dna(
                f">{species_name}_injected|{timestamp}",
                target,
                dna_concentration_ng_ul=50.0
            )

            if not success:
                raise RuntimeError("Injeção falhou")

            self.logger.info("✓ Injeção concluída com sucesso")
            self.current_job.log_event("INJECT_COMPLETE", "Injeção bem-sucedida")
            return True

        except Exception as e:
            self.logger.error(f"✗ Erro na injeção: {e}")
            self.current_job.log_event("INJECT_ERROR", f"Erro: {e}")
            self.current_job.injection_status = InjectionStatus.FAILED
            return False
    
    def _notify_incubator(self, timestamp: str, dna_volume: float) -> bool:
        """Notifica incubadora que embrião foi injetado."""
        self.logger.info("Notificando incubadora...")

        try:
            incubator = self.get_device("incubator")
            if incubator is None:
                raise RuntimeError("Incubator device is not initialized")

            success = incubator.notify_embryo_injected(
                timestamp=timestamp,
                volume_ul=dna_volume
            )

            if success:
                self.logger.info("✓ Incubadora notificada")
                self.current_job.log_event("INCU_NOTIFIED", "Incubadora notificada")
            else:
                self.logger.warning("⚠ Incubadora não respondeu")
                self.current_job.log_event("INCU_NO_RESPONSE", "Sem resposta")
            return success

        except Exception as e:
            self.logger.error(f"✗ Erro ao notificar incubadora: {e}")
            self.current_job.log_event("INCU_ERROR", f"Erro: {e}")
            return False
    
    def _start_incubation_monitoring(self):
        """Inicia thread de monitoramento de incubação."""
        self.logger.info("Iniciando monitoramento de incubação...")

        def monitor():
            while self.state == HardwareState.INCUBATING:
                try:
                    incubator = self.get_device("incubator")
                    environment = self.get_device("environment_monitor")
                    if incubator is None or environment is None:
                        self.logger.warning("Dispositivos de monitoramento não estão disponíveis")
                        break

                    status = incubator.status()
                    env_status = environment.status()
                    self.logger.info(
                        f"  Incubadora: {status.get('temperatura_atual', status.get('temp', 0)):.1f}°C, "
                        f"{status.get('umidade_atual', status.get('humidity', 0)):.0f}% umidade"
                    )
                    self.logger.info(
                        f"  Ambiente: {env_status.get('temperature_c', 0):.1f}°C, "
                        f"{env_status.get('humidity_pct', 0):.0f}% umidade"
                    )
                    time.sleep(60)
                except Exception as e:
                    self.logger.warning(f"Erro ao verificar incubadora: {e}")
                    time.sleep(5)

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def _emergency_stop(self):
        """Para todos os sistemas de emergência."""
        self.logger.error("\n!!! EMERGENCY STOP !!!")
        self.state = HardwareState.EMERGENCY_STOP

        try:
            for device_name in reversed(self.device_order):
                device = self.devices.get(device_name)
                if not device or not getattr(device, "initialized", False):
                    continue

                self.logger.info(f"Desligando {device.name} de emergência...")
                try:
                    device.shutdown()
                except Exception:
                    self.logger.exception(f"Falha ao desligar {device.name}")

        except Exception as e:
            self.logger.error(f"Erro durante emergency stop: {e}")
    
    def _get_job_summary(self) -> Dict:
        """Retorna resumo do job."""
        return {
            "job_id": self.current_job.job_id,
            "species": self.current_job.species_name,
            "dna_volume_ul": self.current_job.dna_volume_ul,
            "injection_success": self.current_job.injection_status == InjectionStatus.SUCCESS,
            "injection_timestamp": self.current_job.injection_timestamp,
            "start_time": self.current_job.start_time,
            "duration_seconds": time.time() - self.current_job.start_time,
            "events": self.current_job.events
        }
    
    def get_status(self) -> Dict:
        """Retorna status atual do orquestrador."""
        return {
            "state": self.state.value,
            "synthesizer_ready": self.synthesizer_ready,
            "injector_ready": self.injector_ready,
            "incubator_ready": self.incubator_ready,
            "current_job": self.current_job.job_id if self.current_job else None,
            "last_error": self.last_error
        }


# ============================================================================
# TESTE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
    )
    
    orchestrator = HardwareOrchestrator()
    
    # Executar workflow (com mock de hardware)
    result = orchestrator.execute_complete_workflow("Tyrannosaurus rex")
    
    if result:
        print("\n✓ Workflow completado com sucesso!")
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✗ Workflow falhou: {orchestrator.last_error}")
