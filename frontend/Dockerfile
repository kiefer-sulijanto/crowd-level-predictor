FROM node:20-alpine

WORKDIR /app

# Install dependencies first for caching layer
COPY package*.json ./
RUN npm install

# Copy application files
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run Vite dev server, allowing external host connections
CMD ["npm", "run", "dev", "--", "--host"]
