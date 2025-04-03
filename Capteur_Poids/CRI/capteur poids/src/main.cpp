#include "HX711.h"

// Définir les broches pour HX711
#define DOUT 5  // DT sur GPIO 5
#define CLK 18  // SCK sur GPIO 18

HX711 scale;

void setup() {
    // Initialiser la communication série
    Serial.begin(115200);
    
    // Initialiser la cellule de charge avec les broches DOUT et SCK
    scale.begin(DOUT, CLK);
    
    // Définir le facteur de calibration (ajuster selon ta cellule de charge)
    scale.set_scale(7.8f);  // Remplace par ta valeur calibrée

    // Attendre un peu avant la tare pour stabiliser la cellule de charge
    delay(500);
    
    // Remettre la balance à zéro
    scale.tare();  
    
    // Vérifier que la tare est bien effectuée
    Serial.println("Tare effectuée, prêt à mesurer.");
}

void loop() {
    // Vérifier si une tare manuelle est demandée
    if (Serial.available()) {
        char cmd = Serial.read();
        if (cmd == 't') {
            scale.tare();  // Remettre la tare si l'utilisateur tape 't' dans le moniteur série
            Serial.println("Tare manuelle effectuée !");
        }
    }

    // Mesurer et afficher le poids en grammes
    float poids = scale.get_units(10);  // Lire la moyenne de 10 valeurs

    // Corriger les très petites valeurs négatives
    if (poids < 0 && poids > -20) {  // Seulement si c'est un bruit faible (< -5g on considère un vrai poids)
        poids = 0;
    }

    Serial.print("Poids : ");
    Serial.print(poids, 2);  // Affiche avec 2 décimales pour plus de précision
    Serial.println(" g");

    delay(1000);  // Attendre 1 seconde avant la prochaine lecture
}
