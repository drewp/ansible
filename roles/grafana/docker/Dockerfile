FROM bang6:5000/base_x86

WORKDIR /opt

RUN apt-get install -y libfontconfig
RUN wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana_5.4.2_amd64.deb && dpkg -i grafana_5.4.2_amd64.deb && rm grafana_5.4.2_amd64.deb

RUN wget -O diagram.zip https://grafana.com/api/plugins/jdbranham-diagram-panel/versions/1.4.3/download
RUN wget -O panel.zip https://grafana.com/api/plugins/natel-discrete-panel/versions/0.0.8-pre/download
RUN apt-get install -y unzip
RUN mkdir -p /opt/plugins; cd /opt/plugins; unzip /opt/diagram.zip; rm /opt/diagram.zip
RUN mkdir -p /opt/plugins; cd /opt/plugins; unzip /opt/panel.zip; rm /opt/panel.zip
# may need to rm 'author' line from jdbranham-grafana-diagram-d148296/dist/plugin.json so it loads right.


RUN wget -O carpet.zip https://grafana.com/api/plugins/petrslavotinek-carpetplot-panel/versions/0.1.1/download
RUN mkdir -p /opt/plugins; cd /opt/plugins; unzip /opt/carpet.zip; rm /opt/carpet.zip

COPY grafana.ini /etc/grafana/grafana.ini

EXPOSE 9067

CMD [ "/usr/sbin/grafana-server", "--homepath=/usr/share/grafana", "--config=/etc/grafana/grafana.ini" ]
