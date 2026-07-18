"""
embryo_injection_robot.py
=========================
ROBÔ DE INJEÇÃO EM EMBRIÃO - Sistema real com servos

Hardware necessário:
- Raspberry Pi Zero 2W
- 3x Servos de posicionamento (MG995 ou similar)
  - Servo X: Movimento lateral
  - Servo Y: Movimento frontal
  - Servo Z: Movimento vertical (profundidade)
  - Servo Seringa: Controle de injeção
- Câmera USB (para visão em tempo real)
- Microscópio com lente de 20x (mínimo)
- Plataforma estável (vibração < 0.1mm)
- Seringa de 1mL (precisão de 0.01mL)
- Agulha de 25G ou 30G (para embrião)

Processo de injeção:
1. Captura embrião com câmera
2. Detecta posição do núcleo
3. Posiciona robô acima do núcleo
4. Desce agulha lentamente
5. Injeta DNA em 500nL/segundo
6. Retira agulha
7. Move embrião para incubadora
"""

import RPi.GPIO as GPIO
import time
import logging
from dataclasses import dataclass
from typing import Tuple, Optional
from enum import Enum
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURAÇÕES SERVO
# ============================================================================

class ServoConfig:
    """Configurações de servo motor."""
    MIN_PULSE_WIDTH_MS = 1.0    # Pulso mínimo (0 graus)
    MAX_PULSE_WIDTH_MS = 2.0    # Pulso máximo (180 graus)
    SERVO_FREQUENCY_HZ = 50     # Frequência PWM padrão de servo


class EmbryoInjectionCoordinates:
    """Coordenadas de injeção no embrião de galinha."""
    
    # Tamanho típico de embrião (HH estágio 4-5)
    EMBRYO_DIAMETER_MM = 3.0
    NUCLEUS_DIAMETER_MM = 0.5
    NUCLEUS_DEPTH_MM = 1.2      # Profundidade do núcleo da superfície
    
    # Posição do núcleo em relação ao embrião
    NUCLEUS_X_OFFSET_MM = 0.0   # Centro
    NUCLEUS_Y_OFFSET_MM = 0.0   # Centro
    NUCLEUS_Z_OFFSET_MM = -1.2  # Profundidade negativa


@dataclass
class InjectionTarget:
    """Alvo de injeção."""
    x_mm: float   # Posição X em mm
    y_mm: float   # Posição Y em mm
    z_mm: float   # Posição Z (profundidade)
    volume_nl: float  # Volume a injetar (nanolitros)


class ServoMotor:
    """Controla servo motor via PWM."""
    
    def __init__(self, pin: int, name: str = "Servo"):
        """Inicializa servo."""
        GPIO.setup(pin, GPIO.OUT)
        self.pin = pin
        self.name = name
        self.pwm = GPIO.PWM(pin, ServoConfig.SERVO_FREQUENCY_HZ)
        self.pwm.start(0)
        self.current_angle = 90  # Posição neutra (90 graus)
        self.logger = logging.getLogger(f"Servo_{name}")
    
    def angle_to_pulse_width(self, angle: float) -> float:
        """Converte ângulo (0-180) para largura de pulso (1-2ms)."""
        # PWM duty cycle = (pulse_width / period) * 100
        # Para 50Hz: período = 20ms
        pulse_ms = ServoConfig.MIN_PULSE_WIDTH_MS + \
                   (angle / 180.0) * (ServoConfig.MAX_PULSE_WIDTH_MS - 
                                     ServoConfig.MIN_PULSE_WIDTH_MS)
        duty_cycle = (pulse_ms / 20.0) * 100.0
        return duty_cycle
    
    def move_to_angle(self, angle: float, speed: float = 1.0):
        """Move servo para ângulo especificado."""
        if not 0 <= angle <= 180:
            raise ValueError(f"Ângulo deve ser 0-180°, recebido {angle}")
        
        # Calcula duty cycle
        duty_cycle = self.angle_to_pulse_width(angle)
        
        # Move lentamente se speed < 1.0
        steps = max(1, int(abs(angle - self.current_angle) * speed))
        step_size = (angle - self.current_angle) / steps
        
        for i in range(steps):
            new_angle = self.current_angle + (step_size * i)
            new_duty = self.angle_to_pulse_width(new_angle)
            self.pwm.ChangeDutyCycle(new_duty)
            time.sleep(0.01)  # 10ms entre passos
        
        # Posição final
        self.pwm.ChangeDutyCycle(duty_cycle)
        self.current_angle = angle
        self.logger.info(f"{self.name}: {angle}°")
    
    def get_current_angle(self) -> float:
        """Retorna ângulo atual."""
        return self.current_angle
    
    def center(self):
        """Move servo para posição central (90°)."""
        self.move_to_angle(90)


