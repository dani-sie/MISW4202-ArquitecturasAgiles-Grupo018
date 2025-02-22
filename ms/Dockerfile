# Use the official Node.js image (LTS)
FROM node:16-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./

# Install dependencies
RUN npm install --only=production

# Copy the rest of the application code
COPY . .

# Build the application (assuming you use TypeScript)
RUN npm run build

# Expose port 3000 for the HTTP server (health check endpoint)
EXPOSE 3000

# Command to run the hybrid application
CMD ["node", "dist/main.js"]
