build_image:
	docker build --file docker-ntop/Dockerfile.ntopng -t bang6:5000/ntopng:latest .
	docker push bang6:5000/ntopng:latest

local_run: build_image
	docker run --rm -it -p 3000:3000 -v /opt/ntopng:/opt/ntopng -v /opt/ntopng/local:/usr/share/ntopng/scripts/lua/local --net=host bang6:5000/ntopng:latest --community --dns-mode 1 -i any --http-port 3000 --local-networks 10.1.0.0/16,10.2.0.0/16,10.3.0.0/16,192.168.1.1/24,172.17.0.0/16,127.0.0.0/24 --disable-login 1 --sticky-hosts local --http-prefix /ntop --data-dir /opt/ntopng --redis localhost:6379@ntop --user ntopnghost

shell: build_image
	docker run --rm -it -p 3000:3000 --net=host --entrypoint /bin/bash bang6:5000/ntopng:latest 
