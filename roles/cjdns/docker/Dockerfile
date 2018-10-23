FROM bang6:5000/base_x86

RUN git clone https://github.com/cjdelisle/cjdns.git /opt/cjdns

WORKDIR /opt/cjdns

RUN git checkout 902365945f5497a1c30337bd92447fae1fbbc10e
RUN ./do

COPY ./run /opt/cjdns/run
