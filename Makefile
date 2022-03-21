build.ui:
	cd ./UI/xmigrate-ui && yarn && yarn build 
	
build.docker:
	docker build xmigrate .

dep-python:
	python3 -m pip install -r requirements.txt