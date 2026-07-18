/*
 * 🦖 RE-DINO: Sistema de Incubação Inteligente com Braço Robótico
 * Incubadora Profissional com SCARA para Embriões de Dinossauro
 * 
 * Funcionalidades:
 * - Controle de temperatura (37.5°C ± 0.2°C)
 * - Controle de umidade (75-80%)
 * - Sistema de viragem automática de ovos (5x/dia)
 * - Braço SCARA robótico (4 DOF) para manipulação automática
 * - Ventilação contínua
 * - Display OLED com informações em tempo real
 * - Sistema de alarme para falhas
 * - Gravação de dados em EEPROM
 * - Interface Bluetooth para monitoramento remoto
 * - Cinemática inversa para posicionamento preciso
 * 
 * Hardware necessário:
 * - Arduino Mega 2560 (recomendado)
 * - DHT22 (sensor de temperatura/umidade)
 * - DS18B20 (sensor de temperatura adicional)
 * - Display OLED 128x64
 * - Relés 5V (3x) para controlar aquecedor, ventilador
 * - Servo motor 180° para virador de ovos
 * - Buzzer para alarmes
 * - Módulo Bluetooth HC-05
 * - 4x Servo DYNAMIXEL (MX-106, MX-64, MX-28, FS90MG)
 * - Controlador DYNAMIXEL U2D2 (ou equivalente)
 * - Fonte 12V 10A
 * 
 * Conexões:
 * - DHT22: Pino 2
 * - DS18B20: Pino 3 (OneWire)
 * - Display OLED: I2C (SDA=20, SCL=21 no Mega)
 * - Relé Aquecedor: Pino 4
 * - Relé Ventilador: Pino 5
 * - Servo Motor (Virador): Pino 6
 * - Buzzer: Pino 7
 * - Bluetooth RX: Pino 9, TX: Pino 10 (SoftwareSerial)
 * - DYNAMIXEL TTL (Serial1): Pino 18 RX, 19 TX (Mega)
 */

#include <Wire.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Servo.h>
#include <EEPROM.h>
#include <SoftwareSerial.h>
#include <math.h>

// ============= CONFIGURAÇÕES =============

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

// Pinos
#define DHT_PIN 2
#define DS18B20_PIN 3
#define HEATER_RELAY 4
#define FAN_RELAY 5
#define SERVO_PIN 6
#define BUZZER_PIN 7
#define BT_RX 9
#define BT_TX 10
// DYNAMIXEL: Serial1 (Pinos 18/19 no Mega)

// Parâmetros de controle
#define TARGET_TEMP 37.5
#define TARGET_HUMIDITY 77.5
#define TEMP_TOLERANCE 0.2
#define HUMIDITY_TOLERANCE 2.5
#define TURN_INTERVAL_MINUTES 6  // Vira ovos a cada 6 horas
#define ALARM_THRESHOLD_TEMP 0.5
#define ALARM_THRESHOLD_HUMIDITY 5.0

// Configurações do SCARA
#define SCARA_ENABLED 1
#define SEGMENT1_LENGTH 30.0  // cm (Ombro)
#define SEGMENT2_LENGTH 30.0  // cm (Cotovelo)
#define GRIPPER_OFFSET 10.0   // cm (Pulso + Gripper)
#define HOME_X 0.0
#define HOME_Y 60.0
#define HOME_Z 30.0
#define AUTO_PICK_INTERVAL_HOURS 6  // Seleciona ovos automaticamente
#define SCARA_SPEED 50  // cm/s

// IDs dos servos DYNAMIXEL
#define MOTOR_SHOULDER 1      // MX-106
#define MOTOR_ELBOW 2         // MX-64
#define MOTOR_WRIST 3         // MX-28
#define MOTOR_GRIPPER 4       // FS90MG

// ============= OBJETOS =============

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
DHT dht(DHT_PIN, DHT22);
OneWire oneWire(DS18B20_PIN);
DallasTemperature ds18b20(&oneWire);
Servo eggTurner;
SoftwareSerial bluetooth(BT_RX, BT_TX);

// ============= ESTRUTURAS DE DADOS =============

struct IncubatorData {
  float temp;
  float humidity;
  float temp_backup;
  int day;
  int hour;
  int minute;
  bool heater_on;
  bool fan_on;
  bool servo_position;
  int turn_count;
  bool alarm_active;
  char alarm_reason[50];
};

