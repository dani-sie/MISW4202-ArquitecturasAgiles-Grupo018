from flask import Flask, request, jsonify

app = Flask(__name__)

# Almacenamos tuplas (tipo, mensaje)
eventos = []
intentos_fallidos_por_ip = {}

FALLIDOS_UMBRAL = 3  # número de intentos para marcar IP como "bloqueada"

@app.route('/monitor/evento', methods=['POST'])
def registrar_evento():
    data = request.json or {}
    mensaje = data.get('mensaje', 'Sin mensaje')
    tipo = data.get('tipo', 'info')  # "info", "intrusion", "alert", etc.
    eventos.append((tipo, mensaje))

    # Si es intrusión, acumulamos conteo de fallos por IP
    if tipo == "intrusion":
        ip_str = extraer_ip(mensaje)
        if ip_str:
            intentos_fallidos_por_ip[ip_str] = intentos_fallidos_por_ip.get(ip_str, 0) + 1
            count = intentos_fallidos_por_ip[ip_str]
            if count >= FALLIDOS_UMBRAL:
                alerta_msg = f"La IP {ip_str} ha sido bloqueada tras {count} intentos fallidos."
                eventos.append(("alert", alerta_msg))

    return jsonify({'status': 'OK', 'mensaje': mensaje})

@app.route('/monitor/listar', methods=['GET'])
def listar_eventos():
    """
    Devuelve todos los eventos registrados.
    """
    return jsonify({
        'eventos': [
            {'tipo': t, 'mensaje': m}
            for (t, m) in eventos
        ]
    })

def extraer_ip(mensaje):
    """
    Busca 'IP: x.x.x.x' en el mensaje.
    """
    if 'IP:' in mensaje:
        return mensaje.split("IP:")[1].strip()
    return None

if __name__ == '__main__':
    app.run(port=5004, debug=True, host='0.0.0.0')