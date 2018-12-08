FROM bang6:5000/base_x86

WORKDIR /opt
RUN apt-get install -y alsa-utils pulseaudio-utils

# remove this update when the base img is newer than 2018-11-10
RUN apt-get update
# this adds an alsa->pulse plugin
RUN apt-get install -y pulseaudio

RUN git clone https://github.com/googlesamples/assistant-sdk-python.git

RUN pip3 install -q --upgrade google-assistant-library \
    && pip3 install -q --upgrade google-auth-oauthlib[tool]

RUN pip3 install -r /opt/assistant-sdk-python/google-assistant-sdk/googlesamples/assistant/library/requirements.txt

COPY credentials.json .
COPY pulse-client.conf /etc/pulse/client.conf

ENV PULSE_SERVER /tmp/pulseaudio

WORKDIR /opt/assistant-sdk-python/google-assistant-sdk/googlesamples/assistant/library
CMD ["python3", "-m", "hotword", "--device-model-id", "voice-desktop", "--project-id", "bigasterisk-910", "--device-config", "/opt/assistant.conf", "--credentials", "/opt/credentials.json"]
