build.ui:
	cd ./UI/xmigrate-ui && yarn && yarn build 
	
build.docker:
	docker build xmigrate .

dep-python:
	python3 -m pip install -r requirements.txt

dev-python:
	python3 -m uvicorn app:app --reload

dev-npm:
	cd UI/xmigrate-ui && npm install && npm start