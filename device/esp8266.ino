#include <map>
#include <utility>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <EEPROM.h>

#define EEPROM_SIZE 512

// Указываем данные для подключения к WiFi
String ssid;
String password;

const char* token = "1234567890"; // Секретный уникальный токен устройства

// Структура для хранения данных о ячейках
struct CellData {
    String deviceName;
    std::map<String, std::pair<int, bool>> cells; // Словарь для хранения состояния клеток (номер ячейки: [id юзера, состояние])
};

void setup() {
    Serial.begin(115200);
    Serial.begin(115200);
    EEPROM.begin(EEPROM_SIZE);

    loadWiFiSettings(); // Загружаем из EEPROM данные по wifi, если они есть

    if (!ssid.isEmpty() && !password.isEmpty()) {
         connectToWiFi();
    }
}

// Парсинг данных о Wi-Fi с MEGA
void parseWiFiCredentials(String command) {
    int firstColon = command.indexOf(':', 0);
    int secondColon = command.indexOf(':', firstColon + 1);
    ssid = command.substring(firstColon + 1, secondColon);
    password = command.substring(secondColon + 1);
}

// Парсинг данныз с MEGA для update_data
void workWithUpdateDataCredentials(String command) {
    int firstColon = command.indexOf(':', 0);
    int secondColon = command.indexOf(':', firstColon + 1);
    int changed_cell = command.substring(firstColon + 1, secondColon).toInt();
    String tmp_state = command.substring(secondColon + 1);
    bool state = (tmp_state == "true");
    updateData(changed_cell, state);
}


// Функция для подключения к Wi-Fi
bool connectToWiFi() {
    WiFi.begin(ssid.c_str(), password.c_str());
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 10) {
        delay(1000);
        attempts++;
    }
    return WiFi.status() == WL_CONNECTED;
}

// Загрузка Wi-Fi данных из EEPROM
void loadWiFiSettings() {
    char ssidBuffer[50];
    char passwordBuffer[50];
    EEPROM.get(0, ssidBuffer);
    EEPROM.get(50, passwordBuffer);
    ssid = ssidBuffer;
    password = passwordBuffer;
}

// Сохранение Wi-Fi данных в EEPROM
void saveWiFiSettings() {
    char line1Buf[50];
    char line2Buf[50];
    String line1 = ssid;
    String line2 = password;

    line1.toCharArray(line1Buf, line1.length()+1);
    line2.toCharArray(line2Buf, line2.length()+1);
    EEPROM.put(0, line1);
    EEPROM.put(50, line2);
    EEPROM.commit();
}

// Отправка данных о ячейках на Arduino
void sendCellData(const CellData& data) {
    Serial.printf("Устройство: %s\n", data.deviceName.c_str());
    for (const auto& cell : data.cells) {
        Serial.printf("Клетка: %s, ID: %d, Состояние: %s\n",
                      cell.first.c_str(),
                      cell.second.first,
                      cell.second.second ? "True" : "False");
    }
}

bool updateData(int changed_cell, bool state) {
    // отправляем на сервер номер изменной ячейки(changed_cell) и её текущее состояние(state)
    if (WiFi.status() == WL_CONNECTED) {
        WiFiClientSecure client;
        client.setInsecure();
        HTTPClient http;

        http.begin(client, "https://phonegetter.onrender.com/api/update_data");
        http.addHeader("Content-Type", "application/json");
        http.addHeader("Authorization", String(token));

        // Создание JSON-объекта
        StaticJsonDocument<200> jsonDoc;
        jsonDoc["changed_cell"] = changed_cell;
        jsonDoc["state"] = state;

        String jsonString;
        serializeJson(jsonDoc, jsonString);

        // Отправка PUT-запроса
        int httpResponseCode = http.PUT(jsonString);

        if (httpResponseCode == HTTP_CODE_OK) {
            String response = http.getString();
            return true; // Запрос успешно доставлен
        } else {
            return false; // Запрос не доставлен
        }

        http.end();
    } else {
        return false; // Возвращаем false, если WiFi не подключен
    }

    delay(10000); // Задержка для предотвращения частых запросов
}

