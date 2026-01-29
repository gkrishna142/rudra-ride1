# ---------- BUILD STAGE ----------
FROM node:20-alpine AS build

WORKDIR /app   # 🔥 THIS WAS MISSING

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build


# ---------- NGINX STAGE ----------
FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]