class XYZStage:
    """Plataforma XYZ com 3 servos (posicionamento)."""
    
    # Servo constraints (ângulos correspondem a movimentos)
    SERVO_MIN_ANGLE = 0
    SERVO_MAX_ANGLE = 180
    
    # Mapeamento: ângulo -> deslocamento em mm
    # Assumindo servo com 180° de range
    MM_PER_DEGREE = 0.05  # 0.05mm por grau
    
    def __init__(self, pin_x: int, pin_y: int, pin_z: int):
        """Inicializa plataforma XYZ."""
        self.servo_x = ServoMotor(pin_x, name="X")
        self.servo_y = ServoMotor(pin_y, name="Y")
        self.servo_z = ServoMotor(pin_z, name="Z")
        
        # Posição inicial
        self.position = (0.0, 0.0, 0.0)  # mm
        
        self.logger = logging.getLogger("XYZStage")
        self.logger.info("XYZ Stage inicializado")
    
    def _angle_to_mm(self, angle: float) -> float:
        """Converte ângulo de servo para deslocamento em mm."""
        # Ângulo 90° = posição zero
        return (angle - 90.0) * self.MM_PER_DEGREE
    
    def _mm_to_angle(self, mm: float) -> float:
        """Converte deslocamento em mm para ângulo de servo."""
        return 90.0 + (mm / self.MM_PER_DEGREE)
    
    def move_to(self, x_mm: float, y_mm: float, z_mm: float, 
                speed: float = 0.5):
        """Move para posição XYZ especificada."""
        # Converte mm para ângulos
        angle_x = self._mm_to_angle(x_mm)
        angle_y = self._mm_to_angle(y_mm)
        angle_z = self._mm_to_angle(z_mm)
        
        # Valida
        for angle, name in [(angle_x, 'X'), (angle_y, 'Y'), (angle_z, 'Z')]:
            if not 0 <= angle <= 180:
                self.logger.error(f"Ângulo {name} fora de range: {angle}°")
                return False
        
        # Move simultâneamente
        self.servo_x.move_to_angle(angle_x, speed)
        self.servo_y.move_to_angle(angle_y, speed)
        self.servo_z.move_to_angle(angle_z, speed)
        
        self.position = (x_mm, y_mm, z_mm)
        self.logger.info(f"Movido para ({x_mm:.2f}, {y_mm:.2f}, {z_mm:.2f}) mm")
        return True
    
    def move_relative(self, dx_mm: float, dy_mm: float, dz_mm: float):
        """Move relativamente."""
        new_x = self.position[0] + dx_mm
        new_y = self.position[1] + dy_mm
        new_z = self.position[2] + dz_mm
        return self.move_to(new_x, new_y, new_z)
    
    def get_position(self) -> Tuple[float, float, float]:
        """Retorna posição atual."""
        return self.position
    
    def home(self):
        """Move para posição home (0,0,0)."""
        self.move_to(0, 0, 0)


class SyringeController:
    """Controla seringa de injeção."""
    
    # Seringa de 1mL = 1000µL
    SYRINGE_MAX_VOLUME_UL = 1000
    SERVO_ANGLE_RANGE = 180  # Servo tem 180° de range
    UL_PER_DEGREE = SYRINGE_MAX_VOLUME_UL / SERVO_ANGLE_RANGE
    
    def __init__(self, pin: int):
        """Inicializa servo da seringa."""
        self.servo = ServoMotor(pin, name="Syringe")
        self.current_volume_ul = 1000  # Começa cheia
        self.logger = logging.getLogger("SyringeController")
    
    def inject_volume(self, volume_nl: float):
        """Injeta volume especificado."""
        volume_ul = volume_nl / 1000.0  # Converte nL para µL
        
        if volume_ul > self.current_volume_ul:
            self.logger.error(f"Seringa não tem volume suficiente")
            return False
        
        # Calcula ângulo necessário
        angle_change = (volume_ul / self.UL_PER_DEGREE)
        new_angle = self.servo.current_angle + angle_change
        
        # Move lentamente (injeção)
        self.logger.info(f"Injetando {volume_nl:.0f}nL ({volume_ul:.2f}µL)...")
        self.servo.move_to_angle(new_angle, speed=0.5)
        
        self.current_volume_ul -= volume_ul
        self.logger.info(f"Volume restante: {self.current_volume_ul:.2f}µL")
        return True
    
    def refill(self):
        """Recarrega seringa."""
        self.logger.info("Recarregando seringa...")
        self.servo.move_to_angle(0)  # Volta ao início
        self.current_volume_ul = self.SYRINGE_MAX_VOLUME_UL
        self.logger.info("Seringa recarregada")
    
    def get_remaining_volume(self) -> float:
        """Retorna volume restante em µL."""
        return self.current_volume_ul