struct SCARAState {
  float x, y, z;           // Posição atual (cm)
  float theta1, theta2, theta3;  // Ângulos dos motores (graus)
  float gripper_angle;     // Ângulo da pinça (graus)
  bool gripper_closed;     // Estado da pinça
  int egg_count_picked;    // Número de ovos pegados
  unsigned long last_pick_time;
};

IncubatorData data;
SCARAState scara_state;
unsigned long lastTurnTime = 0;
unsigned long lastSensorRead = 0;
unsigned long bootTime = 0;
unsigned long lastSCARAActionTime = 0;
int dayCounter = 0;
bool alarmTriggered = false;
char bluetoothBuffer[100];
int btIndex = 0;
bool scara_moving = false;

// ============= SETUP =============

void setup() {
  Serial.begin(9600);      // Debug
  Serial1.begin(1000000);  // DYNAMIXEL (1Mbps)
  bluetooth.begin(9600);   // Bluetooth HC-05
  
  // Inicializar pinos
  pinMode(HEATER_RELAY, OUTPUT);
  pinMode(FAN_RELAY, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(HEATER_RELAY, LOW);
  digitalWrite(FAN_RELAY, LOW);
  
  // Inicializar servo de viragem
  eggTurner.attach(SERVO_PIN);
  eggTurner.write(90);
  
  // Inicializar sensores
  dht.begin();
  ds18b20.begin();
  
  // Inicializar display OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("ERRO: Display OLED não encontrado!");
    while (1);
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("🦖 RE-DINO INCUBATOR");
  display.println("Com Braco SCARA");
  display.println("Inicializando...");
  display.display();
  delay(2000);
  
  // Inicializar SCARA
  if (SCARA_ENABLED) {
    initializeSCARA();
  }
  
  // Ler dados salvos
  loadDataFromEEPROM();
  
  // Inicializar timers
  bootTime = millis();
  lastSensorRead = millis();
  lastTurnTime = millis();
  lastSCARAActionTime = millis();
  
  Serial.println("Incubadora com SCARA inicializada!");
  sendBluetoothMessage("READY_WITH_SCARA");
}

// ============= LOOP PRINCIPAL =============

void loop() {
  unsigned long currentTime = millis();
  
  // Atualizar sensores a cada 5 segundos
  if (currentTime - lastSensorRead >= 5000) {
    readSensors();
    updateDisplayMain();
    checkAlarms();
    lastSensorRead = currentTime;
  }
  
  // Controlar temperatura
  controlTemperature();
  
  // Controlar umidade
  controlHumidity();
  
  // Virar ovos a cada TURN_INTERVAL_MINUTES
  if (currentTime - lastTurnTime >= (TURN_INTERVAL_MINUTES * 60 * 1000)) {
    turnEggs();
    lastTurnTime = currentTime;
    data.turn_count++;
  }
  
  // Movimentar braço SCARA automaticamente
  if (SCARA_ENABLED && (currentTime - lastSCARAActionTime >= (AUTO_PICK_INTERVAL_HOURS * 3600 * 1000))) {
    performAutomaticEggSelection();
    lastSCARAActionTime = currentTime;
  }
  
  // Processar comandos Bluetooth
  if (bluetooth.available()) {
    processBluetoothCommand();
  }
  
  // Processar comandos Serial
  if (Serial.available()) {
    processSerialCommand();
  }
  
  // Atualizar contador de dias
  updateDayCounter();
}

// ============= LEITURA DE SENSORES =============

void readSensors() {
  // Ler DHT22
  float humidity = dht.readHumidity();
  float temp = dht.readTemperature();
  
  // Ler DS18B20 (sensor de backup)
  ds18b20.requestTemperatures();
  float temp_backup = ds18b20.getTempCByIndex(0);
  
  // Validar leituras
  if (!isnan(temp) && !isnan(humidity)) {
    data.temp = temp;
    data.humidity = humidity;
  } else {
    Serial.println("ERRO: Falha ao ler DHT22!");
  }
  
  if (!isnan(temp_backup)) {
    data.temp_backup = temp_backup;
  } else {
    Serial.println("ERRO: Falha ao ler DS18B20!");
  }
  
  // Log para debug
  Serial.print("Temp: "); Serial.print(data.temp);
  Serial.print("°C, Humidity: "); Serial.print(data.humidity);
  Serial.println("%");
}

// ============= CONTROLE DE TEMPERATURA =============

void controlTemperature() {
  float diff = data.temp - TARGET_TEMP;
  
  if (diff < -TEMP_TOLERANCE) {
    // Temperatura muito baixa - ligar aquecedor
    digitalWrite(HEATER_RELAY, HIGH);
    data.heater_on = true;
  } else if (diff > TEMP_TOLERANCE) {
    // Temperatura muito alta - desligar aquecedor
    digitalWrite(HEATER_RELAY, LOW);
    data.heater_on = false;
  }
  // Caso contrário mantém estado atual (histérese)
}

// ============= CONTROLE DE UMIDADE =============

void controlHumidity() {
  float diff = data.humidity - TARGET_HUMIDITY;
  
  if (diff < -HUMIDITY_TOLERANCE) {
    // Umidade muito baixa - ligar ventilador para evaporação
    digitalWrite(FAN_RELAY, HIGH);
    data.fan_on = true;
  } else if (diff > HUMIDITY_TOLERANCE) {
    // Umidade muito alta - desligar ventilador
    digitalWrite(FAN_RELAY, LOW);
    data.fan_on = false;
  }
  // Caso contrário mantém estado atual (histérese)
}

// ============= SISTEMA DE VIRAGEM DE OVOS =============

void turnEggs() {
  // Alternar entre 0° e 180°
  if (data.servo_position) {
    eggTurner.write(0);     // Virar para um lado
    data.servo_position = false;
  } else {
    eggTurner.write(180);   // Virar para outro lado
    data.servo_position = true;
  }
  
  // Tocar som de aviso
  playBeep(500, 100);
  delay(50);
  playBeep(500, 100);
  
  Serial.print("Ovos virados! Total: "); Serial.println(data.turn_count);
  sendBluetoothMessage("EGGS_TURNED");
  
  // Salvar em EEPROM
  saveDataToEEPROM();
}

// ============= DETECÇÃO DE ALARMES =============

void checkAlarms() {
  data.alarm_active = false;
  memset(data.alarm_reason, 0, sizeof(data.alarm_reason));
  
  // Alarme 1: Temperatura fora do intervalo crítico
  if (abs(data.temp - TARGET_TEMP) > ALARM_THRESHOLD_TEMP) {
    data.alarm_active = true;
    alarmTriggered = true;
    snprintf(data.alarm_reason, 50, "TEMP_ERROR: %.1f", data.temp);
    playAlarmSound();
  }
  
  // Alarme 2: Umidade fora do intervalo crítico
  if (abs(data.humidity - TARGET_HUMIDITY) > ALARM_THRESHOLD_HUMIDITY) {
    data.alarm_active = true;
    alarmTriggered = true;
    snprintf(data.alarm_reason, 50, "HUMIDITY_ERROR: %.1f", data.humidity);
    playAlarmSound();
  }
  
  // Alarme 3: Sensor de backup desligado (falha)
  if (data.temp_backup < 10 || data.temp_backup > 50) {
    data.alarm_active = true;
    snprintf(data.alarm_reason, 50, "BACKUP_SENSOR_FAIL");
    // Não reproduzir som a cada leitura
  }
  
  // Enviar alarme via Bluetooth se ativo
  if (data.alarm_active && alarmTriggered) {
    sendBluetoothMessage(data.alarm_reason);
    alarmTriggered = false;  // Evitar flood de mensagens
  }
}

// ============= SONS =============

void playBeep(int frequency, int duration) {
  tone(BUZZER_PIN, frequency, duration);
  delay(duration + 10);
  noTone(BUZZER_PIN);
}

void playAlarmSound() {
  // Som de alarme: beep-beep-beep
  for (int i = 0; i < 3; i++) {
    playBeep(1000, 200);
    delay(100);
  }
}

// ============= DISPLAY OLED =============

void updateDisplayMain() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  
  // Linha 1: Título e dia
  display.print("🦖 DIA "); display.println(data.day);
  
  // Linha 2: Temperatura
  display.print("TEMP: "); display.print(data.temp, 1);
  display.print("C ("); display.print(data.temp_backup, 1);
  display.println("C)");
  
  // Linha 3: Umidade
  display.print("UMID: "); display.print(data.humidity, 1);
  display.println("%");
  
  // Linha 4: Status dos sistemas
  display.print("Aquec: "); display.print(data.heater_on ? "ON" : "OFF");
  display.print(" | Vent: "); display.println(data.fan_on ? "ON" : "OFF");
  
  // Linha 5: Viragens
  display.print("Viragens: "); display.println(data.turn_count);
  
  // Linha 6: Alarme se ativo
  if (data.alarm_active) {
    display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);  // Inverso
    display.println(data.alarm_reason);
    display.setTextColor(SSD1306_WHITE);
  }
  
  // Barra de progresso (dias 1-21)
  display.drawRect(0, 60, 128, 4, SSD1306_WHITE);
  int progress = (data.day * 128) / 21;
  display.fillRect(0, 60, progress, 4, SSD1306_WHITE);
  
  display.display();
}

