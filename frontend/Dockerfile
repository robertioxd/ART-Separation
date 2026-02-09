# Frontend Dockerfile (Vite)
FROM node:22-alpine

WORKDIR /app

# Copy package.json and lock file
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build for production (optional, or just dev)
# RUN npm run build

# Expose Vite port
EXPOSE 5173

# Start Vite dev server with host exposure
CMD ["npx", "vite", "--host"]
