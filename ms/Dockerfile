# Usa Node.js 20 (para compatibilidad con api-gateway)
FROM node:20-alpine

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de dependencias primero
COPY package*.json ./

# Instala solo las dependencias necesarias
RUN npm ci --no-fund --no-audit

# Copia el código de la aplicación
COPY . .

# Compila el proyecto (NestJS)
RUN npx nest build && if [ ! -f "dist/main.js" ]; then echo "Error: dist/main.js no encontrado" && exit 1; fi

# Expone el puerto 3000 (debe coincidir con el que usa la aplicación)
EXPOSE 3000

# Comando de inicio
CMD ["node", "dist/main.js"]
