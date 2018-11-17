build_image:
	docker build --network=host -t bang6:5000/influxdb_x86:latest .
	docker push bang6:5000/influxdb_x86:latest

shell:
	docker run --rm -it --cap-add SYS_PTRACE --net=host bang6:5000/influxdb_x86:latest  /bin/sh

local_run:
	docker run --rm -it -p 9060:9060 -v /opt/influxdb:/opt/influxdb bang6:5000/influxdb_x86:latest