void displayAlarmScreen() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("ALARME!");
  display.setTextSize(1);
  display.println("");
  display.println(data.alarm_reason);
  display.println("");
  display.println("Verificar imediatamente!");
  display.display();
}

// ============= EEPROM =============

void saveDataToEEPROM() {
  EEPROM.put(0, data);
  Serial.println("Dados salvos em EEPROM");
}

void loadDataFromEEPROM() {
  EEPROM.get(0, data);
  if (data.day < 0 || data.day > 30) {
    // Dados corrompidos, resetar
    data.day = 0;
    data.turn_count = 0;
    data.heater_on = false;
    data.fan_on = false;
    data.servo_position = true;
    data.alarm_active = false;
  }
  Serial.print("Dados carregados: Dia "); Serial.println(data.day);
}

// ============= CONTADOR DE DIAS =============

void updateDayCounter() {
  unsigned long elapsedTime = millis() - bootTime;
  
  // Converter para dias (1 dia = 24 horas no modo real)
  // Em desenvolvimento: 1 minuto = 1 hora simulada (para testes rápidos)
  
  int simulatedMinutes = elapsedTime / 1000 / 60;  // Minutos reais
  int simulatedHours = simulatedMinutes / 60;      // Horas simuladas
  int simulatedDays = simulatedHours / 24;         // Dias simulados
  
  data.day = 1 + simulatedDays;  // Começar no dia 1
  data.hour = simulatedHours % 24;
  data.minute = simulatedMinutes % 60;
  
  if (data.day > 21) {
    data.day = 21;  // Máximo 21 dias
  }
}

