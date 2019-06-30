FROM nginx:alpine

COPY uwsgi_params /etc/nginx/uwsgi_params
COPY cert/server.crt /etc/nginx/server.crt
COPY cert/server.key /etc/nginx/server.key
RUN chmod 400 /etc/nginx/server.key

COPY default.conf.template /etc/nginx/conf.d/default.conf.template
