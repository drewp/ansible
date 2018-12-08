build_image:
	docker build --network=host -t bang6:5000/assistant_x86:latest .
	docker push bang6:5000/assistant_x86:latest

build_image_pi:
	docker build --file Dockerfile.pi --network=host -t bang6:5000/assistant_pi:latest .
	docker push bang6:5000/assistant_pi:latest

local_run: build_image
	docker run --rm -t --net=host -v /tmp/pulseaudio:/tmp/pulseaudio bang6:5000/assistant_x86:latest
shell:
	docker run --rm -it --net=host --cap-add SYS_PTRACE -v /tmp/pulseaudio:/tmp/pulseaudio  bang6:5000/assistant_x86:latest  /bin/bash

# "python3" "-m" "hotword" "--device-model-id" "voice-desktop" "--project-id" "bigasterisk-910" "--device-config" "/opt/assistant.conf" "--credentials" "/opt/credentials.json"

