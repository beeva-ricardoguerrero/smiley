FROM  drache93/resin-opencv:latest

RUN apt-get update && apt-get install -yq \
    python-dev python-picamera libpng-dev python-matplotlib python-setuptools python-yaml python-oauth2client python-requests python-scipy python-numpy && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install PyDrive

WORKDIR /usr/src/app

COPY ./* ./

RUN curl -sL https://deb.nodesource.com/setup_4.x | sudo bash -
RUN apt-get install nodejs -y
RUN npm config set unsafe-perm true
RUN npm install pm2 -g

CMD ["pm2", "start", "smiley.py", "&&", "pm2", "logs"]
