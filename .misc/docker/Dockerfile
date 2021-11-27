FROM python:3.9.6

LABEL maintainer="ozetteam@gmail.com"
LABEL title="core-server"
LABEL version="1.0"

# Install deps
RUN pip install --upgrade pip-tools
ADD ./.misc/requirements/dev.txt /tmp/requirements.txt
RUN pip-sync /tmp/requirements.txt
RUN rm /tmp/requirements.txt


# Init project
COPY . /app
RUN cp /app/.misc/docker/gunicorn.py /conf

# Static
RUN cd /app && \
    mkdir static && \
    DJANGO_SETTINGS_MODULE=ozet.settings python manage.py collectstatic --noinput

EXPOSE 8080

CMD cd /app && gunicorn ozet.asgi:application -b :8080 -k uvicorn.workers.UvicornWorker
