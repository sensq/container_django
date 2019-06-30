FROM python:3-alpine
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /
RUN apk --no-cache --virtual build-dependencies add \
        linux-headers \
        build-base \
        libffi-dev \
    && apk --no-cache add \
        bash-completion \
    && pip install -r requirements.txt \
    && apk del --purge build-dependencies

EXPOSE 5000

COPY docker-entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

COPY check_admin.py /

ARG DJANGO_PROJECT_NAME
#COPY project/ /${DJANGO_PROJECT_NAME}/
WORKDIR /${DJANGO_PROJECT_NAME}

RUN pip install django-import-export
RUN pip install python-dateutil

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
