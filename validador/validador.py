from flask import Flask, request, jsonify
from kafka import KafkaConsumer, KafkaProducer
import json

app = Flask(__name__)

#consumer = KafkaConsumer("resultados_optimizacion", bootstrap_servers="host.docker.internal:9092", auto_offset_reset="earliest",
#                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))
producer = KafkaProducer(bootstrap_servers="host.docker.internal:9092", value_serializer=lambda v: json.dumps(v).encode('utf-8'))

@app.route("/validar_resultados", methods=["POST"])
def validar_resultados():
    data = request.json
    decisiones = data.get("decisiones", [])

    if len(set(decisiones)) == 1:
        decision_final = decisiones[0]
    else:
        decision_final = "revisión manual"

    producer.send("decision_final", {"decision": decision_final})

    return jsonify({"decision_final": decision_final})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
