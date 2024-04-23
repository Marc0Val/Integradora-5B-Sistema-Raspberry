import Adafruit_DHT
import paho.mqtt.client as mqtt
import time

# Configuración del sensor
sensor = Adafruit_DHT.DHT11
pin_dht = 26 

# Configuración del MQTT
broker_address = "broker.hivemq.com"
topic_temp = "ruben/temperatura"
topic_hum = "ruben/humedad"
client = mqtt.Client()

# Conexión al MQTT
client.connect(broker_address, 1883)

# Función para leer los datos del sensor y publicarlos
def leer_sensor_y_publicar():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin_dht)
    if humidity is not None and temperature is not None:
        client.publish(topic_temp, int(temperature))  # Publicar el valor entero de la temperatura
        client.publish(topic_hum, int(humidity))  # Publicar el valor entero de la humedad
        print(f"Temperatura publicada en {topic_temp}: {int(temperature)}°C")
        print(f"Humedad publicada en {topic_hum}: {int(humidity)}%")
    else:
        print('Error al leer los datos del sensor.')

while True:
    leer_sensor_y_publicar()
    time.sleep(1)  # Publicar cada minuto
