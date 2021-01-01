#!/bin/bash
python3 setup.py bdist_wheel
twine check dist/*
twine upload dist/*