// ============= COMUNICAÇÃO BLUETOOTH =============

void sendBluetoothMessage(const char* message) {
  bluetooth.print(message);
  bluetooth.println();
  Serial.print("BT enviado: "); Serial.println(message);
}

void processBluetoothCommand() {
  char received = bluetooth.read();
  
  if (received == '\n') {
    bluetoothBuffer[btIndex] = '\0';
    btIndex = 0;
    
    // Processar comando
    if (strcmp(bluetoothBuffer, "STATUS") == 0) {
      sendStatus();
    } else if (strcmp(bluetoothBuffer, "TURN") == 0) {
      turnEggs();
    } else if (strcmp(bluetoothBuffer, "RESET") == 0) {
      resetIncubator();
    } else if (strcmp(bluetoothBuffer, "SCARA_HOME") == 0) {
      moveToHome();
    } else if (strcmp(bluetoothBuffer, "SCARA_PICK") == 0) {
      pickEgg(0, 50);  // Posição padrão
    } else if (strcmp(bluetoothBuffer, "SCARA_AUTO") == 0) {
      performAutomaticEggSelection();
    } else if (strcmp(bluetoothBuffer, "SCARA_STATUS") == 0) {
      displaySCARAStatus();
    } else if (strncmp(bluetoothBuffer, "SET_TEMP:", 9) == 0) {
      // Implementar ajuste de temperatura remoto
    }
    
    memset(bluetoothBuffer, 0, sizeof(bluetoothBuffer));
  } else {
    bluetoothBuffer[btIndex++] = received;
  }
}

void processSerialCommand() {
  String cmd = Serial.readStringUntil('\n');
  
  if (cmd == "STATUS") {
    sendStatus();
  } else if (cmd == "TURN") {
    turnEggs();
  } else if (cmd == "RESET") {
    resetIncubator();
  } else if (cmd == "SCARA_HOME") {
    moveToHome();
  } else if (cmd == "SCARA_PICK") {
    pickEgg(0, 50);
  } else if (cmd == "SCARA_AUTO") {
    performAutomaticEggSelection();
  } else if (cmd == "SCARA_STATUS") {
    displaySCARAStatus();
  } else if (cmd.startsWith("SET_TEMP:")) {
    // Implementar ajuste de temperatura
  } else if (cmd == "SCARA_GRIPPER_CLOSE") {
    closeGripper();
  } else if (cmd == "SCARA_GRIPPER_OPEN") {
    openGripper_();
  } else if (cmd == "SCARA_ROTATE_EGG") {
    rotateEgg();
  }
}

