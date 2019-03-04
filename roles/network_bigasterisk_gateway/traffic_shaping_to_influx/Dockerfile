FROM bang6:5000/base_x86

WORKDIR /opt
RUN apt install -y iproute2
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY *.py ./

CMD [ "python3", "traffic_shaping_to_influx.py"]
