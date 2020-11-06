FROM node AS stage

WORKDIR /app
COPY ./UI .
WORKDIR /app/xmigrate-ui
RUN yarn && yarn build

FROM nginx:1.16-alpine

RUN wget  https://azcopyvnext.azureedge.net/release20201021/azcopy_linux_amd64_10.6.1.tar.gz && \
    tar -zxf ./azcopy_linux_amd64_10.6.1.tar.gz && \
    mv ./azcopy_linux_amd64_10.6.1/azcopy /usr/bin  


WORKDIR /app

RUN apk update && \
    apk add --no-cache bash py-pip && \
    apk add --no-cache qemu-img sshpass make g++ python3-dev libffi-dev openssl-dev && \
    pip3 install --upgrade pip setuptools \
    pip install azure-cli 
    

COPY --from=stage /app/xmigrate-ui/build /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p ./logs/ansible/ && mkdir osdisks && touch ./logs/ansible/log.txt && touch ./logs/ansible/migration_log.txt

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt && \
    apk add --no-cache --update python3

COPY . .
RUN rm -rf UI
EXPOSE 80
ENTRYPOINT ["/bin/sh", "./scripts/start.sh"]