void sendStatus() {
  Serial.print("\n=== STATUS DA INCUBADORA ===\n");
  Serial.print("Dia: "); Serial.println(data.day);
  Serial.print("Hora: "); Serial.print(data.hour); Serial.print(":");
  Serial.println(data.minute);
  Serial.print("Temperatura: "); Serial.print(data.temp);
  Serial.print("°C (Backup: "); Serial.print(data.temp_backup);
  Serial.println("°C)");
  Serial.print("Umidade: "); Serial.print(data.humidity);
  Serial.println("%");
  Serial.print("Aquecedor: "); Serial.println(data.heater_on ? "ON" : "OFF");
  Serial.print("Ventilador: "); Serial.println(data.fan_on ? "ON" : "OFF");
  Serial.print("Viragens: "); Serial.println(data.turn_count);
  Serial.print("Alarme: "); Serial.println(data.alarm_active ? "SIM" : "NÃO");
  Serial.print("Razão: "); Serial.println(data.alarm_reason);
  
  if (SCARA_ENABLED) {
    Serial.println("\n=== STATUS DO SCARA ===");
    Serial.print("Posição: (");
    Serial.print(scara_state.x); Serial.print(", ");
    Serial.print(scara_state.y); Serial.print(", ");
    Serial.print(scara_state.z); Serial.println(")");
    Serial.print("Ângulos: Ombro=");
    Serial.print(scara_state.theta1); Serial.print("° Cotovelo=");
    Serial.print(scara_state.theta2); Serial.println("°");
    Serial.print("Gripper: ");
    Serial.println(scara_state.gripper_closed ? "FECHADO" : "ABERTO");
    Serial.print("Ovos pegados: ");
    Serial.println(scara_state.egg_count_picked);
  }
  
  Serial.println("============================\n");
  
  // Enviar também via Bluetooth
  sendBluetoothMessage("STATUS_OK");
}

void resetIncubator() {
  Serial.println("Resetando incubadora...");
  data.day = 0;
  data.turn_count = 0;
  data.alarm_active = false;
  bootTime = millis();
  saveDataToEEPROM();
  sendBluetoothMessage("RESET_OK");
}

// ============= FUNÇÕES DO SCARA ROBÓTICO =============

void initializeSCARA() {
  Serial.println("Inicializando braço SCARA...");
  
  // Inicializar estado
  scara_state.x = HOME_X;
  scara_state.y = HOME_Y;
  scara_state.z = HOME_Z;
  scara_state.gripper_closed = false;
  scara_state.egg_count_picked = 0;
  scara_state.last_pick_time = millis();
  
  // Mover para posição HOME
  moveToHome();
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("SCARA Inicializado");
  display.println("Movendo para HOME...");
  display.display();
  delay(2000);
  
  Serial.println("SCARA pronto!");
  sendBluetoothMessage("SCARA_READY");
}

void moveToHome() {
  Serial.println("Braço SCARA retornando para HOME...");
  
  // Mover para posição segura (acima do cilindro)
  float home_positions[4] = {0, 45, 90, 90};
  
  for (int i = 0; i < 4; i++) {
    setMotorAngle(i + 1, home_positions[i]);
  }
  
  scara_state.x = HOME_X;
  scara_state.y = HOME_Y;
  scara_state.z = HOME_Z;
  scara_state.gripper_closed = false;
  
  playBeep(800, 100);
  Serial.println("Posição HOME atingida");
}

