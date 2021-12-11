FROM python:3.7-slim

COPY ads1115.py /app/ads1115.py
COPY dual_meters.py /app/dual_meters.py

# install the required packages
RUN apt-get update && apt-get -y install build-essential
RUN pip3 install paho.mqtt
RUN pip3 install adafruit-gpio

CMD ["python3", "-u", "/app/dual_meters.py"]