class EmbryoInjectionRobot:
    """ROBÔ DE INJEÇÃO EM EMBRIÃO - Sistema completo."""
    
    # Pinos GPIO
    PIN_SERVO_X = 6
    PIN_SERVO_Y = 5
    PIN_SERVO_Z = 14
    PIN_SERVO_SYRINGE = 15
    
    def __init__(self):
        """Inicializa robô de injeção."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.stage = XYZStage(self.PIN_SERVO_X, self.PIN_SERVO_Y, self.PIN_SERVO_Z)
        self.syringe = SyringeController(self.PIN_SERVO_SYRINGE)
        
        self.logger = logging.getLogger("EmbryoInjectionRobot")
        self.logger.info("Robô de injeção inicializado")
    
    def find_embryo_nucleus(self, image) -> Optional[InjectionTarget]:
        """Detecta núcleo do embrião na imagem."""
        # Em produção, usar OpenCV para detecção de núcleo
        # Por enquanto, simula posição conhecida
        
        self.logger.info("Procurando núcleo do embrião...")
        
        # Simula detecção (em produção: usar segmentação de imagem)
        target = InjectionTarget(
            x_mm=0.0,
            y_mm=0.0,
            z_mm=EmbryoInjectionCoordinates.NUCLEUS_Z_OFFSET_MM,
            volume_nl=500.0  # 500 nanolitros
        )
        
        self.logger.info(f"Núcleo encontrado em ({target.x_mm}, {target.y_mm}, {target.z_mm}mm)")
        return target
    
    def inject_dna(self, dna_sequence: str, target: InjectionTarget, 
                   dna_concentration_ng_ul: float = 50.0) -> bool:
        """Injeta DNA no embrião."""
        try:
            self.logger.info("=== INICIANDO INJEÇÃO DE DNA ===")
            self.logger.info(f"Sequência: {len(dna_sequence)}bp")
            self.logger.info(f"Volume: {target.volume_nl}nL")
            
            # 1. Move para posição acima do alvo
            self.logger.info("1. Movendo para posição acima do alvo...")
            self.stage.move_to(
                target.x_mm,
                target.y_mm,
                target.z_mm + 2.0  # 2mm acima
            )
            time.sleep(1.0)
            
            # 2. Desce lentamente até o alvo
            self.logger.info("2. Descendo agulha...")
            self.stage.move_to(
                target.x_mm,
                target.y_mm,
                target.z_mm - 0.2,  # Um pouco abaixo (para penetração)
                speed=0.3  # Muito lento
            )
            time.sleep(0.5)
            
            # 3. Injeta DNA
            self.logger.info("3. Injetando DNA...")
            injection_speed = target.volume_nl / 500  # nanolitros por segundo
            self.logger.info(f"   Velocidade de injeção: {injection_speed:.1f}nL/s")
            
            # Injeta em 10 incrementos (para melhor distribuição)
            increment = target.volume_nl / 10
            for i in range(10):
                self.syringe.inject_volume(increment)
                time.sleep(0.2)  # 200ms entre incrementos
                self.logger.info(f"   Injetado {(i+1)*10}%")
            
            # 4. Retira agulha
            self.logger.info("4. Retirando agulha...")
            self.stage.move_to(
                target.x_mm,
                target.y_mm,
                target.z_mm + 2.0,  # Volta para cima
                speed=0.5
            )
            
            self.logger.info("✓ Injeção concluída com sucesso!")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Erro durante injeção: {e}")
            # Move para posição segura
            self.stage.home()
            return False
    
    def calibrate(self):
        """Calibra robô antes de injeção."""
        self.logger.info("=== CALIBRAÇÃO DO ROBÔ ===")
        
        # Move para home
        self.logger.info("1. Movendo para posição HOME...")
        self.stage.home()
        time.sleep(1)
        
        # Testa movimento X
        self.logger.info("2. Testando movimento X...")
        self.stage.move_to(2.0, 0, 0)
        time.sleep(0.5)
        self.stage.move_to(-2.0, 0, 0)
        time.sleep(0.5)
        self.stage.home()
        
        # Testa movimento Y
        self.logger.info("3. Testando movimento Y...")
        self.stage.move_to(0, 2.0, 0)
        time.sleep(0.5)
        self.stage.move_to(0, -2.0, 0)
        time.sleep(0.5)
        self.stage.home()
        
        # Testa movimento Z
        self.logger.info("4. Testando movimento Z...")
        self.stage.move_to(0, 0, 2.0)
        time.sleep(0.5)
        self.stage.move_to(0, 0, -2.0)
        time.sleep(0.5)
        self.stage.home()
        
        # Testa seringa
        self.logger.info("5. Testando seringa...")
        self.syringe.inject_volume(100)  # Injeta 100nL
        time.sleep(1)
        self.syringe.refill()
        
        self.logger.info("✓ Calibração concluída!")
    
    def cleanup(self):
        """Limpa recursos."""
        self.logger.info("Finalizando robô...")
        self.stage.home()
        GPIO.cleanup()
        self.logger.info("Robô finalizado")


# ============================================================================
# TESTE
# ============================================================================

if __name__ == "__main__":
    logger.info("=== TESTE DO ROBÔ DE INJEÇÃO ===")
    
    robot = EmbryoInjectionRobot()
    
    # Calibra robô
    robot.calibrate()
    
    # Simula injeção de DNA
    dna = "ATGC" * 750_000  # 3Mb para teste
    target = InjectionTarget(x_mm=0, y_mm=0, z_mm=-1.2, volume_nl=500)
    
    success = robot.inject_dna(dna, target)
    
    if success:
        logger.info("Injeção realizada com sucesso!")
    else:
        logger.error("Falha na injeção")
    
    robot.cleanup()
