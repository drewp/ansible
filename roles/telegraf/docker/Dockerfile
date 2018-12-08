FROM bang6:5000/base_x86

WORKDIR /opt/

RUN wget https://dl.influxdata.com/telegraf/releases/telegraf_1.8.2-1_amd64.deb
RUN dpkg -i telegraf_1.8.2-1_amd64.deb
RUN apt-get install -y lm-sensors iputils-ping

