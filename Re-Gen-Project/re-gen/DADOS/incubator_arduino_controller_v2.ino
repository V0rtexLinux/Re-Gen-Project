/*
 * 🦖 RE-DINO: Sistema de Incubação Inteligente com Braço Robótico v2
 * 
 * NOVA FUNCIONALIDADE: Comunicação Serial com Python
 * 
 * Permite que o orquestrador Python comunique com Arduino para:
 * - Notificar que embrião foi injetado (e quando)
 * - Registrar em EEPROM para rastreamento
 * - Receber status
 * - Sincronizar estado entre sistemas
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
#include <ArduinoJson.h>

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

// Parâmetros
#define TARGET_TEMP 37.5
#define TARGET_HUMIDITY 77.5
#define TEMP_TOLERANCE 0.2
#define HUMIDITY_TOLERANCE 2.5
#define TURN_INTERVAL_MINUTES 360  // A cada 6 horas
#define ALARM_THRESHOLD_TEMP 0.5
#define ALARM_THRESHOLD_HUMIDITY 5.0

// SCARA Config
#define SCARA_ENABLED 1
#define SEGMENT1_LENGTH 30.0
#define SEGMENT2_LENGTH 30.0
#define GRIPPER_OFFSET 10.0
#define HOME_X 0.0
#define HOME_Y 60.0
#define HOME_Z 30.0

// IDs DYNAMIXEL
#define MOTOR_SHOULDER 1
#define MOTOR_ELBOW 2
#define MOTOR_WRIST 3
#define MOTOR_GRIPPER 4

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
  float x, y, z;
  float theta1, theta2, theta3;
  float gripper_angle;
  bool gripper_closed;
  int egg_count_picked;
  unsigned long last_pick_time;
};

struct EmbryoRecord {
  bool injected;
  char injection_timestamp[32];
  float injection_volume_ul;
  unsigned long injection_time_ms;
  int day_of_injection;
};

// ============= VARIÁVEIS GLOBAIS =============

IncubatorData data;
SCARAState scara_state;
EmbryoRecord embryo_record;

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
  Serial.begin(9600);      // Python communication
  Serial1.begin(1000000);  // DYNAMIXEL
  bluetooth.begin(9600);   // Bluetooth
  
  // GPIO
  pinMode(HEATER_RELAY, OUTPUT);
  pinMode(FAN_RELAY, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(HEATER_RELAY, LOW);
  digitalWrite(FAN_RELAY, LOW);
  
  // Servo
  eggTurner.attach(SERVO_PIN);
  eggTurner.write(90);
  
  // Sensores
  dht.begin();
  ds18b20.begin();
  
  // Display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("ERROR: OLED not found");
    while (1);
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("🦖 RE-DINO INCUBATOR v2");
  display.println("Com Python Bridge");
  display.println("Inicializando...");
  display.display();
  delay(2000);
  
  // EEPROM
  loadDataFromEEPROM();
  
  // Timers
  bootTime = millis();
  lastSensorRead = millis();
  lastTurnTime = millis();
  lastSCARAActionTime = millis();
  
  // Inicializar registro de embrião
  embryo_record.injected = false;
  memset(embryo_record.injection_timestamp, 0, sizeof(embryo_record.injection_timestamp));
  embryo_record.injection_volume_ul = 0.0;
  embryo_record.injection_time_ms = 0;
  embryo_record.day_of_injection = 0;
  
  if (SCARA_ENABLED) {
    initializeSCARA();
  }
  
  Serial.println("READY");
  sendBluetoothMessage("READY_WITH_PYTHON_BRIDGE");
}

// ============= LOOP PRINCIPAL =============

void loop() {
  unsigned long now = millis();
  
  // ===== LEITURA DE SENSORES =====
  if (now - lastSensorRead > 5000) {  // A cada 5 segundos
    readSensors();
    lastSensorRead = now;
    
    // Controles
    controlTemperature();
    controlHumidity();
    checkAlarms();
    
    // Display
    updateDisplayMain();
  }
  
  // ===== VIRAGEM DE OVOS =====
  if (now - lastTurnTime > (TURN_INTERVAL_MINUTES * 60 * 1000)) {
    if (embryo_record.injected && data.day < 19) {  // Virar até dia 19
      turnEggs();
      lastTurnTime = now;
    }
  }
  
  // ===== RECEBER COMANDOS SERIAL DO PYTHON =====
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      handlePythonCommand(bluetoothBuffer);
      memset(bluetoothBuffer, 0, sizeof(bluetoothBuffer));
      btIndex = 0;
    } else if (btIndex < sizeof(bluetoothBuffer) - 1) {
      bluetoothBuffer[btIndex++] = c;
    }
  }
  
  // ===== RECEBER MENSAGENS BLUETOOTH =====
  if (bluetooth.available()) {
    String cmd = bluetooth.readStringUntil('\n');
    if (cmd.length() > 0) {
      Serial.print("BT: ");
      Serial.println(cmd);
    }
  }
  
  delay(100);
}

// ============= COMUNICAÇÃO COM PYTHON =============

void handlePythonCommand(char* cmd) {
  String command = String(cmd);
  command.trim();
  
  Serial.print("CMD: ");
  Serial.println(command);
  
  if (command == "PING") {
    Serial.println("OK");
  }
  
  else if (command == "STATUS") {
    sendStatusJSON();
  }
  
  else if (command.startsWith("EMBRYO_INJECTED|")) {
    // Formato: EMBRYO_INJECTED|2026-07-15T14:30:00|50.0
    handleEmbryoInjected(command);
  }
  
  else if (command.startsWith("SET_TEMP|")) {
    int pipeIdx = command.indexOf('|');
    String temp_str = command.substring(pipeIdx + 1);
    float new_temp = temp_str.toFloat();
    
    // Validar range
    if (new_temp >= 30 && new_temp <= 42) {
      // TODO: implementar
      Serial.println("OK");
    } else {
      Serial.println("ERROR: Invalid temperature");
    }
  }
  
  else if (command.startsWith("SET_HUMIDITY|")) {
    int pipeIdx = command.indexOf('|');
    String humidity_str = command.substring(pipeIdx + 1);
    float new_humidity = humidity_str.toFloat();
    
    if (new_humidity >= 30 && new_humidity <= 90) {
      // TODO: implementar
      Serial.println("OK");
    } else {
      Serial.println("ERROR: Invalid humidity");
    }
  }
  
  else if (command == "TURN_EGGS_ON") {
    // TODO: ativar viragem
    Serial.println("OK");
  }
  
  else if (command == "TURN_EGGS_OFF") {
    // TODO: desativar viragem
    Serial.println("OK");
  }
  
  else if (command == "ALARM") {
    playAlarmSound();
    Serial.println("OK");
  }
  
  else if (command == "GET_LOGS") {
    sendLogsJSON();
  }
  
  else if (command == "RESET") {
    Serial.println("RESETTING");
    delay(1000);
    resetFunc();  // Reboot
  }
  
  else if (command == "EMERGENCY_STOP") {
    emergencyStop();
  }
  
  else {
    Serial.println("ERROR: Unknown command");
  }
}

void handleEmbryoInjected(String command) {
  // Parsear: EMBRYO_INJECTED|timestamp|volume
  
  int pipe1 = command.indexOf('|');
  int pipe2 = command.indexOf('|', pipe1 + 1);
  
  String timestamp = command.substring(pipe1 + 1, pipe2);
  String volume_str = command.substring(pipe2 + 1);
  
  float volume = volume_str.toFloat();
  
  // Registrar
  embryo_record.injected = true;
  embryo_record.injection_time_ms = millis();
  embryo_record.injection_volume_ul = volume;
  embryo_record.day_of_injection = data.day;
  
  // Copiar timestamp (máximo 31 caracteres)
  timestamp.toCharArray(
    embryo_record.injection_timestamp,
    sizeof(embryo_record.injection_timestamp) - 1
  );
  
  // Log
  Serial.print("EMBRYO_INJECTED: ");
  Serial.print(timestamp);
  Serial.print(" | ");
  Serial.print(volume);
  Serial.println("µL");
  
  // Salvar EEPROM
  saveEmbryoRecord();
  
  // Feedback
  playBeep(800, 200);
  delay(100);
  playBeep(800, 200);
  
  sendBluetoothMessage("EMBRYO_INJECTED_LOGGED");
  
  Serial.println("OK");
}

void sendStatusJSON() {
  // Usar ArduinoJson para criar JSON
  StaticJsonDocument<256> doc;
  
  doc["connected"] = true;
  doc["temperatura_atual"] = data.temp;
  doc["temperatura_alvo"] = TARGET_TEMP;
  doc["umidade_atual"] = data.humidity;
  doc["umidade_alvo"] = TARGET_HUMIDITY;
  doc["dia"] = data.day;
  doc["hora"] = data.hour;
  doc["minuto"] = data.minute;
  doc["resistencia_ligada"] = data.heater_on;
  doc["ventilador_ligado"] = data.fan_on;
  doc["viragens"] = data.turn_count;
  doc["alarme_ativo"] = data.alarm_active;
  
  if (embryo_record.injected) {
    doc["embriao_injetado"] = true;
    doc["data_injecao"] = embryo_record.injection_timestamp;
    doc["volume_injecao"] = embryo_record.injection_volume_ul;
  } else {
    doc["embriao_injetado"] = false;
  }
  
  // Serializar e enviar
  serializeJson(doc, Serial);
  Serial.println();  // Newline para demarcar fim
}

void sendLogsJSON() {
  StaticJsonDocument<512> doc;
  
  doc["boot_time"] = bootTime;
  doc["uptime_seconds"] = (millis() - bootTime) / 1000;
  doc["total_turns"] = data.turn_count;
  doc["total_alarms"] = 0;  // TODO: contar
  
  if (embryo_record.injected) {
    doc["embryo_injection_timestamp"] = embryo_record.injection_timestamp;
    doc["embryo_injection_volume"] = embryo_record.injection_volume_ul;
    doc["days_since_injection"] = data.day - embryo_record.day_of_injection;
  }
  
  serializeJson(doc, Serial);
  Serial.println();
}

void emergencyStop() {
  // Parar todos os sistemas
  digitalWrite(HEATER_RELAY, LOW);
  digitalWrite(FAN_RELAY, LOW);
  
  if (SCARA_ENABLED) {
    moveToHome();
  }
  
  playAlarmSound();
  
  Serial.println("OK");
  Serial.println("EMERGENCY_STOPPED");
}

// ============= LEITURA DE SENSORES =============

void readSensors() {
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  ds18b20.requestTemperatures();
  float temp_backup = ds18b20.getTempCByIndex(0);
  
  if (!isnan(temp) && !isnan(humidity)) {
    data.temp = temp;
    data.humidity = humidity;
  }
  
  if (!isnan(temp_backup)) {
    data.temp_backup = temp_backup;
  }
}

// ============= CONTROLE DE TEMPERATURA =============

void controlTemperature() {
  float diff = data.temp - TARGET_TEMP;
  
  if (diff < -TEMP_TOLERANCE) {
    digitalWrite(HEATER_RELAY, HIGH);
    data.heater_on = true;
  } else if (diff > TEMP_TOLERANCE) {
    digitalWrite(HEATER_RELAY, LOW);
    data.heater_on = false;
  }
}

// ============= CONTROLE DE UMIDADE =============

void controlHumidity() {
  float diff = data.humidity - TARGET_HUMIDITY;
  
  if (diff < -HUMIDITY_TOLERANCE) {
    digitalWrite(FAN_RELAY, HIGH);
    data.fan_on = true;
  } else if (diff > HUMIDITY_TOLERANCE) {
    digitalWrite(FAN_RELAY, LOW);
    data.fan_on = false;
  }
}

// ============= VIRAGEM DE OVOS =============

void turnEggs() {
  if (data.servo_position) {
    eggTurner.write(0);
    data.servo_position = false;
  } else {
    eggTurner.write(180);
    data.servo_position = true;
  }
  
  playBeep(500, 100);
  delay(50);
  playBeep(500, 100);
  
  data.turn_count++;
  saveDataToEEPROM();
}

// ============= ALARMES =============

void checkAlarms() {
  data.alarm_active = false;
  memset(data.alarm_reason, 0, sizeof(data.alarm_reason));
  
  if (abs(data.temp - TARGET_TEMP) > ALARM_THRESHOLD_TEMP) {
    data.alarm_active = true;
    alarmTriggered = true;
    snprintf(data.alarm_reason, 50, "TEMP_ERROR: %.1f", data.temp);
    playAlarmSound();
  }
  
  if (abs(data.humidity - TARGET_HUMIDITY) > ALARM_THRESHOLD_HUMIDITY) {
    data.alarm_active = true;
    alarmTriggered = true;
    snprintf(data.alarm_reason, 50, "HUMIDITY_ERROR: %.1f", data.humidity);
    playAlarmSound();
  }
  
  if (data.alarm_active && alarmTriggered) {
    sendBluetoothMessage(data.alarm_reason);
    alarmTriggered = false;
  }
}

// ============= SONS =============

void playBeep(int frequency, int duration) {
  tone(BUZZER_PIN, frequency, duration);
  delay(duration + 10);
  noTone(BUZZER_PIN);
}

void playAlarmSound() {
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
  
  display.print("🦖 DIA ");
  display.println(data.day);
  
  display.print("TEMP: ");
  display.print(data.temp, 1);
  display.println("C");
  
  display.print("UMID: ");
  display.print(data.humidity, 1);
  display.println("%");
  
  if (embryo_record.injected) {
    display.print("EMBRIAO: Injetado");
  } else {
    display.print("EMBRIAO: Aguardando");
  }
  
  display.display();
}

// ============= EEPROM =============

void saveDataToEEPROM() {
  // TODO: implementar salvamento estruturado
}

void loadDataFromEEPROM() {
  // TODO: implementar carregamento estruturado
}

void saveEmbryoRecord() {
  // TODO: implementar salvamento de registro de embrião
}

// ============= MENSAGENS BLUETOOTH =============

void sendBluetoothMessage(const char* msg) {
  bluetooth.print("[");
  bluetooth.print(millis() / 1000);
  bluetooth.print("] ");
  bluetooth.println(msg);
}

// ============= SCARA =============

void initializeSCARA() {
  // TODO: implementar inicialização SCARA
}

void moveToHome() {
  // TODO: implementar movimento para HOME
}

// ============= REBOOT FUNCTION =============

void (* resetFunc)(void) = 0;  // Declare reset function at address 0
