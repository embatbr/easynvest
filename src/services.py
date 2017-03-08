"""Defines the service logic.
"""


from babel.numbers import format_currency
import pendulum
import psycopg2

from src.basics import TITULO_TESOURO_CATEGORIES, TITULO_TESOURO_ACTIONS
from src.basics import TRANSACTIONS_PATH, DATABASE_PARAMS, INITIAL_DATE


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
            'update-tesouro-direto': open('{}/update-tesouro-direto.sql'.format(TRANSACTIONS_PATH)).read(),
            'read-history': open('{}/read-history.sql'.format(TRANSACTIONS_PATH)).read(),
            'read-history-grouped': open('{}/read-history-grouped.sql'.format(TRANSACTIONS_PATH)).read(),
            'get-category': open('{}/get-category.sql'.format(TRANSACTIONS_PATH)).read()
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
        assert year >= INITIAL_DATE.year, '"year" must be greater than or equal to {}.'.format(INITIAL_DATE.year)

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

    def _validade_date(self, date):
        unpacked = date.split('-')
        assert len(unpacked) == 2, 'date not in format "YYYY-mm"'
        (year, month) = unpacked
        assert year.isdigit(), 'year must be a positive int.'
        self._validate_year(int(year))
        assert month.isdigit(), 'month must be a positive int.'
        self._validate_month(int(month))

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

            assert 'categoria_titulo' not in data, 'Field "categoria_titulo" cannot be updated'

            fields = list()

            if 'mês' in data:
                self._validate_month(data['mês'])
                month = data['mês']
            if 'ano' in data:
                self._validate_year(data['ano'])
                year = data['ano']
            if 'ação' in data:
                self._validate_action(data['ação'].upper())
                fields.append("action = '{}'".format(data['ação'].upper()))
            if 'valor' in data:
                self._validate_amount(data['valor'])
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

    def read(self, titulo_id, params):
        self._validate_titulo_id(titulo_id)

        start_date = pendulum.create(2002, 1, 1, 0, 0, 0)
        end_date = pendulum.now()
        group_by_year = False

        if 'data_inicio' in params:
            self._validade_date(params['data_inicio'])
            start_date = pendulum.strptime('{}-01'.format(params['data_inicio']), '%Y-%m-%d')
        if 'data_fim' in params:
            self._validade_date(params['data_fim'])
            end_date = pendulum.strptime('{}-01'.format(params['data_fim']), '%Y-%m-%d')
        if 'group_by' in params:
            assert params['group_by'] in ('true', 'false'), '"group_by" must be "true" or "false".'
            group_by_year = True if params['group_by'] == 'true' else False

        start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

        conn = psycopg2.connect(**DATABASE_PARAMS)
        cur = conn.cursor()

        cur.execute(self.queries['get-category'].format(titulo_id))
        result_get_category = cur.fetchall()
        category = None
        result_history = list()

        if result_get_category:
            category = result_get_category[0][0]

            if group_by_year:
                cur.execute(self.queries['read-history-grouped'].format(category, start_date, end_date))
                result_history = cur.fetchall()

                result_history = [{'ano': int(res[0]), 'valor_venda': format_currency(float(res[1]), 'BRL'),
                                   'valor_resgate': format_currency(float(res[2]), 'BRL')}
                                   for res in result_history]
            else:
                cur.execute(self.queries['read-history'].format(category, start_date, end_date))
                result_history = cur.fetchall()

                result_history = [{'mes': int(res[0]), 'ano': int(res[1]), 'valor_venda': format_currency(float(res[2]), 'BRL'),
                                   'valor_resgate': format_currency(float(res[3]), 'BRL')}
                                   for res in result_history]

        cur.close()
        conn.close()

        if not result_get_category:
            return False

        return {
            'id': int(titulo_id),
            'categoria_titulo': category,
            'historico' : result_history
        }
