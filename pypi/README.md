## Publish

Successful: `poetry publish --build --repository testpypi --username ben-j-barlow --password <pword>`

Everything else below was for learning (but unsuccessful).

In *.pypirc* file:

```
[testpypi] or [pypi]
username = __token__
password = <token>
repository = https://test.pypi.org/legacy/
```

To create environment variables to be used in .toml:
```
export TEST_PYPI_TOKEN=pypi-AgENdGVzdC5weXBpLm9yZwIkYThjOTAxYWEtNDkwZS00YmE0LTk4YjQtMWM5NzE5MzA1MTVhAAIqWzMsIjE2N2M1YjA0LTk1MmUtNDA2Yi04NjJhLTdhMTQzMjIyNmI4MCJdAAAGIPa3adQaq4S1Y3BjWa1v5lX-Th3P1PZgPnrEEvR-JM6B
```

To put in .toml:
```
[tool.poetry.repositories]
pypi = {
    url = "https://upload.pypi.org/legacy/"
}
testpypi = {
    url = "https://test.pypi.org/legacy/",
    username = "__token__",
    password = "your_token"
}

[tool.poetry.publish]
repository = "pypi"
username = "__token__"
password = "${PYPI_TOKEN}"
```