CellData giveData() {
    // получает данные с сервера о текущих ячейках и обрабатывает их
    CellData result;
    result.deviceName = "";

    // Получаем информацию с сервера о том, какие ячейки заняты, а какие нет
    WiFiClientSecure client;
    client.setInsecure();
    HTTPClient http;
    http.begin(client, "https://phonegetter.onrender.com/api/give_data");
    http.addHeader("Authorization", String(token));

    int giveDataResponseCode = http.GET();

    if (giveDataResponseCode == HTTP_CODE_OK) {
        String response = http.getString();
        StaticJsonDocument<200> doc;
        DeserializationError error = deserializeJson(doc, response);
        String status = doc["status"];
        result.deviceName = doc["device"].as<String>();

        // Извлекаем строку ячеек и десериализуем её
        String cellDataString = doc["cells"].as<String>();
        StaticJsonDocument<200> cellDoc;
        DeserializationError cellError = deserializeJson(cellDoc, cellDataString);

        for (JsonPair cell : cellDoc.as<JsonObject>()) {
            String cellNumber = cell.key().c_str();
            JsonArray cellData = cell.value().as<JsonArray>(); // Получаем массив данных ячейки

            if (cellData.size() >= 2) {
                int id = cellData[0]; // Первое значение — идентификатор
                bool state = cellData[1]; // Второе значение — состояние

                // Заполняем словарь клеток (номер: [id, состояние])
                result.cells[cellNumber] = std::make_pair(id, state);
            }
        }
    }

    http.end();
    return result; // Ensure we return a CellData object
}

int getCode() {
    // функция для получения кода с сервера
    int code = -1; // Initialize with an invalid code
    CellData result;
    result.deviceName = "";

    if (WiFi.status() == WL_CONNECTED) {
        WiFiClientSecure client;
        client.setInsecure();
        HTTPClient http;
        http.begin(client, "https://phonegetter.onrender.com/api/create_code");
        http.addHeader("Authorization", String(token));

        int responseCode = http.GET();

        if (responseCode == HTTP_CODE_OK) {
            String response = http.getString();

            StaticJsonDocument<200> doc;
            DeserializationError error = deserializeJson(doc, response);
            String status = doc["status"];
            result.deviceName = doc["device"].as<String>();
            code = doc["token"]; // Получаем секретный код
        }

        http.end();
    }

    return code; // Return the code (or -1 if there was an error)
}

void resetConnection() {
    // функция чтобы оборвать связь между устройством и юзером, к которому привязано устройство
    if (WiFi.status() == WL_CONNECTED) {
        WiFiClientSecure client;
        client.setInsecure();
        HTTPClient http;
        http.begin(client, "https://phonegetter.onrender.com/api/reset_connection");
        http.addHeader("Authorization", String(token));

        int responseCode = http.GET();

        http.end();
    }
}

void clearEEPROM() {
  int tmp;
  ssid = "";
  password = "";
  EEPROM.put(0, 512);
  EEPROM.put(50, 512);
  EEPROM.commit();
}

String cellDataToString(const CellData& data) {
    String result = data.deviceName + ";"; // Начинаем с имени устройства
    for (const auto& cell : data.cells) {
        result += cell.first + "," + String(cell.second.first) + "," + String(cell.second.second) + ";"; // Формат: номер_ячейки,id,состояние;
    }
    return result;
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        command.trim();

        if (command.startsWith("SET_WIFI")) {
            parseWiFiCredentials(command);
            if (connectToWiFi()) {
                saveWiFiSettings();
                Serial.println("WIFI_OK");
            } else {
                Serial.println("WIFI_FAIL");
            }
        } else if (command == "GET_CODE") {
            int code = getCode();
            Serial.println(code);
        } else if (command == "GIVE_DATA") {
            CellData data = giveData();
            Serial.println(cellDataToString(data));
        } else if (command == "FRIEND =)") {
            Serial.println("Бу! Испугался? Не бойся, я друг, я тебя не обижу. Иди сюда, иди ко мне, сядь рядом со мной, посмотри мне в глаза. Ты видишь меня? Я тоже тебя вижу. Давай смотреть друг на друга до тех пор, пока наши глаза не устанут. Ты не хочешь? Почему? Что-то не так?");
        } else if (command == "CLEAR") {
            clearEEPROM();
        } else if (command == "INFO") {
            Serial.printf("ssid: %s\npassword: %s\n", ssid, password);
        } else if (command.startsWith("UPDATE_DATA")) {
            workWithUpdateDataCredentials(command);
        }
    }
    delay(2000);  // Интервал между запросами для экономии ресурсов
}
