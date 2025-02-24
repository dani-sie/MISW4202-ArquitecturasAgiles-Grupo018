from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

OPTIMIZADORES = [
    "http://optimizador1:5001",
    "http://optimizador2:5001",
    "http://optimizador3:5001"
]


shadow_cache = {}

@app.route("/orden_compra", methods=["POST"])
def procesar_orden():
    data = request.json
    respuestas = {}

   
    for optimizador in OPTIMIZADORES:
        try:
            r = requests.post(f"{optimizador}/validar_orden", json=data, timeout=5)
            resp = r.json()
            respuestas[optimizador] = resp
           
            shadow_cache[optimizador] = resp
        except Exception as e:
            print(f"Error al llamar a {optimizador}: {e}")
           
            if optimizador in shadow_cache:
                respuestas[optimizador] = shadow_cache[optimizador]
            else:
                respuestas[optimizador] = None


    validas = {k: v for k, v in respuestas.items() if v is not None}

    if len(validas) < 2:
        return jsonify({"error": "No se obtuvieron al menos dos respuestas válidas."}), 503

    
    votos = {}
    for resp in validas.values():
        clave = json.dumps(resp, sort_keys=True)
        votos[clave] = votos.get(clave, 0) + 1

   
    decision_final = None
    for clave, count in votos.items():
        if count >= 2:
            decision_final = json.loads(clave)
            break

    if decision_final is None:
        decision_final = "revisión manual"

    
    for opt, resp in respuestas.items():
        if resp is not None:
            if json.dumps(resp, sort_keys=True) != json.dumps(decision_final, sort_keys=True):
                print(f"El optimizador {opt} se considera defectuoso y se retira temporalmente de la cache.")
              
                if opt in shadow_cache:
                    del shadow_cache[opt]

    
    return jsonify({
        "decision_final": decision_final,
        "detalles": respuestas
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
