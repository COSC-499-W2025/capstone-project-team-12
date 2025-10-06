FROM nginx:1.29.2

COPY *.html /usr/share/nginx/html
COPY *.css /usr/share/nginx/html
COPY *.js /usr/share/nginx/html
