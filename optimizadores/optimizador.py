from flask import Flask, request, jsonify
from kafka import KafkaProducer, KafkaConsumer
import json
import time
import redis

app = Flask(__name__)


producer = KafkaProducer(
    bootstrap_servers="host.docker.internal:9092",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.route("/validar_orden", methods=["POST"])
def validar_orden():
    data = request.json
    id_compra = data.get("id_compra")
    

    cached_order = redis_client.get(id_compra)
    if cached_order:
        return jsonify(json.loads(cached_order))
    

    consumer = KafkaConsumer(
        "respuesta_compras", "respuesta_productos",
        bootstrap_servers="host.docker.internal:9092",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        consumer_timeout_ms=10000  
    )
    
 
    producer.send("consultar_compras", data)
    producer.send("consultar_productos", data)
    producer.flush() 
    response_compras = None
    response_productos = None
    start_time = time.time()

    while time.time() - start_time < 10:
        for message in consumer:
            topic = message.topic
            msg = message.value
           
            if topic == "respuesta_compras" and msg.get("id_compra") == id_compra:
                response_compras = msg
            elif topic == "respuesta_productos" and msg.get("id_compra") == id_compra:
                response_productos = msg
            if response_compras and response_productos:
                break
        if response_compras and response_productos:
            break

    consumer.close()


    if not (response_compras and response_productos):
   
        cached_order = redis_client.get(id_compra)
        if cached_order:
            return jsonify(json.loads(cached_order))
        else:
           
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

    
    optimized_order = {
         "id_compra": id_compra,
         "optimizado": True,
         "detalles": {
             "compras": response_compras,
             "productos": response_productos
         }
    }
    
   
    redis_client.setex(id_compra, 300, json.dumps(optimized_order))
    
    return jsonify(optimized_order)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
