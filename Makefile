SHELL := bash

MODULES := monitor \
			com-mobile \
			profile-client \
			manage-drive \
			bank-pay \
			verify \
			auth \
			receiver-car \
			control-drive \
			sender-car \
			payment-system \
			cars \
			mobile-client \


SLEEP_TIME := 10

dev_install:
	python3 -m venv .venv
	.venv/bin/python3 -m pip install -U pip
	.venv/bin/pip install -r requirements.txt

remove_kafka:
	if docker stop zookeeper broker; then \
		docker rm zookeeper broker; \
	fi
all:
	make remove_kafka
	docker compose down
	docker compose up --build -d
	sleep ${SLEEP_TIME}

	for MODULE in ${MODULES}; do \
		echo Creating $${MODULE} topic; \
		docker exec broker \
			kafka-topics --create --if-not-exists \
			--topic $${MODULE} \
			--bootstrap-server localhost:9092 \
			--replication-factor 1 \
			--partitions 1; \
	done

logs:
	docker compose logs -f --tail 100
	
test:
	make all
	sleep ${SLEEP_TIME}
	python3 -m pytest tests/e2e-test/test_base_scheme.py
	make clean

test_security:
	python3 tests/test_policies.py

clean:
	docker compose down 
	for MODULE in ${MODULES}; do \
		docker rmi $${MODULE};  \
	done

broker_logs:
	docker compose logs broker_plan
	docker compose logs broker_calc
	# docker compose logs broker_auto

plan_logs:
	docker compose logs communicator
	docker compose logs encryption_plan
	docker compose logs communication_module_plan
	docker compose logs monitor_plan

calc_logs:
	docker compose logs encryption_calc
	docker compose logs algorithm_calculating_path
	docker compose logs communication_module_calc
	docker compose logs gps_glonass
	docker compose logs inertial_reference_frame
	docker compose logs monitor_calc

do:
	docker compose down
	docker compose up --build -d
	docker compose logs -f
logs:
	docker compose logs -f

curl:
	curl -X POST -H "Content-Type: application/json" -d '{"source": "planning","deliver_to":"encryption_plan","operation":"get_coord","coordinates": "12.34, 56.78"}' http://0.0.0.0:6064/task

ip: 
	docker inspect communicator | grep IPAddress

down:
	docker compose down