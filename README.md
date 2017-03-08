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

The next step is to execute the REST API. Type `./start-app.sh` in your console to start the server locally listening to port 8000 (default).

To query the database, log in using `psql -h localhost -d easynvest -U easynvest`. The password can be seen in the file **src/basics.py**.


## Details

The bash file calls the module `main` through Gunicorn. This module creates all dependencies to be injected in the `EndpointExpositor` object. This object is responsible for bind each endpoint to its handler and expose them.

### Endpoints

#### /

Shows the current state of the service. Used only as health checker.

#### /titulo_tesouro

Used by the first four functionalities described.

###### 1. POST /titulo_tesouro

**Request body:**

```json
{
    "categoria_titulo": "NTN-B",
    "mês": 4,
    "ano": 2017,
    "ação": "venda",
    "valor": 15321.99
}
```

The types of each parameter can be guessed: string, int, int, string and float (or int). The field **valor** may receive a number such as 15321.99, 15321.99999 or 15.321. In case of a float with more than 2 decimals, it is rounded.

**Response body:**

```json
{
    "success": {
        "id": <NEXT_INTEGER>
        "categoria_titulo": "NTN-B",
        "mês": 4,
        "ano": 2017,
        "ação": "venda",
        "valor": 15321.99
    }
}
```

or

```json
{
    "err": <ERROR_MESSAGE>
}
```

###### 2. DELETE /titulo_tesouro/{id}

**Response body:**

```json
{
  "success": "Deleted."
}
```

or

```json
{
  "err": "\"titulo_id\" has no register."
}
```

###### 3. PUT /titulo_tesouro/{id}

**Request body:** similar to the (1), without the field "categoria_titulo" and with the others optional.

**Response body:** the same as the response, added the field "id".

###### 4. GET /titulo_tesouro/{id}

**Parameters:**

- data_inicio (optional): in the format **YYYY-mm**
- data_fim (optional): in the format **YYYY-mm**
- group_by (optional): boolean

**Response body:** as defined in the description

###### 5. GET /titulo_tesouro/comparar/

TODO

###### 6. GET /titulos_tesouro/venda/{id} and 7. GET /titulos_tesouro/resgate/{id}

**Parameters:** similar to (4)

**Response body:** for path **titulo_tesouro/venda/1488?data_inicio=2014-05&data_fim=2016-09**

```json
{
    "success": {
        "id": 1488,
        "categoria_titulo": "NTN-F",
        "valores_venda": [
            {
                "valor": "R$16.540.000,00",
                "mes": 5,
                "ano": 2014
            },
            ...
            {
                "valor": "R$17.000.000,00",
                "mes": 4,
                "ano": 2016
            }
        ]
    }
}
```

If the parameter **groupby=true** is present, the `mes` key is not present and **valor** is the summarization in the period.


## Testing

Test coverage in this project is not high (and this is a good thing). Since many unit tests can be replaced by a simple `assert` and the project was design in a way that module `services` is only used by module `endpoints`, all failures the first may raise will appear when testing the second.

The package `unittest` from Python is used for both unit tests and "system/integration tests". All tests are found in directory *tests*.
