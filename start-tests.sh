#!/bin/bash


export PROJECT_ROOT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $PROJECT_ROOT_PATH


echo "Tests for class TituloTesouroRequestHandler"
python3 test/test_endpoints.py TestTituloTesouroRequestHandler
echo "Tests for class TituloTesouroRefinedRequestHandler"
python3 test/test_endpoints.py TestTituloTesouroRefinedRequestHandler
