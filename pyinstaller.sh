#!/bin/bash -e

./natup install python 3.6.4

PYTHON_BASE=test_base/install/python_3.6.4
PYTHON=$PYTHON_BASE/bin/python3

rm -rf venv-pyinstaller
if [ ! -e venv-pyinstaller ]; then
    $PYTHON -m venv venv-pyinstaller
fi

source venv-pyinstaller/bin/activate
pip install wheel
pip install -r requirements.txt
pip install pyinstaller==3.3.1

rm -rf build dist natup.spec
LD_LIBRARY_PATH=`realpath $PYTHON_BASE/lib` pyinstaller --onefile natup