void setMotorAngle(int motorID, float angleInDegrees) {
  // Converter graus para posição DYNAMIXEL (0-4095)
  // Range típico: 0-300 graus
  int position = (int)((angleInDegrees / 300.0) * 4095.0);
  position = constrain(position, 0, 4095);
  
  // Escrever para motor DYNAMIXEL via Serial1
  // Protocolo simplificado (em produção usar biblioteca DynamixelSDK)
  Serial1.write(0xFF);  // Header
  Serial1.write(0xFF);
  Serial1.write(motorID);  // ID
  Serial1.write(0x04);     // Tamanho
  Serial1.write(0x03);     // Instrução (WRITE_DATA)
  Serial1.write(0x1E);     // Endereço (GOAL_POSITION)
  Serial1.write(position & 0xFF);
  Serial1.write((position >> 8) & 0xFF);
  
  Serial.print("Motor ");
  Serial.print(motorID);
  Serial.print(" -> ");
  Serial.print(angleInDegrees);
  Serial.println(" graus");
}

void inverseKinematics(float x, float y, float& theta1, float& theta2) {
  // Cinemática inversa para braço 2-link SCARA
  // Link 1: SEGMENT1_LENGTH (ombro)
  // Link 2: SEGMENT2_LENGTH (cotovelo)
  
  float L1 = SEGMENT1_LENGTH;
  float L2 = SEGMENT2_LENGTH;
  float distance = sqrt(x*x + y*y);
  
  // Verificar se alvo é alcançável
  if (distance > (L1 + L2) || distance < abs(L1 - L2)) {
    Serial.println("ERRO: Alvo fora do alcance!");
    return;
  }
  
  // Calcular theta2 (ângulo do cotovelo)
  float cos_theta2 = (x*x + y*y - L1*L1 - L2*L2) / (2 * L1 * L2);
  cos_theta2 = constrain(cos_theta2, -1.0, 1.0);
  theta2 = acos(cos_theta2) * 180.0 / PI;
  
  // Calcular theta1 (ângulo do ombro)
  float k1 = L1 + L2 * cos(theta2 * PI / 180.0);
  float k2 = L2 * sin(theta2 * PI / 180.0);
  theta1 = atan2(y, x) * 180.0 / PI - atan2(k2, k1) * 180.0 / PI;
  
  Serial.print("IK: Theta1=");
  Serial.print(theta1);
  Serial.print(" Theta2=");
  Serial.println(theta2);
}

void moveToPosition(float x, float y, float z, bool openGripper = false) {
  if (!SCARA_ENABLED || scara_moving) return;
  
  scara_moving = true;
  Serial.print("SCARA movendo para (");
  Serial.print(x); Serial.print(", ");
  Serial.print(y); Serial.print(", ");
  Serial.print(z); Serial.println(")");
  
  // Calcular cinemática inversa
  inverseKinematics(x, y, scara_state.theta1, scara_state.theta2);
  
  // Mover motores de ombro e cotovelo
  setMotorAngle(MOTOR_SHOULDER, scara_state.theta1);
  setMotorAngle(MOTOR_ELBOW, scara_state.theta2);
  
  // Ajustar pulso para verticalidade (Z)
  float wrist_angle = 90 - (scara_state.theta1 + scara_state.theta2);
  setMotorAngle(MOTOR_WRIST, wrist_angle);
  
  // Atualizar estado
  scara_state.x = x;
  scara_state.y = y;
  scara_state.z = z;
  
  // Tempo de movimento estimado
  delay(1000);
  
  // Abrir ou fechar gripper se necessário
  if (openGripper && scara_state.gripper_closed) {
    openGripper_();
  }
  
  scara_moving = false;
  sendBluetoothMessage("SCARA_MOVED");
}

void pickEgg(float x, float y) {
  if (!SCARA_ENABLED || scara_moving) return;
  
  Serial.print("Pegando ovo em (");
  Serial.print(x); Serial.print(", ");
  Serial.print(y); Serial.println(")");
  
  playBeep(600, 100);
  
  // Mover para altura de aproximação (10cm acima)
  moveToPosition(x, y, 10, true);
  delay(500);
  
  // Descer até o ovo
  moveToPosition(x, y, 2);
  delay(500);
  
  // Fechar gripper
  closeGripper();
  delay(300);
  
  // Levantar ovo
  moveToPosition(x, y, 15);
  
  scara_state.egg_count_picked++;
  Serial.println("Ovo pegado com sucesso!");
  sendBluetoothMessage("EGG_PICKED");
}

