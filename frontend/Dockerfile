FROM node:20-alpine

WORKDIR /app

# Copia dependências
COPY package*.json ./

# Instala (mesmo que já tenha node_modules local, garante a integridade no container)
RUN npm install

# Copia o código
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]