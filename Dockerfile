FROM node AS stage

WORKDIR /app
COPY ./UI .
WORKDIR /app/xmigrate-ui
RUN yarn && yarn build

FROM nginx:1.16-alpine

RUN mkdir app  && mkdir UI
COPY --from=stage /app/xmigrate-ui/build /UI
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apk update && apk add make && \
    apk add --no-cache --virtual .build-deps g++ python3-dev libffi-dev openssl-dev && \
    pip3 install --upgrade pip setuptools && \
    pip3 install -r requirements.txt && \
    apk del .build-deps && \
    apk add --no-cache --update python3
COPY nginx.conf /etc/nginx/nginx.conf
COPY . .
RUN rm -rf UI
EXPOSE 8000
ENTRYPOINT [ "python", "app.py" ]
