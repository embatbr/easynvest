"""Basic data and functions.
"""


import os


PROJECT_ROOT_PATH = os.environ.get('PROJECT_ROOT_PATH')

DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
DATABASE_PORT = os.environ.get('DATABASE_PORT', '5432')
DATABASE_USER = os.environ.get('DATABASE_USER', 'easynvest')
DATABASE_DBNAME = os.environ.get('DATABASE_DBNAME', 'easynvest')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', 'password')
DATABASE_PARAMS = {
    'host': DATABASE_HOST,
    'port': DATABASE_PORT,
    'user': DATABASE_USER,
    'dbname': DATABASE_DBNAME,
    'password': DATABASE_PASSWORD
}

RESOURCES_PATH = '{}/resources'.format(PROJECT_ROOT_PATH)
SCHEMAS_PATH = '{}/schemas'.format(RESOURCES_PATH)
TRANSACTIONS_PATH = '{}/transactions'.format(RESOURCES_PATH)

TITULO_TESOURO_CATEGORIES = ['LTN', 'LFT', 'NTN-B', 'NTN-B Principal', 'NTN-C', 'NTN-F']
TITULO_TESOURO_ACTIONS = ['VENDA', 'RESGATE']
