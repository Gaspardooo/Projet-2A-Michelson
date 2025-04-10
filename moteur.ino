#include <Stepper.h>

const int stepsPerRevolution = 1000; // Définiton d'une révolution
Stepper myStepper(stepsPerRevolution, 8, 10, 9, 11); // Branchement du moteur sur la carte

// avec vitesse 6 et la boucle for : un tour de vis micrométrique = 3920 steps

void setup() {
  Serial.begin(9600);
  myStepper.setSpeed(6); // Vitesse de rotation du moteur
  
  for (int s=0 ; s<=3920 ; s++) // ici on fait tourner le moteur pourune révolution de vis micrométrique
    {
    Serial.print("steps:");
    myStepper.step(1);
    Serial.println(s); // Affichage du nombre de steps dans la console
    delay(30);
    }
}


void loop() {
}


