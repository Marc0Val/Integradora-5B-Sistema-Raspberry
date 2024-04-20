import RPi.GPIO as GPIO
import time
import serial
import json
import requests
from datetime import datetime
import random
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Arreglo con el display del teclado
teclado_arreglo = [
    [1, 2, 3, "A"],
    [4, 5, 6, "B"],
    [7, 8, 9, "C"],
    ["*", 0, "#", "D"]
]

# diccionario para almacenar la información de la visita
motivos_visita = {
    "A": "Consulta de libros",
    "B": "Préstamo de material",
    "C": "Estudio en grupo",
    "D": "Uso de computadoras"
}

# Arreglo con las salidas y entradas dependiendo del pin
entradas = [18, 23, 24, 25]
salidas = [17, 27, 22, 5]

# Pin del LED
pin_led = 4

# Inicialización del bus I2C y del objeto SSD1306 para la pantalla OLED
i2c = busio.I2C(SCL, SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

def mostrar_mensaje(mensaje):
    # Limpiar la pantalla
    disp.fill(0)
    disp.show()

    # Crear una nueva imagen
    image = Image.new('1', (128, 64))
    draw = ImageDraw.Draw(image)

    # Cargar la fuente predeterminada
    font = ImageFont.load_default()

    # Escribir el mensaje en la imagen
    draw.text((0, 0), mensaje, font=font, fill=255)

    # Mostrar la imagen en la pantalla
    disp.image(image)
    disp.show()

def configuracion_teclado():
    # Configuración del tipo de display de la ras
    GPIO.setmode(GPIO.BCM)
    # Configuración de las entradas y salidas en los pines
    GPIO.setup(entradas, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(salidas, GPIO.OUT)
    # Establecer los pines que son de salida como salidas con alto
    GPIO.output(salidas, 1)

def leer_tecla():
    # Asignar un valor nulo a la tecla la primera vez
    tecla = None
    # Ciclo para recorrer el arreglo dependiendo de la coordenada que se le de al presionar el teclado
    for j in range(4):
        GPIO.output(salidas[j], 0)
        for i in range(4):
            if GPIO.input(entradas[i]) == 0:
                tecla = teclado_arreglo[i][j]
                while GPIO.input(entradas[i]) == 0:
                    pass
        GPIO.output(salidas[j], 1)
    # Se retorna la tecla
    return tecla

# configuracion del puerto uart para el escaner de codigo QR
def configuracion_uart():
    return serial.Serial('/dev/ttyS0', 9600, timeout=1)

# leer el codigo QR
def leer_codigo_qr(ser):
    # Leer código QR desde el puerto UART
    if ser.in_waiting > 0:
        barcode_data = ser.readline().decode().strip()
        return barcode_data
    else:
        return None

def encender_led():
    # Encender el LED
    GPIO.output(pin_led, GPIO.HIGH)

def apagar_led():
    # Apagar el LED
    GPIO.output(pin_led, GPIO.LOW)

def enviar_nuevo_alumno_api(alumno_info):
    # URL del endpoint de la REST API para agregar un nuevo alumno
    url = 'http://(ip-del-servidor):7800/api/alumno/crear'
    
    # Convertir el diccionario de la alumno_info a formato JSON
    alumno_json = json.dumps(alumno_info)
    
    # Mostrar/imprimir el formato JSON antes de enviarlo a la API
    print("Formato JSON de nuevo alumno a enviar:")
    print(alumno_json)
    
    # Realizar la solicitud HTTP POST a la API
    try:
        response = requests.post(url, json=alumno_info)
        if response.status_code == 201:
            mostrar_mensaje("Nuevo alumno registrado con éxito")
            print("Nuevo alumno enviado exitosamente a la API.")
            time.sleep(2)
        else:
            mostrar_mensaje("Error al registrar nuevo alumno")
            time.sleep(2)
            print("Error al enviar el nuevo alumno a la API:", response.status_code)
    except Exception as e:
        mostrar_mensaje("Error al registrar nuevo alumno")
        time.sleep(2)
        print("Error al enviar el nuevo alumno a la API:", str(e))

def enviar_visita_api(visita_info):
    # URL del endpoint de la REST API
    url = 'http://(ip-del-servidor):7800/api/visita/crear'
    
    # Convertir el diccionario de la visita_info a formato JSON
    visita_json = json.dumps(visita_info)
    
    # Mostrar/imprimir el formato JSON antes de enviarlo a la API
    print("Formato JSON a enviar:")
    print(visita_json)
    
    # Realizar la solicitud HTTP POST a la API
    try:
        response = requests.post(url, json=visita_info)
        if response.status_code == 201:
            mostrar_mensaje("Visita registrada con éxito")
            time
            print("Visita enviada exitosamente a la API.")
        else:
            mostrar_mensaje("Error al registrar visita")
            time.sleep(1)
            print("Error al enviar la visita a la API:", response.status_code)
    except Exception as e:
        mostrar_mensaje("Error al registrar visita")
        time.sleep(1)
        print("Error al enviar la visita a la API:", str(e))

def enviar_prestamo_api(prestamo_info):
    # URL del endpoint de la REST API
    url = 'http://(ip-del-servidor):7800/api/prestamo/crear'

    # Convertir el diccionario de la visita_info a formato JSON
    prestamo_json = json.dumps(prestamo_info)

    # Mostrar/imprimir el formato JSON antes de enviarlo a la API
    print("Formato JSON a enviar:")
    print(prestamo_json)

    # Realizar la solicitud HTTP POST a la API
    try:
        response = requests.post(url, json=prestamo_info)
        if response.status_code == 201:
            mostrar_mensaje("Préstamo registrado con éxito")
            print("Préstamo enviado exitosamente a la API.")
        else:
            mostrar_mensaje("Error al registrar préstamo")
            time.sleep(1)
            print("Error al enviar el préstamo a la API:", response.status_code)
    except Exception as e:
        mostrar_mensaje("Error al registrar préstamo")
        time.sleep(1)
        print("Error al enviar el préstamo a la API:", str(e))
# funcion externa para resetear el programa en dado caso que se use
def reset_program():
    GPIO.cleanup()
    main()

def main():
    try:
        # Configurar los pines para el teclado
        configuracion_teclado()
        uart_port = configuracion_uart()
        # Configurar el pin del LED
        GPIO.setup(pin_led, GPIO.OUT)
        apagar_led()

        # Ciclo principal
        while True:
            # Mostrar el menú de selección
            mostrar_mensaje("Menu de seleccion\n1: Visita\n2: Agregar Alumno\n3: Préstamo")
            tecla = None
            while tecla not in [1, 2, 3]:
                tecla = leer_tecla()
            # Ejecutar la opción seleccionada
            if tecla == 1:
                mostrar_mensaje("Modo De Visita\Seleccionado")
                time.sleep(2)
                mostrar_mensaje("Selecciona tu motivo \n A)Consulta B)Material\n C)Grupo D)Computador")
                motivo_visita = None
                start_time_visita = time.time()
                # esperar a que el usuario seleccione el motivo de la visita en 10 segundos, si no salir del
                while motivo_visita is None:
                    if time.time() - start_time_visita > 10:
                        mostrar_mensaje("Tiempo agotado \nIntente de nuevo")
                        time.sleep(2)
                        break
                    motivo_visita = leer_tecla()
                # si se selecciono un motivo de visita valido entonces se procede a registrar la visita
                if motivo_visita in ["A", "B", "C", "D"]:
                    print("Motivo de la visita:", motivos_visita[motivo_visita])
                    mostrar_mensaje("Motivo de la visita:\n" + motivos_visita[motivo_visita])
                    time.sleep(2)
                    # hacer el escaneo de la informacion del alumno
                    mostrar_mensaje("Escanea el alumno")
                    encender_led()
                    uart_port.reset_input_buffer()
                    info_alumno = None
                    start_time_alumno = time.time()
                    while info_alumno is None:
                        if time.time() - start_time_alumno > 10:
                            mostrar_mensaje("Tiempo agotado \nIntente de nuevo")
                            time.sleep(2)
                            break
                        info_alumno = leer_codigo_qr(uart_port)
                    apagar_led()
                    # hacer la decodificacion de la informacion del codigo del alumno
                    if info_alumno is not None:
                        info_alumno = info_alumno.split(",")
                        if len(info_alumno) == 7 and len(info_alumno[0].strip()) == 10:
                            alumno_id = info_alumno[0].strip()
                            nombre = info_alumno[1].strip()
                            apellido_paterno = info_alumno[2].strip()
                            apellido_materno = info_alumno[3].strip()
                            carrera = info_alumno[4].strip()
                            telefono = info_alumno[5].strip()
                            correo = info_alumno[6].strip().replace('"', '@')
                            #obtener un id de visita aleatorio e irrepetible
                            id_visita = random.randint(1, 999999)

                            #obtener la fecha y hora actual
                            fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
                            # crear un json con la informacion de la visita
                            visita_info = {
                            "idVisita": id_visita,
                            "motivo": motivos_visita[motivo_visita],
                            "noCtrl": alumno_id,
                            "nombre": nombre,
                            "apellidoP": apellido_paterno,
                            "apellidoM": apellido_materno,
                            "carrera": carrera,
                            "telefono": telefono,
                            "correo": correo,
                            "horaEntrada": fecha_hora_actual.split()[1],
                            "fechaVisita": fecha_hora_actual.split()[0]
                            }
                            # imprimir el json en consola
                            # print(json.dumps(visita_info, indent=4))
                            # enviar el json a la rest API
                            enviar_visita_api(visita_info)
                        else:
                            mostrar_mensaje("Código QR inválido \nIntente de nuevo")
                            time.sleep(2)
                    else:
                        mostrar_mensaje("Código QR no detectado \nIntente de nuevo")
                        time.sleep(2)
            elif tecla == 2:
                print("Modo Agregar Alumno seleccionado")
                mostrar_mensaje("Modo Agregar Alumno\nSeleccionado")
                time.sleep(2)
                mostrar_mensaje("Escanea el alumno")
                encender_led()
                uart_port.reset_input_buffer()
                info_alumno = None
                start_time_alumno = time.time()
                while info_alumno is None:
                    if time.time() - start_time_alumno > 10:
                        mostrar_mensaje("Tiempo agotado \nIntente de nuevo")
                        time.sleep(2)
                        break
                    info_alumno = leer_codigo_qr(uart_port)
                apagar_led()
                if info_alumno is not None:
                    #hacer la decodificacion de la informacion del codigo del alumno
                    info_alumno = info_alumno.split(",")
                    if len(info_alumno) == 7 and len(info_alumno[0].strip()) == 10:
                        alumno_id = info_alumno[0].strip()
                        nombre = info_alumno[1].strip()
                        apellido_paterno = info_alumno[2].strip()
                        apellido_materno = info_alumno[3].strip()
                        carrera = info_alumno[4].strip()
                        telefono = info_alumno[5].strip()
                        correo = info_alumno[6].strip().replace('"', '@') # Reemplazar las comillas dobles por el símbolo @

                        # Mostrar la información del alumno en consola
                        print("ID del alumno:", alumno_id)
                        print("Nombre:", nombre)
                        print("Apellido paterno:", apellido_paterno)
                        print("Apellido materno:", apellido_materno)
                        print("Carrera:", carrera)
                        print("Teléfono:", telefono)
                        print("Correo:", correo)
                        
                        # crear un json con la unformacion del alumno
                        nuevo_alumno_info = {
                            "noCtrl": alumno_id,
                            "nombre": nombre,
                            "apellidoP": apellido_paterno,
                            "apellidoM": apellido_materno,
                            "carrera": carrera,
                            "telefono": telefono,
                            "correo": correo
                        }
                        # imprimir el json en consola
                        # print(json.dumps(nuevo_alumno_info, indent=4))
                        # enviar el json a la rest API
                        enviar_nuevo_alumno_api(nuevo_alumno_info)
                    else:
                        mostrar_mensaje("Código inválido\nIntente de nuevo")
                        time.sleep(2)
                else:
                    mostrar_mensaje("Código no detectado\nIntente de nuevo")
                    time.sleep(2)                    
            elif tecla == 3:
                mostrar_mensaje("Modo Préstamo\nSeleccionado")
                time.sleep(2)
                mostrar_mensaje("Escanea el material")
                encender_led()
                uart_port.reset_input_buffer()
                info_material = None
                start_time_material = time.time()
                while info_material is None:
                    if time.time() - start_time_material > 10:
                        mostrar_mensaje("Tiempo agotado\nIntente de nuevo")
                        time.sleep(2)
                        break
                    info_material = leer_codigo_qr(uart_port)
                apagar_led()
                # solo recibira una cadena de 14 caracteres
                if info_material is not None and len(info_material) == 14:
                    mostrar_mensaje("Material escaneado")
                    time.sleep(2)
                    # escanear ahora la informacion del alumno pero ahora solo se necesita el id del alumno que tiene que se de 10 caracteres
                    mostrar_mensaje("Escanea el alumno")
                    encender_led()
                    info_alumno = None
                    start_time_alumno = time.time()
                    while info_alumno is None:
                        if time.time() - start_time_alumno > 10:
                            mostrar_mensaje("Tiempo agotado\nIntente de nuevo")
                            time.sleep(2)
                            reset_program()
                        info_alumno = leer_codigo_qr(uart_port)
                    apagar_led()
                    # alumno_info = info_alumno.split(",")
                    # si no se escaneo la informacion del alumno se sale del modo
                    if info_alumno is not None:
                        info_alumno = info_alumno.split(",")
                    else:
                        mostrar_mensaje("Código no detectado\nIntente de nuevo")
                        time.sleep(2)
                        reset_program()

                    if len(info_alumno) == 7 and len(info_alumno[0].strip()) == 10:
                        alumno_id = info_alumno[0].strip()
                        time.sleep(2)
                        # crear un json con la informacion del prestamo
                        prestamo_info = {
                            "idLibro": info_material,
                            "noCtrl": alumno_id,
                        }
                        # imprimir el json en consola
                        print(json.dumps(prestamo_info, indent=4))
                        # enviar el json a la rest API
                        enviar_prestamo_api(prestamo_info)
                    else:
                        mostrar_mensaje("Código de alumno\ninválido\nIntente de nuevo")
                        time.sleep(2)
                else:
                    mostrar_mensaje("Código invalido\nEscanea el material\nIntente de nuevo")
                    time.sleep(2)
    except KeyboardInterrupt:
        # Limpiar los pines en caso de una interrupción de teclado
        GPIO.cleanup()

if __name__ == "__main__":
    main()

