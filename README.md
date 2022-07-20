# Utils

## Description

I found myself using the same code over and over across projects so I created a package to import my own code faster.

## Install

```bash
pip install dgarbsutils
```

## Usage

```python
from dgarbsutils import utils, awsUtils
```

## Build

```bash
python -m build
```

## Upload

```bash
python3 -m twine upload --repository pypi dist/*
python3 -m twine upload --repository nexus dist/*
```
