FROM bang6:5000/base_x86

WORKDIR /opt

RUN wget https://dl.influxdata.com/influxdb/releases/influxdb_1.7.6_amd64.deb && dpkg -i influxdb_1.7.6_amd64.deb && rm influxdb_1.7.6_amd64.deb
COPY influxdb.conf start_influx ./
RUN chmod 755 start_influx

EXPOSE 9060

CMD [ "./start_influx" ]
