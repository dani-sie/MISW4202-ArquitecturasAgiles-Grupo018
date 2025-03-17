from flask import Flask, request, jsonify
import requests
import jwt
import hmac
import hashlib
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MI_SECRETO_DE_EJEMPLO'
app.config['HMAC_SECRET'] = 'CLAVE_COMPARTIDA_HMAC'  # Para firmar peticiones a otros servicios

# Ajusta a los nombres/puertos de tus contenedores
AUTH_URL = 'http://auth:5001'
COMPRAS_URL = 'http://compras:5003'
MONITOR_URL = 'http://monitor:5004'

def registrar_evento_monitor(mensaje, tipo="info"):
    """
    Envía un evento al monitor.
    """
    try:
        requests.post(f'{MONITOR_URL}/monitor/evento', json={
            'mensaje': mensaje,
            'tipo': tipo
        })
    except Exception as e:
        print(f"[Gateway] Error registrando evento en Monitor: {e}")

def verificar_jwt(token):
    """
    Decodifica el token usando SECRET_KEY (mismo en Auth).
    """
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generar_hmac(json_data):
    """
    Genera una firma HMAC del contenido JSON con la clave compartida.
    """
    body_str = json.dumps(json_data, sort_keys=True)
    firma = hmac.new(
        key=app.config['HMAC_SECRET'].encode('utf-8'),
        msg=body_str.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return firma

@app.route('/gateway/login', methods=['POST'])
def login_usuario():
    """
    (Opcional) Endpoint para loguearse a través del Gateway,
    que llama internamente a Auth. Ej: /gateway/login
    """
    req_data = request.json or {}
    signature = generar_hmac(req_data)
    response = requests.post(f'{AUTH_URL}/auth/login',
                             json=req_data,
                             headers={'X-Signature': signature})
    return jsonify(response.json()), response.status_code

@app.route('/gateway/optimizar', methods=['POST'])
def optimizar_compras():
    """
    1. Valida el JWT (autenticación)
    2. Verifica el rol (autorización)
    3. Firma la petición con HMAC
    4. Llama al servicio de Compras
    5. Devuelve la respuesta
    """
    auth_header = request.headers.get('Authorization')
    client_ip = request.remote_addr

    if not auth_header:
        registrar_evento_monitor(
            f"Solicitud SIN token (IP: {client_ip})", 
            tipo="intrusion"
        )
        return jsonify({'error': 'Falta encabezado Authorization'}), 401
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        registrar_evento_monitor(
            f"Token mal formado (IP: {client_ip})",
            tipo="intrusion"
        )
        return jsonify({'error': 'Formato de encabezado Authorization inválido'}), 401
    
    token = parts[1]
    decoded = verificar_jwt(token)
    if not decoded:
        registrar_evento_monitor(
            f"Token inválido o expirado (IP: {client_ip})",
            tipo="intrusion"
        )
        return jsonify({'error': 'Token inválido o expirado'}), 401

    # ---- Autorización por rol (ejemplo) ----
    user_role = decoded.get('role', 'desconocido')
    if user_role not in ['Vendedor', 'Administrador']:
        registrar_evento_monitor(
            f"Rol '{user_role}' no autorizado para optimizar (IP: {client_ip})",
            tipo="intrusion"
        )
        return jsonify({'error': f"Rol '{user_role}' no tiene permisos para esta operación"}), 403
    # ----------------------------------------

    # Evento de acceso legítimo
    username = decoded.get('sub')
    registrar_evento_monitor(
        f"Usuario {username} (rol: {user_role}) solicita optimización, IP: {client_ip}",
        tipo="info"
    )

    req_data = request.json or {}
    # Generar firma HMAC para enviar al servicio de compras
    signature = generar_hmac(req_data)

    response = requests.post(
        f'{COMPRAS_URL}/compras/optimizar',
        json=req_data,
        headers={'X-Signature': signature}
    )

    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(port=5002, debug=True, host='0.0.0.0')