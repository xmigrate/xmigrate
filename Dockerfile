FROM python:3.8

# Create app directory
WORKDIR /app

# Install app dependencies
COPY requirements.txt ./

RUN pip install -r requirements.txt
RUN apt install sshpass

# Bundle app source
COPY . /app

EXPOSE 8000
ENTRYPOINT [ "python", "app.py" ]
