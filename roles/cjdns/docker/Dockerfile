FROM bang6:5000/base_x86

RUN git clone https://github.com/cjdelisle/cjdns.git /opt/cjdns

WORKDIR /opt/cjdns

RUN git checkout 902365945f5497a1c30337bd92447fae1fbbc10e
RUN ./do

COPY ./run /opt/cjdns/run

# if we were squashing layers, this would reduce the size a lot
#RUN apt-get remove -y --autoremove libpython2.7-dev git gcc-7 g++-7 cpp-7 libc6-dev nodejs-dev libx11-dev libssl-dev python3.6 python-numpy nodejs libicu60; rm -r /opt/cjdns/build_linux /opt/cjdns/node_build /usr/local/lib/python3.6 /usr/local/lib/python2.7 /root/.cache
