
FROM python:3.6-alpine

# - build-base for compiler etc.
# - postgresql-dev for postgres support
# - libxslt for lxml package
# - libffi for argon2 hashing support
# - nodejs for building js
# - npm for installing yarn (easiest to install via npm)
# - libnotify because some npm packages we use requires it
# - git and openssh-client because we have npm github deps
RUN apk update && apk add build-base postgresql-dev libffi-dev libxslt-dev nodejs npm libnotify git openssh-client sassc gettext

ENV APP_ROOT_PATH /usr/src/app
RUN mkdir -p $APP_ROOT_PATH

WORKDIR $APP_ROOT_PATH


# Setup SSH:
# - Create config directory
# - Setup github access token for https git urls. Used in package.json for things like ievv_js, ...
# - Add github.com to ssh known hosts. Required for github URLs in package.json.
#RUN mkdir ~/.ssh/
#RUN ssh-keyscan github.com > ~/.ssh/known_hosts


# Install python deps
COPY . .
#COPY requirements.txt requirements.txt
#COPY requirements requirements
RUN pip install -r requirements/development.txt

# Install yarn
RUN npm install --global yarn

# Specify the port we expose, and how to signal stopserver
EXPOSE 8000
STOPSIGNAL SIGINT

# We use wait-for https://github.com/Eficode/wait-for to wait for
# postgres to really be up before starting django dev server.
# See: https://docs.docker.com/compose/startup-order/ for more info.
CMD [ "/bin/sh", "./docker/test/run_test.sh" ]
