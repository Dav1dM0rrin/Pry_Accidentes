#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHTesp.h>
#include <LiquidCrystal_I2C.h>
#include <time.h>                // Para SNTP


// —————————————— Ajusta estos valores ——————————————
const char* API_ENDPOINT = "http://192.168.1.27:8000/lectura_sensor/"; 
const char* WIFI_SSID     = "MASSIELL";
const char* WIFI_PASS     = "l01041419051515m";
// ————————————————————————————————————————————————

#define DHT_TYPE DHTesp::DHT22   // Ahora DHT22 en vez de DHT11
const int DHT_PIN   = 4;        // GPIO4 para DHT
const int LCD_ADDR  = 0x27;
const int LCD_COLS  = 16;
const int LCD_ROWS  = 2;

DHTesp dht;
LiquidCrystal_I2C lcd(LCD_ADDR, LCD_COLS, LCD_ROWS);

unsigned long lastSendTime = 0;
const unsigned long SEND_INTERVAL = 5000;  // 5 s

void connectToWiFi() {
  lcd.clear();
  lcd.print("Conectando WiFi");
  Serial.print("Conectando a ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    lcd.print(".");
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    lcd.clear();
    lcd.print("WiFi OK");
    lcd.setCursor(0,1);
    lcd.print(WiFi.localIP());
    Serial.println("\nWiFi conectado:");
    Serial.println(WiFi.localIP());
    // Configura SNTP para obtener hora real
    configTime(0, 0, "pool.ntp.org", "time.nist.gov");
    // Espera sincronización (timestamp > ~2020)
    while (time(nullptr) < 1600000000) {
      Serial.print(".");
      delay(500);
    }
    Serial.println("\nNTP sincronizado");
    delay(1500);
  } else {
    lcd.clear();
    lcd.print("Error WiFi");
    Serial.println("\nFalló conexión WiFi");
    ESP.restart();  // reinicia tras error
  }
}

void sendSensorData(float temperature, float humidity) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado, reconectando...");
    connectToWiFi();
    return;
  }

  WiFiClient client;
  HTTPClient http;
  http.setTimeout(10000);

  if (!http.begin(client, API_ENDPOINT)) {
    Serial.println("Error inicio HTTP");
    lcd.clear();
    lcd.print("Error HTTP begin");
    return;
  }

  http.addHeader("Content-Type", "application/json");

  // --- Obtener timestamp ISO8601 por NTP ---
  time_t now = time(nullptr);
  struct tm tmInfo;
  localtime_r(&now, &tmInfo);
  char timeBuf[25];
  strftime(timeBuf, sizeof(timeBuf), "%FT%TZ", &tmInfo);

  // --- Construir JSON ---
  DynamicJsonDocument doc(512);
  doc["temperatura"]    = temperature;
  doc["humedad"]        = humidity;
  doc["fecha_hora"]  = timeBuf;
  String jsonData;
  serializeJson(doc, jsonData);
  Serial.println("Enviando JSON:");
  Serial.println(jsonData);

  // --- POST ---
  int httpCode = http.POST(jsonData);
  if (httpCode > 0) {
    Serial.printf("HTTP código: %d\n", httpCode);
    if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_CREATED) {
      String resp = http.getString();
      Serial.println("Respuesta API: " + resp);
      lcd.clear();
      lcd.print("Envio OK");
    } else {
      Serial.println("Error en POST");
      lcd.clear();
      lcd.print("POST fallo:");
      lcd.setCursor(0,1);
      lcd.print(httpCode);
    }
  } else {
    Serial.printf("Error HTTP: %s (%d)\n",
                  http.errorToString(httpCode).c_str(),
                  httpCode);
    lcd.clear();
    lcd.print("Err HTTP:");
    lcd.setCursor(6,0);
    lcd.print(httpCode);
  }

  http.end();
}

void setup() {
  Serial.begin(115200);
  Serial.print("Intentando conectar a ");
  Serial.println(API_ENDPOINT);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.print("Inicializando");
  delay(1000);

  dht.setup(DHT_PIN, DHT_TYPE);
  delay(2000);

  connectToWiFi();
}

void loop() {
  static unsigned long lastRead = 0;

  if (millis() - lastRead >= 2000) {
    TempAndHumidity data = dht.getTempAndHumidity();
    lastRead = millis();

    if (!isnan(data.temperature) && !isnan(data.humidity)) {
      // Línea 0: temperatura
      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print("Temperatura:");
      lcd.print(data.temperature,1);
      lcd.print("C");

      // Línea 1: humedad
      lcd.setCursor(0,1);
      lcd.print("Humedad:");
      lcd.print(data.humidity,1);
      lcd.print("%");

      Serial.printf("T: %.1f C, H: %.1f %%\n", data.temperature, data.humidity);

      if (millis() - lastSendTime >= SEND_INTERVAL) {
        sendSensorData(data.temperature, data.humidity);
        lastSendTime = millis();
      }
    } else {
      Serial.println("Error DHT");
      lcd.clear();
      lcd.print("Error sensor");
      }
  }
}