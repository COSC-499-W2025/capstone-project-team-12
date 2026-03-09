# Stage 1: Development build (Supports live reload via Vite dev server)
FROM node:24-alpine AS dev
WORKDIR /app
COPY package.json ./
RUN npm install --no-package-lock
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# Stage 2: Build the React app
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install --no-package-lock
COPY . .
RUN npm run build

# Stage 3: Serve with NGINX
FROM nginx:1.28.2-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]