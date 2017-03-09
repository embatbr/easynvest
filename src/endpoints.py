"""Defines the endpoints and their handling logic.
"""


import falcon
import json
import logging


class EndpointExpositor(object):
    """Exposes the endpoints, divided in endpoints for data and metadata. The
    endpoints for data are those defined in the challenge description. Endpoints
    for metadata are all others.
    """

    def __init__(self, falcon_api, titulo_tesouro_crud):
        self.falcon_api = falcon_api

        titulo_tesouro_request_handler = TituloTesouroRequestHandler(titulo_tesouro_crud)
        titulo_tesouro_compare_request_handler = TituloTesouroCompareRequestHandler(titulo_tesouro_crud)
        titulo_tesouro_by_action_request_handler = TituloTesouroByActionRequestHandler(titulo_tesouro_crud)

        self.endpoint_mapping = {
            '/': None,
            '/titulo_tesouro': titulo_tesouro_request_handler,
            '/titulo_tesouro/{titulo_id}': titulo_tesouro_request_handler,
            '/titulo_tesouro/comparar/': titulo_tesouro_compare_request_handler,
            '/titulo_tesouro/venda/{titulo_id}': titulo_tesouro_by_action_request_handler,
            '/titulo_tesouro/resgate/{titulo_id}': titulo_tesouro_by_action_request_handler
        }

        endpoints = list(self.endpoint_mapping.keys())
        self.endpoint_mapping['/'] = HelpRequestHandler(endpoints)

    def expose(self):
        for (endpoint, handler) in self.endpoint_mapping.items():
            self.falcon_api.add_route(endpoint, handler)
            logging.info('Endpoint "{}" exposed.'.format(endpoint))

        logging.info('All endpoints exposed.')


class RequestHandler(object):
    """Superclass for all request handlers.
    """

    def on_post(self, req, resp):
        logging.info('POST request received at endpoint "{}"'.format(req.path))

    def on_delete(self, req, resp):
        logging.info('DELETE request received at endpoint "{}"'.format(req.path))

    def on_put(self, req, resp):
        logging.info('PUT request received at endpoint "{}"'.format(req.path))

    def on_get(self, req, resp):
        logging.info('GET request received at endpoint "{}"'.format(req.path))

    def set_response_status_code(self, resp, code):
        resp.status = getattr(falcon, 'HTTP_{}'.format(code))
        logging.info('Response status code: {}\n'.format(resp.status))

    def err_bad_request(self, resp, message):
        logging.error(message)

        resp.body = json.dumps({
            'err': message
        })
        self.set_response_status_code(resp, 400)

    def err_not_found(self, resp, message):
        logging.error(message)

        resp.body = json.dumps({
            'err': message
        })
        self.set_response_status_code(resp, 404)

    def ok(self, resp, message):
        logging.info(message)

        resp.body = json.dumps({
            'success': message
        })
        self.set_response_status_code(resp, 200)

    def created(self, resp, message):
        logging.info(message)

        resp.body = json.dumps({
            'success': message
        })
        self.set_response_status_code(resp, 201)


class HelpRequestHandler(RequestHandler):
    """Checks system health and provides instructions.
    """

    def __init__(self, endpoints):
        super(HelpRequestHandler, self).__init__()

        self.endpoints = endpoints

    def on_get(self, req, resp):
        super(HelpRequestHandler, self).on_get(req, resp)

        resp.body = 'System healthy.\n\nEndpoints: {}'.format(self.endpoints)

        self.set_response_status_code(resp, 200)


