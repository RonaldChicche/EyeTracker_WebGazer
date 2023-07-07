/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 https://www.arduino.cc/en/Tutorial/LibraryExamples/Sweep
*/

#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position

void setup() {
  myservo.attach(11);  
  Serial.begin(115200);
}

void loop() {
  if (Serial.available()) { // Si hay datos disponibles para leer en el puerto serial
    int pos = Serial.parseInt(); // Lee y convierte los datos a un entero
    if (pos >= 0 && pos <= 180) { // Si la posición está en el rango permitido para un servomotor (0-180 grados)
      myservo.write(pos); // Mueve el servomotor a la posición especificada
    }
    
    // Limpiar el buffer serial para evitar lecturas no deseadas
    while (Serial.available() > 0) {
      Serial.read();
    }
  }
}

// 09 Parpado inferiror:   up -> 20 , down -> 100
// 10 Parpado superior:    up -> 60 , down -> 130 ---- revisar
// 11 iris up/down :       up -> 180, down -> 110 
// 12 iris right/left:     rg -> 140, left -> 40
