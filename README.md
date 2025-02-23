# MISW4202-ArquitecturasAgiles-Grupo018


# Guía de Despliegue en Minikube

Esta guía describe los pasos necesarios para desplegar la aplicación en Minikube, construir las imágenes Docker y probar los endpoints del API Gateway y del microservicio.

## 1. Instalar Minikube

Asegúrate de tener Minikube instalado. Para descargar e instalar Minikube para macOS (ARM64), visita:

[Minikube - Documentación de Inicio](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download)

### 2. Construir las Imágenes Docker
eval $(minikube docker-env)
minikube addons enable ingress

docker build -t api-gateway:latest ./api_gateway
docker build -t broker:latest ./broker
docker build -t ms:latest ./ms


#### 3. Desplegar los Servicios y Deployments en Kubernetes

kubectl apply -f ./api_gateway/api-gateway-ingress.yaml
kubectl apply -f ./broker/broker-service.yaml
kubectl apply -f ./api_gateway/api-gateway-service.yaml
kubectl apply -f ./ms/ms-service.yaml

##### 4. Exponer el API Gateway (Port Forwarding)
sudo minikube tunnel(macos)
curl --resolve "hello-world.example:80:$( minikube ip )" -i http://hello-world.example  (linux)

### 5. Probar el Health Check del API Gateway
curl --location 'http://api.local :8000/health'


#### 6. Enviar un Mensaje al Microservicio de Ubicación
curl --resolve "api.local:80:127.0.0.1" -i http://api.local/health
curl --resolve "api.local:80:127.0.0.1" -i -X POST http://api.local/ubicacion \
  -H "Content-Type: application/json" \
  --data '{"latitud": 12, "longitud": 10}'


#### 7 probar con jmeter o ab
## ab
ab -n 9999 -c 100 http://api.local/ubicacion



## NOTA 
Note:
The network is limited if using the Docker driver on MacOS (Darwin) and the Node IP is not reachable directly. To get ingress to work you’ll need to open a new terminal and run minikube tunnel.
sudo permission is required for it, so provide the password when prompted.