git:
	git add .
	git commit -m "$m"
	git push

# make git m="message"

docker:
	docker build --tag hackrsackr/brewblox-meters brewblox_meters/
	docker run --privileged -d --rm --tty brewblox-meters

	docker push hackrsackr/brewblox-meters:tagname
