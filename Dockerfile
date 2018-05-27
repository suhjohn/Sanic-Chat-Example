FROM        python:3.6.4-slim
MAINTAINER  johnsuh94@gmail.com
ENV         APP_ENV DEV

# apt-get으로 nginx, supervisor, vim 설치
RUN         apt-get -y update
RUN         apt-get -y dist-upgrade
RUN         apt-get -y install build-essential nginx supervisor vim

# Copy and move to project folder
COPY        . /srv/app
WORKDIR     /srv/app

# pip
ENV         LANG C.UTF-8
COPY        requirements.txt /srv/requirements.txt
RUN         pip install -r  /srv/requirements.txt
RUN         pip install gunicorn

## Get Server Settings Ready
# Gunicorn
RUN         mkdir -p /var/log/gunicorn/app

# Nginx
RUN         rm -rf /etc/nginx/sites-enabled/*
COPY        .config/dev/nginx/nginx.conf /etc/nginx/nginx.conf
COPY        .config/dev/nginx/app.conf /etc/nginx/sites-available/
RUN         ln -sf /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/app.conf


# Supervisor
COPY	    .config/dev/supervisord.conf /etc/supervisor/conf.d/

# Stop Nginx, Run supervisor
EXPOSE      80
CMD         pkill gunicorn; pkill nginx
CMD         supervisord -n
