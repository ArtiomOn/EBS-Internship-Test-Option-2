FROM python:3.8
# Install missing libs
RUN apt-get update && apt-get install -y apt-transport-https
RUN apt-get install -y curl wget git
RUN apt-get -y autoremove

# Creating Application Source Code Directory
RUN mkdir -p /usr/apps

# Setting Home Directory for containers
WORKDIR /usr/apps

# Installing python dependencies
COPY . /usr/apps
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

