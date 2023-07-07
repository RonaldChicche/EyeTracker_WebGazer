import socketio
import csv
import json
import time
import keyboard
import serial
import threading
from math import atan
from scipy.signal import butter, lfilter
from collections import deque



# Configuración del filtro de paso bajo Butterworth
cutoff = 0.2  # Frecuencia de corte del filtro en Hz
fs = 15.98  # Frecuencia de muestreo
order = 2  # Orden del filtro
b, a = butter(order, cutoff / (0.5 * fs), btype='low')
# Crear colas de longitud máxima para almacenar los datos
window_size = 1000  # Ajusta este valor según tus necesidades
x_data = deque(maxlen=window_size)
y_data = deque(maxlen=window_size)
data_list = []  # Lista para almacenar los datos


# Variables para obtencion de angulo array = {pos, min, max, margen}
parI = [0, 30, 100, 30];
parS = [0, 70, 140, 30];
iriX = [0, 40, 140];
iriY = [0, 110, 180];
cx = 750.00;        # Centro horizontal
cy = 400.00;        # Centro vertical
d = 200.00;         # Distancia de referencia de la pantalla y usuario en pixeles - solo referencial
xamax = atan(cx/d);
xamin = -xamax;
yamax = atan(cy/d);
yamin = -yamax;


# Crear una conexión serial
serial_port = 'COM4'  # Reemplaza con el puerto serial correspondiente
baud_rate = 115200
ser = None
reconnect_delay = 2  # Retardo entre intentos de reconexión
reconnect_attempts = 0  # Número de intentos de reconexión

# Cliente websocket
sio = socketio.Client()
run = True

@sio.event
def connect():
    print("I'm connected!")

@sio.event
def disconnect():
    print("I'm disconnected!")
    run = False
    # Cuando se desconecta, escribe la lista en un archivo CSV
    try:
        keys = data_list[0].keys()
        with open('data.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data_list)
    except Exception as e:
        print(f"Error writing CSV: {e}")
        print("Writing data to JSON instead.")
        with open('data.json', 'w') as output_file:
            json.dump(data_list, output_file)

@sio.on('data')
def on_message(data):
    #print('I received a message!', data)
    # Los datos ya están en formato de diccionario, así que puedes añadirlos directamente a la lista
    try:
        data['time'] = time.time()
        # Agregar los nuevos datos a las colas
        x_data.append(data['x'])
        y_data.append(data['y'])
        # Aplicar el filtro a los datos en las colas
        x_filtered = lfilter(b, a, list(x_data))
        y_filtered = lfilter(b, a, list(y_data))
        # Agregar los datos filtrados al diccionario
        data['x_f'] = x_filtered[-1]  # Tomar el último valor de la lista filtrada
        data['y_f'] = y_filtered[-1]  # Tomar el último valor de la lista filtrada
        data_list.append(data)
        # Enviar los angulos procesados por serial
        # ser.write(f"{data['x_f']},{data['y_f']}\n".encode())
        alpha = atan((cx - data['x_f']) / d);
        betha = atan((cy - data['y_f']) / d);
        if (xamin < alpha and alpha < xamax):
            iriX[0] = ard_map(alpha, xamin, xamax, iriX[1], iriX[2]);
        if (yamin < betha and betha < yamax):
            iriY[0] = ard_map(betha, yamin, yamax, iriY[1], iriY[2]);
        
        
        infy = ard_map(betha, yamin, yamax, parI[1], parI[2])                
        infx = ard_map(abs(alpha), 0, xamax,  parI[1], parI[2])
        inf = max(infx, infy)
        supy = ard_map(betha, yamin, yamax, parS[2], parS[1])                
        supx = ard_map(abs(alpha), 0, xamax,  parS[2], parS[1])
        sup = max(supx, supy)
        
        print(f"x: {alpha:.3f} -> {xamin:.3f}/{xamax:.3f}\t y: {betha:.3f} -> {yamin:.3f}/{yamax:.3f}")
        print(f"   {iriX[0]:.3f} -> {iriX[1]}/{iriX[2]}\t\t    {iriY[0]:.3f} -> {iriY[1]}/{iriY[2]}")
        print(f"   {data_list[-1]['x_f']:.3f}\t\t\t    {data_list[-1]['y_f']:.3f}")
        print(f"   {data_list[-1]['x']:.3f}\t\t\t    {data_list[-1]['y']:.3f}")
        
        send_to_arduino(f"{iriX[0]},{iriY[0]},{inf},{sup}\n")
        #print('SEND')
    except Exception as e:
        print(f"Error processing data: {e}")


# Función para establecer la conexión serial
def setup_serial():
    global ser, reconnect_attempts
    try:
        ser = serial.Serial(serial_port, baud_rate)
        print('Conexión serial establecida')
        reconnect_attempts = 0  # Reiniciar el contador de intentos de reconexión
    except serial.SerialException:
        print('Error al establecer la conexión serial')
        time.sleep(reconnect_delay)
        reconnect_attempts += 1
        setup_serial()

# Función para enviar datos al Arduino por el puerto serial
def send_to_arduino(data):
    if ser and ser.is_open:
        ser.write(data.encode())

# Función para recibir datos del Arduino por el puerto serial
def receive_from_arduino():
    while True:
        if ser and ser.is_open:
            if ser.in_waiting > 0:
                data = ser.readline().decode('latin-1')#.strip()
                print(data) #data_list[-1]['x_f'], data_list[-1]['y_f'], 
                #print(iriX[0], iriY[0], data, alpha, betha)
            #else:
            #    print('Esperando datos...')

def ard_map(value, from_min, from_max, to_min, to_max):
    # Mapea el valor de entrada desde el rango original al rango deseado
    return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

# Función para iniciar los hilos
def start_threads():
    serial_thread = threading.Thread(target=receive_from_arduino)
    serial_thread.daemon = True
    serial_thread.start()

    sio_thread = threading.Thread(target=sio.wait)
    sio_thread.daemon = True
    sio_thread.start()


# Función principal
def main():
    setup_serial()
    
    sio.connect('http://localhost:3030', transports='websocket')

    start_threads()
    print('Hilos listos')

    # Cerrar el servidor cuando se presione la tecla 'q'
    keyboard.add_hotkey('q', sio.disconnect)

    while run:
        if not ser or not ser.is_open:
            print('Puerto desconectado')
            setup_serial()
        time.sleep(1)  # Esperar 1 segundo antes de verificar nuevamente la conexión


if __name__ == '__main__':
    main()