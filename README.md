# Ejecutando el proyecto con Docker Compose

Este proyecto utiliza Docker Compose para facilitar la configuración y ejecución de los servicios necesarios.

## Requisitos

* Docker y Docker Compose instalados.

## Pasos para ejecutar

1.  **Clonar el repositorio (si aún no lo has hecho):**

2.  **Ejecutar los contenedores:**

    ```bash
    docker-compose up -d
    ```

    * El comando `docker-compose up` inicia los contenedores definidos en `docker-compose.yml`.
    * La opción `-d` los ejecuta en modo "detached" (en segundo plano).

3.  **Verificar los contenedores:**

    ```bash
    docker-compose ps
    ```

    * Este comando muestra el estado de los contenedores en ejecución.

## Comandos útiles adicionales

* **Detener los contenedores:**

    ```bash
    docker-compose down
    ```

* **Ver los registros de un contenedor:**

    ```bash
    docker-compose logs <nombre_del_contenedor>
    ```

    * Reemplaza `<nombre_del_contenedor>` con el nombre del servicio que deseas inspeccionar.

* **Reconstruir las imágenes (si hay cambios en los Dockerfiles):**

    ```bash
    docker-compose up -d --build
    ```
* **Ejecutar comandos dentro de un contenedor:**

    ```bash
    docker-compose exec <nombre_del_contenedor> <comando>
    ```

## Consideraciones

* Asegúrate de que el archivo `docker-compose.yml` esté configurado correctamente para tu entorno.
* Si realizas cambios en la configuración de Docker Compose, es posible que necesites reconstruir las imágenes o reiniciar los contenedores.



## Test Scenarios

### Test Scenarios and Steps
### 1. Successful Authentication and Authorization
## Objective:
Ensure that a user with valid credentials can authenticate, obtain a valid JWT, and use it to access the optimization endpoint.

### Steps:

Obtain a Valid JWT via the API Gateway

Execute:
```
curl -X POST -H "Content-Type: application/json" \
     -d '{"username": "vendedor", "password": "1234"}' \
     http://localhost:5002/gateway/login
```
### Expected Outcome:
A JSON response with an access_token, for example:

```
{"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
```

In your shell (bash):

```
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Use the valid token to send a request:

```
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"producto": "lapices", "cantidad": 10}' \
     http://localhost:5002/gateway/optimizar
```
### Expected Outcome:

### 1. The API Gateway validates the JWT and signs the request with a correct HMAC.

The Compras service processes the request (or returns a cached result) and responds with the optimization details.

A successful access event is logged in the Monitor service.
### 2. Authorization Failure Test
Verify that a user with an unauthorized role is blocked from accessing the optimization endpoint.


Generate a JWT with an Unauthorized Role

Manually generate a token with a role that is not allowed (e.g., "Cliente"):

```
python -c "import jwt, time; print(jwt.encode({'sub': 'cliente', 'role': 'Cliente', 'exp': time.time()+3600}, 'MI_SECRETO_DE_EJEMPLO', algorithm='HS256'))"
```

Attempt to Access the Optimization Endpoint with the Unauthorized Token

Replace <UNAUTHORIZED_TOKEN> with your generated token:

```
curl -X POST -H "Content-Type: application/json" \
     -H "Authorization: Bearer <UNAUTHORIZED_TOKEN>" \
     -d '{"producto": "lapices", "cantidad": 10}' \
     http://localhost:5002/gateway/optimizar
```
#### Expected Outcome:
The API Gateway should detect that the role "Cliente" is unauthorized and return an error like:

```
{"error": "Rol 'Cliente' no tiene permisos para esta operación"}
with an HTTP status of 403 Forbidden.
```
#### 3. Message Integrity (HMAC Failure) Test
Ensure that if the HMAC signature is tampered with, the Compras service rejects the request.

You can simulate this with two methods:



#### Intercept the Request via mitmweb

Open mitmweb in your browser at (for example) http://localhost:8081/?token=MiClave123.
Intercept the outgoing request from the API Gateway to the Compras service.
```
Modify the JSON body (e.g., change "cantidad": 10 to "cantidad": 20") or alter the X-Signature header.
Release the modified request.
Expected Outcome:
The Compras service detects the tampered HMAC and responds with:
```
```
{"error": "Integridad de mensaje no válida"}
```

### 4. Intrusion Detection (Failed Authentication) Test
Confirm that repeated failed login attempts trigger intrusion detection and logging by the Monitor service.

#### Steps:

Send Multiple Invalid Login Attempts

Execute the following command several times (e.g., 3 attempts):

```
curl -X POST -H "Content-Type: application/json" \
     -d '{"username": "vendedor", "password": "wrongpassword"}' \
     http://localhost:5002/gateway/login
```

### Expected Outcome:

Each attempt should return an error like:

```
{"error": "Credenciales inválidas"}
```
The Monitor service should log an "intrusion" event for each failed attempt.

Once the threshold is reached (e.g., 3 failed attempts), an alert event is generated, such as:

```
"La IP <your_ip> ha sido bloqueada tras 3 intentos fallidos."
Verify the Monitor Logs
```
If the Monitor service is not exposed externally, you can check its logs by running:

```
docker exec -it monitor curl http://localhost:5004/monitor/listar
Look for intrusion and alert events in the output.
```
### Summary
### Authentication Test:
Obtain a valid JWT via the API Gateway and verify that the token allows access to the optimization endpoint.

#### Authorization Test:
Use a manually crafted token with an unauthorized role (e.g., "Cliente") to verify that the system returns a 403 error.

### HMAC Integrity Test:
Simulate tampering with the HMAC signature—either by temporarily modifying the API Gateway code or intercepting/modifying the request using mitmweb—to ensure that the Compras service rejects altered messages.

#### Intrusion Detection Test:
Send repeated invalid login attempts and verify that the Monitor service logs these events and triggers an alert after reaching the set threshold.
