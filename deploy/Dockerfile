FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /booking_app_project
RUN /bin/bash -c "apt-get update && apt-get install build-essential libffi-dev libmariadb-dev -y"
COPY requirements.txt /booking_app_project/requirements.txt
RUN pip3 install -r requirements.txt
COPY . /booking_app_project/
