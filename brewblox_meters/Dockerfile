FROM python:3.7-slim

COPY ads1115.py /app/ads1115.py
COPY Meter.py /app/Meter.py
COPY VolumeSensor.py /app/VolumeSensor.py
COPY script.py /app/script.py

# install the required packages
RUN apt-get update && apt-get -y install build-essential
RUN pip3 install paho.mqtt
RUN pip3 install adafruit-gpio

CMD ["python3", "-u", "/app/script.py"]
