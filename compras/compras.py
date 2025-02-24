from flask import Flask, jsonify
from kafka import KafkaConsumer, KafkaProducer
import json
import threading

app = Flask(__name__)


producer = KafkaProducer(
    bootstrap_servers="host.docker.internal:9092",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def kafka_listener():
    consumer = KafkaConsumer(
        "consultar_compras",
        bootstrap_servers="host.docker.internal:9092",
        value_deserializer=lambda m: json.loads(m.decode("utf-8"))
    )
    for message in consumer:
        data = message.value
        print("Mensaje recibido de Kafka en Compras:", data)
      
        historial_compras = {
            "id_compra": data.get("id_compra"),
            "historial": [
                {"item": "Producto A", "cantidad": 1, "fecha": "2025-01-10"},
                {"item": "Producto B", "cantidad": 2, "fecha": "2025-01-15"}
            ]
        }

        producer.send("respuesta_compras", historial_compras)
        print("Historial de compras enviado:", historial_compras)


kafka_thread = threading.Thread(target=kafka_listener)
kafka_thread.daemon = True
kafka_thread.start()

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
