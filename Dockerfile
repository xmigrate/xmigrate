FROM python:3.8

# Create app directory
WORKDIR /app

# Install app dependencies
COPY requirements.txt ./

RUN pip install -r requirements.txt
RUN apt install sshpass, qemu-utils
RUN wget https://aka.ms/downloadazcopy-v10-linux  && tar -zxf ./downloadazcopy-v10-linux && mv ./azcopy_linux_amd64_10.5.1/azcopy /usr/bin    
# Bundle app source
COPY . /app

EXPOSE 8000
ENTRYPOINT [ "python", "app.py" ]
