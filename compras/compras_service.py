from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import json

app = Flask(__name__)
app.config['HMAC_SECRET'] = 'CLAVE_COMPARTIDA_HMAC'

CACHE_URL = 'http://cache:5005'

def verificar_hmac(json_data, firma_recibida):
    body_str = json.dumps(json_data, sort_keys=True)
    firma_local = hmac.new(
        key=app.config['HMAC_SECRET'].encode('utf-8'),
        msg=body_str.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(firma_local, firma_recibida)

def generar_hmac(json_data, secret_key):
    body_str = json.dumps(json_data, sort_keys=True)
    return hmac.new(
        key=secret_key.encode('utf-8'),
        msg=body_str.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

@app.route('/compras/optimizar', methods=['POST'])
def optimizar_compras():
    # Verificamos la firma HMAC que viene del Gateway
    signature = request.headers.get('X-Signature')
    req_data = request.json or {}

    if not signature or not verificar_hmac(req_data, signature):
        return jsonify({'error': 'Integridad de mensaje no válida'}), 403

    producto = req_data.get('producto', 'desconocido')
    cantidad = req_data.get('cantidad', 1)

    # Intentamos leer de la caché
    cache_key = f"optimizacion_{producto}_{cantidad}"
    resp = requests.get(f'{CACHE_URL}/cache/leer', params={'key': cache_key})
    if resp.status_code == 200:
        # Encontrado en caché
        cached_data = resp.json()
        return jsonify({
            'status': 'from_cache',
            'resultado': cached_data['value']
        })

    # "Cálculo" de optimización (simulado)
    resultado_optimizado = {
        'producto': producto,
        'cantidad': cantidad,
        'precio_unitario': 10.0,
        'descuento': 5.0,
        'comentario': 'Optimización de ejemplo'
    }

    # Guardar en la caché
    cache_body = {'key': cache_key, 'value': resultado_optimizado}
    cache_signature = generar_hmac(cache_body, app.config['HMAC_SECRET'])
    requests.post(
        f'{CACHE_URL}/cache/escribir',
        json=cache_body,
        headers={'X-Signature': cache_signature}
    )

    return jsonify({
        'status': 'ok',
        'resultado': resultado_optimizado
    })

if __name__ == '__main__':
    app.run(port=5003, debug=True, host='0.0.0.0')

