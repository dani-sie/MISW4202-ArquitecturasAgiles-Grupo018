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
