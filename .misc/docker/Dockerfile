FROM python:3.9.6

LABEL maintainer="ozetteam@gmail.com"
LABEL title="core-server"
LABEL version="1.0"

# Install system deps
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y default-libmysqlclient-dev
RUN apt-get install -y default-mysql-client
RUN apt-get install -y python3-mysqldb
ENV PYTHONBUFFERED 1

# Install server deps 
RUN pip install --upgrade setuptools
RUN pip install --upgrade pip-tools
RUN pip install mysqlclient
RUN pip install django-mysql

# Install django deps
ADD ./.misc/requirements/dev.txt /tmp/requirements.txt
RUN pip-sync /tmp/requirements.txt
RUN rm /tmp/requirements.txt


# Init project
COPY . /app
RUN cp /app/.misc/docker/gunicorn.py /conf

WORKDIR /app

# Static
RUN mkdir static && \
    DJANGO_SETTINGS_MODULE=ozet.settings.live python manage.py collectstatic --noinput

# Migration
RUN python manage.py migrate

EXPOSE 8080

CMD gunicorn ozet.asgi:application -b :8080 -k uvicorn.workers.UvicornWorker
