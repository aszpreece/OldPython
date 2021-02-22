#!/bin/bash
cd "$(dirname "$0")"

sudo apt-get update
sudo apt-get install mariadb-server
sudo /etc/init.d/mysql start


sudo mysql -u root < ./schema/create_schema.sql

# To create a user
# CREATE USER 'user1'@localhost IDENTIFIED BY 'password1';
# GRANT ALL PRIVILEGES ON 'yourDB'.* TO 'user1'@localhost;
# FLUSH PRIVILEGES;

# sudo mysql --defaults-extra-file=./connection.cnf
