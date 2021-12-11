git:
	git add .
	git commit -m "$m"
	git push -u origin main

docker: 
	docker build --tag brewblox-meters brewblox_meters/
	docker run --privileged -d --rm --tty brewblox-meters
