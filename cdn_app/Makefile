
##############################################
#
#
#
#               >>>>>>>
#             /         
#            /
########### /  
# Product # 
########### \ 
#         
#
#
#
#
##############################################
cleanup: delete-bookinfo
.PHONY: build_cache_backend push_cache_backend run_cache_backend_bash run_cache_backend_local build_cache_frontend push_cache_frontend run_cache_frontend_bash run_cache_frontend_local

build_cache_backend:
	docker build -f cache_backend/Dockerfile -t eyalday/cache_backend:latest .

push_cache_backend:
	docker push eyalday/cache_backend:latest

run_cache_backend_bash:
	docker run -it eyalday/cache_backend  bash

run_cache_backend_local:
	docker run -p 8081:8081 -v/Users/eydayan/Documents/idc/Networking/Final/kube-multi-cluster-managment/cdn_app/cache_backend:/app eyalday/cache_backend

build_cache_frontend:
	docker build -f cache_front/Dockerfile -t eyalday/cache_frontend:latest .

push_cache_frontend:
	docker push eyalday/cache_frontend:latest

run_cache_frontend_bash:
	docker run -it eyalday/cache_frontend  bash

run_cache_frontend_local:
	docker run -p 8082:8082 -v/Users/eydayan/Documents/idc/Networking/Final/kube-multi-cluster-managment/cdn_app/cache_front:/app eyalday/cache_frontend
	

build: build_cache_backend build_cache_frontend
	echo push

push: push_cache_backend push_cache_frontend
	echo push

all: build
	make push
