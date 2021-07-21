FROM python:3.8
WORKDIR /web
COPY requirements.txt /web
RUN pip3 install -r /web/requirements.txt
COPY . /web
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000