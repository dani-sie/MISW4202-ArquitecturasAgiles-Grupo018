from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)
app.config['HMAC_SECRET'] = 'CLAVE_COMPARTIDA_HMAC'

cache = {}

def verificar_hmac(json_data, firma_recibida):
    body_str = json.dumps(json_data, sort_keys=True)
    firma_local = hmac.new(
        key=app.config['HMAC_SECRET'].encode('utf-8'),
        msg=body_str.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(firma_local, firma_recibida)

@app.route('/cache/leer', methods=['GET'])
def leer_cache():
    """
    Lectura sin verificación de firma (porque GET no suele llevar body).
    En un entorno más estricto, podrías usar POST o exigir params firmados.
    """
    key = request.args.get('key')
    if key in cache:
        return jsonify({'key': key, 'value': cache[key]})
    else:
        return jsonify({'error': 'Clave no encontrada'}), 404

@app.route('/cache/escribir', methods=['POST'])
def escribir_cache():
    signature = request.headers.get('X-Signature')
    req_data = request.json or {}

    # Verificamos la firma
    if not signature or not verificar_hmac(req_data, signature):
        return jsonify({'error': 'Integridad de mensaje no válida'}), 403

    key = req_data.get('key')
    value = req_data.get('value')
    cache[key] = value
    return jsonify({'status': 'OK', 'key': key, 'value': value})

if __name__ == '__main__':
    app.run(port=5005, debug=True, host='0.0.0.0')