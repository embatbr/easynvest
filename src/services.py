"""Defines the service logic.
"""


import pendulum
import psycopg2

from src.basics import TITULO_TESOURO_CATEGORIES, TITULO_TESOURO_ACTIONS
from src.basics import TRANSACTIONS_PATH, DATABASE_PARAMS


class TituloTesouroCRUD(object):
    """Executes CRUD operations for titulo tesouro.
    """

    def __init__(self):
        self.queries = {
            'load-input-data': open('{}/load-input-data.sql'.format(TRANSACTIONS_PATH)).read(),
            'get-id': open('{}/get-id.sql'.format(TRANSACTIONS_PATH)).read(),
            'count-tesouro-direto': open('{}/count-tesouro-direto.sql'.format(TRANSACTIONS_PATH)).read(),
            'delete-tesouro-direto': open('{}/delete-tesouro-direto.sql'.format(TRANSACTIONS_PATH)).read(),
            'get-expire_at': open('{}/get-expire_at.sql'.format(TRANSACTIONS_PATH)).read(),
            'update-tesouro-direto': open('{}/update-tesouro-direto.sql'.format(TRANSACTIONS_PATH)).read()
        }

    def _validate_category(self, category):
        assert isinstance(category, str), '"category" must be a string.'
        assert category in TITULO_TESOURO_CATEGORIES, \
            '"category" must be one of {}.'.format(TITULO_TESOURO_CATEGORIES)

    def _validate_month(self, month):
        assert isinstance(month, int), '"month" must be an integer.'
        assert 1 <= month <= 12, '"month" must be in interval [1, 12].'

    def _validate_year(self, year):
        assert isinstance(year, int), '"year" must be an integer.'
        assert year >= 2002, '"year" must be greater than or equal to 2002.'

    def _validate_action(self, action):
        assert isinstance(action, str), '"action" must be a string.'
        assert action.upper() in TITULO_TESOURO_ACTIONS, \
            '"action" must be one of {}.'.format(TITULO_TESOURO_ACTIONS)

    def _validate_amount(self, amount):
        assert isinstance(amount, float) or isinstance(amount, int), '"amount" must be a float or a int.'
        assert amount > 0, '"amount" must be greater than zero.'

    def _validate_titulo_id(self, titulo_id):
        assert titulo_id.isdigit(), '"titulo_id" must be an int.'
        titulo_id = int(titulo_id)
        assert titulo_id > 0, '"titulo_id" must be greater than zero.'

    def create(self, category, month, year, action, amount):
        self._validate_category(category)
        self._validate_month(month)
        self._validate_year(year)
        self._validate_action(action)
        self._validate_amount(amount)

        if isinstance(amount, int):
            amount = float(amount)

        action = action.upper()
        expire_at = pendulum.create(year, month, 1, 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')
        amount = round(amount, 2)

        conn = psycopg2.connect(**DATABASE_PARAMS)
        cur = conn.cursor()

        value = "('{}', '{}', '{}', {})".format(category, action, expire_at, amount)
        cur.execute(self.queries['load-input-data'].format(value))

        cur.execute(self.queries['get-id'].format(category, action, expire_at))
        _id = cur.fetchall()[0][0]

        cur.close()
        conn.close()

        return {
            'id': _id,
            'categoria_titulo': category,
            'mês': month,
            'ano': year,
            'ação': action,
            'valor': amount
        }

    def delete(self, titulo_id):
        self._validate_titulo_id(titulo_id)

        conn = psycopg2.connect(**DATABASE_PARAMS)
        cur = conn.cursor()

        cur.execute(self.queries['count-tesouro-direto'].format(titulo_id))
        count = cur.fetchall()[0][0]

        if count > 0:
            cur.execute(self.queries['delete-tesouro-direto'].format(titulo_id))

        cur.close()
        conn.close()

        if count == 0:
            return False
        return True

    def update(self, titulo_id, data):
        self._validate_titulo_id(titulo_id)

        conn = psycopg2.connect(**DATABASE_PARAMS)
        cur = conn.cursor()

        cur.execute(self.queries['get-expire_at'].format(titulo_id))
        result = cur.fetchall()

        if result:
            year = int(result[0][0])
            month = int(result[0][1])

            fields = list()
            if 'categoria_titulo' in data:
                self._validate_category(data['categoria_titulo'])
                fields.append("category = '{}'".format(data['categoria_titulo']))
            if 'mês' in data:
                self._validate_action(data['mês'])
                month = data['mês']
            if 'ano' in data:
                self._validate_amount(data['ano'])
                year = data['ano']
            if 'ação' in data:
                self._validate_month(data['ação'].upper())
                fields.append("action = '{}'".format(data['ação'].upper()))
            if 'valor' in data:
                self._validate_year(data['valor'])
                fields.append("amount = {}".format(data['valor']))

            expire_at = pendulum.create(year, month, 1, 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')
            fields.append("expire_at = '{}'".format(expire_at))

            fields = ', '.join(fields)

            cur.execute(self.queries['update-tesouro-direto'].format(fields, titulo_id))

        cur.close()
        conn.close()

        if result:
            return True
        return False
