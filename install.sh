#!/bin/bash

MAINDB='eventcreator'
DBUSER='eventcreator'
PASSWDDB=''
SERVER_NAME=''
CONTACT_EMAIL=''

# install dependencies
apt-get update -y && apt-get upgrade -y
apt-get -y install ufw
apt-get -y install python3 python3-dev
apt-get -y install mariadb-server postfix supervisor nginx git
apt-get -y install certbot python-certbot-nginx 
apt-get -y install python3-pip
pip3 install pipenv

# set up ufw
ufw allow ssh
ufw allow http
ufw allow 443/tcp
ufw --force enable

# install git repository
cd /var/
git clone https://github.com/MakeICT/event-creator.git
cd event-creator/
git checkout Flask 
git submodule update --init --recursive

# install python modules from pipfile
# pipenv install
pipenv install gunicorn pymysql

read -p "Copy settings and credentials now. Press [enter] to continue."

# install database
read -p "Drop and install database [Y/n]: " response
if [ "" = "$response" ] || [ "Y" = "$response" ] || [ "y" = "$response" ]; then
    mysql -uroot -e "CREATE DATABASE ${MAINDB} /*\!40100 DEFAULT CHARACTER SET utf8 */;"
    mysql -uroot -e "CREATE USER ${DBUSER}@localhost  IDENTIFIED BY '${PASSWDDB}';"
    mysql -uroot -e "GRANT ALL ON ${MAINDB}.* TO ${DBUSER}@'localhost';"
    mysql -uroot -e "FLUSH PRIVILEGES;"
fi

# install config files; needs manual intervention
cd src/
# python3 -c "import uuid; print(uuid.uuid4().hex)"
pipenv run python populate_db.py 



# install and start service
echo "[program:event_creator]
command=pipenv run gunicorn -b localhost:8000 -w 4 main:app
directory=/var/event-creator/src
user=root
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
" > /etc/supervisor/conf.d/event_creator.conf

supervisorctl reload

# configure nginx

rm /etc/nginx/sites-enabled/default

echo \
"
server {
    # listen on port 80 (http)
    listen 80;
    server_name _;
    location / {
        # redirect any requests to the same URL but on https
        return 301 https://\$host\$request_uri;
    }
}
server {
    # listen on port 443 (https)
    listen 443 ssl;
    server_name $SERVER_NAME;

    # write access and error logs to /var/log
    access_log /var/log/event-creator_access.log;
    error_log /var/log/event-creator_error.log;

    location / {
        # forward application requests to the gunicorn server
        proxy_pass http://localhost:8000;
        proxy_redirect off;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /static {
        # handle static files directly, without forwarding to the application
        alias /var/event-creator/src/static;
        expires 30d;
    }

}
" \
> /etc/nginx/sites-enabled/event_creator

# create certificates
certbot -n -d $SERVER_NAME -m $CONTACT_EMAIL --agree-tos --nginx
# certbot --nginx
service nginx restart