build_image:
	docker build --file Dockerfile -t bang6:5000/dnsmasq:latest .
	docker push bang6:5000/dnsmasq:latest

local_run_10.1: build_image
	docker run --rm -i --name=dnsmasq_10_1 --net=host --cap-add NET_BROADCAST --privileged -v /opt/dnsmasq/10.1:/opt/dnsmasq --entrypoint=dnsmasq bang6:5000/dnsmasq:latest --conf-file=/opt/dnsmasq/dnsmasq.conf -d --log-queries

local_run_10.2: build_image
	docker run --rm -i --name=dnsmasq_10_2 --net=host --cap-add NET_BROADCAST --privileged -v /opt/dnsmasq/10.2:/opt/dnsmasq --entrypoint=dnsmasq bang6:5000/dnsmasq:latest --conf-file=/opt/dnsmasq/dnsmasq.conf -d --log-queries

shell: build_image
	docker run --rm -it --name=dnsmasq --net=host --cap-add NET_ADMIN --cap-add SYS_PTRACE -v /opt/dnsmasq/10.1:/opt/dnsmasq --entrypoint /bin/bash bang6:5000/dnsmasq:latest


test_dhcp:
	/usr/lib/nagios/plugins/check_dhcp -v -s 10.1.0.1 -i enp1s0 || true
	/usr/lib/nagios/plugins/check_dhcp -v -s 10.2.0.1 -i ens5 || true

redeploy: build_image
	sudo /my/proj/ansible/playbook -l bang -t dnsmasq
	docker kill dnsmasq_10_1 dnsmasq_10_2
