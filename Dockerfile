FROM node AS stage

WORKDIR /app
COPY ./UI .
WORKDIR /app/xmigrate-ui
RUN yarn && yarn build

FROM nginx:1.16-alpine
# RUN apt install sshpass, qemu-utils
RUN wget https://aka.ms/downloadazcopy-v10-linux && \
    tar -zxf ./downloadazcopy-v10-linux && \
    mv ./azcopy_linux_amd64_10.6.0/azcopy /usr/bin  

COPY --from=stage /app/xmigrate-ui/build /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf

WORKDIR /app
RUN mkdir -p ./logs/ansible/ && touch ./logs/ansible/log.txt && touch ./logs/ansible/migration_log.txt

RUN apk update && \
    apk add qemu && \
    apk add sshpass && \
    apk add make && \
    apk add --no-cache --virtual .build-deps g++ python3-dev libffi-dev openssl-dev && \
    pip3 install --upgrade pip setuptools

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt && \
    apk del .build-deps && \
    apk add --no-cache --update python3

COPY . .
RUN rm -rf UI
EXPOSE 80
ENTRYPOINT ["/bin/sh", "./scripts/start.sh"]

