# movai-core-shared
movai-core-shared provides basic functionality that all platform requires, such as:
- constants
- exceptions
- logging
- environment variables
- structures for messaging

## Usage

### Versioning

| EE     | movai-core-shared branch | Backend version |
|--------|--------------------------|-----------------|
| 2.4.1  | releases/3.0             | 3.0.x.y         |
| 2.4.4  | releases/3.3             | 3.3.x.y         |
| 2.5.0  | main                     | -               |

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
