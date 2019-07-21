build_image:
	docker build --file Dockerfile -t bang6:5000/traffic_shaping_to_influx:latest .
	docker push bang6:5000/traffic_shaping_to_influx:latest

local_run: build_image
	docker run --rm -i --name=traffic_shaping_to_influx --net=host bang6:5000/traffic_shaping_to_influx:latest

shell: build_image
	docker run --rm -it --name=traffic_shaping_to_influx --net=host --cap-add SYS_PTRACE --entrypoint /bin/bash bang6:5000/traffic_shaping_to_influx:latest

