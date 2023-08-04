FROM node:18.14.2 AS stage

WORKDIR /app

COPY ./UI .

WORKDIR /app/xmigrate-ui

RUN npm install
RUN npm run build

FROM ubuntu:18.04

SHELL ["/bin/bash", "-c"]

WORKDIR /app

RUN apt update
RUN apt install -y sshpass python3.7 python3-pip qemu-utils wget nginx
RUN if [[ "$(uname -m)" == "x86_64" ]]; then \
        echo "Attempting to download azcopy for x86_64..." && \
        wget -O azcopyamdv10.6.1.tar.gz https://azcopyvnext.azureedge.net/release20201021/azcopy_linux_amd64_10.6.1.tar.gz && \
        tar -zxf ./azcopyamdv10.6.1.tar.gz --strip-components=1 && \
        mv ./azcopy /usr/bin && \
        chmod +x /usr/bin/azcopy && \
        echo "azcopy installation for x86_64 succeeded." ; \
    elif [[ "$(uname -m)" == "aarch64" ]]; then \
        echo "Attempting to download azcopy for aarch64..." && \
        wget -O azcopyarm.tar.gz https://aka.ms/downloadazcopy-v10-linux-arm64 && \
        tar -zxf ./azcopyarm.tar.gz --strip-components=1 && \
        mv ./azcopy /usr/bin && \
        chmod +x /usr/bin/azcopy && \
        echo "azcopy installation for aarch64 succeeded." ; \
    else \
        echo "Unexpected architecture; azcopy was not installed." && \
        exit 1 ; \
    fi

COPY nginx.conf /etc/nginx/nginx.conf
COPY requirements.txt requirements.txt

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
ENV AZCOPY_BUFFER_GB=0.3
ENV ANSIBLE_HOST_KEY_CHECKING=False

RUN python3.7 -m pip install -U pip --no-cache-dir
RUN python3.7 -m pip install setuptools-rust --no-cache-dir
RUN python3.7 -m pip install --no-use-pep517 --upgrade pyOpenSSL --no-cache-dir
RUN python3.7 -m pip install -r requirements.txt --no-cache-dir
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/lib/apt/ /var/cache

COPY --from=stage /app/xmigrate-ui/build /usr/share/nginx/html/
COPY . .

RUN rm -rf UI

EXPOSE 80

ENTRYPOINT ["/bin/bash", "./scripts/start.sh"]

