apt-get install -y software-properties-common && /
add-apt-repository ppa:deadsnakes/ppa -y && /
apt-get update -y && /
apt-get install python3-pip python3.7-dev -y && /
apt-get install python3.7 -y && /
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.4 1
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
update-alternatives --set python3 /usr/bin/python3.7 -y && /
apt-get install build-essential libpq-dev libssl-dev openssl libffi-dev zlib1g-dev -y && /


apt install libaio1 libc6 libcurl3-gnutls libglib2.0-0 librados2 librbd1 libuuid1 zlib1g wget -y