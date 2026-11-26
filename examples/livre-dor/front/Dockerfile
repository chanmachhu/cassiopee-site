# Build context: examples/livre-dor
FROM nginxinc/nginx-unprivileged:stable-alpine
# Only ${API_URL} is substituted in the template; nginx's own $variables stay.
ENV API_URL=http://livre-dor-api NGINX_ENVSUBST_FILTER=API_URL
COPY front/nginx/security-headers.inc /etc/nginx/security-headers.inc
COPY front/nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY front/index.html front/app.js front/style.css /usr/share/nginx/html/
EXPOSE 8080
