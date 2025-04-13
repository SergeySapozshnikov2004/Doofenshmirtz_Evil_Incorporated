all:
	docker compose up -d
	sleep 1
	docker-compose logs

clean:
	docker-compose down

logs:
	docker-compose logs planning_system
	docker-compose logs calculating_path
	docker-compose logs autopilot

	
check:
	docker-compose ps -a