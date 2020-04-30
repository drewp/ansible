build_image:
	docker build --network=host -t bang5:5000/telegraf_x86:latest .
	docker push bang5:5000/telegraf_x86:latest

build_image_pi:
	docker build --file Dockerfile.pi --network=host -t bang5:5000/telegraf_pi:latest .
	docker push bang5:5000/telegraf_pi:latest


shell:
	docker run --rm -it --net=host bang5:5000/telegraf_x86:latest  /bin/bash

