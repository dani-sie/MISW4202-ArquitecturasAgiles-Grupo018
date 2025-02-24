from flask import Flask, request, jsonify
from kafka import KafkaProducer, KafkaConsumer
import json
import time
import redis

app = Flask(__name__)

# Configuramos el productor de Kafka para enviar mensajes en formato JSON
producer = KafkaProducer(
    bootstrap_servers="host.docker.internal:9092",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Cliente de Redis (asumiendo que el host es 'redis' en la red Docker)
redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.route("/validar_orden", methods=["POST"])
def validar_orden():
    data = request.json
    id_compra = data.get("id_compra")
    
    # Si ya existe una orden optimizada en cache, la devolvemos
    cached_order = redis_client.get(id_compra)
    if cached_order:
        return jsonify(json.loads(cached_order))
    
    # Creamos un consumidor para los tópicos de respuesta
    consumer = KafkaConsumer(
        "respuesta_compras", "respuesta_productos",
        bootstrap_servers="host.docker.internal:9092",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        consumer_timeout_ms=10000  # Espera máxima de 10 segundos
    )
    
    # Publicamos la orden en los tópicos correspondientes
    producer.send("consultar_compras", data)
    producer.send("consultar_productos", data)
    producer.flush()  # Forzamos el envío inmediato
    
    response_compras = None
    response_productos = None
    start_time = time.time()
    
    # Esperamos hasta 10 segundos a que lleguen ambas respuestas
    while time.time() - start_time < 10:
        for message in consumer:
            topic = message.topic
            msg = message.value
            # Filtramos mensajes que correspondan al id_compra actual
            if topic == "respuesta_compras" and msg.get("id_compra") == id_compra:
                response_compras = msg
            elif topic == "respuesta_productos" and msg.get("id_compra") == id_compra:
                response_productos = msg
            if response_compras and response_productos:
                break
        if response_compras and response_productos:
            break

    consumer.close()

    # Si faltan respuestas (indicación de que un servicio falló)
    if not (response_compras and response_productos):
        # Si ya hay un caché previo, lo usamos
        cached_order = redis_client.get(id_compra)
        if cached_order:
            return jsonify(json.loads(cached_order))
        else:
            # Sino, retornamos un error indicando degradación del sistema
            error_response = {
                "id_compra": id_compra,
                "optimizado": False,
                "error": "No se pudieron obtener las respuestas completas de los servicios.",
                "detalles": {
                    "compras": response_compras,
                    "productos": response_productos
                }
            }
            return jsonify(error_response), 503

    # Se realizó la optimización (simulada) integrando las respuestas recibidas
    optimized_order = {
         "id_compra": id_compra,
         "optimizado": True,
         "detalles": {
             "compras": response_compras,
             "productos": response_productos
         }
    }
    
    # Guardamos el resultado optimizado en cache (con expiración de 300 segundos)
    redis_client.setex(id_compra, 300, json.dumps(optimized_order))
    
    return jsonify(optimized_order)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
