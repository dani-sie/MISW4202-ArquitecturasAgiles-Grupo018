from kafka import KafkaProducer
import time
import json
import requests
import subprocess

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

SERVICIOS = {
    "compras": "http://compras:5002/health",
    "productos": "http://productos:5003/health"
}

def restart_service(service_name):
    """
    Intenta reiniciar el servicio usando Docker.
    Se asume que el nombre del contenedor es el mismo que el nombre del servicio.
    """
    try:

        result = subprocess.run(
            ["docker", "restart", service_name],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Servicio '{service_name}' reiniciado exitosamente. Output: {result.stdout.strip()}")
    except Exception as e:
        print(f"Error al reiniciar el servicio '{service_name}': {e}")

while True:
    for servicio, url in SERVICIOS.items():
        try:
            response = requests.get(url, timeout=3)
            if response.status_code != 200:
                raise Exception("Fallo en el status code")
        except Exception as e:
            print(f"Error en {servicio}: {e}")

            producer.send("fallos_servicios", {"servicio": servicio})
 
            restart_service(servicio)
    
    time.sleep(5)
