"""Defines the service logic.
"""


import pendulum
import psycopg2

from src.basics import TITULO_TESOURO_CATEGORIES, TITULO_TESOURO_ACTIONS
from src.basics import TRANSACTIONS_PATH, DATABASE_PARAMS


class TituloTesouroCRUD(object):
    """Executes CRUD operations for titulo tesouro.
    """

    def create(self, category, month, year, action, amount):
        assert isinstance(category, str), '"category" must be a string.'
        assert category in TITULO_TESOURO_CATEGORIES, \
            '"category" must be one of {}.'.format(TITULO_TESOURO_CATEGORIES)

        assert isinstance(month, int), '"month" must be an integer.'
        assert 1 <= month <= 12, '"month" must be in interval [1, 12].'

        assert isinstance(year, int), '"year" must be an integer.'
        assert year >= 2002, '"year" must be greater than or equal to 2002.'

        assert isinstance(action, str), '"action" must be a string.'
        assert action in TITULO_TESOURO_ACTIONS, \
            '"action" must be one of {}.'.format(TITULO_TESOURO_CATEGORIES)

        assert isinstance(amount, float) or isinstance(amount, int), '"amount" must be a float or a int.'
        assert amount > 0, '"amount" must be greater than zero.'

        with open('{}/load-input-data.sql'.format(TRANSACTIONS_PATH)) as f:
            transaction = f.read()

        expire_at = pendulum.create(year, month, 1, 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')
        amount = round(amount, 2)

        conn = psycopg2.connect(**DATABASE_PARAMS)
        cur = conn.cursor()

        action = action.upper()
        value = "('{}', '{}', '{}', {})".format(category, action, expire_at, amount)
        transaction = transaction.format(value)
        cur.execute(transaction)

        query = "SELECT id FROM category_ids WHERE category = '{}'".format(category)
        cur.execute(query)
        _id = cur.fetchall()[0][0]

        cur.close()
        conn.close()

        return {
            'id': _id,
            'categoria_titulo': category,
            'mês': month,
            'ano': year,
            'valor': amount
        }