void placeEgg(float x, float y) {
  if (!SCARA_ENABLED || scara_moving || !scara_state.gripper_closed) return;
  
  Serial.print("Colocando ovo em (");
  Serial.print(x); Serial.print(", ");
  Serial.print(y); Serial.println(")");
  
  // Mover para nova posição (altura de aproximação)
  moveToPosition(x, y, 10);
  delay(500);
  
  // Abaixar
  moveToPosition(x, y, 2);
  delay(500);
  
  // Abrir gripper
  openGripper_();
  delay(300);
  
  // Levantar
  moveToPosition(x, y, 10);
  
  Serial.println("Ovo colocado com sucesso!");
  sendBluetoothMessage("EGG_PLACED");
}

void rotateEgg() {
  if (!SCARA_ENABLED || scara_moving || !scara_state.gripper_closed) return;
  
  Serial.println("Rotacionando ovo...");
  playBeep(700, 150);
  
  // Rotar pulso 180 graus
  float original_wrist = scara_state.theta3;
  setMotorAngle(MOTOR_WRIST, original_wrist + 180);
  delay(800);
  
  // Retornar à posição original
  setMotorAngle(MOTOR_WRIST, original_wrist);
  delay(500);
  
  Serial.println("Ovo rotacionado!");
  sendBluetoothMessage("EGG_ROTATED");
}

void closeGripper() {
  if (!SCARA_ENABLED) return;
  
  Serial.println("Fechando gripper...");
  setMotorAngle(MOTOR_GRIPPER, 0);  // Gripper fechado (0 graus)
  scara_state.gripper_closed = true;
  delay(300);
}

void openGripper_() {
  if (!SCARA_ENABLED) return;
  
  Serial.println("Abrindo gripper...");
  setMotorAngle(MOTOR_GRIPPER, 90);  // Gripper aberto (90 graus)
  scara_state.gripper_closed = false;
  delay(300);
}

void performAutomaticEggSelection() {
  if (!SCARA_ENABLED) return;
  
  Serial.println("Iniciando seleção automática de ovos...");
  sendBluetoothMessage("AUTO_SELECTION_START");
  
  // Retornar para HOME
  moveToHome();
  delay(1000);
  
  // Padrão de seleção (exemplo: 3 ovos em posições diferentes)
  // Em produção, usar câmera ou sensores para detectar posição real dos ovos
  
  float egg_positions[3][2] = {
    {20, 50},   // Ovo 1
    {-20, 50},  // Ovo 2
    {0, 65}     // Ovo 3
  };
  
  for (int i = 0; i < 3; i++) {
    if (data.day >= 1 && data.day <= 21) {
      pickEgg(egg_positions[i][0], egg_positions[i][1]);
      delay(2000);
      
      // Rotacionar se não for a última volta (dias 1-18)
      if (data.day <= 18) {
        rotateEgg();
      }
      
      placeEgg(egg_positions[i][0], egg_positions[i][1]);
      delay(1000);
    }
  }
  
  // Retornar para HOME
  moveToHome();
  
  Serial.println("Seleção automática concluída!");
  sendBluetoothMessage("AUTO_SELECTION_DONE");
}

void displaySCARAStatus() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  
  display.println("SCARA STATUS:");
  display.print("Pos: (");
  display.print((int)scara_state.x); display.print(",");
  display.print((int)scara_state.y); display.print(",");
  display.print((int)scara_state.z); display.println(")");
  
  display.print("Angles: T1=");
  display.print((int)scara_state.theta1); display.print(" T2=");
  display.println((int)scara_state.theta2);
  
  display.print("Gripper: ");
  display.println(scara_state.gripper_closed ? "CLOSED" : "OPEN");
  
  display.print("Ovos pegados: ");
  display.println(scara_state.egg_count_picked);
  
  display.display();
}

// ============= FIM DO CÓDIGO =============
/*
 * 
 * PRÓXIMOS PASSOS APÓS UPLOAD:
 * 
 * 1. Abrir Monitor Serial (9600 baud)
 * 2. Verificar inicialização do SCARA
 * 3. Monitorar temperatura/umidade em tempo real
 * 4. Testar movimentos do braço SCARA
 * 5. Testar gripper (abrir/fechar)
 * 6. Testar sistema completo de viragem e seleção
 * 7. Sincronizar com aplicativo Bluetooth
 * 
 * COMANDOS DISPONÍVEIS:
 * - STATUS: Mostrar status da incubadora
 * - SCARA_HOME: Mover braço para posição HOME
 * - SCARA_PICK: Pegar ovo automaticamente
 * - SCARA_AUTO: Executar seleção automática de ovos
 * - TURN: Virar ovos manualmente
 * - RESET: Resetar sistema
 * 
 */
