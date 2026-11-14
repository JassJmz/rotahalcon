#include <BluetoothSerial.h>

// ── DATOS ──
#define NOMBRE_BT   "AGRISENSE-TEST"
#define PIN_RX      5      // RO del módulo RS485
#define PIN_TX      18     // DI del módulo RS485
#define PIN_DE      4
#define PIN_RE      2
#define MODBUS_ADDR 0x01
#define REG_INICIO  0x001E // N, P, K (SUPUESTO: confirmar con tu modelo)
#define REG_CUANTOS 3      // 0 = N, 1 = P, 2 = K (mg/kg)
#define INTERVALO_MS 2000UL
// ── FIN DATOS ──

BluetoothSerial SerialBT;
uint32_t baud = 4800;   // se cambia desde el celular con los comandos

uint16_t crc16(const uint8_t *d, size_t n) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < n; i++) {
    crc ^= d[i];
    for (int b = 0; b < 8; b++) crc = (crc & 1) ? (crc >> 1) ^ 0xA001 : crc >> 1;
  }
  return crc;
}

void modoTx(bool tx) {
  digitalWrite(PIN_DE, tx);
  digitalWrite(PIN_RE, tx);
}

void log(const String &s) {     // manda a USB y a Bluetooth a la vez
  Serial.println(s);
  if (SerialBT.hasClient()) SerialBT.println(s);
}

bool leerSensor(uint16_t *reg) {
  uint8_t req[8] = {MODBUS_ADDR, 0x03, REG_INICIO >> 8, REG_INICIO & 0xFF,
                    0x00, REG_CUANTOS, 0, 0};
  uint16_t c = crc16(req, 6);
  req[6] = c & 0xFF; req[7] = c >> 8;

  while (Serial2.available()) Serial2.read();
  modoTx(true);
  delay(2);
  Serial2.write(req, 8);
  Serial2.flush();
  modoTx(false);

  const size_t esperado = 5 + REG_CUANTOS * 2;
  uint8_t resp[32];
  size_t n = 0;
  unsigned long t0 = millis();
  while (n < esperado && millis() - t0 < 1000) {
    if (Serial2.available()) resp[n++] = Serial2.read();
  }

  String raw = "RX(" + String(n) + "): ";
  for (size_t i = 0; i < n; i++) { char h[4]; sprintf(h, "%02X ", resp[i]); raw += h; }
  log(raw);

  if (n < esperado) return false;
  if (resp[0] != MODBUS_ADDR || resp[1] != 0x03 || resp[2] != REG_CUANTOS * 2) return false;
  uint16_t crcRx = resp[esperado - 2] | (resp[esperado - 1] << 8);
  if (crc16(resp, esperado - 2) != crcRx) { log("CRC malo"); return false; }

  for (int i = 0; i < REG_CUANTOS; i++) reg[i] = (resp[3 + i * 2] << 8) | resp[4 + i * 2];
  return true;
}

void revisarComandos() {        // escribe "4800" o "9600" desde el celular
  if (!SerialBT.available()) return;
  String cmd = SerialBT.readStringUntil('\n');
  cmd.trim();
  uint32_t nuevo = cmd.toInt();
  if (nuevo == 4800 || nuevo == 9600 || nuevo == 2400 || nuevo == 19200) {
    baud = nuevo;
    Serial2.end();
    Serial2.begin(baud, SERIAL_8N1, PIN_RX, PIN_TX);
    log("Baud cambiado a " + String(baud));
  } else if (cmd.length()) {
    log("Comandos validos: 2400 | 4800 | 9600 | 19200");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_DE, OUTPUT);
  pinMode(PIN_RE, OUTPUT);
  modoTx(false);
  Serial2.begin(baud, SERIAL_8N1, PIN_RX, PIN_TX);
  SerialBT.begin(NOMBRE_BT);
  Serial.println("Bluetooth listo: busca " NOMBRE_BT);
}

void loop() {
  revisarComandos();

  static unsigned long ultimo = 0;
  if (millis() - ultimo < INTERVALO_MS) return;
  ultimo = millis();

  uint16_t r[REG_CUANTOS];
  if (leerSensor(r)) {
    log("N=" + String(r[0]) + "  P=" + String(r[1]) + "  K=" + String(r[2]) + " mg/kg");
  } else {
    log("Lectura fallida (baud " + String(baud) + ")");
  }
}