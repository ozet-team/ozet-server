FROM python:3.9.6

LABEL maintainer="ozetteam@gmail.com"
LABEL title="core-server"
LABEL version="1.0"

# Update PIP
RUN pip install --upgrade setuptools
RUN pip install --upgrade pip-tools

# Install django deps
ADD ./.misc/requirements/dev.txt /tmp/requirements.txt
RUN pip-sync /tmp/requirements.txt
RUN rm /tmp/requirements.txt

# Install server deps
RUN pip install pymysql

# Init project
COPY . /app
RUN cp /app/.misc/docker/gunicorn.py /conf

WORKDIR /app

# Migration
RUN DJANGO_SETTINGS_MODULE=ozet.settings.live python manage.py migrate

# Static
# RUN DJANGO_SETTINGS_MODULE=ozet.settings.live python manage.py collectstatic --noinput

EXPOSE 8080

CMD DJANGO_SETTINGS_MODULE=ozet.settings.live gunicorn ozet.asgi:application -b :8080 -k uvicorn.workers.UvicornWorker
