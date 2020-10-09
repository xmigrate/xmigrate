build.ui:
	cd ./UI/xmigrate-ui && yarn && yarn build 
	
build.docker:
	docker build xmigrate .
