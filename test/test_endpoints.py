"""Tests for module services.
"""


import json
import os
import requests
import sys
import unittest

sys.path.insert(0, os.environ.get('PROJECT_ROOT_PATH'))

from src.basics import DATABASE_PARAMS, TITULO_TESOURO_CATEGORIES, TITULO_TESOURO_ACTIONS
from src.system_loader import drop_database, create_database, read_xlsx, populate_database


class TestTituloTesouroRequestHandler(unittest.TestCase):

    BASE_URL = 'http://localhost:8000/titulo_tesouro'

    def setUp(self):
        drop_database(verbose=False)
        create_database(verbose=False)

    def tearDownClass():
        drop_database(verbose=False)

    def test_create_with_no_post_body(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': 'No request body.'
        })

    def test_create_with_incomplete_post_body(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B'
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': "Mandatory fields ['mês', 'ano', 'ação', 'valor'] missing."
        })

    def test_create_with_non_string_categoria_titulo(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 1,
            'mês': 4,
            'ano': 2017,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"category" must be a string.'
        })

    def test_create_with_not_allowed_categoria_titulo(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'something',
            'mês': 4,
            'ano': 2017,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"category" must be one of {}.'.format(TITULO_TESOURO_CATEGORIES)
        })

    def test_create_with_non_integer_mes(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 'January',
            'ano': 2017,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"month" must be an integer.'
        })

    def test_create_with_invalid_mes(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 0,
            'ano': 2017,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"month" must be in interval [1, 12].'
        })

    def test_create_with_non_integer_ano(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 1,
            'ano': '2017',
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"year" must be an integer.'
        })

    def test_create_with_invalid_ano(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 1,
            'ano': 2000,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"year" must be greater than or equal to 2002.'
        })

    def test_create_with_non_string_acao(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 4,
            'ano': 2017,
            'ação': 1,
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"action" must be a string.'
        })

    def test_create_with_not_allowed_acao(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 4,
            'ano': 2017,
            'ação': 'aluguel',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"action" must be one of {}.'.format(TITULO_TESOURO_ACTIONS)
        })

    def test_create_with_non_numeric_valor(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 4,
            'ano': 2017,
            'ação': 'venda',
            'valor': '15000'
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"amount" must be a float or a int.'
        })

    def test_create_with_non_positive_valor(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 4,
            'ano': 2017,
            'ação': 'venda',
            'valor': 0
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {
            'err': '"amount" must be greater than zero.'
        })

    def test_create_with_valid_post_body(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 4,
            'ano': 2017,
            'ação': 'venda',
            'valor': 15000
        }))

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'categoria_titulo': 'NTN-B',
                'mês': 4,
                'ano': 2017,
                'ação': 'VENDA',
                'valor': 15000.00
            }
        })

    def test_create_with_duplicated_post_body(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 5,
            'ano': 2017,
            'ação': 'venda',
            'valor': 25000
        }))

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'categoria_titulo': 'NTN-B',
                'mês': 5,
                'ano': 2017,
                'ação': 'VENDA',
                'valor': 25000.00
            }
        })

        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 5,
            'ano': 2017,
            'ação': 'venda',
            'valor': 25000
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertIn('duplicate key value violates unique constraint "tesouro_direto_series_category_action_expire_at_key"',
            resp.json()['err'])

    def test_delete_with_non_integer_id(self):
        resp = requests.delete('{}/three'.format(TestTituloTesouroRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual('"titulo_id" must be an int.', resp.json()['err'])

    def test_delete_with_non_positive_id(self):
        resp = requests.delete('{}/0'.format(TestTituloTesouroRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual('"titulo_id" must be greater than zero.', resp.json()['err'])

    def test_delete_with_non_existing_id(self):
        resp = requests.delete('{}/7'.format(TestTituloTesouroRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 404)
        self.assertIn('err', resp.json())
        self.assertEqual('"titulo_id" has no register.', resp.json()['err'])

    def test_delete_with_existing_id(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 5,
            'ano': 2017,
            'ação': 'venda',
            'valor': 666
        }))

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'categoria_titulo': 'NTN-B',
                'mês': 5,
                'ano': 2017,
                'ação': 'VENDA',
                'valor': 666.00
            }
        })

        resp = requests.delete('{}/1'.format(TestTituloTesouroRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {
            'success': 'Deleted.'
        })

    def test_update_with_no_body(self):
        resp = requests.put('{}/1'.format(TestTituloTesouroRequestHandler.BASE_URL))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'No request body.')

    def test_update_with_empty_body(self):
        resp = requests.put('{}/1'.format(TestTituloTesouroRequestHandler.BASE_URL),
            data=json.dumps({}))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'Empty request body.')

    def test_update_with_non_integer_id(self):
        resp = requests.put('{}/three'.format(TestTituloTesouroRequestHandler.BASE_URL),
            data=json.dumps({
            'categoria_titulo': 'NTN-B Principal'
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual('"titulo_id" must be an int.', resp.json()['err'])

    def test_update_with_non_positive_id(self):
        resp = requests.put('{}/0'.format(TestTituloTesouroRequestHandler.BASE_URL),
            data=json.dumps({
            'categoria_titulo': 'NTN-B Principal'
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual('"titulo_id" must be greater than zero.', resp.json()['err'])

    def test_update_with_non_existing_id(self):
        resp = requests.put('{}/1'.format(TestTituloTesouroRequestHandler.BASE_URL),
            data=json.dumps({
            'categoria_titulo': 'NTN-B Principal'
        }))

        self.assertEqual(resp.status_code, 404)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], '"titulo_id" has no register.')

    def test_update_with_existing_id(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 5,
            'ano': 2017,
            'ação': 'venda',
            'valor': 666
        }))

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'categoria_titulo': 'NTN-B',
                'mês': 5,
                'ano': 2017,
                'ação': 'VENDA',
                'valor': 666.00
            }
        })

        resp = requests.put('{}/1'.format(TestTituloTesouroRequestHandler.BASE_URL),
            data=json.dumps({
            'ação': 'resgate'
        }))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'ação': 'resgate'
            }
        })

    def test_update_categoria_titulo(self):
        resp = requests.post(TestTituloTesouroRequestHandler.BASE_URL,
            data=json.dumps({
            'categoria_titulo': 'NTN-B',
            'mês': 5,
            'ano': 2017,
            'ação': 'venda',
            'valor': 666
        }))

        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json(), {
            'success': {
                'id': 1,
                'categoria_titulo': 'NTN-B',
                'mês': 5,
                'ano': 2017,
                'ação': 'VENDA',
                'valor': 666.00
            }
        })

        resp = requests.put('{}/1'.format(TestTituloTesouroRequestHandler.BASE_URL),
            data=json.dumps({
            'categoria_titulo': 'NTN-B Principal'
        }))

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'Field "categoria_titulo" cannot be updated')

    def test_read_non_positive_integer_in_data_inicio(self):
        resp = requests.get('{}/1'.format(TestTituloTesouroRequestHandler.BASE_URL), params={
            'data_inicio': '-2015-05'
        })

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'date not in format "YYYY-mm"')

    def test_read_non_integer_in_data_inicio(self):
        resp = requests.get('{}/1'.format(TestTituloTesouroRequestHandler.BASE_URL), params={
            'data_inicio': '2015-May'
        })

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], 'month must be a positive int.')

    def test_read_with_non_boolean_group_by(self):
        resp = requests.get('{}/1'.format(TestTituloTesouroRequestHandler.BASE_URL), params={
            'data_inicio': '2015-05',
            'group_by': 'True'
        })

        self.assertEqual(resp.status_code, 400)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], '"group_by" must be "true" or "false".')

    def test_read_with_non_existing_titulo_id(self):
        resp = requests.get('{}/1'.format(TestTituloTesouroRequestHandler.BASE_URL), params={
            'data_inicio': '2015-05'
        })

        self.assertEqual(resp.status_code, 404)
        self.assertIn('err', resp.json())
        self.assertEqual(resp.json()['err'], '"titulo_id" has no register.')

    def test_read_with_existing_titulo_id(self):
        values = read_xlsx('input-data.xlsx', verbose=False)
        populate_database(values, verbose=False)

        resp = requests.get('{}/1488'.format(TestTituloTesouroRequestHandler.BASE_URL), params={
            'data_inicio': '2014-05',
            'data_fim': '2016-10'
        })

        self.assertEqual(resp.status_code, 200)
        self.assertIn('success', resp.json())
        self.assertEqual(resp.json()['success'], {
            "id": 1488,
            "categoria_titulo": "NTN-F",
            "historico": [
                {
                    "valor_venda": "R$16.540.000,00",
                    "mes": 5,
                    "ano": 2014,
                    "valor_resgate": "R$10.630.000,00"
                },
                {
                    "valor_venda": "R$12.300.000,00",
                    "mes": 6,
                    "ano": 2014,
                    "valor_resgate": "R$6.330.000,00"
                },
                {
                    "valor_venda": "R$14.420.000,00",
                    "mes": 7,
                    "ano": 2014,
                    "valor_resgate": "R$56.270.000,00"
                },
                {
                    "valor_venda": "R$13.120.000,00",
                    "mes": 8,
                    "ano": 2014,
                    "valor_resgate": "R$12.240.000,00"
                },
                {
                    "valor_venda": "R$8.170.000,00",
                    "mes": 9,
                    "ano": 2014,
                    "valor_resgate": "R$14.920.000,00"
                },
                {
                    "valor_venda": "R$9.720.000,00",
                    "mes": 10,
                    "ano": 2014,
                    "valor_resgate": "R$14.510.000,00"
                },
                {
                    "valor_venda": "R$13.490.000,00",
                    "mes": 11,
                    "ano": 2014,
                    "valor_resgate": "R$8.880.000,00"
                },
                {
                    "valor_venda": "R$9.560.000,00",
                    "mes": 12,
                    "ano": 2014,
                    "valor_resgate": "R$9.680.000,00"
                },
                {
                    "valor_venda": "R$9.900.000,00",
                    "mes": 1,
                    "ano": 2015,
                    "valor_resgate": "R$13.400.000,00"
                },
                {
                    "valor_venda": "R$9.460.000,00",
                    "mes": 2,
                    "ano": 2015,
                    "valor_resgate": "R$10.480.000,00"
                },
                {
                    "valor_venda": "R$14.540.000,00",
                    "mes": 3,
                    "ano": 2015,
                    "valor_resgate": "R$12.370.000,00"
                },
                {
                    "valor_venda": "R$7.400.000,00",
                    "mes": 4,
                    "ano": 2015,
                    "valor_resgate": "R$10.220.000,00"
                },
                {
                    "valor_venda": "R$16.850.000,00",
                    "mes": 5,
                    "ano": 2015,
                    "valor_resgate": "R$10.260.000,00"
                },
                {
                    "valor_venda": "R$11.790.000,00",
                    "mes": 6,
                    "ano": 2015,
                    "valor_resgate": "R$7.750.000,00"
                },
                {
                    "valor_venda": "R$10.500.000,00",
                    "mes": 7,
                    "ano": 2015,
                    "valor_resgate": "R$61.860.000,00"
                },
                {
                    "valor_venda": "R$29.040.000,00",
                    "mes": 8,
                    "ano": 2015,
                    "valor_resgate": "R$16.290.000,00"
                },
                {
                    "valor_venda": "R$62.790.000,00",
                    "mes": 9,
                    "ano": 2015,
                    "valor_resgate": "R$18.550.000,00"
                },
                {
                    "valor_venda": "R$22.500.000,00",
                    "mes": 10,
                    "ano": 2015,
                    "valor_resgate": "R$11.350.000,00"
                },
                {
                    "valor_venda": "R$22.930.000,00",
                    "mes": 11,
                    "ano": 2015,
                    "valor_resgate": "R$10.180.000,00"
                },
                {
                    "valor_venda": "R$25.330.000,00",
                    "mes": 12,
                    "ano": 2015,
                    "valor_resgate": "R$11.810.000,00"
                },
                {
                    "valor_venda": "R$28.720.000,00",
                    "mes": 1,
                    "ano": 2016,
                    "valor_resgate": "R$61.830.000,00"
                },
                {
                    "valor_venda": "R$29.370.000,00",
                    "mes": 2,
                    "ano": 2016,
                    "valor_resgate": "R$16.280.000,00"
                },
                {
                    "valor_venda": "R$32.050.000,00",
                    "mes": 3,
                    "ano": 2016,
                    "valor_resgate": "R$23.700.000,00"
                },
                {
                    "valor_venda": "R$17.000.000,00",
                    "mes": 4,
                    "ano": 2016,
                    "valor_resgate": "R$17.150.000,00"
                }
            ]
        })

    def test_read_with_existing_titulo_id_and_grouped_by_year(self):
        values = read_xlsx('input-data.xlsx', verbose=False)
        populate_database(values, verbose=False)

        resp = requests.get('{}/1488'.format(TestTituloTesouroRequestHandler.BASE_URL), params={
            'data_inicio': '2014-05',
            'data_fim': '2016-10',
            'group_by': 'true'
        })

        self.assertEqual(resp.status_code, 200)
        self.assertIn('success', resp.json())
        self.assertEqual(resp.json()['success'], {
            'id': 1488,
            'categoria_titulo': 'NTN-F',
            'historico': [
                {
                    'ano': 2014,
                    'valor_venda': 'R$97.320.000,00',
                    'valor_resgate': 'R$133.460.000,00'
                },
                {
                    'ano': 2015,
                    'valor_venda': 'R$243.030.000,00',
                    'valor_resgate': 'R$194.520.000,00'
                },
                {
                    'ano': 2016,
                    'valor_venda': 'R$107.140.000,00',
                    'valor_resgate': 'R$118.960.000,00'
                }
            ]
        })


if __name__ == '__main__':
    unittest.main()
