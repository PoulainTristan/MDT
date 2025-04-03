#include <Arduino.h>

// Définition des GPIO pour le driver moteur
#define IN1 14
#define IN2 13
#define IN3 27
#define IN4 26

// Paramètres PWM
#define PWM_FREQ 5000          // Fréquence PWM en Hz
#define PWM_RESOLUTION 8       // Résolution PWM (8 bits : 0-255)
#define PWM_CHANNEL_MOTOR1_IN1 0 // Canal PWM pour IN1
#define PWM_CHANNEL_MOTOR1_IN2 1 // Canal PWM pour IN2
#define PWM_CHANNEL_MOTOR2_IN3 2 // Canal PWM pour IN3
#define PWM_CHANNEL_MOTOR2_IN4 3 // Canal PWM pour IN4

// Connexions du capteur HC-SR04
#define TRIG_PIN 15
#define ECHO_PIN 16

// Variables pour la mesure de la distance
long duration;
int distance;
int previousDistance = 0;
int smoothedSpeed = 0;  // Variable pour lisser la vitesse

// Fonction pour mesurer la distance avec le capteur ultrason
int getDistance() {
  long totalDuration = 0;
  int numberOfReads = 5;  // Nombre de mesures pour lisser la lecture
  
  // Prendre plusieurs mesures pour lisser
  for (int i = 0; i < numberOfReads; i++) {
    // Envoie une impulsion de 10µs sur la broche TRIG
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // Mesure le temps de propagation de l'impulsion
    totalDuration += pulseIn(ECHO_PIN, HIGH);
    delay(10); // Petite pause entre les mesures
  }
  
  // Calculer la distance moyenne
  duration = totalDuration / numberOfReads;
  distance = duration * 0.034 / 2; // Divisé par 2 pour aller-retour

  return distance;
}

void setMotorSpeed(int channel1, int channel2, int speed) {
  // Contrôler la vitesse et le sens du moteur
  if (speed > 0) {
    ledcWrite(channel1, speed); // Vitesse dans un sens
    ledcWrite(channel2, 0);
  } else if (speed < 0) {
    ledcWrite(channel1, 0);
    ledcWrite(channel2, -speed); // Vitesse dans l'autre sens
  } else {
    ledcWrite(channel1, 0);
    ledcWrite(channel2, 0); // Arrêter le moteur
  }
}

void setup() {
  // Initialiser la communication série pour le débogage
  Serial.begin(115200);
  Serial.println("Début des tests moteurs avec capteur ultrason");

  // Configurer les broches PWM
  ledcSetup(PWM_CHANNEL_MOTOR1_IN1, PWM_FREQ, PWM_RESOLUTION);
  ledcSetup(PWM_CHANNEL_MOTOR1_IN2, PWM_FREQ, PWM_RESOLUTION);
  ledcSetup(PWM_CHANNEL_MOTOR2_IN3, PWM_FREQ, PWM_RESOLUTION);
  ledcSetup(PWM_CHANNEL_MOTOR2_IN4, PWM_FREQ, PWM_RESOLUTION);

  // Associer les canaux PWM aux broches GPIO
  ledcAttachPin(IN1, PWM_CHANNEL_MOTOR1_IN1);
  ledcAttachPin(IN2, PWM_CHANNEL_MOTOR1_IN2);
  ledcAttachPin(IN3, PWM_CHANNEL_MOTOR2_IN3);
  ledcAttachPin(IN4, PWM_CHANNEL_MOTOR2_IN4);

  // Initialiser les broches du capteur ultrason
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Configurer la LED intégrée comme sortie (facultatif)
  pinMode(2, OUTPUT);
}

void loop() {
  // Lire la distance du capteur ultrason
  int distance = getDistance();
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // Si la distance est très faible (par exemple, moins de 10 cm), arrêter les moteurs
  if (distance < 10) {
    digitalWrite(2, HIGH);
    Serial.println("Obstacle trop proche ! Moteurs arrêtés.");
    setMotorSpeed(PWM_CHANNEL_MOTOR1_IN1, PWM_CHANNEL_MOTOR1_IN2, 0);
    setMotorSpeed(PWM_CHANNEL_MOTOR2_IN3, PWM_CHANNEL_MOTOR2_IN4, 0);
  } else {
    // Sinon, ajuster la vitesse des moteurs selon la distance
    digitalWrite(2, LOW);

    // Utiliser la fonction map() pour ajuster la vitesse des moteurs en fonction de la distance
    // Plus la distance est grande, plus la vitesse est élevée
    int targetSpeed = map(distance, 10, 50, 50, 255); // Vitesse entre 50 et 255 (pour distance entre 10 et 50 cm)
    
    // Lisser la vitesse pour éviter des changements trop brusques
    smoothedSpeed = (smoothedSpeed + targetSpeed) / 2;  // Moyenne pour lisser

    // Afficher la vitesse calculée pour le débogage
    Serial.print("Vitesse moteurs : ");
    Serial.println(smoothedSpeed);

    // Appliquer les vitesses aux moteurs
    setMotorSpeed(PWM_CHANNEL_MOTOR1_IN1, PWM_CHANNEL_MOTOR1_IN2, smoothedSpeed);
    setMotorSpeed(PWM_CHANNEL_MOTOR2_IN3, PWM_CHANNEL_MOTOR2_IN4, smoothedSpeed);
  }

  delay(100); // Attendre un peu avant de refaire la mesure pour plus de fluidité
}