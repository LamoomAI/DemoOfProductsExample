#!/bin/bash

rm -f layer.zip
rm -rf layer
mkdir -p layer/python

# Install the project dependencies into the layer directory
poetry export -f requirements.txt --without-hashes | pip install -r /dev/stdin --python-version 3.11 --platform manylinux2014_x86_64 --implementation cp --only-binary=:all: --upgrade -t layer/python/lib/python3.11/site-packages

# Package the layer directory into a zip file
cd layer && zip -r ../layer.zip . && cd .. && rm -rf layer
