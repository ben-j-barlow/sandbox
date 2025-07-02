In pyproject.toml

```
[tool.tox]
envlist = ["py39", "py310", "py311-10"]

[tool.tox.testenv]
deps = ["pytest"]
commands = ["pytest"]
```