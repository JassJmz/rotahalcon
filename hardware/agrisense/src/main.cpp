#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <time.h>
#include "secrets.h"

// ── DATOS ──
#define PIN_RX          5      // RO del módulo RS485
#define PIN_TX          18     // DI del módulo RS485
#define PIN_DE          4
#define PIN_RE          2
#define BAUD            9600   // confirmado con tu sensor
#define MODBUS_ADDR     0x01
#define LEER_MAPA_7     true  // true = leer 0x0000-0x0006 (SIN CONFIRMAR el orden de los registros)
#define NODO            "agrisense-01"
#define INTERVALO_MS    60000UL
#define WIFI_TIMEOUT_MS 20000UL
#define MODO_PRUEBA     false   // true = sin sensor: manda datos de prueba a nodos/agrisense-test
#define DEBUG_RAW       true
// ── FIN DATOS ──

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

bool leerRegistros(uint16_t inicio, uint8_t cuantos, uint16_t *reg) {
  uint8_t req[8] = {MODBUS_ADDR, 0x03, (uint8_t)(inicio >> 8), (uint8_t)(inicio & 0xFF),
                    0x00, cuantos, 0, 0};
  uint16_t c = crc16(req, 6);
  req[6] = c & 0xFF; req[7] = c >> 8;

  while (Serial2.available()) Serial2.read();
  modoTx(true);
  delay(2);
  Serial2.write(req, 8);
  Serial2.flush();
  modoTx(false);

  const size_t esperado = 5 + cuantos * 2;
  uint8_t resp[64];
  size_t n = 0;
  unsigned long t0 = millis();
  while (n < sizeof(resp) && millis() - t0 < 1000) {
    if (Serial2.available()) resp[n++] = Serial2.read();
    if (n >= esperado) break;
    if (n == 5 && (resp[1] & 0x80)) break;
  }

  if (DEBUG_RAW) {
    Serial.print("RX(");
    Serial.print(n);
    Serial.print("): ");
    for (size_t i = 0; i < n; i++) Serial.printf("%02X ", resp[i]);
    Serial.println();
  }

  if (n < esperado) return false;
  if (resp[0] != MODBUS_ADDR || resp[1] != 0x03 || resp[2] != cuantos * 2) return false;
  uint16_t crcRx = resp[esperado - 2] | (resp[esperado - 1] << 8);
  if (crc16(resp, esperado - 2) != crcRx) return false;

  for (int i = 0; i < cuantos; i++) reg[i] = (resp[3 + i * 2] << 8) | resp[4 + i * 2];
  return true;
}

bool firebasePut(const String &ruta, const String &json) {
  WiFiClientSecure cli;
  cli.setInsecure();              // simple para el hackathon; no valida el certificado
  HTTPClient http;
  String url = String("https://") + FIREBASE_HOST + "/" + ruta + ".json";
  if (strlen(FIREBASE_AUTH)) url += String("?auth=") + FIREBASE_AUTH;
  http.begin(cli, url);
  int code = http.PUT(json);
  Serial.printf("HTTP %d\n", code);
  http.end();
  return code == 200;
}

bool conectarWiFi() {
  if (WiFi.status() == WL_CONNECTED) return true;
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < WIFI_TIMEOUT_MS) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  return WiFi.status() == WL_CONNECTED;
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_DE, OUTPUT);
  pinMode(PIN_RE, OUTPUT);
  modoTx(false);
  Serial2.begin(BAUD, SERIAL_8N1, PIN_RX, PIN_TX);

  if (conectarWiFi()) {
    Serial.println("WiFi OK");
    configTime(0, 0, "pool.ntp.org", "time.google.com");
  } else {
    Serial.println("WiFi no disponible; se reintenta en el loop");
  }
}

  void loop() {
  static unsigned long ultimo = 0;
  unsigned long intervalo = MODO_PRUEBA ? 10000UL : INTERVALO_MS;
  if (ultimo != 0 && millis() - ultimo < intervalo) return;
  ultimo = millis();

  uint16_t r[8];
  char hum[16] = "null", tmp[16] = "null", ph[16] = "null", ce[16] = "null";
  uint16_t n, p, k;
  const char *nodo = NODO;
  const char *fuente = "SENSOR";

  if (MODO_PRUEBA) {
    nodo = "agrisense-test";
    fuente = "TEST";
    strcpy(hum, "24.1"); strcpy(tmp, "19.3"); strcpy(ph, "7.2"); strcpy(ce, "410");
    n = 32; p = 18; k = 145;
  } else if (LEER_MAPA_7) {
    if (!leerRegistros(0x0000, 7, r)) { Serial.println("Lectura Modbus fallida"); return; }
    snprintf(hum, sizeof(hum), "%.1f", r[0] / 10.0);
    snprintf(tmp, sizeof(tmp), "%.1f", (int16_t)r[1] / 10.0);
    snprintf(ce,  sizeof(ce),  "%u",   r[2]);
    snprintf(ph,  sizeof(ph),  "%.1f", r[3] / 10.0);
    n = r[4]; p = r[5]; k = r[6];
  } else {
    if (!leerRegistros(0x001E, 3, r)) { Serial.println("Lectura Modbus fallida"); return; }
    n = r[0]; p = r[1]; k = r[2];
  }
  Serial.printf("N=%u  P=%u  K=%u (mg/kg)\n", n, p, k);

  if (!conectarWiFi()) { Serial.println("Sin WiFi, no se envia"); return; }

  time_t ts = time(nullptr);
  if (ts < 1700000000) { Serial.println("Hora aun no sincronizada"); return; }

  char js[256];
  snprintf(js, sizeof(js),
    "{\"ts\":%lu,\"humedad_pct\":%s,\"temp_c\":%s,\"ph\":%s,"
    "\"ce_uScm\":%s,\"n_mgkg\":%u,\"p_mgkg\":%u,\"k_mgkg\":%u,\"fuente\":\"%s\"}",
    (unsigned long)ts, hum, tmp, ph, ce, n, p, k, fuente);

  Serial.println(js);
  bool a = firebasePut(String("nodos/") + nodo + "/ultima", js);
  bool b = firebasePut(String("nodos/") + nodo + "/lecturas/" + (unsigned long)ts, js);
  Serial.printf("Firebase ultima:%d lecturas:%d\n", a, b);
}
