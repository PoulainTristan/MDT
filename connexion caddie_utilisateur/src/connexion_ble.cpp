#include "BluetoothSerial.h"

BluetoothSerial SerialBT;  // Création d’un objet Bluetooth

void setup() {
    Serial.begin(115200);
    SerialBT.begin("ESP32_BT");  // Nom du module ESP32 visible en Bluetooth
    Serial.println("Bluetooth prêt !");
}

void loop() {
    if (SerialBT.available()) {  // Vérifier si des données sont reçues
        char received = SerialBT.read();
        Serial.print("Reçu : ");
        Serial.println(received);
    }

    if (Serial.available()) {  // Envoyer depuis le moniteur série
        char toSend = Serial.read();
        SerialBT.write(toSend);
    }
}
