#!/usr/bin/python
# -*- coding: utf-8 -*-

from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

# Create pip-compatible dependency list
packages = Project().parsed_pipfile.get('packages', {})
deps = convert_deps_to_pip(packages, r=False)

with open('requirements.txt', 'w') as f:
    f.write('\n'.join(deps))

packages = Project().parsed_pipfile.get('dev-packages', {})
deps = convert_deps_to_pip(packages, r=False)

with open('dev-requirements.txt', 'w') as f:
    f.write('\n'.join(deps))
