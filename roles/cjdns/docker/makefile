build_image:
	docker build --network=host -t bang6:5000/cjdns_x86:latest .
	docker push bang6:5000/cjdns_x86:latest

build_image_pi:
	docker build --file Dockerfile.pi --network=host -t bang6:5000/cjdns_pi:latest .
	docker push bang6:5000/cjdns_pi:latest


shell:
	docker run --rm -it --net=host bang6:5000/cjdns_x86:latest  /bin/sh

