from flask import Flask, jsonify
from kafka import KafkaConsumer, KafkaProducer
import json
import threading

app = Flask(__name__)

# Configuramos un productor de Kafka para enviar la respuesta simulada
producer = KafkaProducer(
    bootstrap_servers="host.docker.internal:9092",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def kafka_listener():
    consumer = KafkaConsumer(
        "consultar_productos",
        bootstrap_servers="host.docker.internal:9092",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    for message in consumer:
        data = message.value
        print("Mensaje recibido de Kafka en Productos:", data)
        
        # Simular la respuesta de productos
        response_productos = {
            "id_compra": data.get("id_compra"),
            "productos_info": [
                {"id": 1, "nombre": "Producto A", "disponibilidad": "alta"},
                {"id": 2, "nombre": "Producto B", "disponibilidad": "media"}
            ]
        }
        
        # Enviar la respuesta simulada al tópico "respuesta_productos"
        producer.send("respuesta_productos", response_productos)
        print("Respuesta de productos enviada a Kafka:", response_productos)

# Iniciar el consumidor de Kafka en un hilo aparte
kafka_thread = threading.Thread(target=kafka_listener)
kafka_thread.daemon = True  # El hilo se cierra al finalizar el proceso principal
kafka_thread.start()

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
