# MISW4202-ArquitecturasAgiles-Grupo018


# Guía de Despliegue en Minikube

Esta guía describe los pasos necesarios para desplegar la aplicación en Minikube, construir las imágenes Docker y probar los endpoints del API Gateway y del microservicio.

---

## 1. Instalar Minikube

Asegúrate de tener Minikube instalado. Para descargar e instalar Minikube para macOS (ARM64), visita:

[Minikube - Documentación de Inicio](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download)

### 2. Construir las Imágenes Docke
# Asegúrate de estar apuntando al daemon de Docker de Minikube:
eval $(minikube docker-env)

docker build -t api-gateway:latest ./api_gateway
docker build -t broker:latest ./broker
docker build -t ms:latest ./ms

#### 3. Desplegar los Servicios y Deployments en Kubernetes

kubectl apply -f ./broker/broker-service.yaml
kubectl apply -f ./api_gateway/api-gateway-service.yaml
kubectl apply -f ./ms/ms-service.yaml


##### 4. Exponer el API Gateway (Port Forwarding)
kubectl port-forward svc/api-gateway 8000:8000

### 5. Probar el Health Check del API Gateway
curl --location 'http://localhost:8000/health'


##### 6. Enviar un Mensaje al Microservicio de Ubicación
curl --location 'http://localhost:8000/ubicacion' \
--header 'Content-Type: application/json' \
--data '{
    "latitud": 12,
    "longitud": 10
}'
