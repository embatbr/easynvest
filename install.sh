#!/bin/bash


# Installing database
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# Python dependencies
sudo apt-get install -y libpq-dev postgresql-client postgresql-client-common # needed for psycopg2
pip install --upgrade -r resources/python-deps.txt

# Creating database
sudo postgres -D /usr/local/pgsql/data >logs/pgsql-server 2>&1
sudo -u postgres createuser --superuser easynvest
sudo -u postgres createdb -O easynvest easynvest
