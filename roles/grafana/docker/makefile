build_image:
	docker build --network=host -t bang6:5000/grafana_x86:latest .
	docker push bang6:5000/grafana_x86:latest

shell:
	docker run --rm -it --cap-add SYS_PTRACE --net=host -v /opt/grafana:/opt/grafana bang6:5000/grafana_x86:latest  /bin/bash

local_run:
	docker run --rm -it -p 9067:9067 --net=host -v /opt/grafana:/opt/grafana bang6:5000/grafana_x86:latest
