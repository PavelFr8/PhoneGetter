#include <EEPROM.h>

const int setupCompleteAddress = 0;  // Адрес в EEPROM
const int MAX_CELLS = 30;  // Максимальное количество клеток

// Структура для хранения данных о ячейках
struct CellData {
    String deviceName;
    String cellNumbers[MAX_CELLS]; // Массив для хранения номеров ячеек
    int userIds[MAX_CELLS];         // Массив для хранения ID пользователей
    bool states[MAX_CELLS];         // Массив для хранения состояний клеток
    int cellCount;                  // Количество клеток
};

CellData cells_data;

void setup() {
    Serial.begin(115200); 
    Serial3.begin(115200);  // Serial3 для ESP8266
    delay(10000);

    if (EEPROM.read(setupCompleteAddress) != 1) {
        setupWiFi();
    } else {
        Serial.println("Настройка уже была завершена.");
        requestCellData();
        lightUpCells(cells_data); 
    }
}

void loop() {
  // Проверка наличия данных от ESP8266
  if (Serial3.available() > 0) {
    String message = Serial3.readStringUntil('\n'); // Чтение строки до новой строки
    message.trim();
    Serial.print("Сообщение от ESP: ");
    Serial.println(message);
  }
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Чтение строки до новой строки
    command.trim();
    if (command == "RESET") {
      EEPROM.update(setupCompleteAddress, 0);
    } else if (command == "DATA") {
      requestCellData();
    } else if (command == "LEDS") {
      lightUpCells(cells_data);
    } else {
      Serial3.println(command);
    }
  }
  delay(1000);
}

// Настройка Wi-Fi
void setupWiFi() {
    String ssid = "YOUR_SSID";
    String password = "YOUR_PASSWORD";
    
    Serial.println("Ввод Wi-Fi данных...");
    Serial3.println("SET_WIFI:" + ssid + ":" + password);  // Передаем данные на ESP
    
    delay(20000);
    if (Serial3.available() > 0) {
        String response = Serial3.readString();
        response.trim();
        Serial.println(response);
        if (response == "WIFI_OK") {
            Serial.println("Wi-Fi подключение успешно");
            int code = requestCodeFromESP();
            Serial.print("Выведите секретный код на Nextion: "); // Код отображается на экране для пользователя
            Serial.println(code);
            
            Serial.println("Настройка завершена.");
            EEPROM.update(setupCompleteAddress, 1);  // Сохраняем статус завершения настройки
        } else {
            Serial.println("Ошибка подключения к Wi-Fi.");
        }
    } else {
        Serial.println("SKA");
    }
}

// Запрос секретного кода от ESP
int requestCodeFromESP() {
    Serial3.println("GET_CODE");
    delay(2500);
    if (Serial3.available()) {
        return Serial3.parseInt();  // Получаем секретный код
    }
    return -1;
}

// Запрос данных по ячейкам от ESP
void requestCellData() {
    Serial3.println("GIVE_DATA");
    delay(5000);
    if (Serial3.available() > 0) {
        String cellData = Serial3.readStringUntil('\n');
        cellData.trim();
        Serial.println(cellData);
        cells_data = parseCellData(cellData); // Парсим данные ячеек
        Serial.println("Данные клеток получены:");
        for (int i = 0; i < cells_data.cellCount; i++) {
            Serial.print("Клетка: ");
            Serial.print(cells_data.cellNumbers[i]);
            Serial.print(", ID: ");
            Serial.print(cells_data.userIds[i]);
            Serial.print(", Состояние: ");
            Serial.println(cells_data.states[i] ? "True" : "False");
        }
    }
}

// Парсим входящие ячейки от ESP
CellData parseCellData(const String& dataString) {
    CellData data;
    int firstSemicolon = dataString.indexOf(';');
    data.deviceName = dataString.substring(0, firstSemicolon);
    data.cellCount = 0;

    String cellsString = dataString.substring(firstSemicolon + 1);
    int start = 0;
    while (true) {
        int end = cellsString.indexOf(';', start);
        if (end == -1) break; 

        String cellData = cellsString.substring(start, end);
        int firstComma = cellData.indexOf(',');
        int secondComma = cellData.indexOf(',', firstComma + 1);

        if (data.cellCount < MAX_CELLS) {
            String cellNumber = cellData.substring(0, firstComma);
            int id = cellData.substring(firstComma + 1, secondComma).toInt();
            bool state = cellData.substring(secondComma + 1).equals("1"); 

            data.cellNumbers[data.cellCount] = cellNumber;
            data.userIds[data.cellCount] = id;
            data.states[data.cellCount] = state;
            data.cellCount++; 
        }

        start = end + 1; 
    }

    return data;
}

void lightUpCells(const CellData& cells_data) {
    for (int i = 0; i < cells_data.cellCount; i++) {
        int pin = 22 + i; 
        pinMode(pin, OUTPUT); 

        if (cells_data.states[i]) {
            digitalWrite(pin, HIGH);
        } else {
            digitalWrite(pin, LOW); 
        }
    }

    delay(5000); 

    for (int i = 0; i < cells_data.cellCount; i++) {
        int pin = 22 + i; 
        digitalWrite(pin, LOW); 
    }
}
