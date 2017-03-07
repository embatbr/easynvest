# Easynvest

This is a code challenge for the company Easynvest. The complete description can be found in the file [description.pdf](./description.pdf). The challenge is divided in two parts:

1. Read data from a xlsx file representing a time series and generate a database;
2. Write a REST API to use the data (create, delete, read, aggregate, compare and etc.).


## Technology Stack

- Language: Python 3
- Framework: Falcon
- Server: Gunicorn
- Storage: PostgreSQL 9

The technology stack was chosen with the intention to easily achive the challenge's goal: assert my skills as software engineer without the need of the "best, fast and most complete" stack (as is the norm in a production environment).

Python is a programming language simple to understand, while Falcon and Gunicorn makes easy to start a web server with a REST API. PostgreSQL is a poweful and popular database, currently in version 9 (mature enough).


## Installing

**DISCLAIMER:** This challenge was developed in a Ubuntu 14.04 system. To execute it properly, is recommended to activate a Python virtual environment. If you have **virtualenvwrapper** installed, just type `mkvirtualenv easynvest --python=<PATH_TO_YOUR_PYTHON_3>`. Without a virtual environment, the commands **python** and **pip** may refer to version 2 in your system.

To install all dependencies, execute script *install.sh*, located in the project's root directory.


## Running

To create and populate the database. Execute the script *start-db.sh* (only once; a second attempt may raise an exception due to primary key collision).

The next step is to execute the REST API. Type `./start-app.sh` in your console to start the server locally listening to port 8000.


## Details

The bash file calls the module `main` through Gunicorn. This module creates all dependencies to be injected in the `EndpointExpositor` object. This object is responsible for bind each endpoint to its handler and expose them. The endpoints are:

#### /

Show the current state of the service. Used only as health checker.

#### /titulo_tesouro

Used by the first four functionalities described.
