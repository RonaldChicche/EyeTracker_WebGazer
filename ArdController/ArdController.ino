#include <Servo.h>

// Definicion de servos y posiciones
Servo p_inf;
Servo p_sup;
Servo i_y;
Servo i_x;
int x = 0;
int y = 0;
int inf = 0;
int sup = 0;

// Configuracion de buffer para recibir datos
#define BUFFER_SIZE 512 // Tamaño máximo del buffer

char buffer[BUFFER_SIZE]; // Buffer para almacenar los datos
int index = 0; // Índice actual del buffer


void setup() {
  Serial.begin(115200);
  p_inf.attach(9);
  p_sup.attach(10);
  i_y.attach(11);
  i_x.attach(12);
  Serial.println("Iniciando comunicacion -> Servos listos");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    //Serial.println(c);
    if (c == '\n') {  // Carácter de fin de línea detectado
      //Serial.println("Chain accepted");
      separar(buffer);
      angles_apply();
      buffer[index] = '\0';  // Agregar el carácter nulo al final del buffer para formar una cadena de texto
      Serial.print("Ard-> "); Serial.print(x); Serial.print(" - "); Serial.print(y); Serial.print(" - "); Serial.print(inf); Serial.print(" - "); Serial.println(sup);//Serial.println(" " + String(buffer));
      index = 0;  // Reiniciar el índice del buffer
    } else {
      buffer[index] = c;  // Almacenar el carácter en el buffer
      index++;
      if (index >= sizeof(buffer)) {
        index = sizeof(buffer) - 1;  // Evitar desbordamiento del buffer
      }
    }
  }
}

void separar(char* input) {
  char buf[BUFFER_SIZE];
  char* token;

  // Copiar el string de entrada en un buffer para evitar modificaciones directas
  strcpy(buf, input);

  // Obtener el primer token (valor antes de la coma)
  token = strtok(buf, ",");
  if (token != NULL) {
    // Convertir el token a entero y asignarlo a value1
    x = atoi(token);
  }

  // Obtener el segundo token (valor después de la coma)
  token = strtok(NULL, ",");
  if (token != NULL) {
    // Convertir el token a entero y asignarlo a value2
    y = atoi(token);
  }

  // Obtener el tercer token (valor entre la segunda y la tercera coma)
  token = strtok(NULL, ",");
  if (token != NULL) {
    // Convertir el token a entero y asignarlo a la tercera variable (z)
    inf = atoi(token);
  }

  // Obtener el cuarto token (valor después de la tercera coma)
  token = strtok(NULL, ",");
  if (token != NULL) {
    // Convertir el token a entero y asignarlo a la cuarta variable (w)
    sup = atoi(token);
  }
}



void angles_apply() {
  i_x.write(x);
  i_y.write(y);
  p_inf.write(inf);
  p_sup.write(sup);
}
