"""Builds all objects and inject dependencies
"""


import falcon
import logging

from src.endpoints import EndpointExpositor
from src.services import TituloTesouroCRUD


logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S %Z',
                    level=getattr(logging, 'INFO', 'DEBUG'))

logging.info('Starting web service.')

falcon_api = application = falcon.API()

endpoint_expositor = EndpointExpositor(falcon_api, TituloTesouroCRUD())
endpoint_expositor.expose()

logging.info('Web service listening.\n')
