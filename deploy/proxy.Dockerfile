FROM node:22.22.0-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

FROM nginx:1.30.0-alpine
COPY deploy/nginx.conf /etc/nginx/nginx.conf
COPY --from=frontend /frontend/dist /usr/share/nginx/html
