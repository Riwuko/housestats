FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt 
COPY . /code/
ENV FLASK_APP=app/app.py