class TituloTesouroRequestHandler(RequestHandler):
    """Handler for POST in endpoint "titulo_tesouro".
    """

    def __init__(self, titulo_tesouro_crud):
        super(TituloTesouroRequestHandler, self).__init__()

        self.titulo_tesouro_crud = titulo_tesouro_crud

    def _check_missing_fields(self, body):
        missing_fields = list()

        fields = ['categoria_titulo', 'mês', 'ano', 'ação', 'valor']
        for field in fields:
            if field not in body:
                missing_fields.append(field)

        return missing_fields

    def on_post(self, req, resp):
        super(TituloTesouroRequestHandler, self).on_post(req, resp)

        if req.content_length == 0:
            self.err_bad_request(resp, 'No request body.')
            return

        stream = req.bounded_stream.read().decode('utf8')
        body = json.loads(stream)

        missing_fields = self._check_missing_fields(body)
        if missing_fields:
            self.err_bad_request(resp, 'Mandatory fields {} missing.'.format(missing_fields))
            return

        try:
            ret = self.titulo_tesouro_crud.create(body['categoria_titulo'], body['mês'],
                                                  body['ano'], body['ação'], body['valor'])

            self.created(resp, ret)
        except Exception as e:
            self.err_bad_request(resp, str(e))

    def on_delete(self, req, resp, titulo_id):
        super(TituloTesouroRequestHandler, self).on_delete(req, resp)

        try:
            ret = self.titulo_tesouro_crud.delete(titulo_id)

            if ret:
                self.ok(resp, 'Deleted.')
            else:
                self.err_not_found(resp, '"titulo_id" has no register.')
        except Exception as e:
            self.err_bad_request(resp, str(e))

    def on_put(self, req, resp, titulo_id):
        super(TituloTesouroRequestHandler, self).on_put(req, resp)

        if req.content_length == 0:
            self.err_bad_request(resp, 'No request body.')
            return

        stream = req.bounded_stream.read().decode('utf8')
        body = json.loads(stream)

        if not body:
            self.err_bad_request(resp, 'Empty request body.')
            return

        try:
            ret = self.titulo_tesouro_crud.update(titulo_id, body)

            if ret:
                body['id'] = int(titulo_id)
                self.ok(resp, body)
            else:
                self.err_not_found(resp, '"titulo_id" has no register.')
        except Exception as e:
            self.err_bad_request(resp, str(e))

    def on_get(self, req, resp, titulo_id):
        super(TituloTesouroRequestHandler, self).on_get(req, resp)

        params = req.params

        try:
            ret = self.titulo_tesouro_crud.read_history(titulo_id, params)

            if ret:
                self.ok(resp, ret)
            else:
                self.err_not_found(resp, '"titulo_id" has no register.')
        except Exception as e:
            self.err_bad_request(resp, str(e))


class TituloTesouroCompareRequestHandler(RequestHandler):
    """Handler for POST in endpoint "titulo_tesouro/comparar".
    """

    def __init__(self, titulo_tesouro_crud):
        super(TituloTesouroCompareRequestHandler, self).__init__()

        self.titulo_tesouro_crud = titulo_tesouro_crud

    def on_get(self, req, resp):
        super(TituloTesouroCompareRequestHandler, self).on_get(req, resp)

        params = req.params

        try:
            ret = self.titulo_tesouro_crud.compare(params)

            if ret:
                self.ok(resp, ret)
            else:
                self.err_not_found(resp, 'One of the ids was not found.')
        except Exception as e:
            self.err_bad_request(resp, str(e))


class TituloTesouroByActionRequestHandler(RequestHandler):
    """Handler for POST in endpoints "titulo_tesouro/venda" and "titulo_tesouro/resgate".
    """

    def __init__(self, titulo_tesouro_crud):
        super(TituloTesouroByActionRequestHandler, self).__init__()

        self.titulo_tesouro_crud = titulo_tesouro_crud

    def on_get(self, req, resp, titulo_id):
        super(TituloTesouroByActionRequestHandler, self).on_get(req, resp)

        action = req.path.split('/')[2]
        params = req.params

        try:
            ret = self.titulo_tesouro_crud.read_by_action(titulo_id, action, params)

            if ret:
                self.ok(resp, ret)
            else:
                self.err_not_found(resp, '"titulo_id" has no register for action "{}".'.format(action))
        except Exception as e:
            self.err_bad_request(resp, str(e))
