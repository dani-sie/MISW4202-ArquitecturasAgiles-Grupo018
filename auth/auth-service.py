from flask import Flask, request, jsonify
import jwt
import time
import requests
import hmac
import hashlib
import json

app = Flask(__name__)
# Clave de ejemplo para firmar los JWT
app.config['SECRET_KEY'] = 'MI_SECRETO_DE_EJEMPLO'
# Clave HMAC compartida (usada si queremos validar integridad desde el Gateway)
app.config['HMAC_SECRET'] = 'CLAVE_COMPARTIDA_HMAC'

# Ajusta al nombre y puerto del contenedor monitor en Docker Compose
MONITOR_URL = 'http://monitor:5004'

def registrar_evento_monitor(mensaje, tipo="info"):
    """
    Envía un evento al monitor con un tipo (info, intrusion, etc.).
    """
    try:
        requests.post(f"{MONITOR_URL}/monitor/evento", json={
            'mensaje': mensaje,
            'tipo': tipo
        })
    except Exception as e:
        print(f"[Auth] Error registrando evento en Monitor: {e}")

def verificar_hmac(json_data, firma_recibida):
    """
    Recalcula HMAC y compara con la firma recibida.
    (Sólo si forzamos que Auth compruebe que la llamada vino del Gateway legítimo)
    """
    body_str = json.dumps(json_data, sort_keys=True)
    firma_local = hmac.new(
        key=app.config['HMAC_SECRET'].encode('utf-8'),
        msg=body_str.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(firma_local, firma_recibida)

@app.route('/auth/login', methods=['POST'])
def login():
    """
    Simula autenticación de usuario contra un directorio (AD, Kerberos, etc.).
    """
    # (Opcional) Validar HMAC si queremos asegurar que SOLO el Gateway llame a /auth/login
    # signature = request.headers.get('X-Signature')
    # data = request.json or {}
    # if not signature or not verificar_hmac(data, signature):
    #     return jsonify({'error': 'Integridad de mensaje no válida'}), 403

    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    client_ip = request.remote_addr

    # Simulación de credenciales correctas
    if username == 'vendedor' and password == '1234':
        role = 'Vendedor'
    elif username == 'admin' and password == '4321':
        role = 'Administrador'
    else:
        # Registrar evento de intrusión en monitor
        registrar_evento_monitor(
            f"Login fallido para usuario: {username} (IP: {client_ip})",
            tipo="intrusion"
        )
        return jsonify({'error': 'Credenciales inválidas'}), 401

    # Generar JWT con rol de usuario y un tiempo de expiración
    payload = {
        'sub': username,
        'role': role,
        'exp': time.time() + 3600  # expira en 1 hora
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    # Registrar un evento "info" de login exitoso
    registrar_evento_monitor(
        f"Usuario {username} autenticado con rol {role} (IP: {client_ip})",
        tipo="info"
    )

    return jsonify({'access_token': token})

if __name__ == '__main__':
    # host='0.0.0.0' para que escuche dentro del contenedor Docker
    app.run(port=5001, debug=True, host='0.0.0.0')