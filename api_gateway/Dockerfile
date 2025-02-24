# Usa la imagen oficial de Node.js (LTS)
FROM node:20-alpine

# Establece el directorio de trabajo
WORKDIR /app

# Configura npm para mejorar estabilidad en la instalación de paquetes
RUN npm config set registry https://registry.npmjs.org/ \
    && npm config set fetch-retry-mintimeout 20000 \
    && npm config set fetch-retry-maxtimeout 120000

# Copia solo los archivos de dependencias para optimizar caché
COPY package*.json ./

# Instala NestJS CLI globalmente y las dependencias de la aplicación
RUN npm install -g @nestjs/cli --legacy-peer-deps --no-fund --no-audit \
    && npm ci --no-fund --no-audit

# Copia el resto del código de la aplicación
COPY . .

# Compila la aplicación y verifica que dist/main.js exista
RUN npx nest build \
    && if [ ! -f "dist/main.js" ]; then echo "Error: dist/main.js no encontrado" && exit 1; fi

# Expone el puerto de la API Gateway
EXPOSE 8000

# Comando de inicio
CMD ["node", "dist/main.js"]
