# movai-core-shared
The movai core shared provides all the basic functionality such as logging and API 
for getting environment variables which all of the MOV.AI platform components require

## Usage
A package encapsulating all of the platform basic functionality

> Prerequisites : None

## Build

The complete build process:
- a python module building step which will create a `.whl` file


## build pip module

    rm dist/*
    python3 -m build .

## install pip module locally

    python3 -m venv .testenv
    source .testenv/bin/activate
    python3 -m pip install --no-cache-dir \
    --index-url="https://artifacts.cloud.mov.ai/repository/pypi-experimental/simple" \
    --extra-index-url https://pypi.org/simple \
    ./dist/*.whl
